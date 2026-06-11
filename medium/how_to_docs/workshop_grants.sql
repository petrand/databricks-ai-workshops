-- ============================================================================
-- L200 "Build an AI Agent with Memory" Workshop
-- Unity Catalog grants — SQL ONLY
--
-- IMPORTANT: Databricks has NO SQL to create a group or add users to one — that
-- is done in the account console / SCIM / CLI. For a pure-SQL workflow we skip
-- the group and grant schema-creation rights DIRECTLY to each participant on the
-- shared workshop catalog. Each user then creates and OWNS their own schema in
-- <catalog>, which gives full control (CREATE TABLE, SELECT, MODIFY, build the
-- Vector Search index, and later grant their own app's service principal).
--
-- Run as a metastore admin or owner of <catalog>.
-- Replace <catalog>, then replace the example emails with your participants'.
-- ============================================================================

GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `alice@acme.com`;
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `bob@acme.com`;
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `carol@acme.com`;
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `dave@acme.com`;
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `erin@acme.com`;
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `frank@acme.com`;
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `grace@acme.com`;
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `heidi@acme.com`;
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `ivan@acme.com`;
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `judy@acme.com`;
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `mallory@acme.com`;
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `niaj@acme.com`;
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `olivia@acme.com`;
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `peggy@acme.com`;
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `trent@acme.com`;

-- ----------------------------------------------------------------------------
-- Notes:
--  * CREATE CATALOG is NOT required — the setup notebook's catalog-creation step
--    is commented out; participants reuse <catalog>.
--  * SQL-warehouse and Foundation-Model endpoint access are NOT SQL — see
--    permission_requirements.md for the CLI steps.
--  * If you prefer a GROUP instead of 15 lines: create `genie_day_group` in the
--    account console/CLI first (not possible in SQL), then this single grant
--    replaces all the lines above:
--      GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `genie_day_group`;
-- ----------------------------------------------------------------------------
