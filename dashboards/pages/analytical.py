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
    get_pollution,
    get_weather,
)
from dashboards.utils.constants import POLLUTANTS
from dashboards.utils.transforms import (
    assign_season,
    build_correlation_matrix,
    display_pollutant,
    display_unit,
    merge_pollution_weather,
)

HOURLY_POLLUTANTS = ["CO", "NO2"]


def layout():
    return dbc.Container([
        html.H2("Dashboard Analítico", className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.DatePickerRange(
                id="anal-date-range",
                start_date=date(2025, 6, 1),
                end_date=date(2026, 6, 1),
                display_format="DD/MM/YYYY",
            ), md=6),
            dbc.Col(dcc.Dropdown(
                id="anal-box-pollutant",
                options=[{"label": display_pollutant(p), "value": p} for p in POLLUTANTS],
                value="MP25",
            ), md=3),
            dbc.Col(dcc.Dropdown(
                id="anal-hourly-pollutant",
                options=[{"label": display_pollutant(p), "value": p} for p in HOURLY_POLLUTANTS],
                value="CO",
            ), md=3),
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
        html.H4("Análisis Horario", className="mt-4 mb-3"),
        dbc.Alert(
            "Los datos fuente son agregaciones diarias. El análisis horario tiene resolución "
            "limitada (registro único a las 00:00). La hipótesis de patrones de tráfico debe "
            "interpretarse con esta restricción.",
            color="warning",
        ),
        dbc.Row([
            dbc.Col(dcc.Graph(id="anal-hourly", config=PLOTLY_CONFIG), md=12),
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
    Output("anal-hourly", "figure"),
    Input("anal-date-range", "start_date"),
    Input("anal-date-range", "end_date"),
    Input("anal-box-pollutant", "value"),
    Input("anal-hourly-pollutant", "value"),
)
def update_analytical(start_date, end_date, box_pollutant, hourly_pollutant):
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None

    corrs = get_correlations()
    daily = get_daily(None, start, end)
    weather = get_weather(start, end)
    pollution = get_pollution(None, start, end)
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
    else:
        fig_seasonal = _empty_fig("Sin datos estacionales")
        fig_box = _empty_fig("Sin datos para boxplot")

    if pollution and hourly_pollutant:
        pdf = pd.DataFrame(pollution)
        pdf = pdf[pdf["pollutant"] == hourly_pollutant]
        pdf["measured_at"] = pd.to_datetime(pdf["measured_at"])
        pdf["hour"] = pdf["measured_at"].dt.hour
        hourly = pdf.groupby("hour")["value"].mean().reset_index()
        unit = pdf["unit"].iloc[0] if not pdf.empty else ""
        fig_hourly = px.line(
            hourly, x="hour", y="value", markers=True,
            title=f"Promedio horario de {display_pollutant(hourly_pollutant)}",
            labels={
                "hour": "Hora del día",
                "value": f"Concentración ({display_unit(unit)})",
            },
        )
        fig_hourly.update_xaxes(dtick=1, range=[0, 23])
    else:
        fig_hourly = _empty_fig("Sin datos horarios")

    return fig_corr, fig_temp_o3, fig_wind_mp25, fig_rain_mp10, fig_seasonal, fig_box, fig_hourly
