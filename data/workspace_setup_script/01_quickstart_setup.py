# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "1"
# ///
# MAGIC %md
# MAGIC    
# MAGIC # EduPath Academy Workshop Setup
# MAGIC
# MAGIC This notebook creates everything you need for the workshop:
# MAGIC
# MAGIC | Step | What it creates |
# MAGIC |------|----------------|
# MAGIC | 1 | Catalog and schema in Unity Catalog |
# MAGIC | 2 | 6 education data tables (students, courses, campuses, enrollments, etc.) |
# MAGIC | 3 | Policy documents table (chunked for search) |
# MAGIC | 4 | Vector Search endpoint and index |
# MAGIC | 5 | Genie Space for natural language data queries |
# MAGIC | 6 | MLflow experiment for agent evaluation |
# MAGIC
# MAGIC **Instructions:** Fill in your catalog and schema names in the widgets at the top of the notebook, then click **Run All**.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration
# MAGIC
# MAGIC Set your catalog and schema names using the widgets above. These will be used for all resources created in this notebook.

# COMMAND ----------

# MAGIC %pip install databricks-vectorsearch 
# MAGIC %restart_python

# COMMAND ----------

if "catalog" not in dbutils.widgets.getAll():
    dbutils.widgets.text("catalog", "", "Catalog Name")
if "schema" not in dbutils.widgets.getAll():
    dbutils.widgets.text("schema", "", "Schema Name")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")

if not CATALOG:
    raise ValueError("Please enter a catalog name in the widget at the top of the notebook.")

FULL_SCHEMA = f"{CATALOG}.{SCHEMA}"
print(f"Using schema: {FULL_SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Create Catalog and Schema

# COMMAND ----------

# spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}") # Only if you have access to create catalog and want to have a new catalog for the workshop
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {FULL_SCHEMA}")
print(f"Catalog '{CATALOG}' and schema '{FULL_SCHEMA}' are ready.")

# COMMAND ----------

# MAGIC %md
# MAGIC    
# MAGIC ## Step 2: Create Education Data Tables
# MAGIC
# MAGIC This generates synthetic data for a fictional online learning platform called **EduPath Academy**:
# MAGIC - **customers** — 200 students with enrollment tiers and academic preferences
# MAGIC - **products** — ~500 courses across 10 departments
# MAGIC - **stores** — 10 EduPath campus locations
# MAGIC - **transactions** — 2,000 enrollment records
# MAGIC - **transaction_items** — ~8,000 course enrollment line items
# MAGIC - **payment_history** — 400 tuition payment records

# COMMAND ----------

import json
import random
from datetime import datetime, timedelta

random.seed(42)

# ── Domain data ──────────────────────────────────────────────────────

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Lisa", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Carol", "Kevin", "Amanda", "Brian", "Dorothy", "George", "Melissa",
    "Timothy", "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Anna", "Stephen", "Brenda",
    "Larry", "Pamela", "Justin", "Emma", "Scott", "Nicole", "Brandon", "Helen",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Raymond", "Christine", "Gregory", "Debra",
    "Frank", "Rachel", "Alexander", "Carolyn", "Patrick", "Janet", "Jack", "Catherine",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts",
]

STREETS = [
    "Main St", "Oak Ave", "Elm St", "Park Blvd", "Cedar Ln", "Maple Dr", "Pine St",
    "Washington Ave", "Lake Rd", "Hill St", "Forest Dr", "River Rd", "Church St",
    "Spring St", "Meadow Ln", "Sunset Blvd", "Valley Rd", "Garden Way", "Market St",
    "Highland Ave",
]

CITIES_STATES = [
    ("Portland", "OR"), ("Seattle", "WA"), ("San Francisco", "CA"), ("Los Angeles", "CA"),
    ("Denver", "CO"), ("Austin", "TX"), ("Chicago", "IL"), ("Boston", "MA"),
    ("New York", "NY"), ("Atlanta", "GA"), ("Miami", "FL"), ("Phoenix", "AZ"),
    ("Minneapolis", "MN"), ("Nashville", "TN"), ("Salt Lake City", "UT"),
]

MEMBERSHIP_TIERS = ["Freshman", "Sophomore", "Junior", "Senior"]
LEARNING_STYLES = ["visual", "auditory", "reading", "kinesthetic", "hybrid", "self-paced", "collaborative", "none"]
FAVORITE_DEPARTMENTS = ["Computer Science", "Mathematics", "Business", "Engineering", "Arts", "Sciences", "Humanities", "Health Sciences", "Education"]
PAYMENT_METHODS = ["credit_card", "debit_card", "financial_aid", "scholarship", "wire_transfer"]

PRODUCTS_BY_CATEGORY = {
    "Computer Science": [
        ("Introduction to Python", "Dr. Chen", 299.99, "3 credits"), ("Data Structures & Algorithms", "Dr. Kumar", 349.99, "4 credits"),
        ("Machine Learning Fundamentals", "Dr. Zhang", 399.99, "3 credits"), ("Web Development", "Prof. Miller", 279.99, "3 credits"),
        ("Database Systems", "Dr. Patel", 329.99, "3 credits"), ("Computer Networks", "Dr. Wilson", 349.99, "3 credits"),
        ("Operating Systems", "Dr. Brown", 349.99, "4 credits"), ("Software Engineering", "Prof. Davis", 329.99, "3 credits"),
        ("Cybersecurity Basics", "Dr. Thompson", 379.99, "3 credits"), ("Cloud Computing", "Dr. Garcia", 399.99, "3 credits"),
        ("Artificial Intelligence", "Dr. Lee", 449.99, "4 credits"), ("Mobile App Development", "Prof. Taylor", 299.99, "3 credits"),
        ("DevOps & CI/CD", "Dr. Martinez", 349.99, "3 credits"), ("Natural Language Processing", "Dr. Wang", 399.99, "3 credits"),
        ("Computer Vision", "Dr. Singh", 399.99, "3 credits"), ("Blockchain Technology", "Prof. Anderson", 349.99, "3 credits"),
    ],
    "Mathematics": [
        ("Calculus I", "Dr. Roberts", 249.99, "4 credits"), ("Linear Algebra", "Dr. Johnson", 279.99, "3 credits"),
        ("Statistics & Probability", "Dr. Williams", 279.99, "3 credits"), ("Discrete Mathematics", "Dr. Jones", 249.99, "3 credits"),
        ("Differential Equations", "Dr. Moore", 299.99, "3 credits"), ("Number Theory", "Prof. Clark", 279.99, "3 credits"),
        ("Abstract Algebra", "Dr. Hall", 299.99, "3 credits"), ("Real Analysis", "Dr. Young", 329.99, "4 credits"),
        ("Numerical Methods", "Prof. Wright", 299.99, "3 credits"), ("Combinatorics", "Dr. Allen", 279.99, "3 credits"),
        ("Calculus II", "Dr. Roberts", 249.99, "4 credits"), ("Calculus III", "Dr. Hill", 279.99, "4 credits"),
        ("Mathematical Modeling", "Prof. Green", 329.99, "3 credits"), ("Topology", "Dr. Baker", 349.99, "3 credits"),
    ],
    "Business": [
        ("Principles of Management", "Prof. Adams", 299.99, "3 credits"), ("Financial Accounting", "Dr. Nelson", 329.99, "3 credits"),
        ("Marketing Fundamentals", "Prof. Carter", 279.99, "3 credits"), ("Business Analytics", "Dr. Mitchell", 349.99, "3 credits"),
        ("Entrepreneurship", "Prof. Rivera", 299.99, "3 credits"), ("Corporate Finance", "Dr. Campbell", 349.99, "3 credits"),
        ("Operations Management", "Prof. Torres", 299.99, "3 credits"), ("Strategic Management", "Dr. Lewis", 329.99, "3 credits"),
        ("Business Ethics", "Prof. Robinson", 249.99, "3 credits"), ("International Business", "Dr. Walker", 299.99, "3 credits"),
        ("Supply Chain Management", "Prof. Perez", 329.99, "3 credits"), ("Human Resource Management", "Dr. Sanchez", 279.99, "3 credits"),
    ],
    "Engineering": [
        ("Statics & Dynamics", "Dr. Thompson", 349.99, "4 credits"), ("Thermodynamics", "Dr. White", 349.99, "3 credits"),
        ("Circuit Analysis", "Prof. Harris", 329.99, "3 credits"), ("Fluid Mechanics", "Dr. Martin", 349.99, "3 credits"),
        ("Materials Science", "Dr. Jackson", 299.99, "3 credits"), ("Control Systems", "Prof. Taylor", 349.99, "3 credits"),
        ("Engineering Design", "Dr. Anderson", 279.99, "4 credits"), ("Signal Processing", "Dr. Thomas", 379.99, "3 credits"),
        ("Robotics Fundamentals", "Prof. Garcia", 399.99, "3 credits"), ("Structural Analysis", "Dr. Martinez", 349.99, "4 credits"),
        ("Heat Transfer", "Dr. Robinson", 329.99, "3 credits"), ("Engineering Ethics", "Prof. Clark", 199.99, "2 credits"),
    ],
    "Arts & Humanities": [
        ("Introduction to Philosophy", "Dr. King", 229.99, "3 credits"), ("World History I", "Prof. Wright", 249.99, "3 credits"),
        ("Creative Writing", "Prof. Scott", 229.99, "3 credits"), ("Art History", "Dr. Flores", 249.99, "3 credits"),
        ("Music Theory", "Prof. Green", 249.99, "3 credits"), ("Introduction to Sociology", "Dr. Adams", 229.99, "3 credits"),
        ("Cultural Anthropology", "Dr. Nelson", 249.99, "3 credits"), ("Film Studies", "Prof. Baker", 229.99, "3 credits"),
        ("Ethics & Society", "Dr. Hall", 229.99, "3 credits"), ("Comparative Literature", "Prof. Young", 249.99, "3 credits"),
    ],
    "Natural Sciences": [
        ("General Chemistry I", "Dr. Nguyen", 299.99, "4 credits"), ("General Physics I", "Dr. Hill", 299.99, "4 credits"),
        ("Biology I", "Dr. Flores", 279.99, "4 credits"), ("Organic Chemistry", "Dr. Rivera", 349.99, "4 credits"),
        ("Environmental Science", "Prof. Torres", 249.99, "3 credits"), ("Astronomy", "Dr. Campbell", 229.99, "3 credits"),
        ("Genetics", "Dr. Mitchell", 299.99, "3 credits"), ("Biochemistry", "Dr. Carter", 349.99, "4 credits"),
        ("Ecology", "Prof. Sanchez", 249.99, "3 credits"), ("Geology", "Dr. Perez", 249.99, "3 credits"),
        ("General Physics II", "Dr. Hill", 299.99, "4 credits"), ("General Chemistry II", "Dr. Nguyen", 299.99, "4 credits"),
    ],
    "Health Sciences": [
        ("Human Anatomy", "Dr. Lewis", 329.99, "4 credits"), ("Physiology", "Dr. Walker", 329.99, "4 credits"),
        ("Nutrition Science", "Prof. Robinson", 249.99, "3 credits"), ("Public Health", "Dr. Allen", 279.99, "3 credits"),
        ("Pharmacology", "Dr. Young", 349.99, "3 credits"), ("Epidemiology", "Prof. King", 299.99, "3 credits"),
        ("Health Informatics", "Dr. Wright", 329.99, "3 credits"), ("Clinical Psychology", "Dr. Scott", 299.99, "3 credits"),
        ("Biostatistics", "Prof. Green", 299.99, "3 credits"), ("Healthcare Management", "Dr. Baker", 279.99, "3 credits"),
    ],
    "Education": [
        ("Educational Psychology", "Dr. Hall", 249.99, "3 credits"), ("Curriculum Design", "Prof. Adams", 279.99, "3 credits"),
        ("Classroom Management", "Dr. Nelson", 249.99, "3 credits"), ("Assessment & Evaluation", "Prof. Carter", 249.99, "3 credits"),
        ("Special Education", "Dr. Mitchell", 279.99, "3 credits"), ("Educational Technology", "Prof. Rivera", 299.99, "3 credits"),
        ("Early Childhood Education", "Dr. Torres", 249.99, "3 credits"), ("Adult Learning Theory", "Prof. Campbell", 249.99, "3 credits"),
        ("Multicultural Education", "Dr. Sanchez", 249.99, "3 credits"), ("Instructional Design", "Prof. Perez", 279.99, "3 credits"),
    ],
    "Communications": [
        ("Public Speaking", "Prof. Lewis", 229.99, "3 credits"), ("Mass Media & Society", "Dr. Walker", 249.99, "3 credits"),
        ("Digital Marketing", "Prof. Robinson", 299.99, "3 credits"), ("Journalism Fundamentals", "Dr. Allen", 249.99, "3 credits"),
        ("Visual Communication", "Prof. King", 279.99, "3 credits"), ("Social Media Strategy", "Dr. Wright", 279.99, "3 credits"),
        ("Technical Writing", "Prof. Scott", 229.99, "3 credits"), ("Intercultural Communication", "Dr. Flores", 249.99, "3 credits"),
        ("Media Production", "Prof. Green", 329.99, "3 credits"), ("Communication Research", "Dr. Baker", 249.99, "3 credits"),
    ],
    "Languages": [
        ("Spanish I", "Prof. Garcia", 229.99, "3 credits"), ("French I", "Prof. Martin", 229.99, "3 credits"),
        ("Mandarin Chinese I", "Dr. Wang", 249.99, "3 credits"), ("Japanese I", "Prof. Tanaka", 249.99, "3 credits"),
        ("German I", "Prof. Fischer", 229.99, "3 credits"), ("Arabic I", "Dr. Hassan", 249.99, "3 credits"),
        ("English Composition", "Prof. Roberts", 199.99, "3 credits"), ("Advanced Academic Writing", "Dr. Johnson", 229.99, "3 credits"),
        ("Spanish II", "Prof. Garcia", 249.99, "3 credits"), ("French II", "Prof. Martin", 249.99, "3 credits"),
    ],
}

CAMPUS_NAMES = [
    "EduPath Main Campus", "EduPath Westside", "EduPath Downtown Center",
    "EduPath Technology Hub", "EduPath Lake Campus", "EduPath North Campus",
    "EduPath Arts Center", "EduPath Science Park", "EduPath Business School",
    "EduPath Health Sciences",
]


def random_phone():
    return f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}"


def random_email(first, last):
    domains = ["gmail.com", "yahoo.com", "outlook.com", "university.edu", "student.edu"]
    sep = random.choice([".", "_", ""])
    num = random.choice(["", str(random.randint(1, 99))])
    return f"{first.lower()}{sep}{last.lower()}{num}@{random.choice(domains)}"


print("Domain data loaded. Generating tables...")

# COMMAND ----------

# MAGIC %md
# MAGIC    
# MAGIC ### Students (200 rows)

# COMMAND ----------

customers = []
for i in range(1, 201):
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    city, state = random.choice(CITIES_STATES)
    prefs = {
        "learning_style": random.sample(LEARNING_STYLES, k=random.randint(0, 2)),
        "favorite_departments": random.sample(FAVORITE_DEPARTMENTS, k=random.randint(1, 3)),
        "full_time": random.choice([True, False]),
    }
    customers.append({
        "customer_id": f"CUST-{i:04d}",
        "first_name": first,
        "last_name": last,
        "email": random_email(first, last),
        "phone": random_phone(),
        "address": f"{random.randint(100,9999)} {random.choice(STREETS)}",
        "city": city,
        "state": state,
        "zip_code": f"{random.randint(10000, 99999)}",
        "membership_tier": random.choices(MEMBERSHIP_TIERS, weights=[40, 30, 20, 10])[0],
        "join_date": (datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1800))).strftime("%Y-%m-%d"),
        "preferences": json.dumps(prefs),
    })

customers_df = spark.createDataFrame(customers)
customers_df.write.mode("overwrite").saveAsTable(f"{FULL_SCHEMA}.customers")
print(f"Created {FULL_SCHEMA}.customers — {customers_df.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC    
# MAGIC ### Courses (~500 rows)

# COMMAND ----------

products = []
pid = 1
buildings = {}
building_num = 1
for cat in PRODUCTS_BY_CATEGORY:
    if cat not in buildings:
        buildings[cat] = building_num
        building_num += 1
    for name, instructor, price, unit in PRODUCTS_BY_CATEGORY[cat]:
        products.append({
            "product_id": f"PROD-{pid:04d}",
            "name": name,
            "category": cat,
            "brand": instructor,
            "price": round(price, 2),
            "stock_quantity": random.randint(15, 120),  # available seats
            "aisle": buildings[cat],  # building number
            "unit": unit,
        })
        pid += 1

# Pad to ~500 courses with level variations
while len(products) < 500:
    cat = random.choice(list(PRODUCTS_BY_CATEGORY.keys()))
    base = random.choice(PRODUCTS_BY_CATEGORY[cat])
    variation = random.choice(["Advanced ", "Honors ", "Graduate ", "Intensive ", "Online "])
    products.append({
        "product_id": f"PROD-{pid:04d}",
        "name": f"{variation}{base[0]}",
        "category": cat,
        "brand": base[1],
        "price": round(base[2] * random.uniform(0.8, 1.5), 2),
        "stock_quantity": random.randint(15, 120),
        "aisle": buildings[cat],
        "unit": base[3],
    })
    pid += 1

products_df = spark.createDataFrame(products)
products_df.write.mode("overwrite").saveAsTable(f"{FULL_SCHEMA}.products")
print(f"Created {FULL_SCHEMA}.products — {products_df.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC    
# MAGIC ### Campuses (10 rows)

# COMMAND ----------

stores = []
for i, name in enumerate(CAMPUS_NAMES, 1):
    city, state = CITIES_STATES[i % len(CITIES_STATES)]
    stores.append({
        "store_id": f"STORE-{i:02d}",
        "name": name,
        "address": f"{random.randint(100,9999)} {random.choice(STREETS)}",
        "city": city,
        "state": state,
        "zip_code": f"{random.randint(10000, 99999)}",
        "hours": "7:00 AM - 10:00 PM",
        "phone": random_phone(),
    })

stores_df = spark.createDataFrame(stores)
stores_df.write.mode("overwrite").saveAsTable(f"{FULL_SCHEMA}.stores")
print(f"Created {FULL_SCHEMA}.stores — {stores_df.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC    
# MAGIC ### Enrollments (2,000 rows) and Enrollment Items (~8,000 rows)

# COMMAND ----------

transactions = []
transaction_items = []
item_id = 1

for txn_id in range(1, 2001):
    customer = random.choice(customers)
    store = random.choice(stores)
    txn_date = datetime(2024, 1, 1) + timedelta(
        days=random.randint(0, 440),
        hours=random.randint(7, 21),
        minutes=random.randint(0, 59),
    )
    num_items = random.randint(2, 6)  # courses per enrollment
    txn_products = random.sample(products, k=min(num_items, len(products)))

    total = 0.0
    for prod in txn_products:
        qty = 1  # typically 1 section per course
        discount = round(random.choice([0.0, 0.0, 0.0, 25.0, 50.0, 75.0, 100.0]), 2)  # scholarship discounts
        unit_price = prod["price"]
        line_total = round(qty * unit_price - discount, 2)
        total += line_total

        transaction_items.append({
            "item_id": f"ITEM-{item_id:06d}",
            "transaction_id": f"TXN-{txn_id:05d}",
            "product_id": prod["product_id"],
            "quantity": float(qty),
            "unit_price": unit_price,
            "discount": discount,
        })
        item_id += 1

    transactions.append({
        "transaction_id": f"TXN-{txn_id:05d}",
        "customer_id": customer["customer_id"],
        "store_id": store["store_id"],
        "transaction_date": txn_date.strftime("%Y-%m-%d %H:%M:%S"),
        "total_amount": round(total, 2),
        "payment_method": random.choice(PAYMENT_METHODS),
        "status": random.choices(["completed", "withdrawn", "pending"], weights=[85, 10, 5])[0],
    })

transactions_df = spark.createDataFrame(transactions)
transactions_df.write.mode("overwrite").saveAsTable(f"{FULL_SCHEMA}.transactions")
print(f"Created {FULL_SCHEMA}.transactions — {transactions_df.count()} rows")

transaction_items_df = spark.createDataFrame(transaction_items)
transaction_items_df.write.mode("overwrite").saveAsTable(f"{FULL_SCHEMA}.transaction_items")
print(f"Created {FULL_SCHEMA}.transaction_items — {transaction_items_df.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC    
# MAGIC ### Tuition Payment History (400 rows)

# COMMAND ----------

payment_history = []
for pay_id in range(1, 401):
    customer = random.choice(customers)
    method = random.choice(PAYMENT_METHODS)
    card_last4 = str(random.randint(1000, 9999)) if method in ("credit_card", "debit_card") else None
    payment_history.append({
        "payment_id": f"PAY-{pay_id:04d}",
        "customer_id": customer["customer_id"],
        "payment_method": method,
        "card_last4": card_last4,
        "billing_address": f"{random.randint(100,9999)} {random.choice(STREETS)}, {customer['city']}, {customer['state']}",
        "created_date": (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 440))).strftime("%Y-%m-%d"),
    })

payment_history_df = spark.createDataFrame(payment_history)
payment_history_df.write.mode("overwrite").saveAsTable(f"{FULL_SCHEMA}.payment_history")
print(f"Created {FULL_SCHEMA}.payment_history — {payment_history_df.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Verify All Tables

# COMMAND ----------

print(f"Tables in {FULL_SCHEMA}:\n")
tables = ["customers", "products", "stores", "transactions", "transaction_items", "payment_history"]
for table in tables:
    count = spark.sql(f"SELECT COUNT(*) as cnt FROM {FULL_SCHEMA}.{table}").collect()[0]["cnt"]
    print(f"  {table:25s} {count:>8,} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Create Policy Documents Datasets in local repository
# MAGIC
# MAGIC This codebase creates synthetic data in a newly generated edu_policy_docs subfolder in the data folder . This holds all the policy documents that vector search index will be utilising

# COMMAND ----------

import os
import sys

# Add the notebook directory to the path so we can import the script
notebook_dir = os.path.dirname(os.path.abspath(dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()))
sys.path.insert(0, f"/Workspace{notebook_dir}")

from generate_edu_policy_docs import generate_docs, EDU_POLICY_DOCS

edu_docs_dir = os.path.join(os.path.dirname(os.path.abspath(".")), "edu_policy_docs")
generate_docs(edu_docs_dir)
print(f"Created {len(EDU_POLICY_DOCS)} policy documents in: {edu_docs_dir}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Create Policy Documents Table
# MAGIC
# MAGIC This reads the 7 Education policy documents from the `data/policy_docs/` directory, splits them into
# MAGIC overlapping text chunks, and writes them to a table that Vector Search will index.

# COMMAND ----------

import hashlib
import os

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Locate the policy_docs directory relative to this notebook
# In a Databricks Repo, the repo root is available via the workspace file system
notebook_path = dbutils.entry_point.getDbutils().notebook().getContext().notebookPath().get()
repo_root = "/".join(notebook_path.split("/")[:-2])  # go up from simple/00_quickstart_setup
docs_dir = f"/Workspace{repo_root}/data/edu_policy_docs"

# Fallback: try relative path if running locally or in a different context
if not os.path.isdir(docs_dir):
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(".")), "edu_policy_docs")
if not os.path.isdir(docs_dir):
    raise FileNotFoundError(
        f"Could not find policy_docs directory. Looked in:\n"
        f"  /Workspace{repo_root}/data/edu_policy_docs\n"
        f"  {os.path.join(os.path.dirname(os.path.abspath('.')), 'edu_policy_docs')}\n"
        f"Make sure you cloned the full repository."
    )


def chunk_text(text):
    """Split text into overlapping chunks by paragraph."""
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) + 2 <= CHUNK_SIZE:
            current = f"{current}\n\n{para}" if current else para
        else:
            if current:
                chunks.append(current.strip())
            if len(para) > CHUNK_SIZE:
                words = para.split()
                current = ""
                for word in words:
                    if len(current) + len(word) + 1 <= CHUNK_SIZE:
                        current = f"{current} {word}" if current else word
                    else:
                        chunks.append(current.strip())
                        overlap_text = current[-CHUNK_OVERLAP:] if len(current) > CHUNK_OVERLAP else current
                        current = f"{overlap_text} {word}"
            else:
                if chunks:
                    prev = chunks[-1]
                    overlap_text = prev[-CHUNK_OVERLAP:] if len(prev) > CHUNK_OVERLAP else prev
                    current = f"{overlap_text}\n\n{para}"
                else:
                    current = para

    if current.strip():
        chunks.append(current.strip())
    return chunks


# Read and chunk all policy documents
all_chunks = []
print(f"Reading policy documents from: {docs_dir}\n")
for filename in sorted(os.listdir(docs_dir)):
    if not filename.endswith(".md"):
        continue
    filepath = os.path.join(docs_dir, filename)
    with open(filepath, "r") as f:
        content = f.read()

    doc_name = filename.replace(".md", "")
    chunks = chunk_text(content)
    print(f"  {filename}: {len(chunks)} chunks")

    for i, chunk in enumerate(chunks):
        chunk_id = hashlib.md5(f"{doc_name}::{i}".encode()).hexdigest()[:16]
        all_chunks.append({
            "chunk_id": chunk_id,
            "doc_name": doc_name,
            "content": chunk,
        })

chunks_df = spark.createDataFrame(all_chunks)
chunks_df.write.mode("overwrite").saveAsTable(f"{FULL_SCHEMA}.policy_docs_chunked")
print(f"\nCreated {FULL_SCHEMA}.policy_docs_chunked — {chunks_df.count()} chunks from {len(set(c['doc_name'] for c in all_chunks))} documents")

# COMMAND ----------

# MAGIC %md
# MAGIC    
# MAGIC ## Step 4: Create Vector Search Endpoint and Index
# MAGIC
# MAGIC Vector Search lets you find relevant policy documents using natural language instead of exact keyword matches.
# MAGIC This creates:
# MAGIC 1. A **Vector Search endpoint** (the compute that powers similarity search)
# MAGIC 2. A **Delta Sync index** on the policy docs table (automatically generates embeddings)
# MAGIC
# MAGIC The endpoint takes 5-10 minutes to become ready. The cell will wait automatically.

# COMMAND ----------

import time
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.vectorsearch import (
    DeltaSyncVectorIndexSpecRequest,
    EmbeddingSourceColumn,
    EndpointType,
    PipelineType,
    VectorIndexType,
)

w = WorkspaceClient()

VS_ENDPOINT_NAME = f"edupath-vs-{SCHEMA.strip().replace('_', '-')}"
VS_INDEX_NAME = f"{FULL_SCHEMA}.policy_docs_index"

# --- Create endpoint (or reuse existing) ---
try:
    endpoint = w.vector_search_endpoints.get_endpoint(VS_ENDPOINT_NAME)
    print(f"Vector Search endpoint '{VS_ENDPOINT_NAME}' already exists (status: {endpoint.endpoint_status.state.value})")
except Exception:
    print(f"Creating Vector Search endpoint '{VS_ENDPOINT_NAME}'...")
    w.vector_search_endpoints.create_endpoint_and_wait(
        name=VS_ENDPOINT_NAME,
        endpoint_type=EndpointType.STANDARD,
    )
    print(f"Vector Search endpoint '{VS_ENDPOINT_NAME}' is ONLINE.")

# Wait until endpoint is ONLINE
for attempt in range(60):
    endpoint = w.vector_search_endpoints.get_endpoint(VS_ENDPOINT_NAME)
    status = endpoint.endpoint_status.state.value
    if status == "ONLINE":
        break
    if attempt % 6 == 0:
        print(f"  Waiting for endpoint to be ONLINE (currently: {status})...")
    time.sleep(10)
else:
    print(f"WARNING: Endpoint status is '{status}' after 10 minutes. It may still be provisioning.")

print(f"Endpoint '{VS_ENDPOINT_NAME}' is ready.")

# COMMAND ----------

spark.sql(f"""
ALTER TABLE {FULL_SCHEMA}.policy_docs_chunked
  SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# COMMAND ----------

from databricks.vector_search.client import VectorSearchClient

client = VectorSearchClient()

# Delete the existing index if it exists
try:
    client.delete_index(
        endpoint_name=VS_ENDPOINT_NAME,
        index_name=VS_INDEX_NAME,
        # force=True
    )
    print(f"Deleted existing index: {VS_INDEX_NAME}")
except Exception as e:
    print(f"No existing index to delete or error occurred: {e}")

# Create a new index
index = client.create_delta_sync_index(
    endpoint_name=VS_ENDPOINT_NAME,
    source_table_name=f"{FULL_SCHEMA}.policy_docs_chunked",
    index_name=VS_INDEX_NAME,
    pipeline_type="TRIGGERED",
    primary_key="chunk_id",
    embedding_source_column="content",
    embedding_model_endpoint_name="databricks-gte-large-en",
)

# COMMAND ----------

# MAGIC %md
# MAGIC    
# MAGIC ## Step 5: Create Genie Space
# MAGIC
# MAGIC Genie lets you ask questions about your data in plain English. It converts your questions into SQL automatically.
# MAGIC
# MAGIC This creates a Genie Space connected to all 6 EduPath Academy data tables.

# COMMAND ----------

import json

GENIE_SPACE_TITLE = f"EduPath_Academy_Data_({SCHEMA})"

# Get the first available SQL warehouse
warehouses = w.warehouses.list()
warehouse_id = None
for wh in warehouses:
    if wh.state and wh.state.value in ("RUNNING", "STARTING"):
        warehouse_id = wh.id
        break
    if wh.id:
        warehouse_id = wh.id  # fallback to any warehouse

if not warehouse_id:
    print("WARNING: No SQL warehouse found. Please create one and re-run this cell.")
else:
    table_identifiers = [f"{FULL_SCHEMA}.{t}" for t in tables]

    # Check if a Genie Space with this title already exists
    existing_spaces = w.api_client.do("GET", "/api/2.0/genie/spaces")
    genie_space_id = None
    for space in existing_spaces.get("spaces", []):
        if space.get("title") == GENIE_SPACE_TITLE:
            genie_space_id = space.get("space_id")
            print(f"Genie Space '{GENIE_SPACE_TITLE}' already exists (ID: {genie_space_id})")
            break

    if not genie_space_id:
        print(f"Creating Genie Space '{GENIE_SPACE_TITLE}'...")
        serialized = json.dumps({
            "version": 2,
            "data_sources": {
                "tables": [{"identifier": t} for t in sorted(table_identifiers)]
            }
        })
        response = w.api_client.do("POST", "/api/2.0/genie/spaces", body={
            "title": GENIE_SPACE_TITLE,
            "description": (
                "EduPath Academy education data for the AI workshop. "
                "Contains student information, course catalog, campus locations, "
                "enrollment history, and tuition payment records."
            ),
            "warehouse_id": warehouse_id,
            "serialized_space": serialized,
        })
        genie_space_id = response.get("space_id")
        print(f"Genie Space created (ID: {genie_space_id})")

# COMMAND ----------

# MAGIC %md
# MAGIC    
# MAGIC ## Step 6: Create MLflow Experiment
# MAGIC
# MAGIC MLflow tracks your agent's performance. This creates an experiment where traces and evaluation metrics will be logged.

# COMMAND ----------

import mlflow

mlflow.set_tracking_uri("databricks")

username = spark.sql("SELECT current_user()").collect()[0][0]
experiment_name = f"/Users/{username}/edupath-agent-workshop"

try:
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment and experiment.lifecycle_stage == "active":
        experiment_id = experiment.experiment_id
        print(f"MLflow experiment already exists: {experiment_name} (ID: {experiment_id})")
    else:
        experiment_id = mlflow.create_experiment(experiment_name)
        print(f"MLflow experiment created: {experiment_name} (ID: {experiment_id})")
except Exception:
    experiment_id = mlflow.create_experiment(experiment_name)
    print(f"MLflow experiment created: {experiment_name} (ID: {experiment_id})")

# COMMAND ----------

from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import ArrayType, IntegerType
import pandas as pd

# Register as a Python UC function in the same schema
spark.sql(f"""
CREATE OR REPLACE FUNCTION {FULL_SCHEMA}.student_forecast(
    current_students INT,
    monthly_growth INT
)
RETURNS ARRAY<INT>
LANGUAGE PYTHON
AS $$
def deterministic_student_forecast(current_students: int, monthly_growth: int = 10) -> list:
    return [current_students + monthly_growth * i for i in range(1, 7)]
return deterministic_student_forecast(current_students, monthly_growth)
$$
""")

# COMMAND ----------

# MAGIC %sql
# MAGIC select ${catalog}.${schema}.student_forecast(20, 10) as result

# COMMAND ----------

# MAGIC %md
# MAGIC    
# MAGIC ## Setup Complete
# MAGIC
# MAGIC All resources have been created. Here's a summary of everything that's ready for you:

# COMMAND ----------

print("=" * 70)
print("  EDUPATH ACADEMY WORKSHOP SETUP COMPLETE")
print("=" * 70)
print()
print(f"  Catalog/Schema:     {FULL_SCHEMA}")
print()
print("  Data Tables:")
for table in tables:
    count = spark.sql(f"SELECT COUNT(*) as cnt FROM {FULL_SCHEMA}.{table}").collect()[0]["cnt"]
    print(f"    {table:25s} {count:>8,} rows")
chunks_count = spark.sql(f"SELECT COUNT(*) as cnt FROM {FULL_SCHEMA}.policy_docs_chunked").collect()[0]["cnt"]
print(f"    {'policy_docs_chunked':25s} {chunks_count:>8,} chunks")
print()
print(f"  Vector Search Endpoint:  {VS_ENDPOINT_NAME}")
print(f"  Vector Search Index:     {VS_INDEX_NAME}")
print()
if genie_space_id:
    print(f"  Genie Space ID:          {genie_space_id}")
    print(f"  Genie Space Title:       {GENIE_SPACE_TITLE}")
print()
print(f"  MLflow Experiment:       {experiment_name}")
print(f"  MLflow Experiment ID:    {experiment_id}")
print()
print("=" * 70)
print("  Next Steps:")
print("    1. Open the Genie Space and try asking questions about your data")
print("    2. Explore the Vector Search index in Catalog Explorer")
print("    3. Open the Databricks Playground to build your first agent")
print("    4. See the README for detailed workshop modules")
print("=" * 70)

# COMMAND ----------

# import mlflow 
# mlflow.create_experiment(
#     name="/Users/<your email>/<experiment name>",
#     artifact_location="dbfs:/Volumes/<catalog>/<schema>/<volume>/mlflow-artifacts"
# )
