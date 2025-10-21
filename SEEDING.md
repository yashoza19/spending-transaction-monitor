# Seeding Guide

This guide explains how to seed your development environment with sample data for both the database and Keycloak authentication.

## Quick Start

### Full Environment Setup

To set up everything from scratch (migrations + all data):

```bash
# Using pnpm (recommended for local development)
pnpm setup:data

# Using make (works in any environment)
make setup-data
```

This will:
1. Start the database container
2. Wait for database to be ready
3. Run database migrations
4. Seed the database with sample users, transactions, and alert rules
5. Set up Keycloak realm with test users
6. Sync any database users to Keycloak

### Seed Everything (Assumes migrations are already run)

```bash
# Seed both database and Keycloak
pnpm seed:all

# Or using make
make seed-all
```

## Individual Seeding Commands

### Database Seeding

Seed the database with sample data (users, transactions, credit cards, alert rules):

```bash
# Using pnpm
pnpm seed:db
pnpm db:seed  # Alias

# Using make
make seed-db
```

**What gets seeded:**
- Sample user: `john.doe@example.com`
- Credit card linked to the user
- Sample transactions (grocery, electronics, dining)
- Sample alert rules (high amount, merchant category, AI-based)

### Keycloak Seeding

#### Basic Keycloak Setup (Test Users Only)

Set up Keycloak realm with pre-defined test users:

```bash
# Using pnpm
pnpm seed:keycloak

# Using make
make seed-keycloak

# Direct script execution
cd packages/auth
pnpm setup-keycloak
```

**What gets created:**
- Keycloak realm: `spending-monitor`
- Test users:
  - `testuser@example.com` / `password123` (user role)
  - `admin@example.com` / `admin123` (admin role)
- OIDC client configuration
- Role mappings

#### Keycloak Setup + Database User Sync

Set up Keycloak realm AND sync all database users to Keycloak:

```bash
# Using pnpm
pnpm seed:keycloak-with-users

# Using make
make seed-keycloak-with-users

# Direct script execution
cd packages/auth
pnpm setup-keycloak-with-users
```

**What this does:**
1. Everything from basic Keycloak setup above
2. Queries the database for all users
3. Creates corresponding Keycloak accounts for each database user
4. Assigns appropriate roles
5. Sets default password: `password123` (configurable via `KEYCLOAK_DEFAULT_PASSWORD` env var)

#### Sync Database Users to Keycloak (Keycloak Realm Must Exist)

If you've already set up Keycloak and just want to sync new database users:

```bash
# Using pnpm
cd packages/auth
pnpm sync-users

# Direct script execution
uv run python packages/auth/scripts/sync_db_users_to_keycloak.py
```

## Workflow Examples

### Starting Fresh Development Environment

```bash
# 1. Start all services (except database which setup:data handles)
make run-local

# 2. Set up all data (starts DB, runs migrations, seeds everything)
pnpm setup:data

# That's it! Database and Keycloak are ready.
```

**Note:** `setup:data` now handles starting the database automatically, so you only need to run `make run-local` for the other services (Keycloak, SMTP, etc.).

### After Adding New Users to Database

If you've added users via the API or database scripts and want them in Keycloak:

```bash
cd packages/auth
pnpm sync-users
```

### Resetting Keycloak (Keep Database)

If you need to reset Keycloak but keep your database data:

```bash
# 1. Stop and remove Keycloak container
podman stop spending-monitor-keycloak
podman rm spending-monitor-keycloak

# 2. Restart Keycloak
cd packages/auth
pnpm start

# 3. Wait for Keycloak to start (about 30 seconds)
sleep 30

# 4. Recreate realm and sync all DB users
pnpm setup-keycloak-with-users
```

### Complete Reset (Nuclear Option)

To completely reset everything:

```bash
# 1. Stop all services and remove volumes
make stop-local

# 2. Start services (except DB)
make run-local

# 3. Set up all data (starts DB + migrations + seeding)
pnpm setup:data
```

## Environment Variables

### Database Connection

The seeding scripts use the following environment variables (read from `.env.development`):

```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/spending-monitor
# Or individual vars:
POSTGRES_HOST=localhost
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=spending-monitor
DB_PORT=5432
```

### Keycloak Configuration

```bash
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=spending-monitor
KEYCLOAK_CLIENT_ID=spending-monitor

# Admin credentials (for setup scripts)
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASSWORD=admin

# Default password for synced users
KEYCLOAK_DEFAULT_PASSWORD=password123

# Redirect URIs (for OIDC client setup)
KEYCLOAK_REDIRECT_URIS=http://localhost:5173/*
KEYCLOAK_WEB_ORIGINS=http://localhost:5173
```

## Containerized vs Local Development

### When Running API Locally

When your API runs locally (via `pnpm dev`), use `localhost` for Keycloak:

```bash
KEYCLOAK_URL=http://localhost:8080
```

### When Running API in Container

When your API runs in a container (via `podman-compose`), use the container hostname:

```bash
KEYCLOAK_URL=http://keycloak:8080
```

The API middleware automatically handles hostname resolution based on the OIDC discovery response.

## Troubleshooting

### "Realm does not exist" Error

**Problem:** API returns "Realm does not exist" when trying to authenticate.

**Solution:** Run Keycloak setup:
```bash
pnpm seed:keycloak
```

### "User not found in Keycloak" Error

**Problem:** You can see users in the database but can't log in.

**Solution:** Sync database users to Keycloak:
```bash
cd packages/auth
pnpm sync-users
```

### Keycloak Won't Start or Connection Refused

**Problem:** Scripts fail with connection errors to Keycloak.

**Solution:**
1. Check if Keycloak is running: `podman ps | grep keycloak`
2. Wait for Keycloak to fully start (check logs): `podman logs -f spending-monitor-keycloak`
3. Look for "Listening on: http://0.0.0.0:8080" in the logs
4. Try again after Keycloak is ready

### Database Connection Errors

**Problem:** Scripts can't connect to the database.

**Solution:**
1. Check if PostgreSQL is running: `podman ps | grep postgres`
2. Verify DATABASE_URL in your `.env.development` file
3. For local development, ensure `localhost:5432` is accessible
4. Run: `pnpm db:verify` to check database connection

## Script Locations

- **Database seeding:** `packages/db/src/db/scripts/seed.py`
- **Keycloak realm setup:** `packages/auth/scripts/setup_keycloak.py`
- **Database user sync:** `packages/auth/scripts/sync_db_users_to_keycloak.py`
- **Combined setup:** `packages/auth/scripts/setup_keycloak_with_db_users.py`

## Additional Seeding Scripts

### Alert Rule Seeding

Seed specific alert rules from JSON samples:

```bash
cd packages/db

# List available samples
pnpm run seed:custom

# Seed specific alert rule
pnpm run seed:dining
pnpm run seed:over-500-transaction
pnpm run seed:outside-home-state

# See package.json for all available seed scripts
```

### CSV Data Loading

Load transactions and users from CSV files:

```bash
cd packages/db/src/db/scripts
uv run python load_csv_data.py
```

Default CSV files are in `data/sample_transactions.csv` and `data/sample_users.csv`.

## See Also

- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Complete development setup guide
- [Authentication Documentation](docs/AUTH_BYPASS.md) - Authentication configuration details
- [Database README](packages/db/README.md) - Database management and migrations
- [Makefile](Makefile) - All available make targets


