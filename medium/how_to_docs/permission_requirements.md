# Databricks Permission Requirements — L200 "Build an AI Agent with Memory" Workshop

This document lists every Databricks permission, entitlement, and feature a participant
needs to complete the **medium** workshop end-to-end: preparing data, running the agent
locally, and deploying it as a Databricks App with Lakebase-backed memory.

It is written for two audiences:

- **Workshop participants** — check you (or your workspace) have what's listed before you start.
- **Workspace admins** — use the [Admin pre-flight checklist](#admin-pre-flight-checklist) to provision a workspace for a cohort.

> **Two identities are involved.** Most steps run as **you** (your Databricks user, via CLI
> OAuth or notebook). The final deployed app runs as an **app service principal (SP)** — a
> separate identity that needs its *own* grants. Permissions are called out for each.

---

## Quick reference

| Area | Capability needed | Who needs it | Granted as |
|---|---|---|---|
| Workspace | Log in + workspace access entitlement | You | Account/workspace admin |
| Compute | Serverless notebooks / compute | You | Workspace entitlement |
| Compute | A running **SQL warehouse** with `CAN_USE` | You | Warehouse ACL |
| Unity Catalog | `USE CATALOG` + `CREATE SCHEMA` on target catalog | You | UC privilege |
| Unity Catalog | `USE SCHEMA`, `CREATE TABLE`, `SELECT`, `MODIFY` on the schema | You | UC privilege |
| Vector Search | Create a Vector Search **endpoint** + **index** | You | Feature enabled + UC `CREATE TABLE` |
| Foundation Models | `CAN_QUERY` on `databricks-gte-large-en` (embeddings) | You | Serving endpoint ACL |
| Foundation Models | `CAN_QUERY` on the chat model (e.g. `databricks-claude-sonnet-4-6`) | You **and** app SP | Serving endpoint ACL |
| Genie | Create + run a Genie Space | You | Genie enabled |
| MLflow | Create an experiment in your `/Users/<you>` folder | You | Workspace folder ACL |
| Lakebase (OLTP) | Create a database instance; admin/owner role on it | You | Lakebase feature + DB role |
| Databricks Apps | Create / deploy an app | You | Apps enabled + `CAN_MANAGE` |
| Workspace files | Write to `/Users/<you>`; create Repos/Git folder | You | Workspace ACL |
| Web Terminal | Enabled (workspace-only deploy path) | You | Admin setting |

---

## 1. Workspace & account access

- **A Databricks account and workspace login.** Unity Catalog must be enabled on the workspace.
- **Workspace access entitlement** (`workspace-access`) so you can open notebooks, the file browser, and the SQL/Compute UIs.
- **Local CLI path only:** ability to authenticate the Databricks CLI. The workshop uses
  **OAuth (U2M)** via `databricks auth login` — no personal access token is strictly required,
  but if your org disables OAuth you'll need PAT generation enabled (`Allow personal access tokens`).

## 2. Compute

- **Serverless compute access.** The data setup notebook (`01_quickstart_setup.py`) is run on
  **serverless** compute. You need the entitlement to attach notebooks to serverless (or to a
  cluster that can run Spark SQL + Python).
- **A running SQL warehouse you can use (`CAN_USE`).** Required because:
  - The Genie Space is bound to a SQL warehouse (the notebook picks the first available warehouse).
  - The local-CLI data path (Option B) passes `--warehouse-id` to run the SQL/chunking scripts.
  - If no warehouse is running/visible to you, Genie Space creation is skipped with a warning.

## 3. Unity Catalog (data preparation)

The setup notebook writes into a catalog + schema you choose via widgets. It runs
`CREATE SCHEMA IF NOT EXISTS` and creates **7 tables** plus the Vector Search index.

On the **target catalog** you need:

- `USE CATALOG`
- `CREATE SCHEMA` (unless you point at a schema that already exists and you can write to)

On the **target schema** (whether you create it or reuse one) you need:

- `USE SCHEMA`
- `CREATE TABLE`
- `SELECT` and `MODIFY` on the tables it creates

Tables created: `customers`, `products`, `stores`, `transactions`, `transaction_items`,
`payment_history`, `policy_docs_chunked` (the source for the Vector Search index).

> **Catalog creation is optional.** A `CREATE CATALOG` line exists in the notebook but is
> commented out. Only enable it (and hold the `CREATE CATALOG` privilege on the metastore) if
> you want a dedicated catalog. Most participants should reuse an existing catalog such as
> `users` or a sandbox catalog where they already have `CREATE SCHEMA`.

## 4. Vector Search

The notebook creates a **Vector Search endpoint** and a **Delta Sync index**
(`<catalog>.<schema>.policy_docs_index`, HYBRID, TRIGGERED).

You need:

- **Vector Search enabled** in the workspace/region.
- Permission to **create a Vector Search endpoint** (`vector_search_endpoints.create_endpoint`).
- `CREATE TABLE` on the target schema — the index is registered as a UC object.
- `SELECT` on the source table `policy_docs_chunked` (you'll own it, so this is automatic).
- **`CAN_QUERY` on the embedding model endpoint `databricks-gte-large-en`** — the Delta Sync
  index calls this Foundation Model endpoint to generate embeddings. This is a pay-per-token
  system endpoint and must be enabled in your region.

## 5. Foundation Models / AI Gateway (the LLM)

The agent calls a chat model through the Foundation Models API / AI Gateway
(default `databricks-claude-sonnet-4-6`, configurable in `agent_server/agent.py`).

- **Foundation Model APIs must be enabled** for the workspace/region.
- **`CAN_QUERY`** on the chat model serving endpoint is needed by:
  - **You**, when running the agent locally (`uv run start-app`) — it uses your credentials.
  - The **app service principal**, when the agent runs deployed.
- If your org governs model access through AI Gateway, ensure the chosen model is allowed.

## 6. Genie

- **Genie enabled** in the workspace.
- Permission to **create a Genie Space** (`POST /api/2.0/genie/spaces`).
- The Genie Space is bound to a **SQL warehouse** — see §2 (`CAN_USE`).
- The deployed app's SP needs **`CAN_RUN`** on the Genie Space (declared in `databricks.yml`, see §11).

## 7. MLflow

- The setup/quickstart creates an experiment at `/Users/<your-email>/agents-on-apps`.
  You implicitly have `CAN_MANAGE` on your own user folder, so no extra grant is normally needed.
- The deployed app's SP needs **`CAN_MANAGE`** on that experiment (declared in `databricks.yml`, see §11).

## 8. Lakebase (managed PostgreSQL / OLTP)

Lakebase powers both the agent's short-term memory (`agent_openai_memory`) and the chat UI
history (`ai_chatbot`, `drizzle` schemas).

You need:

- **Lakebase / Database Instances enabled** in the workspace.
- Permission to **create a Lakebase instance** — either:
  - **Autoscaling**: create a project + branch + endpoint (`postgres.create_project` / `create_branch`), **or**
  - **Provisioned**: create a provisioned instance (e.g. `CU_1`).
  - (You can also bind to an existing instance you have access to.)
- A **PostgreSQL role with admin/owner rights** on that instance. Lakebase maps your Databricks
  identity to a Postgres role; you connect as `PGUSER=<your-email>`. You must be able to:
  - Connect (`CAN_CONNECT_AND_CREATE`).
  - **Create a Postgres role for the app's SP** and **GRANT** schema/table/sequence privileges to it
    (the `scripts/grant_lakebase_permissions.py` / Step 11 SQL). This requires role-creation and
    grant privileges on the database — i.e. you must own the schemas or be a Postgres superuser/admin on the instance.

### Lakebase grants the app SP requires (run by you, after first deploy)

The app SP needs, on each of `agent_openai_memory`, `ai_chatbot`, and `drizzle`:

- Schema: `USAGE`, `CREATE`
- Tables: `SELECT`, `INSERT`, `UPDATE`, `DELETE` (the guide uses `GRANT ALL ... TO PUBLIC`)
- **Sequences**: `USAGE`, `SELECT`, `UPDATE` — **granted separately**; table grants alone are not
  enough (auto-increment / `SERIAL` columns fail with "permission denied for sequence" otherwise).

> **Shortcut:** If you drop all three schemas before the first deploy, the app SP creates them
> itself and owns them — no grants needed. See Step 9/11 of the setup guide.

## 9. Databricks Apps (deployment)

- **Databricks Apps enabled** in the workspace.
- Permission to **create and deploy apps** — `CAN_MANAGE` on the app (or workspace permission to
  create apps). Deploying via `databricks bundle deploy` + `bundle run` (or the Apps UI) creates
  the app and provisions its **service principal**.
- App names must be **lowercase letters, numbers, and dashes** (no underscores).
- To redeploy onto an existing app you need rights to **bind** it
  (`databricks bundle deployment bind ...`) or **delete** it (`databricks apps delete ...`).

## 10. Workspace files, Repos & Web Terminal

- **Write access to `/Users/<your-email>/`** — the quickstart uploads the `data/` folder and the
  setup notebook lands here.
- **Repos / Git folders** (workspace-only path) — permission to create a Git folder and configured
  Git credentials to clone the repo into the workspace.
- **Web Terminal enabled** (Settings → Developer → Web Terminal) — required for the recommended
  workspace-only deploy path (running `databricks bundle` commands in-browser).

## 11. App service-principal grants (declared in `databricks.yml`)

When you deploy, these resource bindings are applied to the app SP. You must have permission to
grant each (i.e. you must be able to manage/share these resources):

| Resource | Type in `databricks.yml` | Permission granted to SP |
|---|---|---|
| MLflow experiment | `experiment` | `CAN_MANAGE` |
| Lakebase (autoscaling) | `postgres` (branch + database) | `CAN_CONNECT_AND_CREATE` |
| Lakebase (provisioned) | `database` (instance + database) | `CAN_CONNECT_AND_CREATE` |
| Vector Search index | `uc_securable` + `securable_type: TABLE` | `SELECT` |
| Genie Space | `genie_space` | `CAN_RUN` |
| UC Function (if added) | `uc_securable` + `securable_type: FUNCTION` | `EXECUTE` |
| SQL Warehouse (if added) | `sql_warehouse` | `CAN_USE` |

> These grants apply only to the **deployed** app. **Local development uses your personal
> credentials and bypasses them** — which is why the local run can succeed while the deployed app
> returns 403s from a tool until the matching grant is added and the app redeployed.

---

## Admin pre-flight checklist

Provision these once per workspace so a cohort can self-serve:

- [ ] Unity Catalog enabled; participants have `USE CATALOG` + `CREATE SCHEMA` on a shared/sandbox
      catalog (or a per-user catalog/schema).
- [ ] Serverless compute enabled for participants.
- [ ] At least one **SQL warehouse** running with `CAN_USE` for all participants (Genie needs it).
- [ ] **Vector Search** enabled in-region.
- [ ] **Foundation Model APIs** enabled; `CAN_QUERY` on `databricks-gte-large-en` and the chat
      model (`databricks-claude-sonnet-4-6` or your chosen model).
- [ ] **Genie** enabled with space-creation allowed.
- [ ] **Lakebase / Database Instances** enabled; participants can create instances (or a shared
      instance is provided with role-creation/grant rights).
- [ ] **Databricks Apps** enabled; participants can create apps.
- [ ] **Web Terminal** enabled (Settings → Developer) for the workspace-only path.
- [ ] **Repos / Git folders** allowed, with Git credentials set up.
- [ ] Participants can write to their own `/Users/<email>/` workspace folder.

---

## Common permission-related failures

| Symptom | Missing permission |
|---|---|
| `Schema '<x>' does not exist` / cannot `CREATE SCHEMA` | `CREATE SCHEMA` / `USE CATALOG` on the catalog |
| "No SQL warehouse found" (Genie skipped) | No running warehouse with `CAN_USE` |
| Vector Search index never becomes ready / embedding errors | `CAN_QUERY` on `databricks-gte-large-en`, or VS not enabled |
| Agent LLM calls fail (local or deployed) | `CAN_QUERY` on the chat model endpoint (you / app SP) |
| **403** from an MCP tool on the **deployed** app | Missing `uc_securable` / `genie_space` grant in `databricks.yml` (§11) |
| `permission denied for schema` (deployed app) | App SP not granted on Lakebase schema (§8) |
| `permission denied for sequence` | Sequence grants missing — grant `USAGE, SELECT, UPDATE` on sequences separately (§8) |
| Cannot create Lakebase role for SP / GRANT fails | Your Lakebase role lacks role-creation/admin rights on the instance |
| `An app with the same name already exists` | Need rights to bind or delete the existing app (§9) |

---

## Source references (within this repo)

- `lab_instructions/SETUP_GUIDE.md` — local CLI path (Steps 1–12, incl. SP grants in Step 11)
- `lab_instructions/SETUP_GUIDE_WORKSPACE_ONLY.md` — workspace-only path, prerequisites & deploy
- `data/workspace_setup_script/01_quickstart_setup.py` — what data resources get created
- `databricks.yml` — app resource bindings / SP permissions
- `scripts/quickstart.py` — auth, MLflow experiment, Lakebase provisioning
- `scripts/grant_lakebase_permissions.py` — exact Lakebase schema/table/sequence grants
- `RUNSHEET.md` — real-run gotchas, including permission-related ones
