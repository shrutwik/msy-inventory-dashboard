import pandas as pd
from pathlib import Path

# Load cleaned data
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
df = pd.read_csv(DATA_DIR / "cleaned_monthly_data.csv")

# Ensure numeric
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)

# Group by Month + Sheet_Type
summary_check = (
    df.groupby(["Month", "Sheet_Type"])["Amount"]
    .sum()
    .unstack(fill_value=0)
    .reset_index()
)

# Compute difference
summary_check["Difference"] = summary_check["Summary"] - summary_check["Details"]
summary_check["Match_%"] = (
    (summary_check["Summary"] / summary_check["Details"]) * 100
).round(2)

print("\n📊 Summary vs Details Comparison by Month:\n")
print(summary_check.to_string(index=False))

# Optional: flag significant mismatches
threshold = 0.5  # e.g. if off by more than 50 cents
mismatches = summary_check[summary_check["Difference"].abs() > threshold]
if not mismatches.empty:
    print("\n⚠️ Mismatch detected in these months:\n")
    print(mismatches)
else:
    print("\n✅ All summary totals approximately match details totals!")