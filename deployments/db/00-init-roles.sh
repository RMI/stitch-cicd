#!/bin/sh
set -e

# This script runs automatically on first database initialization
# via /docker-entrypoint-initdb.d.
#
# It bootstraps two roles:
#   - stitch_migrator: DDL + seed (used by db-init job)
#   - stitch_app:      runtime access only (used by API)
#
# Passwords and DB name are taken from environment variables.

: "${POSTGRES_DB:?POSTGRES_DB must be set}"
: "${STITCH_MIGRATOR_PASSWORD:?STITCH_MIGRATOR_PASSWORD must be set}"
: "${STITCH_APP_PASSWORD:?STITCH_APP_PASSWORD must be set}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

DO \$\$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'stitch_migrator') THEN
    CREATE ROLE stitch_migrator
      LOGIN
      PASSWORD '${STITCH_MIGRATOR_PASSWORD}';
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'stitch_app') THEN
    CREATE ROLE stitch_app
      LOGIN
      PASSWORD '${STITCH_APP_PASSWORD}';
  END IF;
END
\$\$;

-- Allow both roles to connect to the database
GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO stitch_migrator;
GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO stitch_app;

-- Schema access (public for now)
GRANT USAGE ON SCHEMA public TO stitch_migrator;
GRANT USAGE ON SCHEMA public TO stitch_app;

-- Migrator can create/alter objects
GRANT CREATE ON SCHEMA public TO stitch_migrator;

-- Default privileges for objects created by stitch_migrator
ALTER DEFAULT PRIVILEGES FOR ROLE stitch_migrator IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO stitch_app;

ALTER DEFAULT PRIVILEGES FOR ROLE stitch_migrator IN SCHEMA public
  GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO stitch_app;

ALTER DEFAULT PRIVILEGES FOR ROLE stitch_migrator IN SCHEMA public
  GRANT EXECUTE ON FUNCTIONS TO stitch_app;

-- Defensive: apply to existing objects too (usually none on first init)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO stitch_app;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO stitch_app;

-- Tighten public schema defaults
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

EOSQL

