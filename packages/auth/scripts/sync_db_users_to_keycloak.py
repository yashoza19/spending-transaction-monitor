#!/usr/bin/env python3
"""
Sync database users to Keycloak realm
"""

import time
import requests
import psycopg2
from typing import Optional, List, Dict
import os


class DatabaseUserSyncer:
    def __init__(self):
        self.base_url = "http://localhost:8080"
        self.admin_username = "admin"
        self.admin_password = "admin"
        self.master_realm = "master"
        self.app_realm = "spending-monitor"
        self.access_token: Optional[str] = None
        
        # Database connection
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'spending-monitor',
            'user': 'user',
            'password': 'password'
        }

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

    def get_database_users(self) -> List[Dict]:
        """Get all users from the database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, email, first_name, last_name 
                FROM users 
                ORDER BY id
            """)
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row[0],
                    'email': row[1],
                    'first_name': row[2],
                    'last_name': row[3],
                    'username': row[1].split('@')[0],  # Use email prefix as username
                    'password': 'password123'  # Default password for all users
                })
            
            cursor.close()
            conn.close()
            
            self.log(f"✅ Retrieved {len(users)} users from database")
            return users
            
        except Exception as e:
            self.log(f"❌ Failed to get database users: {e}", "ERROR")
            return []

    def create_keycloak_user(self, user_data: Dict) -> bool:
        """Create a user in Keycloak"""
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            users_url = f"{self.base_url}/admin/realms/{self.app_realm}/users"
            
            # Check if user already exists
            check_url = f"{users_url}?username={user_data['username']}"
            response = requests.get(check_url, headers=headers, timeout=10)
            
            if response.status_code == 200 and len(response.json()) > 0:
                self.log(f"ℹ️  User '{user_data['username']}' already exists in Keycloak")
                return True
            
            # Create new user
            keycloak_user_data = {
                "username": user_data['username'],
                "email": user_data['email'],
                "firstName": user_data['first_name'],
                "lastName": user_data['last_name'],
                "enabled": True,
                "emailVerified": True,
                "credentials": [
                    {"type": "password", "value": user_data['password'], "temporary": False}
                ],
            }

            response = requests.post(users_url, json=keycloak_user_data, headers=headers, timeout=10)

            if response.status_code == 201:
                self.log(f"✅ User '{user_data['username']}' created successfully in Keycloak")
                return True
            elif response.status_code == 409:
                self.log(f"ℹ️  User '{user_data['username']}' already exists in Keycloak")
                return True
            else:
                self.log(f"❌ Failed to create user '{user_data['username']}': {response.status_code}")
                return False

        except Exception as e:
            self.log(f"❌ Error creating user '{user_data['username']}': {e}", "ERROR")
            return False

    def sync_users(self) -> bool:
        """Sync all database users to Keycloak"""
        self.log("🚀 Starting database user sync to Keycloak")
        self.log("=" * 50)

        # Step 1: Get admin token
        if not self.get_admin_token():
            return False

        # Step 2: Get database users
        db_users = self.get_database_users()
        if not db_users:
            self.log("❌ No database users found")
            return False

        # Step 3: Create users in Keycloak
        success_count = 0
        for user_data in db_users:
            if self.create_keycloak_user(user_data):
                success_count += 1
            else:
                self.log(f"⚠️  Failed to sync user {user_data['username']}, continuing...")

        self.log("=" * 50)
        self.log(f"🎉 User sync completed!")
        self.log(f"📊 Successfully synced {success_count}/{len(db_users)} users")
        self.log("🔗 Users can now log in with:")
        self.log("   • Email: their email address")
        self.log("   • Password: password123 (default)")

        return success_count > 0


def main():
    syncer = DatabaseUserSyncer()
    success = syncer.sync_users()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
