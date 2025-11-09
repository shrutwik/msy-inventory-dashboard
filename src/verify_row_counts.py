import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

# All your files
files = {
    "May": "May_Data_Matrix (1).xlsx",
    "June": "June_Data_Matrix.xlsx",
    "July": "July_Data_Matrix (1).xlsx",
    "August": "August_Data_Matrix (1).xlsx",
    "September": "September_Data_Matrix.xlsx",
    "October": "October_Data_Matrix_20251103_214000.xlsx"
}

def count_raw_rows():
    """Count rows in every sheet for every file."""
    raw_counts = []
    for month, filename in files.items():
        file_path = DATA_DIR / filename
        xls = pd.ExcelFile(file_path)

        for sheet in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet)
            raw_counts.append({
                "Month": month,
                "Sheet_Name": sheet,
                "Raw_Rows": len(df)
            })
    return pd.DataFrame(raw_counts)

def count_combined_rows():
    """Count rows from the cleaned dataset."""
    combined_path = DATA_DIR / "cleaned_monthly_data.csv"
    df = pd.read_csv(combined_path)
    combined_counts = df.groupby(["Month", "Sheet_Type"]).size().reset_index(name="Loaded_Rows")
    return combined_counts

if __name__ == "__main__":
    raw_df = count_raw_rows()
    combined_df = count_combined_rows()

    print("\n📘 Raw Excel Row Counts:")
    print(raw_df)

    print("\n📗 Combined CSV Row Counts (from cleaned file):")
    print(combined_df)

    # Try to align the sheet names
    # We expect 3 sheets per month -> 1 Summary, 2 Details
    # So let’s compare total rows per month
    raw_totals = raw_df.groupby("Month")["Raw_Rows"].sum().reset_index(name="Total_Raw_Rows")
    combined_totals = combined_df.groupby("Month")["Loaded_Rows"].sum().reset_index(name="Total_Loaded_Rows")

    merged = pd.merge(raw_totals, combined_totals, on="Month", how="outer")
    merged["Match"] = merged["Total_Raw_Rows"] == merged["Total_Loaded_Rows"]

    print("\n🧾 Month-wise Row Verification:")
    print(merged)