import dash_bootstrap_components as dbc
from dash import html

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
        "title": "Hipótesis 4: Patrones Semanales de Tráfico",
        "text": "CO y NO2 presentan mayor concentración en días laborables que en fin de semana.",
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
        html.H4("Navegación", className="mb-3"),
        dbc.Row([
            dbc.Col(dbc.Button("Dashboard Ejecutivo", href="/ejecutivo", color="primary", external_link=True), md=3),
            dbc.Col(dbc.Button("Dashboard Analítico", href="/analitico", color="secondary", external_link=True), md=3),
            dbc.Col(dbc.Button("Dashboard Operacional", href="/operacional", color="info", external_link=True), md=3),
        ]),
    ], fluid=True)
