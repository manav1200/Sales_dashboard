import pandas as pd
import sqlite3

# Load CSV file
df = pd.read_csv("superstore.csv", encoding="latin1")

# Clean column names
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("-", "_")  
)

# Convert date column
df["order_date"] = pd.to_datetime(df["order_date"])

# Create derived column
df["year"] = df["order_date"].dt.year

# Load into SQLite database
with sqlite3.connect("sales.db") as conn:
    df.to_sql(
        "orders",
        conn,
        if_exists="replace",
        index=False
    )

print("Data loaded successfully!")