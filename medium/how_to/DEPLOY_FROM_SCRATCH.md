# Deploy from scratch — Vicinity Policy & Foot-Traffic Agent

A follow-along runbook to stand up the whole app in a fresh workspace: seed data, Vector
Search, Knowledge Assistant, Genie, Lakebase, and the deployed Databricks App.

> **Mental model:** the Databricks Asset Bundle (DAB) only creates **two** things — the
> **App** and the **Lakebase instance** — and **grants** the app access to everything else.
> All data and AI assets are created by a **workspace notebook** or **by hand**. Follow the
> steps in order; each is tagged with who does the work:
> `[CLI]` `[notebook]` `[UI]` `[SQL]` `[DAB]` `[auto]`.

---

## 0. Prerequisites

- Databricks workspace with Unity Catalog, Serverless SQL, Vector Search, Agent Bricks, and Lakebase enabled.
- Local tools: `uv`, `node` 20+, `npm`, the `databricks` CLI, and `psql`.
- A Databricks CLI profile authenticated to the target workspace:
  ```bash
  databricks auth login --host https://<your-workspace-host>
  databricks auth profiles      # note the profile name; used as <profile> below
  ```

Throughout, replace `<profile>` with your profile name.

---

## 1. Environment & MLflow experiment — `[CLI]`

```bash
cd medium
uv run quickstart --profile <profile>
```

This authenticates, writes `.env`, and **creates an MLflow experiment** (or reuses one).
Note the **experiment id** it prints — you'll put it in `databricks.yml`.

---

## 2. Seed data + AI assets — `[notebook]`

Import the repo into the workspace and **Run All** on:

```
data/workspace_setup_script/create_property_policy_data.py
```

Widgets (defaults are fine): `catalog=dev`, `schema=policies`, `table=policy_docs`,
`ops_schema=operations`, `ops_table=foot_traffic`, `traffic_days=180`.

This single notebook creates, in order:

1. `dev.policies.policy_docs` + 100 seed policies (CDF enabled on the table).
2. A **Vector Search endpoint** + the `dev.policies.policy_docs_index` Delta Sync index (allow ~5–10 min to sync).
3. A **Knowledge Assistant** (Agent Bricks) + knowledge source → a serving endpoint named like `ka-xxxxxxxx-endpoint`.
4. `dev.operations.foot_traffic` — synthetic daily foot-traffic for the Genie space (Section 7 of the notebook).

Then **also Run All** on the hourly foot-traffic notebook (the foot-traffic demo):

```
data/workspace_setup_script/create_foot_traffic_hourly_data.py
```

Widgets (defaults are fine): `catalog=dev`, `ops_schema=operations`, `ops_table=foot_traffic_hourly`,
`traffic_days=90`. This creates `dev.operations.foot_traffic_hourly` — one row per centre per
trading hour — used for intra-day ("busiest hour", weekday vs weekend by hour) Genie questions.

**Write these down** from the notebook output:

| Value | Example | Used in |
|---|---|---|
| Vector Search index name | `dev.policies.policy_docs_index` | `databricks.yml`, `agent.py` |
| Knowledge Assistant endpoint | `ka-a9d02891-endpoint` | `databricks.yml` |

---

## 3. Create the Foot Traffic Genie space — `[UI]`

Genie spaces can't be created from the notebook — build it by hand once.

1. **Genie → New**.
2. Add **both** foot-traffic tables as data sources:
   - `dev.operations.foot_traffic` — one row per centre per **day**.
   - `dev.operations.foot_traffic_hourly` — one row per centre per **trading hour**.
3. Name it *Vicinity Foot Traffic Genie* and attach a Serverless SQL warehouse.
4. Paste the **sample instructions** below into the space's **Instructions** box.
5. Add the **benchmark questions** below as sample/curated questions (optional but recommended).
6. Copy the **space id** from the URL (e.g. `01f1693a7f2f1e148e53cc17d77fe89d`) — you'll wire it
   into `databricks.yml` and `agent.py` in step 5.

### Sample Genie instructions

> ```
> This space answers foot-traffic questions for the Vicinity Centres shopping-centre
> portfolio. There are two tables, both fictional/synthetic:
>
> - dev.operations.foot_traffic — ONE ROW PER CENTRE PER DAY. Use this for daily,
>   weekly, monthly, weekend-vs-weekday, holiday, and "which centre" questions.
>   Key columns: traffic_date, centre_name, state, centre_type, visitor_count
>   (total visitors that day), peak_hour, avg_dwell_minutes, is_weekend,
>   is_public_holiday, holiday_name, is_trading_day.
> - dev.operations.foot_traffic_hourly — ONE ROW PER CENTRE PER TRADING HOUR. Use this
>   ONLY for intra-day / "by hour" / "busiest hour" / "morning vs evening" questions.
>   Key columns: traffic_hour_ts, hour_of_day (0-23), centre_name, visitor_count
>   (visitors in that hour).
>
> Rules of thumb:
> - "How busy", "total visitors", "compare centres", "trend over time" → use foot_traffic.
> - Anything mentioning an hour, time of day, morning/afternoon/evening, or "busiest hour"
>   → use foot_traffic_hourly. Do NOT sum hourly rows to get a daily total unless the user
>   explicitly asks to reconcile the two; prefer foot_traffic.visitor_count for daily totals.
> - Centres do not trade on Christmas Day or Good Friday: foot_traffic has visitor_count = 0
>   (is_trading_day = false) and foot_traffic_hourly has no rows for those dates.
> - States are Australian: VIC, NSW, WA, SA. "Last weekend" means the most recent Sat+Sun.
> - When the user names a centre (e.g. "Chadstone"), filter on centre_name.
> - Always show centre_name (not centre_id) in results, and order results sensibly
>   (most-recent date first, or highest visitor_count first).
> ```

### Benchmark questions

Use these to sanity-check the space after setup (mix of daily and hourly):

Daily (`foot_traffic`):
- Which centre had the highest foot traffic last weekend?
- Compare weekday vs weekend visitors for Chadstone.
- What were total visitors by state last month?
- Show the daily visitor trend for Emporium Melbourne over the last 30 days.
- Which days were centres closed, and why?
- How does Boxing Day traffic compare to a normal Saturday?
- What is the average dwell time by centre type?

Hourly (`foot_traffic_hourly`):
- What is the busiest hour of the day at Chadstone?
- Compare morning vs evening foot traffic on weekdays across the portfolio.
- Show the hourly visitor curve for Emporium Melbourne last Thursday (late-night trade).
- Which centre has the most evening (after 5pm) traffic on weekends?
- What is the average visitors per hour by hour of day?

> If hourly questions return "table not found" or empty results, confirm step 2 added
> `dev.operations.foot_traffic_hourly` and that the app SP has `SELECT` on it (step 8).

---

## 4. Pick a SQL warehouse — `[UI/CLI]`

The `/dashboard` runs its compliance queries on a warehouse. Choose one and note its **id**:

```bash
databricks warehouses list --profile <profile>
```

---

## 5. Wire up config — `[edit files]`

Replace the environment-specific IDs with **your** values from steps 1–4.

In `databricks.yml` (the `agent_openai_agents_sdk` app):
- `config.env` → `MLFLOW_EXPERIMENT_ID` (step 1)
- `resources` → `experiment` id (step 1)
- `resources` → `sql-warehouse` `id` (step 4)
- `resources` → `knowledge_assistant_endpoint` name (step 2)
- `resources` → `policy_docs_index` / `policy_docs` names (step 2, usually already correct)
- `resources` → `foot_traffic_genie` `space_id` (step 3)

In `agent_server/agent.py`:
- The Vector Search MCP URL: `/api/2.0/mcp/vector-search/dev/policies/policy_docs_index`
- The Genie MCP URL: `/api/2.0/mcp/genie/<your-genie-space-id>`

Validate before deploying:
```bash
databricks bundle validate --profile <profile>
```

---

## 6. Deploy the app + Lakebase instance — `[DAB]`

```bash
databricks bundle deploy --profile <profile>
databricks bundle run agent_openai_agents_sdk --profile <profile>
```

`deploy` creates the **App**, the **Lakebase instance** (`agent-router-lakebase`, CU_1),
grants the app's service principal access to the bound resources, and injects env vars.
`run` builds the frontend and starts it. Note the **app URL** it prints.

> The app's frontend runs a DB migration on startup, and the backend creates its memory
> schema — both as the app's **service principal**. On a clean first deploy the SP creates
> and **owns** these schemas, so the next step is usually a quick confirm. (If you ever
> delete/recreate the app or instance, the SP changes and you must re-run step 7.)

---

## 7. Lakebase grants — `[CLI] + [SQL]`

Capture the app's service principal client id into `$SP` (reused in step 8 — keep the same shell):
```bash
export SP=$(databricks apps get agent-vicinity-router --profile <profile> -o json \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['service_principal_client_id'])")
echo "SP=$SP"
```

Create its Postgres role + grants on the memory/chat schemas:
```bash
DATABRICKS_CONFIG_PROFILE=<profile> uv run python scripts/grant_lakebase_permissions.py \
  "$SP" --memory-type openai --instance-name agent-router-lakebase
```

Grant the SP `CONNECT`/`CREATE` on the database (run once, as a workspace/Lakebase admin).
This connects with an OAuth token as the Postgres password:
```bash
export PGHOST=$(databricks database get-database-instance agent-router-lakebase --profile <profile> -o json \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['read_write_dns'])")
export PGUSER=$(databricks current-user me --profile <profile> -o json \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['userName'])")

PGPASSWORD="$(databricks auth token --profile <profile> | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')" \
psql "host=$PGHOST port=5432 dbname=databricks_postgres user=$PGUSER sslmode=require" \
  -c "GRANT CONNECT, CREATE ON DATABASE databricks_postgres TO \"$SP\";"
```

If the memory schema/tables were created by a different identity (e.g. after recreating the
instance), also grant access to them — same `psql` connection:
```bash
PGPASSWORD="$(databricks auth token --profile <profile> | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')" \
psql "host=$PGHOST port=5432 dbname=databricks_postgres user=$PGUSER sslmode=require" \
  -c "GRANT USAGE ON SCHEMA agent_openai_memory TO \"$SP\";" \
  -c "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA agent_openai_memory TO \"$SP\";" \
  -c "GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA agent_openai_memory TO \"$SP\";" \
  -c "ALTER DEFAULT PRIVILEGES IN SCHEMA agent_openai_memory GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO \"$SP\";"
```

Then restart the app so it picks up the grants:
```bash
databricks bundle run agent_openai_agents_sdk --profile <profile>
```

---

## 8. Unity Catalog grants for Genie + dashboard — `[CLI]`

The app binding grants `SELECT` on `policy_docs`, but **catalog/schema `USE` and the Genie
table can't be expressed in the bundle** — grant them directly:

```bash
databricks grants update CATALOG dev          --json "{\"changes\":[{\"principal\":\"$SP\",\"add\":[\"USE_CATALOG\"]}]}" --profile <profile>
databricks grants update SCHEMA  dev.policies  --json "{\"changes\":[{\"principal\":\"$SP\",\"add\":[\"USE_SCHEMA\"]}]}"  --profile <profile>
databricks grants update SCHEMA  dev.operations --json "{\"changes\":[{\"principal\":\"$SP\",\"add\":[\"USE_SCHEMA\"]}]}" --profile <profile>
databricks grants update TABLE   dev.operations.foot_traffic --json "{\"changes\":[{\"principal\":\"$SP\",\"add\":[\"SELECT\"]}]}" --profile <profile>
databricks grants update TABLE   dev.operations.foot_traffic_hourly --json "{\"changes\":[{\"principal\":\"$SP\",\"add\":[\"SELECT\"]}]}" --profile <profile>
```

Also grant the SP **`CAN_RUN`** on the Genie space (Genie UI → Share), if not already.

---

## 9. (Optional) Uploaded-policy sync pipeline — `[SQL] + [job]`

Only needed if you want policies uploaded in the app to flow into `dev.policies.policy_docs`
(and thus the dashboard + agent retrieval). See
`data/workspace_setup_script/UPLOADED_POLICY_CDF_SYNC.md`. In short:

1. Run `data/workspace_setup_script/lakebase_cdf_setup.sql` against the Lakebase DB
   (sets `REPLICA IDENTITY FULL` on `ai_chatbot."PolicyUpload"`).
2. Enable Lakebase **Change Data Feed** (source schema `ai_chatbot` → destination `dev`/`policies`).
   **Requires an autoscaling Postgres 17 Lakebase project** — different from the provisioned
   CU_1 instance the bundle creates, so plan this deliberately.
3. Schedule `data/workspace_setup_script/sync_uploaded_policies_cdf.py` as a job (every 5–10 min).

Without this, uploads are still saved (and editable/listed) in Lakebase, but won't appear on
the dashboard or to the agent.

---

## 10. Verify

- App status `RUNNING`: `databricks apps get agent-vicinity-router --profile <profile>`
- Open the app URL → **/dashboard** loads the 100 policies and KPIs (warehouse + UC OK).
- Click **Approved** on an overdue policy → it flips to **Current** (review-date write-back OK).
- Upload a sample PDF from `data/sample_policies/` → no "Failed to fetch … pdf.min.mjs" (proxy allowlist OK).
- Ask the chat a foot-traffic question → Genie answers (Genie grants OK).
- Chat persists across turns → Lakebase memory OK.

---

## Gotchas (all hit during the first rollout)

1. **Don't casually delete/recreate the app** — it orphans the service principal that owns
   the Lakebase objects, which is painful to recover. If you must, redo steps 7–8 for the new SP.
2. **Frontend Lakebase login** (OAuth) is provisioned by the **database binding**, not by the
   grant script. A clean deploy sets it up; recreating the instance out-of-band does not —
   unbind/rebind the `database` resource to force re-provisioning.
3. **Memory schema needs `USAGE`**, or unqualified queries report *"relation does not exist"*.
4. **PDF upload** needs `CHAT_PROXY_ALLOWED_PATH_PREFIXES=/pdfjs/` (already in `databricks.yml`).
5. **Swap every hardcoded env-specific id** in `databricks.yml` / `agent.py` for a new workspace
   (experiment, warehouse, KA endpoint, Genie space id, index name).

---

## What DAB does vs. doesn't

| Asset | Who creates it |
|---|---|
| Databricks App, Lakebase instance | **DAB** (`bundle deploy`) |
| App env vars, service principal, resource **grants** | **DAB** |
| Lakebase schemas/tables (`agent_openai_memory`, `ai_chatbot`, `drizzle`) | **auto** at app startup (needs SP privileges) |
| MLflow experiment | `uv run quickstart` (step 1) |
| `policy_docs`, Vector Search index, Knowledge Assistant, `foot_traffic`, `foot_traffic_hourly` | **notebook** (step 2) |
| Genie space | **UI** (step 3) |
| SQL warehouse | pre-existing (step 4) |
| `USE CATALOG`/`USE SCHEMA`, Genie table SELECT | **manual** grants (step 8) |
| Lakebase CDF + uploaded-policy sync | **manual** (step 9) |

---

## Day-2: everyday loop & troubleshooting

Once deployed, the inner loop after any code or `databricks.yml` change:
```bash
databricks bundle deploy --profile <profile> && \
databricks bundle run   agent_openai_agents_sdk --profile <profile>
```

Tail logs / check status:
```bash
databricks apps logs agent-vicinity-router --profile <profile>
databricks apps get  agent-vicinity-router --profile <profile> -o json \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['app_status'])"
```
