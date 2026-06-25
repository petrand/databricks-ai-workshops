# Clean up — tear down the workshop resources

Destroys everything created by [`DEPLOY_FROM_SCRATCH.md`](./DEPLOY_FROM_SCRATCH.md), in
dependency order. Run the blocks top-to-bottom. Replace `<profile>` with your CLI profile.

> ⚠️ **Destructive and irreversible.** This permanently deletes the app, the Lakebase
> database (all chat history, agent memory, uploaded-policy records), the seed UC tables,
> the Vector Search index/endpoint, the Knowledge Assistant, the Genie space, and the MLflow
> experiment. Make sure you're pointed at the right workspace: `databricks auth env --profile <profile>`.

> 💸 **Biggest cost drivers** (delete these first if you just want to stop spend): the
> **Lakebase instance**, the **Vector Search endpoint**, the **Knowledge Assistant endpoint**,
> and any dedicated **SQL warehouse**.

Resource names below are from this deployment — adjust if yours differ:

| Resource | Name |
|---|---|
| App | `agent-vicinity-router` |
| Lakebase instance | `agent-router-lakebase` |
| Vector Search index | `dev.policies.policy_docs_index` |
| Vector Search endpoint | `vicinity-policies-vs` |
| Knowledge Assistant endpoint | `ka-a9d02891-endpoint` |
| Genie space | `Vicinity Foot Traffic Genie` (`01f1693a7f2f1e148e53cc17d77fe89d`) |
| Seed tables | `dev.policies.policy_docs`, `dev.operations.foot_traffic` |
| MLflow experiment | the id in `databricks.yml` (`MLFLOW_EXPERIMENT_ID`) |

---

## 0. Stop the uploaded-policy CDF stream — `[UI]` (only if you enabled step 9 of deploy)

In **Postgres → your project/branch → Change Data Feed → Stop** before deleting the Lakebase
instance, and unschedule/delete the `sync_uploaded_policies_cdf.py` job. Skip if you never set CDF up.

---

## 1. Destroy the app + Lakebase instance — `[DAB]`

`bundle destroy` removes the two DAB-managed resources (the **App** and the **Lakebase
instance**) and the uploaded bundle files. It prompts twice; add `--auto-approve` to skip.

```bash
cd medium
databricks bundle destroy --profile <profile>
```

This also frees the app's service principal — the UC/Genie grants made to it (deploy steps 7–8)
become orphaned automatically, so there's nothing to revoke.

> If the app delete is blocked or the instance lingers, delete them explicitly:
> ```bash
> databricks apps delete agent-vicinity-router --profile <profile>
> databricks database delete-database-instance agent-router-lakebase --profile <profile>
> ```

---

## 2. Delete the Knowledge Assistant + serving endpoint — `[SDK/UI]`

Agent Bricks Knowledge Assistants are easiest to remove in the **Agent Bricks UI**
(open the assistant → Delete). The serving endpoint is removed with it.

Or via the SDK (best-effort — confirm method names with your `databricks-sdk` version):
```bash
DATABRICKS_CONFIG_PROFILE=<profile> uv run python - <<'PY'
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
for ka in w.knowledge_assistants.list_knowledge_assistants():
    if "Vicinity" in (ka.display_name or ""):
        print("deleting", ka.name, ka.display_name)
        w.knowledge_assistants.delete_knowledge_assistant(name=ka.name)
PY
```
If the serving endpoint outlives the KA, delete it directly:
```bash
databricks serving-endpoints delete ka-a9d02891-endpoint --profile <profile>
```

---

## 3. Delete the Vector Search index, then the endpoint — `[CLI]`

Delete the index before the endpoint (the index lives on the endpoint).

```bash
databricks vector-search-indexes delete-index dev.policies.policy_docs_index --profile <profile>
databricks vector-search-endpoints delete-endpoint vicinity-policies-vs --profile <profile>
```
> If your CLI version differs, delete both from the **Compute → Vector Search** UI.

---

## 4. Delete the Genie space — `[UI]`

Open **Genie → Vicinity Foot Traffic Genie → ⋯ → Delete**. (Genie space deletion isn't exposed
as a stable CLI command, so use the UI.)

---

## 5. Delete the MLflow experiment — `[CLI/UI]`

```bash
databricks experiments delete-experiment <experiment-id> --profile <profile>
```
(or open the experiment in the **Experiments** UI → Delete). The id is in `databricks.yml`.

---

## 6. Drop the seed UC tables and schemas — `[CLI]`

Delete the tables, then the (now-empty) schemas. `--force` drops a schema with any remaining objects.

```bash
# tables
databricks tables delete dev.policies.policy_docs        --profile <profile>
databricks tables delete dev.operations.foot_traffic     --profile <profile>
# the CDF history table, only if step 9/CDF was used:
databricks tables delete dev.policies.lb_PolicyUpload_history --profile <profile> 2>/dev/null || true

# schemas (we created these for the workshop)
databricks schemas delete dev.policies   --force --profile <profile>
databricks schemas delete dev.operations --force --profile <profile>
```

Equivalent SQL if you prefer the SQL editor / a notebook:
```sql
DROP SCHEMA IF EXISTS dev.policies   CASCADE;
DROP SCHEMA IF EXISTS dev.operations CASCADE;
```

---

## 7. Leave these alone (shared / pre-existing)

- **`dev` catalog** — typically shared; only the `policies`/`operations` schemas were ours. Don't drop the catalog unless you created it solely for this workshop.
- **SQL warehouse** — pre-existing/shared; do **not** delete it (just stop spending by leaving it auto-stopped).

Local cleanup (optional):
```bash
rm -rf .databricks/bundle        # local bundle state/build artifacts
# rm .env                        # only if you don't want the cached config
```

---

## 8. Verify everything is gone

```bash
databricks apps list --profile <profile> | grep -i agent-vicinity-router || echo "app gone"
databricks database list-database-instances --profile <profile> | grep -i agent-router-lakebase || echo "lakebase gone"
databricks vector-search-endpoints list-endpoints --profile <profile> | grep -i vicinity-policies-vs || echo "vs endpoint gone"
databricks serving-endpoints list --profile <profile> | grep -i ka-a9d02891 || echo "KA endpoint gone"
databricks schemas list dev --profile <profile> | grep -iE "policies|operations" || echo "schemas gone"
```
Then confirm in the UI that the **Genie space** and **MLflow experiment** are deleted.

---

## Quick teardown (TL;DR)

```bash
cd medium
databricks bundle destroy --profile <profile> --auto-approve          # app + lakebase
databricks vector-search-indexes  delete-index    dev.policies.policy_docs_index --profile <profile>
databricks vector-search-endpoints delete-endpoint vicinity-policies-vs          --profile <profile>
databricks serving-endpoints delete ka-a9d02891-endpoint --profile <profile>     # if KA endpoint remains
databricks experiments delete-experiment <experiment-id> --profile <profile>
databricks tables  delete dev.policies.policy_docs    --profile <profile>
databricks tables  delete dev.operations.foot_traffic --profile <profile>
databricks schemas delete dev.policies   --force --profile <profile>
databricks schemas delete dev.operations --force --profile <profile>
# then: delete the Knowledge Assistant + Genie space in the UI
```
