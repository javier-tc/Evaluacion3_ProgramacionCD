import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html

from dashboards.api_client import get_correlations
from dashboards.utils.constants import HYPOTHESIS_PAIRS
from dashboards.utils.transforms import get_correlation_value

POLLUTANT_INFO = [
    {
        "title": "CO (Monóxido de Carbono)",
        "body": (
            "Fuente: vehículos y combustión incompleta. "
            "Reduce la capacidad de la sangre para transportar oxígeno. "
            "Relación meteorológica esperada: más viento dispersa CO; "
            "inversiones térmicas lo acumulan."
        ),
    },
    {
        "title": "MP2.5 (Material Particulado fino)",
        "body": (
            "Fuente: vehículos, calefacción e industria. "
            "Contaminante más peligroso para la salud respiratoria. "
            "Relación meteorológica: la lluvia lo reduce; el viento dispersa."
        ),
    },
    {
        "title": "MP10 (Material Particulado)",
        "body": (
            "Fuente: polvo, construcción y tránsito. "
            "Afecta vías respiratorias superiores. "
            "Relación meteorológica: la lluvia reduce significativamente su concentración."
        ),
    },
    {
        "title": "NO2 (Dióxido de Nitrógeno)",
        "body": (
            "Fuente: vehículos y combustión industrial. "
            "Precursor del ozono troposférico. "
            "Relación meteorológica: viento y lluvia lo reducen; horarios punta lo aumentan."
        ),
    },
    {
        "title": "O3 (Ozono troposférico)",
        "body": (
            "No se emite directamente; se forma por reacciones fotoquímicas "
            "entre NOx, COV y radiación solar. "
            "Relación meteorológica: mayor temperatura y radiación aumentan O3."
        ),
    },
]

HYPOTHESES = [
    {
        "title": "Hipótesis 1: Temperatura y Ozono",
        "text": "Mayor temperatura produce mayor concentración de ozono (O3).",
    },
    {
        "title": "Hipótesis 2: Lluvia y Material Particulado",
        "text": "La lluvia reduce las concentraciones de MP2.5 y MP10.",
    },
    {
        "title": "Hipótesis 3: Viento y Dispersión",
        "text": "El viento dispersa contaminantes como CO y NO2.",
    },
    {
        "title": "Hipótesis 4: Patrones Horarios de Tráfico",
        "text": "CO y NO2 presentan patrones horarios asociados al tráfico vehicular.",
    },
]


def layout():
    return dbc.Container([
        html.H2("Presentación — Calidad del Aire en Santiago", className="mb-3"),
        dbc.Alert(
            "Pregunta de investigación: ¿Cómo afectan las condiciones meteorológicas "
            "a la calidad del aire en Santiago?",
            color="primary",
            className="mb-4",
        ),
        html.H4("Hipótesis", className="mb-3"),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H5(h["title"]),
                html.P(h["text"]),
            ])), md=6, className="mb-3")
            for h in HYPOTHESES
        ]),
        html.H4("Resumen por Contaminante", className="mt-3 mb-3"),
        dbc.Accordion([
            dbc.AccordionItem(p["body"], title=p["title"])
            for p in POLLUTANT_INFO
        ], start_collapsed=True, className="mb-4"),
        html.H4("Hallazgos Dinámicos (Correlaciones)", className="mb-3"),
        dcc.Interval(id="pres-interval", interval=60000, n_intervals=0),
        html.Div(id="pres-findings", className="mb-4"),
        html.H4("Navegación", className="mb-3"),
        dbc.Row([
            dbc.Col(dbc.Button("Dashboard Ejecutivo", href="/ejecutivo", color="primary", external_link=True), md=3),
            dbc.Col(dbc.Button("Dashboard Analítico", href="/analitico", color="secondary", external_link=True), md=3),
            dbc.Col(dbc.Button("Dashboard Operacional", href="/operacional", color="info", external_link=True), md=3),
        ]),
    ], fluid=True)


def _finding_badge(label: str, corr: float | None, expected: str) -> dbc.Alert:
    if corr is None:
        return dbc.Alert(f"{label}: sin datos", color="secondary")
    if expected == "positive":
        ok = corr > 0
        detail = f"r = {corr:.3f} (esperado: positivo)"
    else:
        ok = corr < 0
        detail = f"r = {corr:.3f} (esperado: negativo)"
    color = "success" if ok else "warning"
    status = "Consistente con hipótesis" if ok else "Revisar / no concluyente"
    return dbc.Alert([html.Strong(label), html.Br(), detail, html.Br(), status], color=color)


@callback(Output("pres-findings", "children"), Input("pres-interval", "n_intervals"))
def update_findings(_):
    corrs = get_correlations()
    badges = []
    for pair in HYPOTHESIS_PAIRS:
        val = get_correlation_value(corrs, pair["var_x"], pair["var_y"])
        badges.append(dbc.Col(
            _finding_badge(pair["label"], val, pair["expected"]),
            md=4, className="mb-2",
        ))
    return dbc.Row(badges)
