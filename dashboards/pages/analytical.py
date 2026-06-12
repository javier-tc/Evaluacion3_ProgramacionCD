from datetime import date

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from dashboards.api_client import (
    PLOTLY_CONFIG,
    get_correlations,
    get_daily,
    get_pollution,
    get_weather,
)

POLLUTANTS = ["CO", "MP10", "MP25", "NO2", "O3"]


def layout():
    return dbc.Container([
        html.H2("Dashboard Analitico", className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.DatePickerRange(
                id="anal-date-range",
                start_date=date(2025, 6, 1),
                end_date=date(2026, 6, 1),
                display_format="DD/MM/YYYY",
            ), md=6),
            dbc.Col(dcc.Dropdown(
                id="anal-pollutant",
                options=[{"label": p, "value": p} for p in POLLUTANTS],
                value="MP25",
            ), md=6),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="anal-corr", config=PLOTLY_CONFIG), md=6),
            dbc.Col(dcc.Graph(id="anal-heatmap", config=PLOTLY_CONFIG), md=6),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="anal-boxplot", config=PLOTLY_CONFIG), md=6),
            dbc.Col(dcc.Graph(id="anal-histogram", config=PLOTLY_CONFIG), md=6),
        ], className="mt-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="anal-weekly", config=PLOTLY_CONFIG), md=6),
            dbc.Col(dcc.Graph(id="anal-hourly", config=PLOTLY_CONFIG), md=6),
        ], className="mt-3"),
    ], fluid=True)


@callback(
    Output("anal-corr", "figure"),
    Output("anal-heatmap", "figure"),
    Output("anal-boxplot", "figure"),
    Output("anal-histogram", "figure"),
    Output("anal-weekly", "figure"),
    Output("anal-hourly", "figure"),
    Input("anal-date-range", "start_date"),
    Input("anal-date-range", "end_date"),
    Input("anal-pollutant", "value"),
)
def update_analytical(start_date, end_date, pollutant):
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None

    corrs = get_correlations()
    pollution = get_pollution(pollutant, start, end)
    daily = get_daily(None, start, end)
    weather = get_weather(start, end)

    if corrs:
        corr_df = pd.DataFrame(corrs)
        pivot = corr_df.pivot(index="var_x", columns="var_y", values="correlation")
        fig_corr = px.imshow(
            pivot, title="Matriz de correlacion",
            color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
        )
    else:
        fig_corr = go.Figure().update_layout(title="Sin datos de correlacion")

    if daily:
        df = pd.DataFrame(daily)
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.month
        df["weekday"] = df["date"].dt.day_name()
        heatmap_data = df.pivot_table(index="month", columns="pollutant", values="avg_value", aggfunc="mean")
        fig_heatmap = px.imshow(
            heatmap_data, title="Heatmap temporal (mes x contaminante)",
            labels=dict(x="Contaminante", y="Mes", color="Concentracion"),
            color_continuous_scale="YlOrRd",
        )
        fig_box = px.box(
            df, x="pollutant", y="avg_value", color="pollutant",
            title="Distribucion por contaminante (boxplot)",
        )
        fig_hist = px.histogram(
            df[df["pollutant"] == pollutant] if pollutant else df,
            x="avg_value", color="pollutant" if not pollutant else None,
            title=f"Distribucion de {pollutant or 'contaminantes'}",
            nbins=30,
        )
        df["week"] = df["date"].dt.isocalendar().week
        weekly = df.groupby(["week", "pollutant"])["avg_value"].mean().reset_index()
        fig_weekly = px.line(
            weekly, x="week", y="avg_value", color="pollutant",
            title="Analisis semanal",
        )
    else:
        fig_heatmap = go.Figure().update_layout(title="Sin datos")
        fig_box = go.Figure().update_layout(title="Sin datos")
        fig_hist = go.Figure().update_layout(title="Sin datos")
        fig_weekly = go.Figure().update_layout(title="Sin datos")

    if pollution:
        pdf = pd.DataFrame(pollution)
        pdf["measured_at"] = pd.to_datetime(pdf["measured_at"])
        pdf["hour"] = pdf["measured_at"].dt.hour
        hourly = pdf.groupby("hour")["value"].mean().reset_index()
        fig_hourly = px.bar(
            hourly, x="hour", y="value",
            title="Analisis horario (datos diarios: hora 00:00)",
            labels={"hour": "Hora", "value": "Concentracion"},
        )
    else:
        fig_hourly = go.Figure().update_layout(title="Sin datos horarios")

    return fig_corr, fig_heatmap, fig_box, fig_hist, fig_weekly, fig_hourly
