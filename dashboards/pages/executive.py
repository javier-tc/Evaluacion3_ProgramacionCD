from datetime import date

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from dashboards.api_client import PLOTLY_CONFIG, get_annual_averages, get_monthly
from dashboards.utils.constants import POLLUTANTS
from dashboards.utils.normalization import normalize_monthly
from dashboards.utils.transforms import display_pollutant, display_unit

KPI_ORDER = ["MP25", "MP10", "NO2", "O3", "CO"]


def layout():
    return dbc.Container([
        html.H2("Dashboard Ejecutivo", className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.DatePickerRange(
                id="exec-date-range",
                start_date=date(2025, 6, 1),
                end_date=date(2026, 6, 1),
                display_format="DD/MM/YYYY",
            ), md=8),
        ], className="mb-4"),
        html.H4("Indicadores Anuales", className="mb-3"),
        dbc.Row(id="exec-kpis", className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="exec-ranking", config=PLOTLY_CONFIG), md=5),
            dbc.Col(dcc.Graph(id="exec-monthly-norm", config=PLOTLY_CONFIG), md=7),
        ]),
    ], fluid=True)


@callback(
    Output("exec-kpis", "children"),
    Output("exec-ranking", "figure"),
    Output("exec-monthly-norm", "figure"),
    Input("exec-date-range", "start_date"),
    Input("exec-date-range", "end_date"),
)
def update_executive(start_date, end_date):
    annual = get_annual_averages()
    monthly = get_monthly()

    annual_map = {a["pollutant"]: a for a in annual}

    kpis = []
    for pol in KPI_ORDER:
        item = annual_map.get(pol)
        if item:
            kpis.append(dbc.Col(html.Div([
                html.Div(f"{item['annual_avg']:.2f}", className="kpi-value"),
                html.Div(
                    f"Promedio anual {display_pollutant(pol)} ({display_unit(item['unit'])})",
                    className="kpi-label",
                ),
            ], className="kpi-card"), md=2, xs=6))
        else:
            kpis.append(dbc.Col(html.Div([
                html.Div("N/A", className="kpi-value"),
                html.Div(f"Promedio anual {display_pollutant(pol)}", className="kpi-label"),
            ], className="kpi-card"), md=2, xs=6))

    if annual:
        rank_df = pd.DataFrame(annual)
        rank_df["label"] = rank_df.apply(
            lambda r: f"{display_pollutant(r['pollutant'])} ({display_unit(r['unit'])})", axis=1
        )
        fig_rank = px.bar(
            rank_df.sort_values("annual_avg", ascending=True),
            x="annual_avg",
            y="label",
            orientation="h",
            title="Ranking de contaminantes (valores reales)",
            labels={"annual_avg": "Promedio anual", "label": "Contaminante"},
            text="annual_avg",
        )
        fig_rank.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig_rank.add_annotation(
            text="Cada barra en su unidad física (ppm, μg/m³ o ppb)",
            xref="paper", yref="paper", x=0, y=-0.15, showarrow=False,
            font=dict(size=11),
        )
    else:
        fig_rank = go.Figure().update_layout(title="Sin datos de ranking")

    if monthly:
        mdf = pd.DataFrame(monthly)
        if start_date:
            mdf = mdf[mdf["year_month"] >= start_date[:7]]
        if end_date:
            mdf = mdf[mdf["year_month"] <= end_date[:7]]
        mdf["pollutant_label"] = mdf["pollutant"].map(display_pollutant)
        norm_df = normalize_monthly(mdf)
        fig_norm = px.line(
            norm_df,
            x="year_month",
            y="normalized",
            color="pollutant_label",
            title="Evolución mensual normalizada (min-max por contaminante)",
            labels={
                "normalized": "Índice normalizado (0-1)",
                "year_month": "Mes",
                "pollutant_label": "Contaminante",
            },
            markers=True,
        )
        fig_norm.add_annotation(
            text="Normalización min-max solo para comparar tendencias, no magnitudes absolutas",
            xref="paper", yref="paper", x=0, y=-0.12, showarrow=False,
            font=dict(size=11),
        )
    else:
        fig_norm = go.Figure().update_layout(title="Sin datos mensuales")

    return kpis, fig_rank, fig_norm
