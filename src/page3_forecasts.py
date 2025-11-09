# =====================================================
# page3_forecasts.py — Forecasts & Predictions Page
# =====================================================
import os
import pandas as pd
import plotly.express as px
from dash import html, dcc
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.linear_model import LinearRegression
from difflib import SequenceMatcher
import re

# =====================================================
# LOAD DATA SAFELY
# =====================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH_MONTHLY = os.path.join(BASE_DIR, "../data/cleaned_monthly_data.csv")
DATA_PATH_ING = os.path.join(BASE_DIR, "../data/ingredient.csv")

try:
    monthly_df = pd.read_csv(DATA_PATH_MONTHLY)
    ingredient_df = pd.read_csv(DATA_PATH_ING)
except FileNotFoundError:
    print("=" * 60)
    print("ERROR: One or more data files not found for Page 3.")
    print("=" * 60)
    monthly_df = pd.DataFrame(columns=["Amount", "Count", "Month", "Sheet_Type", "Category", "Item Name"])
    ingredient_df = pd.DataFrame(columns=["Item Name"])

# =====================================================
# CLEAN DATA
# =====================================================
monthly_df["Amount"] = pd.to_numeric(monthly_df["Amount"], errors="coerce").fillna(0)
monthly_df["Count"] = pd.to_numeric(monthly_df["Count"], errors="coerce").fillna(0)
month_order = ["May", "June", "July", "August", "September", "October"]
monthly_df["Month"] = pd.Categorical(monthly_df["Month"], categories=month_order, ordered=True)

summary_df = monthly_df[monthly_df["Sheet_Type"] == "Summary"]
details_df = monthly_df[monthly_df["Sheet_Type"] == "Details"].copy()

# =====================================================
# GRAPH 1 — REVENUE FORECAST (HOLT-WINTERS)
# =====================================================
monthly_revenue = summary_df.groupby("Month", as_index=False, observed=False)["Amount"].sum()
forecast_fig = px.line()
forecast_df = pd.DataFrame(columns=["Month", "Forecasted_Revenue"])

if len(monthly_revenue) >= 2:
    month_map = {
        "May": "2025-05-01", "June": "2025-06-01", "July": "2025-07-01",
        "August": "2025-08-01", "September": "2025-09-01", "October": "2025-10-01"
    }
    revenue_series = monthly_revenue.copy()
    revenue_series["ds"] = pd.to_datetime(revenue_series["Month"].map(month_map))
    revenue_series.set_index("ds", inplace=True)

    # Forecast with graceful fallback (silent)
    try:
        model = ExponentialSmoothing(
            revenue_series["Amount"],
            trend="add",
            seasonal="add",
            seasonal_periods=6,
            freq="MS"
        )
        fit = model.fit()
        forecast_values = fit.forecast(3)
    except Exception:
        # Fallback: trend-only model silently
        model = ExponentialSmoothing(
            revenue_series["Amount"],
            trend="add",
            seasonal=None,
            freq="MS"
        )
        fit = model.fit()
        forecast_values = fit.forecast(3)

    # Build forecast DataFrame
    forecast_months = pd.date_range(
        revenue_series.index[-1] + pd.offsets.MonthBegin(),
        periods=3,
        freq="MS"
    )
    forecast_df = pd.DataFrame({
        "Month": forecast_months.strftime("%B"),
        "Forecasted_Revenue": forecast_values
    })

    # =====================================================
    # APPLY COLLEGE-TOWN SEASONAL LOGIC
    # =====================================================
    # December & January -> fewer students = sales dip
    # February -> rebound when spring semester starts
    forecast_df.loc[forecast_df["Month"] == "December", "Forecasted_Revenue"] *= 0.75
    forecast_df.loc[forecast_df["Month"] == "January", "Forecasted_Revenue"] *= 0.80
    forecast_df.loc[forecast_df["Month"] == "February", "Forecasted_Revenue"] *= 1.05

    # Add both actual + forecasted lines
    forecast_fig.add_scatter(
        x=revenue_series.index.strftime("%B"),
        y=revenue_series["Amount"],
        mode="lines+markers",
        name="Actual Revenue",
        line=dict(color="#8B0000", width=3)
    )
    forecast_fig.add_scatter(
        x=forecast_df["Month"],
        y=forecast_df["Forecasted_Revenue"],
        mode="lines+markers",
        name="Forecasted Revenue",
        line=dict(color="#B71C1C", dash="dash", width=3)
    )

forecast_fig.update_layout(
    template="plotly_white",
    showlegend=True,
    title=None,
    height=430,
    legend=dict(orientation="h", y=-0.2, x=0.3)
)

# =====================================================
# GRAPH 2 — INGREDIENT DEMAND FORECAST (REGRESSION)
# =====================================================
usage_summary = pd.DataFrame(columns=["Month", "Ingredient", "Total_Used"])
if not ingredient_df.empty and not details_df.empty:
    ingredient_df.columns = [c.strip().lower().replace(" ", "_") for c in ingredient_df.columns]
    ingredient_df.rename(columns={"item_name": "Item Name"}, inplace=True, errors="ignore")

    def normalize(text):
        return re.sub(r'[^a-z0-9]+', ' ', str(text).lower()).strip()

    details_df["key"] = details_df["Item Name"].apply(normalize)
    ingredient_df["key"] = ingredient_df["Item Name"].apply(normalize)

    def is_similar(a, b, threshold=0.85):
        return SequenceMatcher(None, a, b).ratio() >= threshold

    merged_rows = []
    for _, irow in ingredient_df.iterrows():
        key_i = irow["key"]
        matches = details_df[details_df["key"].apply(lambda x: is_similar(x, key_i))]
        if not matches.empty:
            tmp = matches.copy()
            for col in ingredient_df.columns:
                if col not in tmp.columns:
                    tmp[col] = irow[col]
            merged_rows.append(tmp)

    if merged_rows:
        merged_df = pd.concat(merged_rows, ignore_index=True)
        ingredient_cols = [col for col in merged_df.columns if col not in
                           ["source_page", "source_table", "Group", "Count", "Amount", "Month",
                            "Sheet_Type", "Category", "Item Name", "key"]]
        usage_records = []
        for _, row in merged_df.iterrows():
            for col in ingredient_cols:
                val = pd.to_numeric(row[col], errors="coerce")
                if pd.notna(val) and val > 0:
                    usage_records.append({
                        "Month": row["Month"],
                        "Ingredient": col,
                        "Total_Used": val * row["Count"]
                    })
        if usage_records:
            usage_df = pd.DataFrame(usage_records)
            usage_summary = usage_df.groupby(["Month", "Ingredient"], as_index=False, observed=False)["Total_Used"].sum()

ing_forecast_fig = px.line()
if not forecast_df.empty and not usage_summary.empty:
    total_ing_df = usage_summary.groupby("Month", as_index=False, observed=False)["Total_Used"].sum()
    merged_forecast_data = pd.merge(monthly_revenue, total_ing_df, on="Month", how="inner")

    if len(merged_forecast_data) >= 2:
        X = merged_forecast_data[["Amount"]].values
        y = merged_forecast_data["Total_Used"].values
        reg = LinearRegression().fit(X, y)
        forecast_df["Predicted_Ingredients"] = reg.predict(forecast_df[["Forecasted_Revenue"]].values)

        ing_forecast_fig.add_scatter(
            x=merged_forecast_data["Month"],
            y=merged_forecast_data["Total_Used"],
            mode="lines+markers",
            name="Actual Usage",
            line=dict(color="#8B0000", width=3)
        )
        ing_forecast_fig.add_scatter(
            x=forecast_df["Month"],
            y=forecast_df["Predicted_Ingredients"],
            mode="lines+markers",
            name="Forecasted Usage",
            line=dict(color="#B71C1C", dash="dash", width=3)
        )

ing_forecast_fig.update_layout(
    template="plotly_white",
    title=None,
    showlegend=True,
    height=430,
    legend=dict(orientation="h", y=-0.2, x=0.3)
)

# =====================================================
# PAGE 3 LAYOUT (Dark Red Theme)
# =====================================================
layout = html.Div([
    html.H2("Forecasts & Predictions", className="text-center fw-bold mt-4 mb-4", style={"color": "#2B0000"}),

    html.Div([
        html.Div("3-Month Revenue Forecast (Holt-Winters with College-Town Adjustments)",
                 className="fw-bold text-center text-white",
                 style={"backgroundColor": "#8B0000", "padding": "10px", "borderRadius": "8px 8px 0 0"}),
        html.Div([
            dcc.Graph(figure=forecast_fig, style={"height": "430px"})
        ], style={"border": "1px solid #ddd", "borderTop": "none",
                  "padding": "20px", "borderRadius": "0 0 8px 8px"})
    ], style={"marginBottom": "50px"}),

    html.Div([
        html.Div("3-Month Ingredient Demand Forecast",
                 className="fw-bold text-center text-white",
                 style={"backgroundColor": "#8B0000", "padding": "10px", "borderRadius": "8px 8px 0 0"}),
        html.Div([
            dcc.Graph(figure=ing_forecast_fig, style={"height": "430px"})
        ], style={"border": "1px solid #ddd", "borderTop": "none",
                  "padding": "20px", "borderRadius": "0 0 8px 8px"})
    ])
],
style={
    "maxWidth": "1600px",
    "margin": "auto",
    "paddingBottom": "60px",
    "overflowX": "hidden"
})

# =====================================================
# CALLBACKS (none for now)
# =====================================================
def register_callbacks(app):
    """Register callbacks for this page (currently none)."""
    pass