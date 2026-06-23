# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "1"
# ///
# MAGIC %md
# MAGIC # Vicinity Centres — Hourly Foot Traffic (Synthetic Data)
# MAGIC
# MAGIC Generates synthetic **hourly foot-traffic** records per shopping centre and writes
# MAGIC `${catalog}.${ops_schema}.${ops_table}` (defaults `dev` / `operations` / `foot_traffic_hourly`).
# MAGIC
# MAGIC **One row per centre per date per trading hour**, with realistic patterns:
# MAGIC - Centre opening hours (weekday/Thursday late-night/Saturday/Sunday).
# MAGIC - Intra-day curve: morning ramp, lunchtime peak, evening peak, close-of-day tail.
# MAGIC - Weekend uplift, a December pre-Christmas surge, a Boxing Day spike, and
# MAGIC   zero trade on Christmas Day / Good Friday.
# MAGIC
# MAGIC The data is fictional and intended for demos, Genie/RAG, and testing. Set the widgets
# MAGIC at the top, then **Run All**. Company portfolio and holiday logic match the daily
# MAGIC foot-traffic notebook so the two tables tie out.

# COMMAND ----------

# MAGIC %md ## 1. Configuration

# COMMAND ----------

import datetime

dbutils.widgets.text("catalog", "dev", "Target catalog")
dbutils.widgets.text("ops_schema", "operations", "Foot-traffic schema")
dbutils.widgets.text("ops_table", "foot_traffic_hourly", "Foot-traffic table")
dbutils.widgets.text("traffic_days", "90", "Days of history to generate")
dbutils.widgets.text("traffic_end_date", "", "End date YYYY-MM-DD (blank = today)")
dbutils.widgets.dropdown("write_mode", "overwrite", ["overwrite", "append"], "Write mode")

CATALOG = dbutils.widgets.get("catalog")
OPS_SCHEMA = dbutils.widgets.get("ops_schema")
OPS_TABLE = dbutils.widgets.get("ops_table")
WRITE_MODE = dbutils.widgets.get("write_mode")
OPS_FQN = f"{CATALOG}.{OPS_SCHEMA}.{OPS_TABLE}"
N_DAYS = int(dbutils.widgets.get("traffic_days") or "90")
_end_raw = dbutils.widgets.get("traffic_end_date").strip()
END_DATE = (datetime.datetime.strptime(_end_raw, "%Y-%m-%d").date()
            if _end_raw else datetime.date.today())
START_DATE = END_DATE - datetime.timedelta(days=N_DAYS - 1)
print(f"Hourly foot-traffic target: {OPS_FQN}  "
      f"({N_DAYS} days, {START_DATE} -> {END_DATE}, mode={WRITE_MODE})")

# COMMAND ----------

# MAGIC %md ## 2. Portfolio, calendar & hourly profiles

# COMMAND ----------

import random

random.seed(42)  # reproducible

# Fictional Vicinity-style portfolio. base_daily = typical weekday visitor count.
# centre_id, name, state, centre_type, gla_sqm, base_daily
CENTRES = [
    ("CTR-01", "Chadstone",          "VIC", "Flagship",     210000, 78000),
    ("CTR-02", "Emporium Melbourne", "VIC", "CBD",           62000, 41000),
    ("CTR-03", "Northland",          "VIC", "Regional",      98000, 39000),
    ("CTR-04", "Box Hill Central",   "VIC", "Sub-regional",  47000, 24000),
    ("CTR-05", "The Glen",           "VIC", "Sub-regional",  64000, 27000),
    ("CTR-06", "DFO South Wharf",    "VIC", "Outlet",        38000, 21000),
    ("CTR-07", "Bankstown Central",  "NSW", "Regional",      83000, 34000),
    ("CTR-08", "Chatswood Chase",    "NSW", "Sub-regional",  46000, 26000),
    ("CTR-09", "Roselands",          "NSW", "Sub-regional",  58000, 23000),
    ("CTR-10", "Galleria",           "WA",  "Regional",      75000, 31000),
    ("CTR-11", "Mandurah Forum",     "WA",  "Sub-regional",  56000, 19000),
    ("CTR-12", "Castle Plaza",       "SA",  "Neighbourhood", 34000, 14000),
]

# --- Australian public holidays: fixed-date + Easter-derived (Anonymous Gregorian) ---
def _easter(year):
    a = year % 19; b = year // 100; c = year % 100; d = b // 4; e = b % 4
    f = (b + 8) // 25; g = (b - f + 1) // 3; h = (19 * a + b - d - g + 15) % 30
    i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31; day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime.date(year, month, day)

def au_holidays(years):
    hol = {}
    for y in years:
        hol[datetime.date(y, 1, 1)]   = "New Year's Day"
        hol[datetime.date(y, 1, 26)]  = "Australia Day"
        hol[datetime.date(y, 4, 25)]  = "ANZAC Day"
        hol[datetime.date(y, 12, 25)] = "Christmas Day"
        hol[datetime.date(y, 12, 26)] = "Boxing Day"
        es = _easter(y)
        hol[es - datetime.timedelta(days=2)] = "Good Friday"
        hol[es]                              = "Easter Sunday"
        hol[es + datetime.timedelta(days=1)] = "Easter Monday"
    return hol

HOLIDAYS = au_holidays(range(START_DATE.year, END_DATE.year + 1))
CLOSED = {"Christmas Day", "Good Friday"}  # centres do not trade

DOW = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
# Total-day multiplier vs. the weekday baseline (matches the daily notebook).
DOW_FACTOR = {0: 0.92, 1: 0.90, 2: 0.95, 3: 1.00, 4: 1.18, 5: 1.45, 6: 1.22}

def _season(d):
    # December pre-Christmas surge, January sales, mid-winter dip.
    return {12: 1.35, 1: 1.12, 6: 0.93, 7: 0.90}.get(d.month, 1.0)

# Trading hours per day type: (open_hour, close_hour) inclusive of the open hour,
# exclusive of the close hour. Thursday is late-night trade in AU shopping centres.
HOURS_BY_DAY = {
    0: (9, 18), 1: (9, 18), 2: (9, 18),   # Mon-Wed
    3: (9, 21),                            # Thu late-night
    4: (9, 18),                            # Fri
    5: (9, 18),                            # Sat
    6: (10, 17),                           # Sun (shorter)
}

# Relative shape of foot traffic across the open hours. Weights are normalised per
# day, so only the SHAPE matters here. Morning ramp -> lunch peak -> evening peak.
def hour_weights(open_h, close_h, is_weekend):
    w = {}
    for h in range(open_h, close_h):
        if h < 11:
            base = 0.45 + 0.15 * (h - open_h)          # morning ramp-up
        elif 11 <= h <= 14:
            base = 1.25 if h in (12, 13) else 1.05     # lunchtime peak
        elif 15 <= h <= 17:
            base = 0.95
        else:
            base = 0.80 if not is_weekend else 0.70    # evening (late-night Thu)
        # Weekends are flatter (steady all-day family visits); weekdays spikier.
        if is_weekend:
            base = 0.75 + 0.55 * (base - 0.45)
        w[h] = max(base, 0.2)
    total = sum(w.values())
    return {h: v / total for h, v in w.items()}

# COMMAND ----------

# MAGIC %md ## 3. Generate hourly rows

# COMMAND ----------

rows = []
d = START_DATE
while d <= END_DATE:
    wd = d.weekday()
    is_weekend = wd >= 5
    hol_name = HOLIDAYS.get(d)
    is_hol = hol_name is not None
    closed = hol_name in CLOSED
    if closed:
        d += datetime.timedelta(days=1)
        continue  # no trading hours on closed days -> no rows

    open_h, close_h = HOURS_BY_DAY[wd]
    weights = hour_weights(open_h, close_h, is_weekend)

    # Day-level multiplier, mirroring the daily notebook so totals tie out.
    day_factor = DOW_FACTOR[wd] * _season(d)
    if hol_name == "Boxing Day":
        day_factor *= 2.4
    elif hol_name == "Easter Sunday":
        day_factor *= 0.6  # restricted trade
    elif is_hol:
        day_factor *= 1.08

    for cid, name, state, ctype, gla, base in CENTRES:
        day_total = base * day_factor * random.uniform(0.90, 1.10)
        for h in range(open_h, close_h):
            visitors = int(day_total * weights[h] * random.uniform(0.93, 1.07))
            rows.append((
                cid, name, state, ctype, gla,
                d, datetime.datetime.combine(d, datetime.time(hour=h)),
                DOW[wd], h, is_weekend, is_hol, hol_name, visitors,
            ))
    d += datetime.timedelta(days=1)

print(f"Generated {len(rows):,} rows "
      f"({len(CENTRES)} centres x ~{len(rows)//max(len(CENTRES),1):,} centre-hours)")

# COMMAND ----------

# MAGIC %md ## 4. Create schema and write the table

# COMMAND ----------

from pyspark.sql.types import (StructType, StructField, StringType, DateType,
                               TimestampType, IntegerType, BooleanType)

hourly_schema = StructType([
    StructField("centre_id", StringType(), False),
    StructField("centre_name", StringType(), False),
    StructField("state", StringType(), True),
    StructField("centre_type", StringType(), True),
    StructField("gla_sqm", IntegerType(), True),
    StructField("traffic_date", DateType(), False),
    StructField("traffic_hour_ts", TimestampType(), False),
    StructField("day_of_week", StringType(), True),
    StructField("hour_of_day", IntegerType(), False),
    StructField("is_weekend", BooleanType(), True),
    StructField("is_public_holiday", BooleanType(), True),
    StructField("holiday_name", StringType(), True),
    StructField("visitor_count", IntegerType(), True),
])

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{OPS_SCHEMA} "
          f"COMMENT 'Synthetic operational data (foot traffic) for the property management demo'")

hourly_df = spark.createDataFrame(rows, hourly_schema)
(hourly_df.write
   .format("delta")
   .mode(WRITE_MODE)
   .option("overwriteSchema", "true")
   .saveAsTable(OPS_FQN))

# Table + column comments help Genie generate accurate SQL.
spark.sql(
    f"COMMENT ON TABLE {OPS_FQN} IS "
    f"'Hourly foot-traffic (visitor counts) per Vicinity shopping centre; one row per centre "
    f"per trading hour. Rows exist only for hours the centre is open, so non-trading public "
    f"holidays (Christmas Day, Good Friday) have no rows.'")
for _col, _desc in [
    ("centre_id", "Stable centre identifier, e.g. CTR-01"),
    ("centre_name", "Shopping centre name"),
    ("state", "Australian state/territory (VIC, NSW, WA, SA)"),
    ("centre_type", "Format: Flagship, CBD, Regional, Sub-regional, Outlet, Neighbourhood"),
    ("gla_sqm", "Gross lettable area in square metres (a proxy for centre size)"),
    ("traffic_date", "Calendar date of the foot-traffic measurement"),
    ("traffic_hour_ts", "Timestamp at the start of the measured hour (local centre time)"),
    ("day_of_week", "Day name (Monday..Sunday)"),
    ("hour_of_day", "Hour of day (0-23) the visitor count covers"),
    ("is_weekend", "True for Saturday and Sunday"),
    ("is_public_holiday", "True if the date is an Australian public holiday"),
    ("holiday_name", "Name of the public holiday, otherwise null"),
    ("visitor_count", "Visitors entering the centre during this hour (foot traffic)"),
]:
    spark.sql(f"COMMENT ON COLUMN {OPS_FQN}.{_col} IS '{_desc}'")

print(f"Wrote {hourly_df.count():,} rows to {OPS_FQN}")
display(hourly_df.orderBy("traffic_hour_ts", ascending=False).limit(24))

# COMMAND ----------

# MAGIC %md ## 5. Verify
# MAGIC
# MAGIC A few sanity checks: busiest hour of the day, and a per-centre daily rollup that should
# MAGIC line up with the daily `foot_traffic` table's order of magnitude.

# COMMAND ----------

print("Average visitors by hour of day (across all centres):")
display(spark.sql(f"""
    SELECT hour_of_day, ROUND(AVG(visitor_count)) AS avg_visitors
    FROM {OPS_FQN}
    GROUP BY hour_of_day
    ORDER BY hour_of_day
"""))

print("Daily totals per centre (last 7 days):")
display(spark.sql(f"""
    SELECT centre_name, traffic_date, SUM(visitor_count) AS daily_visitors
    FROM {OPS_FQN}
    WHERE traffic_date >= date_sub((SELECT MAX(traffic_date) FROM {OPS_FQN}), 6)
    GROUP BY centre_name, traffic_date
    ORDER BY traffic_date DESC, daily_visitors DESC
"""))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Use it in a Genie space
# MAGIC
# MAGIC Add `${catalog}.${ops_schema}.${ops_table}` as a data table in a Genie space to answer
# MAGIC hourly questions. Sample prompts to seed the space:
# MAGIC - "What is the busiest hour of the day at Chadstone?"
# MAGIC - "Compare morning vs evening foot traffic on weekdays."
# MAGIC - "Show hourly visitors for Emporium Melbourne last Thursday (late-night trade)."
# MAGIC - "Which centre has the most evening traffic on weekends?"
# MAGIC - "Plot the intra-day curve for VIC centres."
