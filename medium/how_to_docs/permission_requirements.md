# Admin Grants for Workshop Participants — L200 "Build an AI Agent with Memory"

This document lists **only the grants and entitlements a workspace/account admin must give to
each workshop participant** so they can complete the **medium** workshop: prepare the data, run
the agent locally, and deploy it as a Databricks App with Lakebase-backed memory.

**Scope assumption:** participants grant their own deployed app's **service principal** whatever
it needs (Unity Catalog `SELECT`, Genie `Can Run`, Lakebase access) as part of the workshop
guides — that is *not* an admin task and is **out of scope** here. See the bottom of this doc for
what participants handle themselves.

> **Tip:** Put all participants in a group (e.g. `workshop-users`) and apply every grant below to
> the group once, rather than per user.

---

## Quick reference

| # | Grant / enablement | Scope | Where the admin sets it |
|---|---|---|---|
| 1 | Workspace access | Per user/group | Admin console → entitlements |
| 1 | Databricks SQL access | Per user/group | Admin console → entitlements |
| 1 | Serverless / cluster use | Per user/group | Admin console → entitlements |
| 2 | Unity Catalog enabled | Workspace | Account/metastore |
| 2 | Vector Search enabled | Workspace/region | Workspace setting |
| 2 | Foundation Model APIs enabled | Workspace/region | Workspace setting |
| 2 | Genie enabled | Workspace | Workspace setting |
| 2 | Lakebase / Database Instances enabled | Workspace | Workspace setting |
| 2 | Databricks Apps enabled | Workspace | Workspace setting |
| 2 | Web Terminal enabled | Workspace | Settings → Developer |
| 2 | Repos / Git folders allowed | Workspace | Workspace setting |
| 3 | `CAN_USE` on a running **SQL warehouse** | Warehouse | Warehouse permissions |
| 4 | `USE CATALOG` + `CREATE SCHEMA` on a catalog | Catalog | Catalog Explorer / `GRANT` |
| 5 | `CAN_QUERY` on `databricks-gte-large-en` | Serving endpoint | Serving endpoint permissions |
| 5 | `CAN_QUERY` on the chat model (e.g. `databricks-claude-sonnet-4-6`) | Serving endpoint | Serving endpoint permissions |
| 6 | Can **create Vector Search endpoints** | Workspace | Feature access |
| 6 | Can **create Genie Spaces** | Workspace | Genie access |
| 6 | Can **create Lakebase instances** | Workspace | Lakebase/OLTP access |
| 6 | Can **create Databricks Apps** | Workspace | Apps access |

---

## 1. Per-user entitlements (admin console)

Grant these entitlements to each participant (or the `workshop-users` group):

- **Workspace access** (`workspace-access`) — open notebooks, the file browser, Compute/SQL UIs.
- **Databricks SQL access** (`databricks-sql-access`) — use SQL warehouses and the SQL editor
  (needed for the data setup and for granting the SP later).
- **Serverless / compute use** — the data setup notebook runs on **serverless** compute. Ensure
  participants can attach to serverless (or grant cluster-create / `CAN_ATTACH` on a shared
  cluster that runs Spark SQL + Python).

## 2. Workspace features to enable

These are workspace/region-level toggles (no per-user object ACL). Confirm all are on:

- **Unity Catalog** (required throughout).
- **Vector Search** (in a supported region).
- **Foundation Model APIs** (pay-per-token; in a supported region).
- **Genie**.
- **Lakebase / Database Instances** (OLTP).
- **Databricks Apps**.
- **Web Terminal** (Settings → Developer) — required for the recommended workspace-only deploy path.
- **Repos / Git folders** — allow Git folder creation; make sure participants can add Git credentials.

## 3. Compute — SQL warehouse

- Grant **`CAN_USE`** on at least one **running SQL warehouse** to all participants.
- This is needed because the Genie Space is bound to a warehouse and the data setup uses one. If
  no warehouse is running/visible, Genie Space creation is skipped.

## 4. Unity Catalog — where participants create data

Participants create a schema and ~7 tables plus the Vector Search index. The simplest model is to
let each participant **own their own schema** (so they automatically get table privileges).

Grant on a shared/sandbox catalog (or a per-user catalog):

- **`USE CATALOG`**
- **`CREATE SCHEMA`**

Example:

```sql
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG <catalog> TO `workshop-users`;
```

> If you instead pre-create one schema per participant, grant `USE SCHEMA` + `CREATE TABLE` on
> that schema. Granting `CREATE SCHEMA` and letting users make (and own) their own schema is
> simpler and avoids per-table grants. `CREATE CATALOG` is **not** required — the catalog-creation
> step in the setup notebook is commented out.

## 5. Model serving — Foundation Models

The Delta Sync Vector Search index calls an embedding endpoint, and the agent calls a chat model.
Grant **`CAN_QUERY`** to participants on:

- **`databricks-gte-large-en`** — embeddings for the Vector Search index.
- **The chat model** the agent uses (default **`databricks-claude-sonnet-4-6`**, configurable in
  `agent_server/agent.py`).

> Pay-per-token system endpoints are often queryable by all users by default. In governed
> workspaces (where serving-endpoint ACLs are restricted) the admin must grant `CAN_QUERY`
> explicitly. If your org gates models through AI Gateway, ensure the chosen model is allowed.

## 6. Permission to create the workshop resources

Participants create several resources themselves. Ensure they're allowed to:

- **Create Vector Search endpoints** (plus the index — covered by `CREATE SCHEMA`/owning the schema in §4).
- **Create Genie Spaces.**
- **Create Lakebase instances** (autoscaling project + branch + endpoint, or a provisioned instance).
- **Create Databricks Apps** (deploying creates the app and its service principal).

These are governed by the corresponding feature being enabled (§2) plus, in locked-down
workspaces, a "users may create …" setting or `CAN_MANAGE`-type permission. If participants can't
create one of these, that's the admin lever to flip.

---

## What participants handle themselves (no admin action)

These are **out of scope** for the admin — listed so there's no confusion:

- **MLflow experiment** — created in the participant's own `/Users/<email>` folder, which they
  already own (`CAN_MANAGE`). No grant needed.
- **Service-principal grants for the deployed app** — after deploying, participants grant their
  app's SP what it needs:
  - Unity Catalog `USE CATALOG` / `USE SCHEMA` / `SELECT` on their schema,
  - Genie Space **Can Run** (Share dialog),
  - Lakebase schema/table/sequence grants (or let the app create+own its tables).
  
  This is documented in the workshop guides (`WORKSHOP_INSTRUCTIONS.md`,
  `WORKSHOP_INSTRUCTIONS_WORKSPACE.md`, Step 7). Participants can only grant what they own, which
  is why §4 has them owning their schema.
- **Writing to their own workspace folder** — default for any user with workspace access.

---

## Verification (optional, per participant)

A participant can sanity-check their access before starting:

```sql
-- Unity Catalog: can they create a schema?
CREATE SCHEMA IF NOT EXISTS <catalog>.<test_schema>;
```

```bash
# SQL warehouse visible + usable?
databricks warehouses list --profile <profile>

# Foundation model endpoints queryable?
databricks serving-endpoints list --profile <profile>
```

If schema creation, warehouse use, or endpoint listing fails, the matching grant above is missing.

---

## Source references (within this repo)

- `medium/WORKSHOP_INSTRUCTIONS.md` — local-CLI participant guide
- `medium/WORKSHOP_INSTRUCTIONS_WORKSPACE.md` — workspace-only guide (prereqs list features to enable)
- `data/README.md` — data setup paths
- `data/workspace_setup_script/01_quickstart_setup.py` — creates UC tables, Vector Search index, Genie Space, MLflow experiment
- `medium/scripts/quickstart.py` — auth, MLflow experiment, Lakebase provisioning
