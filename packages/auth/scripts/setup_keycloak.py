#!/usr/bin/env python3
"""
Consolidated Keycloak Setup Script
Creates Keycloak realm and populates it with users from database (if available)
or falls back to hardcoded test users.
"""

import asyncio
import os
import time
from typing import Optional, List, Dict, Any
import requests

# Optional database imports
try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import text
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


class KeycloakSetup:
    def __init__(self):
        self.base_url = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
        self.admin_username = "admin"
        self.admin_password = "admin"
        self.master_realm = "master"
        self.app_realm = "spending-monitor"
        self.client_id = "spending-monitor"
        self.access_token: Optional[str] = None
        
        # Try to set up database connection if available
        self.db_available = False
        self.engine = None
        self.async_session = None
        
        if DB_AVAILABLE:
            try:
                database_url = os.getenv(
                    'DATABASE_URL', 
                    'postgresql+asyncpg://user:password@localhost:5432/spending-monitor'
                )
                self.engine = create_async_engine(database_url, echo=False)
                self.async_session = sessionmaker(
                    self.engine, class_=AsyncSession, expire_on_commit=False
                )
                self.db_available = True
                self.log("📦 Database connection available - will sync users from DB")
            except Exception as e:
                self.log(f"ℹ️  Database not available: {e}")
                self.log("   Will use hardcoded test users instead")

    def log(self, message: str, level: str = "INFO"):
        """Print formatted log message"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def get_admin_token(self) -> bool:
        """Get admin access token from master realm"""
        try:
            url = f"{self.base_url}/realms/{self.master_realm}/protocol/openid-connect/token"
            data = {
                "username": self.admin_username,
                "password": self.admin_password,
                "grant_type": "password",
                "client_id": "admin-cli",
            }

            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.log("✅ Admin token obtained successfully")
            return True

        except Exception as e:
            self.log(f"❌ Failed to get admin token: {e}", "ERROR")
            return False

    def create_realm(self) -> bool:
        """Create a new realm for the spending-monitor application"""
        try:
            url = f"{self.base_url}/admin/realms"
            headers = {"Authorization": f"Bearer {self.access_token}"}

            realm_data = {
                "realm": self.app_realm,
                "enabled": True,
                "displayName": "Spending Monitor",
                "displayNameHtml": '<div class="kc-logo-text"><span>Spending Monitor</span></div>',
                "attributes": {"frontendUrl": "http://localhost:8080"},
            }

            response = requests.post(url, json=realm_data, headers=headers, timeout=10)

            if response.status_code == 201:
                self.log(f"✅ Realm '{self.app_realm}' created successfully")
                return True
            elif response.status_code == 409:
                self.log(f"ℹ️  Realm '{self.app_realm}' already exists")
                return True
            else:
                self.log(f"❌ Failed to create realm: {response.status_code}")
                return False

        except Exception as e:
            self.log(f"❌ Error creating realm: {e}", "ERROR")
            return False

    def create_client(self) -> bool:
        """Create or update the spending-monitor client in the realm"""
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}

            # Check if client already exists
            clients_url = f"{self.base_url}/admin/realms/{self.app_realm}/clients"
            response = requests.get(clients_url, headers=headers, timeout=10)

            if response.status_code != 200:
                self.log(f"❌ Failed to get clients: {response.status_code}")
                return False

            existing_client = None
            for client in response.json():
                if client.get("clientId") == self.client_id:
                    existing_client = client
                    break

            client_data = {
                "clientId": self.client_id,
                "name": "Spending Monitor Frontend",
                "description": "Frontend application for spending transaction monitoring",
                "enabled": True,
                "publicClient": True,
                "standardFlowEnabled": True,
                "directAccessGrantsEnabled": True,
                "serviceAccountsEnabled": False,
                "implicitFlowEnabled": False,
                "redirectUris": ["http://localhost:3000/*"],
                "webOrigins": ["http://localhost:3000"],
                "attributes": {"pkce.code.challenge.method": "S256"},
            }

            if existing_client:
                # Update existing client
                client_uuid = existing_client["id"]
                update_url = f"{self.base_url}/admin/realms/{self.app_realm}/clients/{client_uuid}"

                # Merge with existing data to preserve other settings
                update_data = {**existing_client, **client_data}

                response = requests.put(
                    update_url, json=update_data, headers=headers, timeout=10
                )

                if response.status_code == 204:
                    self.log("✅ Client 'spending-monitor' updated successfully")
                    self.log(f"   • Redirect URIs: {client_data['redirectUris']}")
                    self.log(f"   • Web Origins: {client_data['webOrigins']}")
                    return True
                else:
                    self.log(f"❌ Failed to update client: {response.status_code}")
                    if response.text:
                        self.log(f"   Response: {response.text[:200]}")
                    return False
            else:
                # Create new client
                response = requests.post(
                    clients_url, json=client_data, headers=headers, timeout=10
                )

                if response.status_code == 201:
                    self.log("✅ Client 'spending-monitor' created successfully")
                    self.log(f"   • Redirect URIs: {client_data['redirectUris']}")
                    self.log(f"   • Web Origins: {client_data['webOrigins']}")
                    return True
                else:
                    self.log(f"❌ Failed to create client: {response.status_code}")
                    if response.text:
                        self.log(f"   Response: {response.text[:200]}")
                    return False

        except Exception as e:
            self.log(f"❌ Error creating/updating client: {e}", "ERROR")
            return False

    def create_roles(self) -> bool:
        """Create user and admin roles in the new realm"""
        try:
            roles = ["user", "admin"]
            headers = {"Authorization": f"Bearer {self.access_token}"}

            for role_name in roles:
                url = f"{self.base_url}/admin/realms/{self.app_realm}/roles"
                role_data = {
                    "name": role_name,
                    "description": f"{role_name.title()} role for spending-monitor",
                }

                response = requests.post(
                    url, json=role_data, headers=headers, timeout=10
                )

                if response.status_code == 201:
                    self.log(f"✅ Role '{role_name}' created successfully")
                elif response.status_code == 409:
                    self.log(f"ℹ️  Role '{role_name}' already exists")
                else:
                    self.log(
                        f"❌ Failed to create role '{role_name}': {response.status_code}"
                    )
                    return False

            return True

        except Exception as e:
            self.log(f"❌ Error creating roles: {e}", "ERROR")
            return False

    def create_keycloak_user(
        self, username: str, email: str, password: str, roles: list
    ) -> bool:
        """Create or verify a user with specified roles in the realm"""
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}

            # Check if user already exists
            users_url = f"{self.base_url}/admin/realms/{self.app_realm}/users"
            check_url = f"{users_url}?username={username}"
            response = requests.get(check_url, headers=headers, timeout=10)

            user_id = None
            if response.status_code == 200 and len(response.json()) > 0:
                existing_user = response.json()[0]
                user_id = existing_user["id"]
            else:
                # Create new user
                user_data = {
                    "username": username,
                    "email": email,
                    "enabled": True,
                    "emailVerified": True,
                    "credentials": [
                        {"type": "password", "value": password, "temporary": False}
                    ],
                }

                response = requests.post(
                    users_url, json=user_data, headers=headers, timeout=10
                )

                if response.status_code == 201:
                    user_id = response.headers.get("Location", "").split("/")[-1]
                elif response.status_code == 409:
                    # User exists, get the user ID
                    response = requests.get(check_url, headers=headers, timeout=10)
                    if response.status_code == 200 and len(response.json()) > 0:
                        user_id = response.json()[0]["id"]
                    else:
                        return False
                else:
                    return False

            # Assign roles if we have a user ID
            if user_id:
                for role_name in roles:
                    # Get role data
                    role_url = f"{self.base_url}/admin/realms/{self.app_realm}/roles/{role_name}"
                    role_response = requests.get(role_url, headers=headers, timeout=10)

                    if role_response.status_code == 200:
                        role_data = role_response.json()

                        # Check if role is already assigned
                        user_roles_url = f"{self.base_url}/admin/realms/{self.app_realm}/users/{user_id}/role-mappings/realm"
                        user_roles_response = requests.get(
                            user_roles_url, headers=headers, timeout=10
                        )

                        has_role = False
                        if user_roles_response.status_code == 200:
                            user_roles = user_roles_response.json()
                            has_role = any(r["name"] == role_name for r in user_roles)

                        if not has_role:
                            # Assign role to user
                            assign_response = requests.post(
                                user_roles_url,
                                json=[role_data],
                                headers=headers,
                                timeout=10,
                            )

            return True

        except Exception as e:
            self.log(f"⚠️  Error creating user {username}: {e}")
            return False

    async def get_users_from_database(self) -> List[Dict[str, Any]]:
        """Fetch active users from the database"""
        if not self.db_available or not self.async_session:
            return []
        
        try:
            async with self.async_session() as session:
                query = text("""
                    SELECT id, email, first_name, last_name, is_active
                    FROM users
                    WHERE is_active = true
                    ORDER BY id
                """)
                result = await session.execute(query)
                rows = result.fetchall()
                
                users = []
                for row in rows:
                    # Create username from email (part before @)
                    username = row.email.split('@')[0] if row.email else f"user{row.id}"
                    users.append({
                        "username": username,
                        "email": row.email,
                        "password": "password123",  # Default password for all users
                        "roles": ["user"]
                    })
                
                return users
                
        except Exception as e:
            self.log(f"⚠️  Could not fetch users from database: {e}")
            return []

    def get_fallback_users(self) -> List[Dict[str, Any]]:
        """Get hardcoded test users as fallback"""
        return [
            {
                "username": "testuser",
                "email": "testuser@example.com",
                "password": "password123",
                "roles": ["user"],
            },
            {
                "username": "user1",
                "email": "user1@example.com",
                "password": "password123",
                "roles": ["user"],
            },
        ]

    async def create_users_async(self) -> bool:
        """Create users from database or fallback list"""
        try:
            # Try to get users from database
            users = await self.get_users_from_database()
            
            if not users:
                self.log("ℹ️  No database users found, using hardcoded test users")
                users = self.get_fallback_users()
            else:
                self.log(f"📖 Found {len(users)} active users in database")
            
            # Create users in Keycloak
            self.log(f"👥 Creating {len(users)} users in Keycloak...")
            success_count = 0
            
            for i, user_data in enumerate(users, 1):
                self.log(f"   [{i}/{len(users)}] Creating {user_data['email']}...")
                if self.create_keycloak_user(**user_data):
                    success_count += 1
                    self.log(f"✅ User '{user_data['email']}' created successfully")
            
            self.log(f"✅ Successfully created/updated {success_count}/{len(users)} users")
            
            # Always create an admin user
            self.log("👤 Creating admin user...")
            admin_created = self.create_keycloak_user(
                username="admin",
                email="admin@example.com",
                password="password123",
                roles=["user", "admin"]
            )
            
            if admin_created:
                self.log("✅ User 'admin@example.com' created successfully")
                self.log("✅ Admin role assigned to admin@example.com")
                self.log("✅ Admin user created successfully")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error creating users: {e}", "ERROR")
            return False

    def test_oidc_config(self) -> bool:
        """Test if OIDC configuration is accessible in the new realm"""
        try:
            url = f"{self.base_url}/realms/{self.app_realm}/.well-known/openid-configuration"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                config = response.json()
                self.log("✅ OIDC configuration is accessible")
                self.log(f"   Issuer: {config.get('issuer', 'N/A')}")
                self.log(
                    f"   Authorization endpoint: {config.get('authorization_endpoint', 'N/A')}"
                )
                self.log(f"   Token endpoint: {config.get('token_endpoint', 'N/A')}")
                self.log(
                    f"   Userinfo endpoint: {config.get('userinfo_endpoint', 'N/A')}"
                )
                self.log(f"   JWKS URI: {config.get('jwks_uri', 'N/A')}")
                return True
            else:
                self.log(
                    f"❌ OIDC configuration not accessible: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log(f"❌ Error testing OIDC config: {e}", "ERROR")
            return False

    async def run_setup_async(self) -> bool:
        """Run the complete realm setup (async version)"""
        self.log("🚀 Starting Keycloak setup with database users")
        self.log("=" * 60)

        # Step 1: Get admin token
        if not self.get_admin_token():
            return False

        # Step 2: Create new realm
        if not self.create_realm():
            return False

        # Step 3: Create client
        if not self.create_client():
            return False

        # Step 4: Create roles
        if not self.create_roles():
            return False

        # Step 5: Create users (from DB or fallback)
        if not await self.create_users_async():
            return False

        # Step 6: Test OIDC configuration
        self.log("⏳ Waiting for Keycloak to process changes...")
        time.sleep(3)

        if not self.test_oidc_config():
            self.log("❌ OIDC configuration test failed")
            return False

        self.log("=" * 60)
        self.log("🎉 Keycloak setup completed successfully!")
        self.log("📋 Summary:")
        self.log(f"   • Realm: {self.app_realm}")
        if self.db_available:
            self.log("   • Users synced from database")
        self.log("   • Admin user: admin@example.com / password123")
        self.log("   • Test users: user1@example.com (and others) / password123")
        self.log("🔗 Next steps:")
        self.log("   1. Set BYPASS_AUTH=false in your environment")
        self.log("   2. Test the UI: http://localhost:3000")
        self.log("   3. Login with created users")

        return True

    def run_setup(self) -> bool:
        """Run the complete realm setup (sync wrapper)"""
        return asyncio.run(self.run_setup_async())


def main():
    """Main entry point"""
    creator = KeycloakSetup()

    try:
        success = creator.run_setup()
        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
