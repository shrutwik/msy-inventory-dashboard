import os
import pandas as pd
from pathlib import Path

# -----------------------------
#  File paths setup
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

excel_files = [
    ("May", DATA_DIR / "May_Data_Matrix (1).xlsx"),
    ("June", DATA_DIR / "June_Data_Matrix.xlsx"),
    ("July", DATA_DIR / "July_Data_Matrix (1).xlsx"),
    ("August", DATA_DIR / "August_Data_Matrix (1).xlsx"),
    ("September", DATA_DIR / "September_Data_Matrix.xlsx"),
    ("October", DATA_DIR / "October_Data_Matrix_20251103_214000.xlsx")
]

# -----------------------------
#  Helper function: Clean numeric columns
# -----------------------------
def clean_amount(series):
    return (
        series.astype(str)
        .replace(r"[\$,]", "", regex=True)
        .replace("nan", "0")
        .astype(float)
    )

# -----------------------------
#  Load and clean data
# -----------------------------
all_data = []

for month_name, file_path in excel_files:
    if not file_path.exists():
        print(f"⚠️ Missing file: {file_path}")
        continue

    print(f"\n📘 Loading {month_name} — {file_path.name}")
    xls = pd.ExcelFile(file_path)
    sheets = xls.sheet_names
    print(f"   Found sheets: {sheets}")

    for i, sheet_name in enumerate(sheets, start=1):
        df = pd.read_excel(xls, sheet_name=sheet_name)
        df.columns = [col.strip() for col in df.columns]

        if "Amount" not in df.columns:
            print(f"   ⚠️ Skipping sheet {sheet_name} — no 'Amount' column.")
            continue

        df["Amount"] = clean_amount(df["Amount"])
        if "Count" in df.columns:
            df["Count"] = pd.to_numeric(df["Count"], errors="coerce").fillna(0)
        else:
            df["Count"] = 0

        df["Month"] = month_name
        df["source_table"] = i
        df["Sheet_Type"] = "Summary" if i == 1 else "Details"
        all_data.append(df)

        print(f"   ✅ Loaded sheet {i}: {sheet_name} — {len(df)} rows")

# -----------------------------
#  Combine and save cleaned data
# -----------------------------
combined = pd.concat(all_data, ignore_index=True)
combined.to_csv(DATA_DIR / "cleaned_monthly_data.csv", index=False)

print(f"\n✅ Cleaned dataset saved to: {DATA_DIR / 'cleaned_monthly_data.csv'}")
print(f"📏 Rows: {combined.shape[0]} | Columns: {combined.shape[1]}")
print(f"📋 Columns: {list(combined.columns)}\n")
print("🔍 Sample:")
print(combined.head(10))

# -----------------------------
#  Verify Summary vs Details
# -----------------------------
summary_df = combined[combined["Sheet_Type"] == "Summary"]
details_df = combined[combined["Sheet_Type"] == "Details"]

summary_totals = summary_df.groupby("Month")["Amount"].sum()
details_totals = details_df.groupby("Month")["Amount"].sum()

comparison_df = pd.DataFrame({
    "Summary": summary_totals,
    "Details": details_totals
})
comparison_df["Difference"] = comparison_df["Summary"] - comparison_df["Details"]
comparison_df["Match_%"] = (
    (comparison_df["Summary"] / comparison_df["Details"]) * 100
).round(2)

print("\n📊 Summary vs Details (Amount Totals):\n")
print(comparison_df.to_string())

# -----------------------------
#  Step 1: Overlapping Group Names
# -----------------------------
summary_groups = set(summary_df["Group"].unique())
details_groups = set(details_df["Group"].unique())
overlap = summary_groups.intersection(details_groups)

print(f"\n🔍 Overlapping group names between Summary & Details: {len(overlap)}")
if overlap:
    print(f"   Examples: {list(overlap)[:10]}")

# -----------------------------
#  Step 2: Compare Count Totals
# -----------------------------
count_compare = combined.groupby(["Month", "Sheet_Type"])["Count"].sum().unstack()
print("\n📦 Total 'Count' comparison by Month:\n")
print(count_compare)

# -----------------------------
#  Step 3: Detect Consistent Ratios
# -----------------------------
comparison_df["Ratio"] = (comparison_df["Details"] / comparison_df["Summary"]).round(2)
if (comparison_df["Ratio"] == 2.00).all():
    print("\n⚠️ Pattern detected: Details totals are consistently double Summary totals.")
    print("💡 Likely cause: Each 'Details' sheet (data 2 & 3) contains full totals already, or Summary is per-shift average.")
elif (comparison_df["Ratio"] == 0.50).all():
    print("\n⚠️ Pattern detected: Summary totals are consistently double Details totals.")
else:
    print("\n✅ No consistent 0.5x or 2x pattern detected across all months.")

# -----------------------------
#  Conclusion
# -----------------------------
print("\n📈 Diagnostic Summary:")
print("- If the overlap list above includes menu categories (e.g., 'All Day Menu', 'Drinks'), you’re double-counting.")
print("- If Count totals are fine but Amount differs by 2x, the Summary may be a per-shift or averaged total.")
print("- You can safely use 'Summary' for monthly totals and 'Details' for deeper item-level analysis.")
print("- Adjust later (divide Details by 2 or ignore duplicates) once pattern confirmed.")