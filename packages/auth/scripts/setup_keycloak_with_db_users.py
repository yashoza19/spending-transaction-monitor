#!/usr/bin/env python3
"""
Combined script to:
1. Set up Keycloak realm with spending-monitor configuration
2. Sync all database users to Keycloak
"""

import subprocess
import sys
import time


def log(message: str, level: str = 'INFO'):
    """Print formatted log message"""
    timestamp = time.strftime('%H:%M:%S')
    print(f'[{timestamp}] {level}: {message}')


def run_script(script_name: str, description: str) -> bool:
    """Run a Python script and return success status"""
    log(f'🚀 {description}...')
    log('=' * 60)

    try:
        # Get the directory where this script is located
        import os

        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, script_name)

        # Run the script
        subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=False,  # Show output in real-time
        )
        log(f'✅ {description} completed successfully')
        return True
    except subprocess.CalledProcessError as e:
        log(f'❌ {description} failed with exit code {e.returncode}', 'ERROR')
        return False
    except Exception as e:
        log(f'❌ Error running {description}: {e}', 'ERROR')
        return False


def main():
    """Main execution flow"""
    log('🎯 Starting Keycloak setup with database user sync')
    log('=' * 60)
    print()

    # Step 1: Set up Keycloak realm
    if not run_script('setup_keycloak.py', 'Keycloak realm setup'):
        log('❌ Failed to set up Keycloak realm', 'ERROR')
        sys.exit(1)

    print()
    log('⏳ Waiting 5 seconds for Keycloak to process realm setup...')
    time.sleep(5)
    print()

    # Step 2: Sync database users to Keycloak
    if not run_script('sync_db_users_to_keycloak.py', 'Database user sync'):
        log(
            '⚠️  Database user sync failed - this is OK if no users exist yet', 'WARNING'
        )
        log("   You can run 'pnpm --filter @*/auth sync-users' later to sync users")

    print()
    log('=' * 60)
    log('🎉 Keycloak setup with database users completed!')
    log('=' * 60)
    print()
    log('📋 Summary:')
    log("   • Keycloak realm 'spending-monitor' is configured")
    log('   • Test users have been created:')
    log('     - testuser@example.com / password123 (user role)')
    log('     - admin@example.com / admin123 (admin role)')
    log('   • Database users (if any) have been synced to Keycloak')
    print()
    log('🔗 Next steps:')
    log('   1. Test authentication: http://localhost:5173')
    log('   2. Add more users to database, then run: pnpm --filter @*/auth sync-users')
    log('   3. Check Keycloak admin: http://localhost:8080 (admin/admin)')


if __name__ == '__main__':
    main()
