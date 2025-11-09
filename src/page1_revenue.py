import os
import pandas as pd
import plotly.express as px
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

# =====================================================
# LOAD DATA
# =====================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../data/cleaned_monthly_data.csv")

try:
    monthly_df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    print("=" * 50)
    print("ERROR: cleaned_monthly_data.csv not found.")
    print("=" * 50)
    monthly_df = pd.DataFrame(columns=["Amount", "Count", "Month", "Sheet_Type", "Category", "Item Name"])

# =====================================================
# CLEANING
# =====================================================
monthly_df["Amount"] = pd.to_numeric(monthly_df["Amount"], errors="coerce").fillna(0)
monthly_df["Count"] = pd.to_numeric(monthly_df["Count"], errors="coerce").fillna(0)
month_order = ["May", "June", "July", "August", "September", "October"]
monthly_df["Month"] = pd.Categorical(monthly_df["Month"], categories=month_order, ordered=True)

summary_df = monthly_df[monthly_df["Sheet_Type"] == "Summary"].copy()
details_df = monthly_df[monthly_df["Sheet_Type"] == "Details"].copy()

# =====================================================
# GRAPH 1 — Total Monthly Revenue Trend
# =====================================================
monthly_revenue = summary_df.groupby("Month", as_index=False, observed=False)["Amount"].sum()
revenue_fig = px.line(monthly_revenue, x="Month", y="Amount", markers=True,
                      labels={"Amount": "Revenue ($)", "Month": "Month"})
revenue_fig.update_traces(line_color="#8B0000", line_width=3)  # dark red
revenue_fig.update_layout(template="plotly_white", height=430, title=None)

# Revenue Stats
revenue_insight_1, revenue_insight_2, revenue_insight_3 = "💰 No data.", "📉 No data.", ""
if not monthly_revenue.empty:
    hi = monthly_revenue.loc[monthly_revenue["Amount"].idxmax()]
    lo = monthly_revenue.loc[monthly_revenue["Amount"].idxmin()]
    avg_val = monthly_revenue["Amount"].mean()
    revenue_insight_1 = f"Highest revenue: **{hi['Month']}** — **${hi['Amount']:,.2f}**."
    revenue_insight_2 = f"Lowest revenue: **{lo['Month']}** — **${lo['Amount']:,.2f}**."

# =====================================================
# GRAPH 2 — Category Revenue by Month
# =====================================================
category_revenue = details_df.groupby(["Month", "Category"], as_index=False, observed=False)["Amount"].sum()
month_options = [{"label": m, "value": m} for m in month_order if m in category_revenue["Month"].unique()]

# =====================================================
# GRAPH 3 — Top 5 Category Trends Over Time
# =====================================================
top_categories = category_revenue.groupby("Category", observed=False)["Amount"].sum().nlargest(5).index
top5_df = category_revenue[category_revenue["Category"].isin(top_categories)].copy()
top5_df["Month"] = pd.Categorical(top5_df["Month"], categories=month_order, ordered=True)

# darker red palette
red_palette = ["#B71C1C", "#8B0000", "#A40000", "#C62828", "#D32F2F"]
trend_fig = px.line(
    top5_df,
    x="Month", y="Amount", color="Category", markers=True,
    color_discrete_sequence=red_palette
)
trend_fig.update_traces(line=dict(width=3))
trend_fig.update_layout(template="plotly_white", height=430, title=None)

# =====================================================
# GRAPH 4 — Year-to-Date (Cumulative) Revenue + Stats
# =====================================================
monthly_revenue["Cumulative_Revenue"] = monthly_revenue["Amount"].cumsum()
cumulative_fig = px.line(monthly_revenue, x="Month", y="Cumulative_Revenue", markers=True)
cumulative_fig.update_traces(line_color="#6A0000", line_width=3)  # deeper crimson
cumulative_fig.update_layout(template="plotly_white", height=430, title=None)

# Month-on-Month Growth
monthly_revenue_sorted = monthly_revenue.sort_values("Month")
monthly_revenue_sorted["MoM_Growth_%"] = monthly_revenue_sorted["Amount"].pct_change() * 100
avg_growth = monthly_revenue_sorted["MoM_Growth_%"].mean()
growth_text = "Avg. MoM Growth: N/A"
if not pd.isna(avg_growth):
    growth_text = f"Avg. Month-on-Month Growth: **{avg_growth:.2f}%**"

total_revenue = monthly_revenue["Amount"].sum()
total_revenue_text = f"Total YTD Revenue: **${total_revenue:,.2f}**"

# =====================================================
# PAGE 1 LAYOUT
# =====================================================
layout = html.Div([
    html.H2("Revenue & Category Overview", className="text-center fw-bold mt-4 mb-4", style={"color": "#2B0000"}),

    # ROW 1
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Total Monthly Revenue Trend", className="fw-bold text-center text-white",
                               style={"backgroundColor": "#8B0000"}),  # dark red
                dbc.CardBody([
                    dcc.Graph(figure=revenue_fig, style={"height": "430px"}),
                    html.Div([
                        dcc.Markdown(revenue_insight_1, style={'fontSize': '16px', 'fontWeight': '500'}),
                        dcc.Markdown(revenue_insight_2, style={'fontSize': '16px', 'fontWeight': '500'}),
                        dcc.Markdown(revenue_insight_3, style={'fontSize': '16px', 'fontWeight': '500'})
                    ], style={'textAlign': 'center', 'marginTop': '10px'})
                ])
            ], className="shadow-sm")
        ], width=7),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Year-to-Date Revenue Trend", className="fw-bold text-center text-white",
                               style={"backgroundColor": "#8B0000"}),
                dbc.CardBody([
                    dcc.Graph(figure=cumulative_fig, style={"height": "430px"}),
                    html.Div([
                        dcc.Markdown(total_revenue_text, style={
                            'textAlign': 'center', 'fontSize': '16px',
                            'fontWeight': '500', 'marginTop': '10px'
                        }),
                        dcc.Markdown(growth_text, style={
                            'textAlign': 'center', 'fontSize': '16px',
                            'fontWeight': '500', 'marginTop': '4px'
                        })
                    ])
                ])
            ], className="shadow-sm")
        ], width=5)
    ], className="g-4 mb-4", style={"padding": "0px 30px"}),

    # ROW 2
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Top 8 Category Revenue by Month", className="fw-bold text-center text-white",
                               style={"backgroundColor": "#8B0000"}),
                dbc.CardBody([
                    html.Div([
                        html.Label("Select Month:", style={"fontWeight": "bold", "display": "block"}),
                        dcc.Dropdown(
                            id="month-dropdown", options=month_options,
                            value=month_options[0]["value"] if month_options else None,
                            clearable=False, style={
                                "width": "40%", "margin": "10px auto 20px auto", "textAlign": "center"
                            }
                        )
                    ], style={"textAlign": "center"}),

                    dcc.Graph(id="category-bar-chart", style={"height": "430px"}),
                    html.Div(id="category-insights", style={'textAlign': 'center', 'marginTop': '10px'})
                ])
            ], className="shadow-sm")
        ], width=12)
    ], className="g-4 mb-4", style={"padding": "0px 30px"}),

    # ROW 3
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Top 5 Category Trends Over Time", className="fw-bold text-center text-white",
                               style={"backgroundColor": "#8B0000"}),
                dbc.CardBody([
                    dcc.Graph(figure=trend_fig, style={"height": "430px"})
                ])
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
# CALLBACK
# =====================================================
def register_callbacks(app):
    @app.callback(
        [Output("category-bar-chart", "figure"),
         Output("category-insights", "children")],
        [Input("month-dropdown", "value")]
    )
    def update_category_chart(selected_month):
        if selected_month is None:
            return px.bar(), "⚠️ No month selected."
        filtered = category_revenue[category_revenue["Month"] == selected_month]
        filtered = filtered.sort_values("Amount", ascending=False).head(8)
        bar_fig = px.bar(filtered, x="Category", y="Amount", text="Amount",
                         color="Amount", color_continuous_scale=["#E57373", "#B71C1C", "#7F0000"])
        bar_fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        bar_fig.update_layout(template="plotly_white", height=430, title=None)
        if not filtered.empty:
            top_cat = filtered.iloc[0]
            insight = f"In **{selected_month}**, highest-earning category: **{top_cat['Category']}** (${top_cat['Amount']:,.2f})."
        else:
            insight = f"⚠️ No data for {selected_month}."
        return bar_fig, dcc.Markdown(insight, style={'fontSize': '16px', 'fontWeight': '500'})