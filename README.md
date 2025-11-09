The Mai Shan Yun Dashboard seamlessly merges analytics, forecasting, and usability into one data intelligence system.
It captures how data science can improve restaurant management, particularly in dynamic, seasonally driven environments like college towns.

“From understanding what sells to predicting what’s next — this dashboard helps Mai Shan Yun operate smarter every single day.”
# 🥢 Mai Shan Yun Inventory Intelligence Dashboard

Transforming restaurant data into smart, actionable insights.

---

## 🌟 Overview

The **Mai Shan Yun Dashboard** is a data-driven analytics platform designed to optimize restaurant operations using real business data from *Mai Shan Yun*, a college-town restaurant in College Station, Texas.

Built with **Python Dash**, this project turns raw purchase logs, ingredient usage, and shipment data into interactive visual insights and predictive forecasts — helping managers minimize waste, avoid shortages, and plan for seasonal demand shifts.

---

## 🧭 System Architecture

```
MSY/
│
├── data/                                 # Raw and processed datasets
│   ├── May_Data_Matrix.xlsx
│   ├── June_Data_Matrix.xlsx
│   ├── July_Data_Matrix.xlsx
│   ├── August_Data_Matrix.xlsx
│   ├── September_Data_Matrix.xlsx
│   ├── October_Data_Matrix.xlsx
│   ├── cleaned_monthly_data.csv          # Output from data_processing.py
│   ├── ingredient.csv
│   └── shipment.csv
│
├── src/
│   ├── assets/                           # App styling and logo
│   │   └── logo.png
│   │
│   ├── app.py                            # Main app layout and navigation
│   ├── data_processing.py                # Cleans and merges monthly Excel sheets
│   ├── page1_revenue.py                  # Revenue & category analytics
│   ├── page2_ingredients_shipments.py    # Ingredient usage and shipment tracking
│   ├── page3_forecasts.py                # Revenue & demand forecasting (Holt-Winters + regression)
│   │
│   ├── verify_row_counts.py              # Validation: record counts
│   ├── verify_sheet_totals.py            # Validation: totals per sheet
│   ├── verify_summary_vs_details.py      # Validation: consistency check
│   └── verify_totals.py                  # Validation: grand totals
│
└── README.md                             # Documentation
```

---

## ⚙️ Data Pipeline

### 1️⃣ Data Processing

**File:** `data_processing.py`
- Combines all six monthly Excel sheets (May–October).
- Normalizes column names, data types, and monetary values.
- Outputs a single `cleaned_monthly_data.csv` file used by the dashboard.

### 2️⃣ Data Verification

Scripts ensure data integrity before visualization:
- `verify_row_counts.py` → Confirms all records from each sheet are loaded.
- `verify_sheet_totals.py` → Matches monthly subtotals to aggregated data.
- `verify_summary_vs_details.py` → Ensures category and item-level consistency.
- `verify_totals.py` → Final cross-check for accuracy across datasets.

### 3️⃣ Data Integration

`app.py` and each `pageX_*.py` module pull data from `cleaned_monthly_data.csv`, `ingredient.csv`, and `shipment.csv`, merging them dynamically to generate analytics and forecasts.

---

## 🧩 Dashboard Overview

### 🟥 Page 1 — Revenue & Category Overview

**Goal:** Track revenue performance and identify top-selling categories.

**Features:**
- Total monthly revenue trend and year-to-date cumulative line charts.
- Highlight of highest and lowest earning months.
- Top 8 categories by revenue per month (interactive dropdown).
- Top 5 categories trend line over time (with distinct red gradients).

**Example Insight:**
> “Tossed Ramen and Fried Chicken lead in revenue for May, showing strong early semester demand.”

---

### 🟥 Page 2 — Ingredients & Shipments

**Goal:** Optimize inventory and supply chain efficiency.

**Features:**
- Top 5 and Bottom 5 ingredients per month.
- Shipment frequency visualization (weekly, biweekly, monthly).
- Highlights most expensive ingredients and recurring shipment costs.
- Links ingredient consumption with purchase trends.

**Example Insight:**
> “Chicken and Rice drive the largest ingredient costs — ideal for bulk purchasing agreements.”

---

### 🟥 Page 3 — Forecasts & Predictions

**Goal:** Predict future sales and inventory demand.

**Features:**
- 3-Month Revenue Forecast using **Holt-Winters Exponential Smoothing** (trend-only model).
- Ingredient Demand Forecast using **Linear Regression** correlated with forecasted revenue.
- **College-Town Seasonal Adjustment:** accounts for lower footfall during winter breaks and spikes during the start of semesters.
- Auto-fallback to trend-based forecast when data is below two full seasonal cycles.

**Example Insight:**
> “Revenue expected to dip in December–January due to winter break, then rebound in February as students return.”

---

## 📈 Predictive Models

**1. Holt-Winters Forecasting (Revenue):**
- Captures overall trend and short-term changes.
- Ideal for restaurants with monthly data and short history windows.

**2. Linear Regression (Ingredient Demand):**
- Maps relationship between forecasted revenue and ingredient usage.
- Provides predictive insight into how much of each ingredient should be restocked.

---

## 🧮 Data Insights

1. Revenue peaks occur around **September–October**, aligning with mid-semester dining surges.  
2. Low revenue months (**June**) correspond to fewer students in town.  
3. Top ingredients like **Ramen noodles** and **Chicken** dominate monthly usage.  
4. Frequent shipments for perishables (**vegetables, proteins**) indicate high rotation.  
5. Predictive analysis allows planning for restocks and staffing before demand shifts.  

---

## 🧠 Tech Stack

- **Python Dash** — Interactive dashboard framework  
- **Plotly** — Visualizations  
- **Pandas / NumPy** — Data processing  
- **Statsmodels / Scikit-learn** — Forecasting & regression models  
- **Bootstrap Components** — UI styling  
- **Excel & CSV** — Data integration  

---

## 🧰 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/shrutwik/msy-dashboard.git
cd MSY/src
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Prepare Data
Place all CSV and Excel files inside the `/data` folder.

### 4️⃣ Run the Dashboard
```bash
python app.py
```

### 5️⃣ View in Browser
Visit [http://127.0.0.1:8050](http://127.0.0.1:8050)

---

## 🏁 Conclusion

The **Mai Shan Yun Dashboard** seamlessly merges analytics, forecasting, and usability into one data intelligence system.  
It demonstrates how **data science can enhance restaurant management**, particularly in dynamic, seasonally driven environments like college towns.

> “From understanding what sells to predicting what’s next — this dashboard helps Mai Shan Yun operate smarter every single day.”

---