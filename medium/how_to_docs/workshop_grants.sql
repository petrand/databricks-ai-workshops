-- ============================================================================
-- L200 "Build an AI Agent with Memory" Workshop
-- Unity Catalog grants — workshop group can create its own schemas
--
-- Model: one shared catalog; every participant (via the genie_day_group group)
-- can create — and own — their own schema inside it. Owning the schema grants
-- full control (CREATE TABLE, SELECT, MODIFY, build the Vector Search index,
-- and later grant their own app's service principal) with no per-table grants.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Step 1 — Create the group + add members  (NOT SQL — run via CLI / console)
-- ----------------------------------------------------------------------------
--   databricks account groups create --display-name "genie_day_group"
--   # then add each participant in:
--   #   Admin Settings -> Identity and access -> Groups -> genie_day_group -> Add members
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- Step 2 — Grant the group schema-creation rights on the workshop catalog (SQL)
-- Run as a metastore admin or owner of <catalog>. Replace <catalog>.
-- ----------------------------------------------------------------------------
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `genie_day_group`;

-- Note:
--  * CREATE CATALOG is NOT required — the setup notebook's catalog-creation step
--    is commented out; participants reuse <catalog>.
--  * SQL-warehouse and Foundation-Model endpoint access are NOT SQL — grant those
--    to genie_day_group via the CLI (see permission_requirements.md).
