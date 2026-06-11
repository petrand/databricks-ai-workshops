-- ============================================================================
-- L200 "Build an AI Agent with Memory" Workshop
-- Unity Catalog provisioning — ONE dedicated catalog + ONE schema PER USER
--
-- Each participant gets their own catalog and schema, and is made the OWNER.
-- Ownership automatically grants full control (USE, CREATE SCHEMA/TABLE, SELECT,
-- MODIFY, create the Vector Search index, etc.) and lets them later grant their
-- own app's service principal — no further per-table grants needed.
--
-- Run as a METASTORE ADMIN (CREATE CATALOG + set-owner require it), in a SQL
-- editor or a notebook attached to a SQL warehouse.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- PER-USER BLOCK — repeat once per participant.
-- Replace <user_email>, <catalog>, <schema> each time. Suggested convention:
--   catalog = workshop_<username>   schema = agent
-- ----------------------------------------------------------------------------

CREATE CATALOG IF NOT EXISTS `<catalog>`;
ALTER CATALOG `<catalog>` OWNER TO `<user_email>`;

CREATE SCHEMA IF NOT EXISTS `<catalog>`.`<schema>`;
ALTER SCHEMA `<catalog>`.`<schema>` OWNER TO `<user_email>`;


-- ----------------------------------------------------------------------------
-- WORKED EXAMPLE (jane.smith@acme.com)
-- ----------------------------------------------------------------------------
-- CREATE CATALOG IF NOT EXISTS `workshop_jsmith`;
-- ALTER CATALOG `workshop_jsmith` OWNER TO `jane.smith@acme.com`;
-- CREATE SCHEMA IF NOT EXISTS `workshop_jsmith`.`agent`;
-- ALTER SCHEMA `workshop_jsmith`.`agent` OWNER TO `jane.smith@acme.com`;


-- ----------------------------------------------------------------------------
-- BULK (optional): run in a Databricks notebook to provision many users at once.
-- ----------------------------------------------------------------------------
-- users = ["jane.smith@acme.com", "john.doe@acme.com"]
-- for u in users:
--     cat = "workshop_" + u.split("@")[0].replace(".", "")
--     spark.sql(f"CREATE CATALOG IF NOT EXISTS `{cat}`")
--     spark.sql(f"ALTER CATALOG `{cat}` OWNER TO `{u}`")
--     spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{cat}`.`agent`")
--     spark.sql(f"ALTER SCHEMA `{cat}`.`agent` OWNER TO `{u}`")

-- Note: SQL-warehouse and Foundation-Model endpoint access are NOT SQL — grant
-- those to the genie-day-workshop group via the CLI (see permission_requirements.md).
