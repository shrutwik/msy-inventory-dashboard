import pandas as pd
from pathlib import Path

# Load data
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
df = pd.read_csv(DATA_DIR / "cleaned_monthly_data.csv")

# Quick clean (in case of minor blanks)
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
df["Count"] = pd.to_numeric(df["Count"], errors="coerce").fillna(0)

# Group by Month and Sheet_Type
summary = df.groupby(["Month", "Sheet_Type"])["Amount"].sum().round(2).unstack()
print("\n📊 Total Amount by Month and Sheet Type:\n")
print(summary)

# Grand total per month
total_month = df.groupby("Month")["Amount"].sum().round(2)
print("\n💰 Total Revenue by Month:\n")
print(total_month)

# Check number of unique groups per month
print("\n📋 Unique 'Group' entries per Month:\n")
print(df.groupby("Month")["Group"].nunique())