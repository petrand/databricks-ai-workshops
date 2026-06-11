-- ============================================================================
-- L200 "Build an AI Agent with Memory" Workshop
-- Unity Catalog grants — SQL ONLY
--
-- About groups in SQL: Databricks DOES have `CREATE GROUP` / `ALTER GROUP` SQL
-- (admin-only), BUT they manage WORKSPACE-LOCAL (legacy) groups that are "not
-- synchronized to the account and not compatible with Unity Catalog". Because
-- USE CATALOG / CREATE SCHEMA are Unity Catalog privileges, you CANNOT grant
-- them to a CREATE GROUP-made group — the grant won't apply. (Docs:
-- /aws/en/sql/language-manual/security-create-group and .../security-alter-group)
--
-- So for a pure-SQL workflow we grant schema-creation rights DIRECTLY to each
-- participant (account-level principals) on the shared workshop catalog. Each
-- user then creates and OWNS their own schema in <catalog>, giving full control
-- (CREATE TABLE, SELECT, MODIFY, build the Vector Search index, and later grant
-- their own app's service principal).
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
--  * To collapse the 15 lines into one, you need an ACCOUNT-LEVEL group as the
--    grant target. Account groups are created in the account console / SCIM /
--    CLI (NOT via SQL `CREATE GROUP`, which makes a UC-incompatible workspace
--    group). Once `genie_day_group` exists as an account group:
--      GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `genie_day_group`;
-- ----------------------------------------------------------------------------
