-- Lakebase Change Data Feed setup for the uploaded-policies table.
-- Run this against the Lakebase Postgres database (databricks_postgres) using
-- the Lakebase SQL editor or psql. The app's Drizzle migration 0004 already sets
-- REPLICA IDENTITY FULL on the table; this script is the manual equivalent plus
-- an optional event trigger so any future ai_chatbot tables are CDF-ready too.
--
-- After running this, enable CDF in the Lakebase app UI:
--   Postgres -> project/branch -> Branch overview -> Change Data Feed -> Start
--   Source schema:      ai_chatbot
--   Destination:        <catalog>.<schema>   (e.g. dev.policies)  [no default storage]

-- 1) Full row images are required for CDF to build complete change history.
ALTER TABLE ai_chatbot."PolicyUpload" REPLICA IDENTITY FULL;

-- 2) (Optional) Auto-apply REPLICA IDENTITY FULL to future tables in ai_chatbot.
CREATE OR REPLACE FUNCTION public.set_full_replica_identity()
RETURNS event_trigger
LANGUAGE plpgsql AS $$
DECLARE obj record;
BEGIN
  FOR obj IN
    SELECT * FROM pg_event_trigger_ddl_commands()
    WHERE command_tag = 'CREATE TABLE'
  LOOP
    EXECUTE format('ALTER TABLE %s REPLICA IDENTITY FULL;', obj.object_identity);
  END LOOP;
END $$;

DROP EVENT TRIGGER IF EXISTS set_full_replica_identity_on_create;
CREATE EVENT TRIGGER set_full_replica_identity_on_create
ON ddl_command_end
WHEN TAG IN ('CREATE TABLE')
EXECUTE FUNCTION public.set_full_replica_identity();

-- 3) Monitor CDF status once it is started (STREAMING = healthy).
--    SELECT * FROM wal2delta.tables;
