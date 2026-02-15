-- Create the database if it doesn't exist
DO $$
BEGIN
   IF NOT EXISTS (
      SELECT
      FROM   pg_catalog.pg_database
      WHERE  datname = 'plf_db') THEN
      -- Note: this assumes you have dblink extension installed.
      -- If not, install it in the 'postgres' database: CREATE EXTENSION dblink;
      PERFORM dblink_exec('dbname=postgres user=' || current_user, 'CREATE DATABASE plf_db');
   END IF;
END
$$;

-- Connect to the plf_db database
\c plf_db

-- Create the users table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    uid VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL
);
