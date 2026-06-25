# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "1"
# ///
# MAGIC %md
# MAGIC # Sync uploaded policies: Lakebase CDF → Delta `policy_docs`
# MAGIC
# MAGIC The chatbot app's **Add policy** tab converts an uploaded PDF to text and writes a row
# MAGIC to the Lakebase Postgres table `ai_chatbot."PolicyUpload"` (the editable "in-between"
# MAGIC table). **Lakebase Change Data Feed** (`wal2delta`) captures every insert/update/delete
# MAGIC on that table from the Postgres write-ahead log and lands them — batched, flushed every
# MAGIC ~15s — in a Unity Catalog Delta **history** table named `lb_PolicyUpload_history`.
# MAGIC
# MAGIC This notebook reads that history table, reduces it to the **latest state per policy**,
# MAGIC and `MERGE`s it into the Delta `policy_docs` table the agent searches. The existing
# MAGIC Vector Search Delta Sync index + Knowledge Assistant over `policy_docs` then pick the
# MAGIC new/edited policy up automatically.
# MAGIC
# MAGIC ```
# MAGIC  Add policy tab ──▶ Lakebase  ai_chatbot."PolicyUpload"   (REPLICA IDENTITY FULL)
# MAGIC                        │  wal2delta CDF  (~15s flush)
# MAGIC                        ▼
# MAGIC               <cdf_catalog>.<cdf_schema>.lb_PolicyUpload_history
# MAGIC                        │  this notebook: latest-state MERGE
# MAGIC                        ▼
# MAGIC               dev.policies.policy_docs ──▶ Vector Search index ──▶ Knowledge Assistant
# MAGIC ```
# MAGIC
# MAGIC ### Prerequisites (one-time)
# MAGIC 1. The Lakebase table has `REPLICA IDENTITY FULL` — the app's `0004` migration sets this.
# MAGIC    Re-apply with `lakebase_cdf_setup.sql` if you created the table another way.
# MAGIC 2. **Enable CDF** in the Lakebase app: *Postgres → project/branch → Branch overview →
# MAGIC    Change Data Feed → Start*. Source schema `ai_chatbot`; destination catalog/schema =
# MAGIC    the `cdf_catalog`/`cdf_schema` widgets below. (Destination catalog must not use
# MAGIC    default storage.)
# MAGIC 3. Schedule this notebook as a job (e.g. every 5–10 min) or run it on demand. It is
# MAGIC    idempotent — it always recomputes latest state from the full history table.

# COMMAND ----------

dbutils.widgets.text("cdf_catalog", "dev", "CDF destination catalog")
dbutils.widgets.text("cdf_schema", "policies", "CDF destination schema")
dbutils.widgets.text("history_table", "lb_PolicyUpload_history", "CDF history table name")
dbutils.widgets.text("target_catalog", "dev", "Policy table catalog")
dbutils.widgets.text("target_schema", "policies", "Policy table schema")
dbutils.widgets.text("target_table", "policy_docs", "Policy table name")

CDF_CATALOG = dbutils.widgets.get("cdf_catalog")
CDF_SCHEMA = dbutils.widgets.get("cdf_schema")
HISTORY_TABLE = dbutils.widgets.get("history_table")
HISTORY_FQN = f"{CDF_CATALOG}.{CDF_SCHEMA}.{HISTORY_TABLE}"

TARGET_FQN = (
    f"{dbutils.widgets.get('target_catalog')}."
    f"{dbutils.widgets.get('target_schema')}."
    f"{dbutils.widgets.get('target_table')}"
)
print(f"History (source): {HISTORY_FQN}")
print(f"Policy (target):  {TARGET_FQN}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Reduce the change feed to the latest row per policy
# MAGIC
# MAGIC Each update produces an `update_preimage` + `update_postimage` pair; inserts produce a
# MAGIC single `insert`; deletes a single `delete`. We keep, per `policyId`, the most recent
# MAGIC change (highest `_sort_by`). Rows whose latest change is a delete are dropped from the
# MAGIC upsert set and removed from the target. Postgres column identifiers are camelCase.

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.window import Window

history = spark.read.table(HISTORY_FQN)

latest = (
    history.withColumn(
        "_rn",
        F.row_number().over(
            Window.partitionBy("policyId").orderBy(F.col("_sort_by").desc())
        ),
    )
    .filter(F.col("_rn") == 1)
    .drop("_rn")
)

# Current (non-deleted) policies, mapped to the Delta `policy_docs` schema.
upserts = (
    latest.filter(F.col("_pg_change_type") != "delete")
    .select(
        F.col("policyId").alias("policy_id"),
        F.col("docName").alias("doc_name"),
        F.col("category"),
        F.col("title"),
        F.col("effectiveDate").cast("date").alias("effective_date"),
        F.col("reviewDate").cast("date").alias("review_date"),
        F.col("owner"),
        F.col("version"),
        F.col("content"),
    )
)

deletes = latest.filter(F.col("_pg_change_type") == "delete").select(
    F.col("policyId").alias("policy_id")
)

print(f"Upserts: {upserts.count()} | Deletes: {deletes.count()}")
upserts.select("policy_id", "title", "category").show(truncate=60)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. MERGE into the Delta policy table
# MAGIC
# MAGIC Only the policy columns are touched — the review columns (`review_status`,
# MAGIC `review_comment`, `reviewed_by`, `reviewed_at`) written by the dashboard's review
# MAGIC endpoint are intentionally left untouched on matched rows.

# COMMAND ----------

from delta.tables import DeltaTable

target = DeltaTable.forName(spark, TARGET_FQN)

(
    target.alias("t")
    .merge(upserts.alias("s"), "t.policy_id = s.policy_id")
    .whenMatchedUpdate(
        set={
            "doc_name": "s.doc_name",
            "category": "s.category",
            "title": "s.title",
            "effective_date": "s.effective_date",
            "review_date": "s.review_date",
            "owner": "s.owner",
            "version": "s.version",
            "content": "s.content",
        }
    )
    .whenNotMatchedInsert(
        values={
            "policy_id": "s.policy_id",
            "doc_name": "s.doc_name",
            "category": "s.category",
            "title": "s.title",
            "effective_date": "s.effective_date",
            "review_date": "s.review_date",
            "owner": "s.owner",
            "version": "s.version",
            "content": "s.content",
        }
    )
    .execute()
)

# Propagate deletes (a policy removed from Lakebase is removed from the agent's view).
if deletes.count() > 0:
    target.alias("t").merge(
        deletes.alias("s"), "t.policy_id = s.policy_id"
    ).whenMatchedDelete().execute()

print("MERGE complete.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Verify
# MAGIC
# MAGIC Uploaded policies use the `UPL-###` id prefix (seed policies use `POL-###`).

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT policy_id, title, category, owner, review_date,
               LENGTH(content) AS content_chars
        FROM {TARGET_FQN}
        WHERE policy_id LIKE 'UPL-%'
        ORDER BY policy_id
        """
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC The Vector Search Delta Sync index over `policy_docs` (created in
# MAGIC `create_property_policy_data.py`) re-syncs the changed rows on its own schedule, after
# MAGIC which the agent's **Vicinity Policy Search** and **Knowledge Assistant** tools can answer
# MAGIC from the newly uploaded policy.
