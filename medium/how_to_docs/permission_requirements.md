# Admin Provisioning Script — L200 "Build an AI Agent with Memory" Workshop

Run-once setup for an admin to provision a cohort. Everything is keyed to a single group:
**`genie_day_group`**. Apply the grants to the group, add participants to it, done.

> **What is / isn't SQL.** In Databricks, only **Unity Catalog** privileges are real SQL `GRANT`
> statements. Creating a group, adding users, entitlements, and SQL-warehouse / serving-endpoint
> ACLs are managed via the **CLI / admin console**, not SQL. Both are below, clearly labeled.
>
> **Out of scope:** participants grant their own deployed app's **service principal** (UC `SELECT`,
> Genie `Can Run`, Lakebase) during the workshop — not an admin task. See the end of this doc.

Replace these placeholders before running: `<catalog>`, `<warehouse-id>`, and the chat-model
endpoint name (default `databricks-claude-sonnet-4-6`).

---

## Step 1 — Create the group and add users (CLI / admin console)

Not SQL. Create an account-level group, then add each participant.

```bash
# Create the workshop group
databricks account groups create --display-name "genie_day_group"

# Add each participant (repeat per user, or do it in bulk in the admin console)
databricks account groups patch <group-id> \
  --json '{"Operations":[{"op":"add","path":"members","value":[{"value":"<user-id>"}]}]}'
```

Easiest in the UI: **Admin Settings → Identity and access → Groups → genie_day_group → Add members**.

---

## Step 2 — Entitlements for the group (CLI / admin console)

Not SQL. Assign the group to the workspace with the required entitlements:

```bash
# Grant workspace access + Databricks SQL access to the group
databricks permission-assignments set \
  --principal-id <group-id> \
  --permissions '["USER"]'   # workspace user
```

In the admin console, confirm the `genie_day_group` group has:

- **Workspace access** — open notebooks, file browser, Compute/SQL UIs.
- **Databricks SQL access** — use SQL warehouses and the SQL editor.
- **Serverless compute** — the data-setup notebook runs on serverless (or grant cluster use).

---

## Step 3 — Unity Catalog grants (SQL) ✅

Real SQL. Run as a **metastore admin** or owner of the catalog. The `genie_day_group` group is
granted schema-creation rights on a shared catalog; each participant creates and **owns** their own
schema, which gives full control (create tables, build the Vector Search index, and later grant
their own service principal) with no per-table grants.

See **[`workshop_grants.sql`](./workshop_grants.sql)** for the full script:

```sql
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG `<catalog>` TO `genie_day_group`;
```

> `CREATE CATALOG` is **not** needed (the setup notebook's catalog-creation step is commented out).

---

## Step 4 — SQL warehouse access (CLI) 

Not SQL — warehouse permissions are an object ACL. Grant `CAN_USE` on a **running** warehouse
(Genie and the data setup both need one):

```bash
databricks warehouses update-permissions <warehouse-id> --json '{
  "access_control_list": [
    { "group_name": "genie_day_group", "permission_level": "CAN_USE" }
  ]
}'
```

---

## Step 5 — Foundation Model endpoint access (CLI)

Not SQL — serving-endpoint ACLs. Grant `CAN_QUERY` on the embedding model (used by the Vector
Search index) and the chat model (used by the agent):

```bash
# Embeddings endpoint (Vector Search index)
databricks serving-endpoints update-permissions databricks-gte-large-en --json '{
  "access_control_list": [
    { "group_name": "genie_day_group", "permission_level": "CAN_QUERY" }
  ]
}'

# Chat model endpoint (agent) — default databricks-claude-sonnet-4-6
databricks serving-endpoints update-permissions databricks-claude-sonnet-4-6 --json '{
  "access_control_list": [
    { "group_name": "genie_day_group", "permission_level": "CAN_QUERY" }
  ]
}'
```

> Pay-per-token system endpoints are often queryable by everyone by default; the grants above are
> only required in workspaces with restricted serving-endpoint ACLs.

---

## Step 6 — Enable workspace features (admin console)

Not SQL and not per-group — workspace/region toggles. Confirm all are **on** so participants can
create the resources the workshop needs:

- **Unity Catalog**
- **Vector Search** (supported region) — participants create a VS endpoint + index
- **Foundation Model APIs** (supported region)
- **Genie** — participants create a Genie Space
- **Lakebase / Database Instances** — participants create a Lakebase instance
- **Databricks Apps** — participants deploy the app
- **Web Terminal** (Settings → Developer) — for the workspace-only deploy path
- **Repos / Git folders** — allow Git folder creation + Git credentials

If a "users may create …" setting gates any of these, allow it for `genie_day_group`.

---

## What participants do themselves (no admin action)

- **MLflow experiment** — created in their own `/Users/<email>` folder, which they already own.
- **Service-principal grants for the deployed app** — after deploy, participants grant their app's
  SP: UC `USE CATALOG`/`USE SCHEMA`/`SELECT` on their schema, Genie **Can Run** (Share dialog), and
  Lakebase access (or let the app own the tables it creates). Documented in
  `WORKSHOP_INSTRUCTIONS.md` / `WORKSHOP_INSTRUCTIONS_WORKSPACE.md`, Step 7. They can only grant
  what they own — which is why Step 3 has them owning their schema.

---

## Verification (a participant can self-check)

```sql
-- UC: can they create a schema?
CREATE SCHEMA IF NOT EXISTS `<catalog>`.`<test_schema>`;
```

```bash
# Warehouse usable + model endpoints queryable?
databricks warehouses list --profile <profile>
databricks serving-endpoints list --profile <profile>
```

A failure on any line points to the matching step above being incomplete.

---

## Source references (within this repo)

- `medium/WORKSHOP_INSTRUCTIONS.md` — local-CLI participant guide
- `medium/WORKSHOP_INSTRUCTIONS_WORKSPACE.md` — workspace-only guide (lists features to enable)
- `data/workspace_setup_script/01_quickstart_setup.py` — creates UC tables, Vector Search index, Genie Space, MLflow experiment
- `medium/scripts/quickstart.py` — auth, MLflow experiment, Lakebase provisioning
