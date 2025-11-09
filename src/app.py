# =====================================================
# app.py — Main Entry for Mai Shan Yun Dashboard
# =====================================================
import dash
from dash import html, dcc, Output, Input
import dash_bootstrap_components as dbc

# =====================================================
# IMPORT PAGE LAYOUTS & CALLBACKS
# =====================================================
from page1_revenue import layout as page1_layout, register_callbacks as register_page1_callbacks
from page2_ingredients_shipments import layout as page2_layout, register_callbacks as register_page2_callbacks
from page3_forecasts import layout as page3_layout, register_callbacks as register_page3_callbacks

# =====================================================
# INITIALIZE DASH APP
# =====================================================
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.title = "Mai Shan Yun Dashboard"
server = app.server

# =====================================================
# APP LAYOUT (Header + Navigation + Dynamic Page Content)
# =====================================================
app.layout = html.Div([

    # ---------- HEADER ----------
    html.Div([
        html.Div([
            html.Img(
                src="/assets/logo.png",
                height="110px",
                style={
                    "display": "block",
                    "margin": "0 auto",
                    "paddingBottom": "8px",
                    "filter": "drop-shadow(0px 2px 4px rgba(0,0,0,0.4))"
                }
            ),
            html.H2(
                "Mai Shan Yun Dashboard",
                style={
                    "textAlign": "center",
                    "color": "white",
                    "fontWeight": "700",
                    "fontSize": "32px",
                    "margin": "0",
                    "paddingBottom": "4px",
                    "letterSpacing": "1px"
                }
            ),
            html.H5(
                "103 College Ave, College Station, TX 77840",
                style={
                    "textAlign": "center",
                    "color": "lightgray",
                    "fontWeight": "400",
                    "fontSize": "16px",
                    "margin": "0",
                    "paddingBottom": "10px",
                    "letterSpacing": "0.5px"
                }
            ),
        ]),
    ],
        style={
            "backgroundColor": "black",
            "padding": "25px 0",
            "boxShadow": "0px 2px 8px rgba(0,0,0,0.3)"
        }
    ),

    # ---------- NAVIGATION ----------
    html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col(
                    dbc.Button(
                        "Revenue Overview",
                        id="nav-page1",
                        className="w-100",
                        n_clicks=0,
                        style={
                            "backgroundColor": "#8B0000",
                            "color": "white",
                            "fontWeight": "600",
                            "border": "none",
                            "fontSize": "16px",
                            "boxShadow": "0px 2px 6px rgba(0,0,0,0.3)",
                            "transition": "all 0.2s ease-in-out"
                        }
                    ),
                    width=4
                ),
                dbc.Col(
                    dbc.Button(
                        "Ingredients & Shipments",
                        id="nav-page2",
                        className="w-100",
                        n_clicks=0,
                        style={
                            "backgroundColor": "#8B0000",
                            "color": "white",
                            "fontWeight": "600",
                            "border": "none",
                            "fontSize": "16px",
                            "boxShadow": "0px 2px 6px rgba(0,0,0,0.3)",
                            "transition": "all 0.2s ease-in-out"
                        }
                    ),
                    width=4
                ),
                dbc.Col(
                    dbc.Button(
                        "Forecasts & Predictions",
                        id="nav-page3",
                        className="w-100",
                        n_clicks=0,
                        style={
                            "backgroundColor": "#8B0000",
                            "color": "white",
                            "fontWeight": "600",
                            "border": "none",
                            "fontSize": "16px",
                            "boxShadow": "0px 2px 6px rgba(0,0,0,0.3)",
                            "transition": "all 0.2s ease-in-out"
                        }
                    ),
                    width=4
                ),
            ], className="mb-4 text-center gx-3"),
        ])
    ], style={"paddingTop": "20px"}),

    # ---------- PAGE CONTENT ----------
    dbc.Container([
        html.Div(id="page-content", children=page1_layout)
    ])
])

# =====================================================
# PAGE SWITCHING CALLBACK
# =====================================================
@app.callback(
    Output("page-content", "children"),
    [Input("nav-page1", "n_clicks"),
     Input("nav-page2", "n_clicks"),
     Input("nav-page3", "n_clicks")]
)
def display_page(page1, page2, page3):
    ctx = dash.callback_context

    if not ctx.triggered:
        return page1_layout

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "nav-page1":
        return page1_layout
    elif button_id == "nav-page2":
        return page2_layout
    elif button_id == "nav-page3":
        return page3_layout
    else:
        return page1_layout

# =====================================================
# REGISTER CALLBACKS FOR ALL PAGES
# =====================================================
register_page1_callbacks(app)
register_page2_callbacks(app)
register_page3_callbacks(app)

# =====================================================
# RUN APP
# =====================================================
if __name__ == "__main__":
    app.run(debug=True)