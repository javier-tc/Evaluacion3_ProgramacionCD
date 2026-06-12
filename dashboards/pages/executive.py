from datetime import date

import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from dashboards.api_client import (
    PLOTLY_CONFIG,
    get_annual_averages,
    get_daily,
    get_monthly,
    get_top_days,
    get_trends,
)

POLLUTANTS = ["CO", "MP10", "MP25", "NO2", "O3"]


def layout():
    return dbc.Container([
        html.H2("Dashboard Ejecutivo", className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.DatePickerRange(
                id="exec-date-range",
                start_date=date(2025, 6, 1),
                end_date=date(2026, 6, 1),
                display_format="DD/MM/YYYY",
            ), md=6),
            dbc.Col(dcc.Dropdown(
                id="exec-pollutant",
                options=[{"label": p, "value": p} for p in POLLUTANTS],
                value="MP25",
                clearable=True,
                placeholder="Todos los contaminantes",
            ), md=6),
        ], className="mb-4"),
        dbc.Row(id="exec-kpis", className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="exec-timeline", config=PLOTLY_CONFIG), md=8),
            dbc.Col(dcc.Graph(id="exec-bar-compare", config=PLOTLY_CONFIG), md=4),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="exec-monthly", config=PLOTLY_CONFIG), md=6),
            dbc.Col(dcc.Graph(id="exec-top-days", config=PLOTLY_CONFIG), md=6),
        ], className="mt-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="exec-trends", config=PLOTLY_CONFIG), md=12),
        ], className="mt-3"),
    ], fluid=True)


@callback(
    Output("exec-kpis", "children"),
    Output("exec-timeline", "figure"),
    Output("exec-bar-compare", "figure"),
    Output("exec-monthly", "figure"),
    Output("exec-top-days", "figure"),
    Output("exec-trends", "figure"),
    Input("exec-date-range", "start_date"),
    Input("exec-date-range", "end_date"),
    Input("exec-pollutant", "value"),
)
def update_executive(start_date, end_date, pollutant):
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None

    annual = get_annual_averages()
    daily = get_daily(pollutant, start, end)
    monthly = get_monthly(pollutant)
    top = get_top_days(pollutant, 10)
    trends = get_trends()

    kpis = []
    for item in annual:
        kpis.append(dbc.Col(html.Div([
            html.Div(f"{item['annual_avg']:.2f}", className="kpi-value"),
            html.Div(f"Promedio anual {item['pollutant']} ({item['unit']})", className="kpi-label"),
        ], className="kpi-card"), md=2))

    if annual:
        predominant = max(annual, key=lambda x: x["annual_avg"])
        kpis.append(dbc.Col(html.Div([
            html.Div(predominant["pollutant"], className="kpi-value"),
            html.Div("Contaminante predominante", className="kpi-label"),
        ], className="kpi-card"), md=2))

    fig_timeline = px.line(
        daily, x="date", y="avg_value", color="pollutant" if not pollutant else None,
        title="Evolucion temporal de contaminantes",
        labels={"avg_value": "Concentracion promedio", "date": "Fecha"},
    ) if daily else go.Figure().update_layout(title="Sin datos")

    fig_bar = px.bar(
        annual, x="pollutant", y="annual_avg", color="pollutant",
        title="Comparacion promedios anuales",
        labels={"annual_avg": "Promedio anual", "pollutant": "Contaminante"},
    ) if annual else go.Figure().update_layout(title="Sin datos")

    fig_monthly = px.bar(
        monthly, x="year_month", y="avg_value", color="pollutant" if not pollutant else None,
        title="Evolucion mensual",
        labels={"avg_value": "Promedio mensual", "year_month": "Mes"},
    ) if monthly else go.Figure().update_layout(title="Sin datos")

    fig_top = px.bar(
        top, x="date", y="value", color="pollutant",
        title="Dias con mayor contaminacion",
        labels={"value": "Concentracion maxima", "date": "Fecha"},
    ) if top else go.Figure().update_layout(title="Sin datos")

    if trends:
        fig_trends = go.Figure()
        for t in trends:
            direction = "↑" if t["trend_direction"] == "increasing" else "↓"
            fig_trends.add_trace(go.Bar(
                x=[t["pollutant"]],
                y=[t["slope"]],
                name=f"{t['pollutant']} {direction} (R²={t['r_squared']:.3f})",
            ))
        fig_trends.update_layout(title="Tendencias por contaminante (pendiente)", barmode="group")
    else:
        fig_trends = go.Figure().update_layout(title="Sin datos de tendencias")

    return kpis, fig_timeline, fig_bar, fig_monthly, fig_top, fig_trends
