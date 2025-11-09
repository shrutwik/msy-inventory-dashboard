import os
import re
import pandas as pd
import plotly.express as px
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
from difflib import SequenceMatcher

# =====================================================
# LOAD DATA
# =====================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH_MONTHLY = os.path.join(BASE_DIR, "../data/cleaned_monthly_data.csv")
DATA_PATH_ING = os.path.join(BASE_DIR, "../data/ingredient.csv")
DATA_PATH_SHIP = os.path.join(BASE_DIR, "../data/shipment.csv")

try:
    monthly_df = pd.read_csv(DATA_PATH_MONTHLY)
    ingredient_df = pd.read_csv(DATA_PATH_ING)
    shipment_df = pd.read_csv(DATA_PATH_SHIP)
except FileNotFoundError:
    print("=" * 50)
    print("ERROR: Data files not found for page 2.")
    print("=" * 50)
    monthly_df = pd.DataFrame(columns=["Amount", "Count", "Month", "Sheet_Type", "Category", "Item Name"])
    ingredient_df = pd.DataFrame(columns=["Item Name"])
    shipment_df = pd.DataFrame(columns=["frequency", "ingredient", "quantity_per_shipment"])

# =====================================================
# CLEANING
# =====================================================
monthly_df["Amount"] = pd.to_numeric(monthly_df["Amount"], errors="coerce").fillna(0)
monthly_df["Count"] = pd.to_numeric(monthly_df["Count"], errors="coerce").fillna(0)
month_order = ["May", "June", "July", "August", "September", "October"]
monthly_df["Month"] = pd.Categorical(monthly_df["Month"], categories=month_order, ordered=True)
details_df = monthly_df[monthly_df["Sheet_Type"] == "Details"].copy()

# =====================================================
# INGREDIENT USAGE CALCULATION
# =====================================================
usage_summary = pd.DataFrame(columns=["Month", "Ingredient", "Total_Used"])
if not ingredient_df.empty and not details_df.empty:
    ingredient_df.columns = [c.strip().lower().replace(" ", "_") for c in ingredient_df.columns]
    ingredient_df.rename(columns={"item_name": "Item Name"}, inplace=True, errors="ignore")

    def normalize(text): return re.sub(r'[^a-z0-9]+', ' ', str(text).lower()).strip()
    details_df["key"] = details_df["Item Name"].apply(normalize)
    ingredient_df["key"] = ingredient_df["Item Name"].apply(normalize)

    def is_similar(a, b, threshold=0.85): return SequenceMatcher(None, a, b).ratio() >= threshold

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
        ingredient_cols = [c for c in merged_df.columns if c not in
                           ["source_page", "source_table", "Group", "Count", "Amount", "Month",
                            "Sheet_Type", "Category", "Item Name", "key"]]
        usage_records = []
        for _, row in merged_df.iterrows():
            for col in ingredient_cols:
                val = pd.to_numeric(row[col], errors="coerce")
                if pd.notna(val) and val > 0:
                    usage_records.append({"Month": row["Month"], "Ingredient": col, "Total_Used": val * row["Count"]})
        usage_df = pd.DataFrame(usage_records)
        if not usage_df.empty:
            usage_summary = usage_df.groupby(["Month", "Ingredient"], as_index=False, observed=False)["Total_Used"].sum()

month_dropdown_ing = [{"label": m, "value": m} for m in month_order if m in usage_summary["Month"].unique()]

# =====================================================
# INGREDIENT COSTS + COST GRAPHS
# =====================================================
ingredient_costs = {
    "braised_beef_used_(g)": 0.0088, "braised_chicken(g)": 0.0055, "braised_pork(g)": 0.0066,
    "egg(count)": 0.20, "rice(g)": 0.0022, "ramen_(count)": 0.35, "rice_noodles(g)": 0.0033,
    "chicken_thigh_(pcs)": 0.50, "chicken_wings_(pcs)": 0.60, "flour_(g)": 0.0011,
    "pickle_cabbage": 0.0044, "green_onion": 0.0026, "cilantro": 0.0044, "white_onion": 0.002,
    "peas(g)": 0.0026, "carrot(g)": 0.0026, "boychoy(g)": 0.0040, "tapioca_starch": 0.0022
}

if not usage_summary.empty:
    usage_summary["Estimated_Cost"] = usage_summary.apply(
        lambda r: r["Total_Used"] * ingredient_costs.get(r["Ingredient"], 0), axis=1)

monthly_cost = usage_summary.groupby("Month", as_index=False, observed=False)["Estimated_Cost"].sum()
if not monthly_cost.empty:
    monthly_cost["Month"] = pd.Categorical(monthly_cost["Month"], categories=month_order, ordered=True)
    monthly_cost = monthly_cost.sort_values("Month")

# =====================================================
# SHIPMENT FREQUENCY
# =====================================================
freq_grouped = pd.DataFrame(columns=["frequency", "ingredient_count", "ingredient_list"])
if not shipment_df.empty:
    ship = shipment_df.copy()
    ship.columns = [c.strip().lower().replace(" ", "_") for c in ship.columns]
    ship["frequency"] = ship["frequency"].str.lower().str.strip()
    freq_order = ["weekly", "biweekly", "monthly"]
    ship["frequency"] = pd.Categorical(ship["frequency"], categories=freq_order, ordered=True)
    freq_counts = ship.groupby("frequency", as_index=False, observed=False)["ingredient"].count()
    freq_counts.rename(columns={"ingredient": "ingredient_count"}, inplace=True)
    ingredient_lists = ship.groupby("frequency", observed=False)["ingredient"].apply(lambda x: ", ".join(sorted(x))).reset_index()
    ingredient_lists.rename(columns={"ingredient": "ingredient_list"}, inplace=True)
    freq_grouped = pd.merge(freq_counts, ingredient_lists, on="frequency", how="left")

# =====================================================
# FIGURE HELPERS
# =====================================================
def make_top_ing(month):
    if month is None or usage_summary.empty:
        return px.bar()
    df = usage_summary[usage_summary["Month"] == month].nlargest(5, "Total_Used")
    fig = px.bar(df, x="Ingredient", y="Total_Used",
                 color="Total_Used", color_continuous_scale=["#E57373", "#B71C1C", "#7F0000"])
    fig.update_layout(template="plotly_white", height=430, title=None)
    return fig


def make_bottom_ing(month):
    if month is None or usage_summary.empty:
        return px.bar()
    df = usage_summary[usage_summary["Month"] == month].nsmallest(5, "Total_Used")
    fig = px.bar(df, x="Ingredient", y="Total_Used",
                 color="Total_Used", color_continuous_scale=["#E57373", "#B71C1C", "#7F0000"])
    fig.update_layout(template="plotly_white", height=430, title=None)
    return fig


# Darker reds for all visuals
cost_trend_fig = px.area(monthly_cost, x="Month", y="Estimated_Cost", color_discrete_sequence=["#8B0000"])
cost_trend_fig.update_layout(template="plotly_white", height=430, title=None)

ingredient_cost_totals = usage_summary.groupby("Ingredient", as_index=False, observed=False)["Estimated_Cost"].sum()
ingredient_cost_totals = ingredient_cost_totals.sort_values("Estimated_Cost", ascending=False).head(5)
top_cost_fig = px.bar(ingredient_cost_totals, x="Estimated_Cost", y="Ingredient",
                      orientation="h", color="Estimated_Cost",
                      color_continuous_scale=["#E57373", "#B71C1C", "#7F0000"])
top_cost_fig.update_layout(template="plotly_white", height=430, title=None)

freq_fig = px.bar(freq_grouped.sort_values("frequency"), x="frequency", y="ingredient_count",
                  text="ingredient_count", color="ingredient_count",
                  color_continuous_scale=["#E57373", "#B71C1C", "#7F0000"])
freq_fig.update_traces(
    texttemplate="%{text}", textposition="outside",
    hovertemplate="<b>%{x}</b><br><b>Ingredients:</b><br>%{customdata}<extra></extra>",
    customdata=freq_grouped["ingredient_list"]
)
freq_fig.update_layout(template="plotly_white", height=430, title=None)

# =====================================================
# PAGE 2 LAYOUT
# =====================================================
layout = html.Div([
    html.H2("Ingredients & Shipments", className="text-center fw-bold mt-4 mb-4", style={"color": "#2B0000"}),

    # INGREDIENT USAGE (TOP/BOTTOM)
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Top 5 Ingredients Used Each Month",
                               className="fw-bold text-center text-white",
                               style={"backgroundColor": "#8B0000"}),
                dbc.CardBody([
                    html.Div([
                        html.Label("Select Month:", style={"fontWeight": "bold", "display": "block"}),
                        dcc.Dropdown(
                            id="top-ing-month", options=month_dropdown_ing,
                            value=month_dropdown_ing[0]["value"] if month_dropdown_ing else None,
                            clearable=False,
                            style={"width": "60%", "margin": "10px auto 20px auto", "textAlign": "center"}
                        )
                    ], style={"textAlign": "center"}),
                    dcc.Graph(id="top-ingredients-chart",
                              figure=make_top_ing(month_dropdown_ing[0]["value"] if month_dropdown_ing else None),
                              style={"height": "430px"})
                ])
            ], className="shadow-sm")
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Bottom 5 Ingredients Used Each Month",
                               className="fw-bold text-center text-white",
                               style={"backgroundColor": "#8B0000"}),
                dbc.CardBody([
                    html.Div([
                        html.Label("Select Month:", style={"fontWeight": "bold", "display": "block"}),
                        dcc.Dropdown(
                            id="bottom-ing-month", options=month_dropdown_ing,
                            value=month_dropdown_ing[0]["value"] if month_dropdown_ing else None,
                            clearable=False,
                            style={"width": "60%", "margin": "10px auto 20px auto", "textAlign": "center"}
                        )
                    ], style={"textAlign": "center"}),
                    dcc.Graph(id="bottom-ingredients-chart",
                              figure=make_bottom_ing(month_dropdown_ing[0]["value"] if month_dropdown_ing else None),
                              style={"height": "430px"})
                ])
            ], className="shadow-sm")
        ], width=6)
    ], className="g-4 mb-4", style={"padding": "0px 30px"}),

    # COST TRENDS
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Estimated Monthly Ingredient Cost Trend",
                               className="fw-bold text-center text-white",
                               style={"backgroundColor": "#8B0000"}),
                dbc.CardBody([dcc.Graph(figure=cost_trend_fig, style={"height": "430px"})])
            ], className="shadow-sm")
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Top 5 Ingredients Driving the Most Spending",
                               className="fw-bold text-center text-white",
                               style={"backgroundColor": "#8B0000"}),
                dbc.CardBody([dcc.Graph(figure=top_cost_fig, style={"height": "430px"})])
            ], className="shadow-sm")
        ], width=6)
    ], className="g-4 mb-4", style={"padding": "0px 30px"}),

    # SHIPMENT FREQUENCY
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Shipment Frequency Overview",
                               className="fw-bold text-center text-white",
                               style={"backgroundColor": "#8B0000"}),
                dbc.CardBody([dcc.Graph(figure=freq_fig, style={"height": "430px"})])
            ], className="shadow-sm")
        ], width=12)
    ], className="g-4 mb-4", style={"padding": "0px 30px"})
],
style={
    "maxWidth": "1600px",
    "margin": "auto",
    "paddingBottom": "60px",
    "overflowX": "hidden"
})

# =====================================================
# CALLBACKS
# =====================================================
def register_callbacks(app):
    @app.callback(Output("top-ingredients-chart", "figure"), Input("top-ing-month", "value"))
    def update_top(month):
        return make_top_ing(month)

    @app.callback(Output("bottom-ingredients-chart", "figure"), Input("bottom-ing-month", "value"))
    def update_bottom(month):
        return make_bottom_ing(month)