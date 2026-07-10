from datetime import date

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from dashboards.api_client import (
    PLOTLY_CONFIG,
    get_correlations,
    get_daily,
    get_weather,
)
from dashboards.utils.constants import POLLUTANTS
from dashboards.utils.transforms import (
    WEEKDAY_ORDER,
    assign_season,
    assign_weekday,
    build_correlation_matrix,
    display_pollutant,
    display_unit,
    merge_pollution_weather,
)


def layout():
    return dbc.Container([
        html.H2("Dashboard Analítico", className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.DatePickerRange(
                id="anal-date-range",
                start_date=date(2025, 6, 1),
                end_date=date(2026, 6, 1),
                display_format="DD/MM/YYYY",
            ), md=8),
            dbc.Col(dcc.Dropdown(
                id="anal-box-pollutant",
                options=[{"label": display_pollutant(p), "value": p} for p in POLLUTANTS],
                value="MP25",
            ), md=4),
        ], className="mb-4"),
        html.H4("Correlaciones", className="mb-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="anal-corr", config=PLOTLY_CONFIG), md=12),
        ]),
        html.H4("Correlación Clima-Contaminación", className="mt-4 mb-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="anal-scatter-temp-o3", config=PLOTLY_CONFIG), md=4),
            dbc.Col(dcc.Graph(id="anal-scatter-wind-mp25", config=PLOTLY_CONFIG), md=4),
            dbc.Col(dcc.Graph(id="anal-scatter-rain-mp10", config=PLOTLY_CONFIG), md=4),
        ]),
        html.H4("Patrones Estacionales y Distribución", className="mt-4 mb-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="anal-seasonal", config=PLOTLY_CONFIG), md=6),
            dbc.Col(dcc.Graph(id="anal-boxplot", config=PLOTLY_CONFIG), md=6),
        ], className="mt-3"),
        html.H4("Análisis Semanal", className="mt-4 mb-3"),
        dbc.Alert(
            "Con datos diarios se analizan patrones por día de la semana "
            "(días laborables vs fin de semana). Especialmente relevante para "
            "CO y NO2, asociados al tráfico vehicular.",
            color="info",
        ),
        dbc.Row([
            dbc.Col(dcc.Graph(id="anal-weekly", config=PLOTLY_CONFIG), md=12),
        ], className="mt-3"),
    ], fluid=True)


def _empty_fig(title: str) -> go.Figure:
    return go.Figure().update_layout(title=title)


def _scatter(merged: pd.DataFrame, x_col: str, y_col: str, x_label: str, y_label: str, title: str):
    if merged.empty or x_col not in merged.columns or y_col not in merged.columns:
        return _empty_fig(f"Sin datos: {title}")
    sub = merged[[x_col, y_col]].dropna()
    if sub.empty:
        return _empty_fig(f"Sin datos: {title}")
    return px.scatter(
        sub, x=x_col, y=y_col, trendline="ols",
        title=title,
        labels={x_col: x_label, y_col: y_label},
    )


@callback(
    Output("anal-corr", "figure"),
    Output("anal-scatter-temp-o3", "figure"),
    Output("anal-scatter-wind-mp25", "figure"),
    Output("anal-scatter-rain-mp10", "figure"),
    Output("anal-seasonal", "figure"),
    Output("anal-boxplot", "figure"),
    Output("anal-weekly", "figure"),
    Input("anal-date-range", "start_date"),
    Input("anal-date-range", "end_date"),
    Input("anal-box-pollutant", "value"),
)
def update_analytical(start_date, end_date, box_pollutant):
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None

    corrs = get_correlations()
    daily = get_daily(None, start, end)
    weather = get_weather(start, end)
    merged = merge_pollution_weather(daily, weather)

    corr_matrix = build_correlation_matrix(corrs)
    if not corr_matrix.empty:
        fig_corr = px.imshow(
            corr_matrix.astype(float),
            title="Matriz de correlación (contaminantes y clima)",
            color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1,
            aspect="auto",
        )
    else:
        fig_corr = _empty_fig("Sin datos de correlación")

    fig_temp_o3 = _scatter(merged, "temp_max", "O3", "Temperatura máx. (°C)", "O3 (ppb)", "Temperatura vs O3")
    fig_wind_mp25 = _scatter(
        merged, "wind_speed_max", "MP25",
        "Viento máx. (m/s)", "MP2.5 (μg/m³)", "Viento vs MP2.5",
    )
    fig_rain_mp10 = _scatter(
        merged, "rain_sum", "MP10",
        "Lluvia (mm)", "MP10 (μg/m³)", "Lluvia vs MP10",
    )

    if daily:
        df = pd.DataFrame(daily)
        df["date"] = pd.to_datetime(df["date"])
        df["season"] = df["date"].apply(lambda d: assign_season(d.date()))
        seasonal = df.groupby(["season", "pollutant"])["avg_value"].mean().reset_index()
        seasonal["pollutant_label"] = seasonal["pollutant"].map(display_pollutant)
        season_order = ["Verano", "Otoño", "Invierno", "Primavera"]
        fig_seasonal = px.bar(
            seasonal, x="season", y="avg_value", color="pollutant_label",
            barmode="group",
            category_orders={"season": season_order},
            title="Promedio por estación del año (valores reales)",
            labels={"avg_value": "Concentración promedio", "season": "Estación"},
        )

        box_df = df[df["pollutant"] == box_pollutant] if box_pollutant else df
        unit = box_df["unit"].iloc[0] if not box_df.empty else ""
        fig_box = px.box(
            box_df, y="avg_value",
            title=f"Distribución de {display_pollutant(box_pollutant or '')} (valores reales)",
            labels={"avg_value": f"Concentración ({display_unit(unit)})"},
        )

        df["weekday"] = df["date"].apply(lambda d: assign_weekday(d.date()))
        weekly = df.groupby(["weekday", "pollutant"])["avg_value"].mean().reset_index()
        weekly["pollutant_label"] = weekly["pollutant"].map(display_pollutant)
        fig_weekly = px.bar(
            weekly,
            x="weekday",
            y="avg_value",
            color="pollutant_label",
            barmode="group",
            category_orders={"weekday": WEEKDAY_ORDER},
            title="Promedio por día de la semana (valores reales)",
            labels={
                "avg_value": "Concentración promedio diaria",
                "weekday": "Día de la semana",
                "pollutant_label": "Contaminante",
            },
        )
    else:
        fig_seasonal = _empty_fig("Sin datos estacionales")
        fig_box = _empty_fig("Sin datos para boxplot")
        fig_weekly = _empty_fig("Sin datos semanales")

    return fig_corr, fig_temp_o3, fig_wind_mp25, fig_rain_mp10, fig_seasonal, fig_box, fig_weekly
