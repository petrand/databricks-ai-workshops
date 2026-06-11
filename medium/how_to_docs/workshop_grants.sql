-- ============================================================================
-- L200 "Build an AI Agent with Memory" Workshop
-- Unity Catalog grants for workshop participants
--
-- Group:   genie-day-workshop   (must already exist as an account group;
--                                create it + add members in the admin console
--                                or via the Databricks CLI — not SQL)
--
-- Run as a metastore admin or an owner of <catalog>, in a SQL editor or a
-- notebook attached to a SQL warehouse.
--
-- Replace <catalog> before running.
-- ============================================================================

-- Let workshop users create — and own — their own schema in the workshop catalog.
-- Owning the schema gives them CREATE TABLE + full table privileges automatically,
-- and lets them later grant their own app's service principal.
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `genie-day-workshop`;

-- ----------------------------------------------------------------------------
-- Alternative: if you pre-create ONE schema per participant instead of letting
-- them create their own, comment out the grant above and use this instead
-- (replace <schema>):
--
-- GRANT USE CATALOG ON CATALOG `<catalog>` TO `genie-day-workshop`;
-- GRANT USE SCHEMA, CREATE TABLE ON SCHEMA `<catalog>`.`<schema>` TO `genie-day-workshop`;
-- ----------------------------------------------------------------------------

-- Note: CREATE CATALOG is NOT required — the setup notebook's catalog-creation
-- step is commented out; participants reuse <catalog>.
