import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html

from dashboards.api_client import get_data_quality, get_etl_status, get_health

REFRESH_MS = 30000


def layout():
    return dbc.Container([
        html.H2("Dashboard Operacional", className="mb-4"),
        dcc.Interval(id="op-interval", interval=REFRESH_MS, n_intervals=0),
        html.H4("Estado del Sistema", className="mb-3"),
        dbc.Row(id="op-status-cards", className="mb-4"),
        dbc.Row([
            dbc.Col([
                html.H4("Estado ETL", className="mb-3"),
                html.Div(id="op-etl-table"),
            ], md=6),
            dbc.Col([
                html.H4("Calidad de Datos", className="mb-3"),
                html.Div(id="op-quality-table"),
            ], md=6),
        ]),
        dbc.Row([
            dbc.Col(html.Div(id="op-alerts"), md=12),
        ], className="mt-3"),
    ], fluid=True)


def _status_badge(label: str, status: str) -> dbc.Card:
    css = "status-ok" if status in ("healthy", "connected", "success") else (
        "status-warn" if status in ("warning", "degraded") else "status-error"
    )
    return dbc.Card(dbc.CardBody([
        html.H5(label),
        html.P(status.upper(), className=css),
    ]), className="mb-3")


@callback(
    Output("op-status-cards", "children"),
    Output("op-etl-table", "children"),
    Output("op-quality-table", "children"),
    Output("op-alerts", "children"),
    Input("op-interval", "n_intervals"),
)
def update_operational(_):
    health = get_health()
    etl = get_etl_status()
    quality = get_data_quality()

    api_status = health.get("status", "error")
    db_status = health.get("database", "disconnected")
    etl_status = etl.get("status", "unknown")

    cards = [
        dbc.Col(_status_badge("Estado API", api_status), md=3),
        dbc.Col(_status_badge("PostgreSQL", db_status), md=3),
        dbc.Col(_status_badge("Último ETL", etl_status), md=3),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H5("Registros procesados"),
            html.P(str(quality.get("etl_records_processed", 0)), className="kpi-value"),
        ])), md=3),
    ]

    etl_table = dbc.Table([
        html.Thead(html.Tr([html.Th("Campo"), html.Th("Valor")])),
        html.Tbody([
            html.Tr([html.Td("Última ejecución"), html.Td(str(quality.get("etl_last_run", "N/A")))]),
            html.Tr([html.Td("Estado"), html.Td(etl_status)]),
            html.Tr([html.Td("Registros procesados"), html.Td(str(quality.get("etl_records_processed", 0)))]),
            html.Tr([html.Td("Duplicados eliminados"), html.Td(str(quality.get("duplicates_removed", 0)))]),
            html.Tr([html.Td("Errores ETL"), html.Td(str(quality.get("etl_errors", 0)))]),
            html.Tr([html.Td("Duración (s)"), html.Td(str(quality.get("etl_duration_seconds", "N/A")))]),
            html.Tr([html.Td("Última validación"), html.Td(str(quality.get("last_validation", "N/A")))]),
        ]),
    ], bordered=True, hover=True, className="chart-container")

    corrected = (
        quality.get("preliminary_records", 0)
        + quality.get("non_validated_records", 0)
    )
    quality_table = dbc.Table([
        html.Thead(html.Tr([html.Th("Métrica"), html.Th("Valor")])),
        html.Tbody([
            html.Tr([html.Td("Total registros"), html.Td(str(quality.get("total_records", 0)))]),
            html.Tr([html.Td("Registros validados"), html.Td(str(quality.get("valid_records", 0)))]),
            html.Tr([html.Td("Valores preliminares"), html.Td(str(quality.get("preliminary_records", 0)))]),
            html.Tr([html.Td("Valores no validados"), html.Td(str(quality.get("non_validated_records", 0)))]),
            html.Tr([html.Td("Valores corregidos/coalescidos"), html.Td(str(corrected))]),
            html.Tr([html.Td("Valores faltantes estimados"), html.Td(str(quality.get("missing_values_estimated", 0)))]),
            html.Tr([html.Td("Duplicados eliminados"), html.Td(str(quality.get("duplicates_removed", 0)))]),
        ]),
    ], bordered=True, hover=True, className="chart-container")

    alerts = []
    if api_status != "healthy":
        alerts.append(dbc.Alert("API no disponible o degradada", color="danger"))
    if db_status != "connected":
        alerts.append(dbc.Alert("PostgreSQL desconectado", color="danger"))
    if etl_status == "failed":
        alerts.append(dbc.Alert(f"ETL fallido: {etl.get('error_message', '')}", color="danger"))
    elif etl_status == "no_runs":
        alerts.append(dbc.Alert("No se han ejecutado pipelines ETL", color="warning"))
    elif quality.get("missing_values_estimated", 0) > 0:
        alerts.append(dbc.Alert(
            f"Se estiman {quality['missing_values_estimated']} valores faltantes en la última ejecución",
            color="warning",
        ))
    else:
        alerts.append(dbc.Alert("Sistema operando correctamente", color="success"))

    return cards, etl_table, quality_table, html.Div(alerts)
