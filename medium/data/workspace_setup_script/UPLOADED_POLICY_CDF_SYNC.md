# Uploaded policies: Lakebase → Delta via Change Data Feed

The chatbot app's **Add policy** tab lets users upload a policy PDF. The flow keeps
uploads transactional and editable in Lakebase, then streams them down to the Delta
table the agent searches using **Lakebase Change Data Feed** (`wal2delta`).

```
Add policy tab
   │  PDF → text in the browser (pdf.js)         ← editable immediately
   ▼
Lakebase Postgres  ai_chatbot."PolicyUpload"     ← the "in-between" table
   │  edits (Add policy tab / dashboard) update this row
   ▼  wal2delta CDF — every insert/update/delete, flushed ~15s
UC Delta  <catalog>.<schema>.lb_PolicyUpload_history
   │  sync_uploaded_policies_cdf.py — latest-state MERGE
   ▼
Delta  dev.policies.policy_docs                  ← existing agent source
   │  existing Vector Search Delta Sync index
   ▼
Knowledge Assistant + Vicinity Policy Search (agent tools)
```

## Why Lakebase first?

* **Fast, transactional writes** — uploads/edits don't need the SQL warehouse; they're
  plain Postgres `INSERT`/`UPDATE`s through the app's existing Drizzle connection.
* **Editable text** — `content` lives in Postgres, so the dashboard review modal and the
  Add policy tab can edit it in place; the edit re-flows to Delta through CDF.
* **One sync path** — CDF is the single, auditable channel from Lakebase to Unity Catalog.

## One-time setup

1. **Migrate the app DB** so the `PolicyUpload` table exists with full replica identity:
   ```bash
   npm run db:migrate    # applies 0004_*, which runs REPLICA IDENTITY FULL
   ```
   Or run [`lakebase_cdf_setup.sql`](./lakebase_cdf_setup.sql) directly against
   `databricks_postgres`.

2. **Enable CDF** in the Lakebase app:
   *Postgres → your project/branch → Branch overview → Change Data Feed → Start*
   * Database: `databricks_postgres`
   * Source schema: `ai_chatbot`
   * Destination catalog / schema: e.g. `dev` / `policies` (destination catalog must
     **not** use default storage)

   The destination history table appears as `lb_PolicyUpload_history`. Confirm health with
   `SELECT * FROM wal2delta.tables;` (status `STREAMING`).

3. **Schedule the sync notebook** [`sync_uploaded_policies_cdf.py`](./sync_uploaded_policies_cdf.py)
   as a Databricks job (every 5–10 min works well for demos), or run it on demand. It is
   idempotent: it recomputes latest state per `policyId` from the full history table and
   `MERGE`s into `policy_docs`, preserving the dashboard's review columns.

## Notes

* Uploaded policies use the `UPL-###` id prefix; seed policies use `POL-###`.
* Requirements: Lakebase Autoscaling project on Postgres 17; the identity running CDF needs
  `USE CATALOG`, `USE SCHEMA`, and `CREATE TABLE` on the destination.
* Reference: https://docs.databricks.com/aws/en/oltp/projects/lakebase-cdf
