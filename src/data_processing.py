import pandas as pd
from pathlib import Path

# ==========================================
# 1️⃣ Setup
# ==========================================
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OUTPUT_FILE = DATA_DIR / "cleaned_monthly_data.csv"

# Excel files for each month
monthly_files = [
    ("May", "May_Data_Matrix (1).xlsx"),
    ("June", "June_Data_Matrix.xlsx"),
    ("July", "July_Data_Matrix (1).xlsx"),
    ("August", "August_Data_Matrix (1).xlsx"),
    ("September", "September_Data_Matrix.xlsx"),
    ("October", "October_Data_Matrix_20251103_214000.xlsx"),
]

all_data = []

# ==========================================
# 2️⃣ Read All Sheets per File
# ==========================================
for month_name, filename in monthly_files:
    file_path = DATA_DIR / filename
    print(f"\n📘 Loading {month_name} — {filename}")

    try:
        # Load the workbook
        xls = pd.ExcelFile(file_path)
        sheets = xls.sheet_names
        print(f"   Found sheets: {sheets}")

        # Loop through all sheets
        for idx, sheet_name in enumerate(sheets, start=1):
            df = pd.read_excel(xls, sheet_name=sheet_name)

            # Standardize column names
            df.columns = (
                df.columns.str.strip()
                .str.replace(" ", "_")
                .str.replace("-", "_")
                .str.replace(r"[^\w\s]", "", regex=True)
                .str.lower()
            )

            # Rename common columns
            rename_map = {
                "group": "Group",
                "category": "Group",
                "count": "Count",
                "amount": "Amount",
            }
            df = df.rename(columns=rename_map)

            # Only keep relevant columns
            expected_cols = ["Group", "Count", "Amount"]
            available_cols = [c for c in expected_cols if c in df.columns]
            df = df[available_cols]

            # Clean currency column
            if "Amount" in df.columns:
                df["Amount"] = (
                    df["Amount"]
                    .astype(str)
                    .replace("[\$,]", "", regex=True)
                    .replace(",", "", regex=True)
                )
                df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)

            # Add metadata columns
            df["source_page"] = 1
            df["source_table"] = idx
            df["Month"] = month_name

            # Sheet type
            if idx == 1:
                df["Sheet_Type"] = "Summary"
            else:
                df["Sheet_Type"] = "Details"

            all_data.append(df)

            print(f"   ✅ Loaded sheet {idx}: {sheet_name} — {len(df)} rows")

    except Exception as e:
        print(f"⚠️ Error reading {filename}: {e}")

# ==========================================
# 3️⃣ Combine Everything
# ==========================================
combined_df = pd.concat(all_data, ignore_index=True)

# Reorder columns for readability
combined_df = combined_df[
    ["source_page", "source_table", "Group", "Count", "Amount", "Month", "Sheet_Type"]
]

# Save to CSV
combined_df.to_csv(OUTPUT_FILE, index=False)

print(f"\n✅ Cleaned dataset saved to: {OUTPUT_FILE}")
print(f"📏 Rows: {len(combined_df)} | Columns: {len(combined_df.columns)}")
print(f"📋 Columns: {list(combined_df.columns)}")

# Show sample
print("\n🔍 Sample:")
print(combined_df.head(10))