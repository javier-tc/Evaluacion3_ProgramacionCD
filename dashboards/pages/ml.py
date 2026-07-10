import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dash_table, dcc, html

from dashboards.api_client import PLOTLY_CONFIG, get_model_metrics

MODEL_DEFINITIONS = {
    "linear_regression": {
        "title": "Regresión Lineal",
        "task": "Regresión",
        "body": (
            "Estima una relación lineal entre variables meteorológicas y el promedio "
            "diario de MP2.5. Es interpretable y rápido, pero asume relaciones "
            "aproximadamente lineales entre clima y contaminación."
        ),
    },
    "random_forest_regressor": {
        "title": "Random Forest (Regresión)",
        "task": "Regresión",
        "body": (
            "Combina múltiples árboles de decisión para capturar relaciones no lineales "
            "e interacciones entre variables. Suele ser robusto ante outliers y no exige "
            "supuestos fuertes sobre la forma de la relación."
        ),
    },
    "gradient_boosting_regressor": {
        "title": "Gradient Boosting (Regresión)",
        "task": "Regresión",
        "body": (
            "Construye árboles de forma secuencial corrigiendo errores previos. "
            "Puede alcanzar alta precisión predictiva, aunque es más sensible al "
            "sobreajuste si los datos son limitados."
        ),
    },
    "logistic_regression": {
        "title": "Regresión Logística",
        "task": "Clasificación",
        "body": (
            "Clasifica cada día en normal, moderado o alerta según umbrales de MP2.5. "
            "Modelo lineal probabilístico, útil como baseline interpretable para "
            "decisiones de alerta temprana."
        ),
    },
    "random_forest_classifier": {
        "title": "Random Forest (Clasificación)",
        "task": "Clasificación",
        "body": (
            "Clasifica niveles de alerta usando votación entre árboles. Captura "
            "patrones no lineales entre clima y categorías de riesgo sin depender "
            "de relaciones lineales."
        ),
    },
    "svc_classifier": {
        "title": "SVC (Máquinas de Vectores de Soporte)",
        "task": "Clasificación",
        "body": (
            "Separa clases buscando fronteras de decisión óptimas en un espacio "
            "transformado. Puede funcionar bien con pocas clases, pero es menos "
            "interpretable que modelos lineales o basados en árboles."
        ),
    },
}

METRIC_DEFINITIONS = [
    {
        "name": "MAE",
        "key": "mae",
        "task": "Regresión",
        "interpretation": (
            "Error Absoluto Medio. Indica cuántos μg/m³ se desvía en promedio la "
            "predicción del valor real de MP2.5. Mientras más bajo, mejor."
        ),
        "guide": "Ejemplo: MAE = 5 significa que, en promedio, el modelo se equivoca por 5 μg/m³.",
    },
    {
        "name": "RMSE",
        "key": "rmse",
        "task": "Regresión",
        "interpretation": (
            "Raíz del Error Cuadrático Medio. Penaliza más los errores grandes. "
            "También se expresa en μg/m³ y debe ser lo más bajo posible."
        ),
        "guide": "Si RMSE es mucho mayor que MAE, hay días con errores de predicción muy altos.",
    },
    {
        "name": "R²",
        "key": "r2",
        "task": "Regresión",
        "interpretation": (
            "Coeficiente de determinación. Mide qué proporción de la variabilidad "
            "de MP2.5 explica el modelo usando clima y estacionalidad."
        ),
        "guide": "Valores cercanos a 1 indican buen ajuste; cercanos a 0, poco poder explicativo.",
    },
    {
        "name": "Accuracy",
        "key": "accuracy",
        "task": "Clasificación",
        "interpretation": (
            "Proporción de días clasificados correctamente en normal, moderado o alerta."
        ),
        "guide": "Útil cuando las clases están relativamente balanceadas; no basta por sí sola.",
    },
    {
        "name": "F1 macro",
        "key": "f1_macro",
        "task": "Clasificación",
        "interpretation": (
            "Promedio del F1 entre clases, balanceando precisión y recall. "
            "Es la métrica principal para comparar modelos de alerta."
        ),
        "guide": "Valores más altos indican mejor desempeño global; idealmente por encima de 0.70.",
    },
    {
        "name": "CV mean / CV std",
        "key": "cv_mean",
        "task": "Ambas",
        "interpretation": (
            "Promedio y desviación estándar de validación cruzada. Miden estabilidad "
            "del modelo en distintos subconjuntos de datos."
        ),
        "guide": "Un CV mean alto con CV std bajo sugiere un modelo consistente y confiable.",
    },
]


def _model_cards():
    regression = [
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6(info["title"], className="card-title"),
            html.Small(info["task"], className="text-muted"),
            html.P(info["body"], className="mb-0 mt-2"),
        ])), md=4, className="mb-3")
        for key, info in MODEL_DEFINITIONS.items()
        if info["task"] == "Regresión"
    ]
    classification = [
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6(info["title"], className="card-title"),
            html.Small(info["task"], className="text-muted"),
            html.P(info["body"], className="mb-0 mt-2"),
        ])), md=4, className="mb-3")
        for key, info in MODEL_DEFINITIONS.items()
        if info["task"] == "Clasificación"
    ]
    return [
        html.H4("Definición de modelos", className="mb-3"),
        html.P(
            "Antes de comparar resultados, conviene entender qué hace cada algoritmo "
            "y qué tipo de problema resuelve.",
            className="text-muted",
        ),
        html.H5("Modelos de regresión", className="mb-3"),
        dbc.Row(regression, className="mb-2"),
        html.H5("Modelos de clasificación", className="mb-3"),
        dbc.Row(classification, className="mb-4"),
    ]


def _metric_cards():
    cards = []
    for metric in METRIC_DEFINITIONS:
        cards.append(dbc.Col(dbc.Card(dbc.CardBody([
            html.H6(metric["name"], className="card-title"),
            html.Small(metric["task"], className="text-muted"),
            html.P(metric["interpretation"], className="mb-2"),
            html.P(html.Em(metric["guide"]), className="mb-0 small"),
        ])), md=6, lg=4, className="mb-3"))
    return [
        html.H4("Interpretación de métricas", className="mb-3"),
        html.P(
            "Estas métricas permiten evaluar si un modelo predice bien MP2.5 o "
            "clasifica correctamente los niveles de alerta.",
            className="text-muted",
        ),
        dbc.Row(cards, className="mb-4"),
    ]


def layout():
    return dbc.Container([
        html.H2("Modelos Predictivos", className="mb-4"),
        dbc.Alert(
            "Comparación de modelos supervisados para predecir MP2.5 diario "
            "y clasificar niveles de alerta usando variables meteorológicas.",
            color="primary",
            className="mb-4",
        ),
        *_model_cards(),
        *_metric_cards(),
        html.H4("Comparación de desempeño", className="mb-3"),
        dbc.Row([
            dbc.Col(dbc.Button("Actualizar métricas", id="ml-refresh", color="primary"), md=3),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="ml-metrics-chart", config=PLOTLY_CONFIG), md=7),
            dbc.Col(html.Div(id="ml-summary"), md=5),
        ]),
        html.H4("Detalle de métricas", className="mt-4 mb-3"),
        dash_table.DataTable(
            id="ml-metrics-table",
            page_size=12,
            sort_action="native",
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "8px"},
            style_header={"fontWeight": "bold"},
        ),
    ], fluid=True)


@callback(
    Output("ml-metrics-chart", "figure"),
    Output("ml-metrics-table", "data"),
    Output("ml-metrics-table", "columns"),
    Output("ml-summary", "children"),
    Input("ml-refresh", "n_clicks"),
)
def update_ml(_):
    metrics = get_model_metrics()
    if not metrics:
        fig = go.Figure().update_layout(title="Sin métricas de modelos entrenados")
        return fig, [], [], dbc.Alert(
            "Ejecuta python scripts/run_training.py o levanta Docker Compose "
            "para generar artefactos y métricas.",
            color="warning",
        )

    df = pd.DataFrame(metrics)
    df["label"] = df["task_type"] + " - " + df["model_name"]
    chart_df = df[df["metric_name"].isin(["mae", "r2", "accuracy", "f1_macro"])].copy()
    fig = px.bar(
        chart_df,
        x="label",
        y="metric_value",
        color="metric_name",
        barmode="group",
        title="Comparación de desempeño por modelo",
        labels={"label": "Modelo", "metric_value": "Valor", "metric_name": "Métrica"},
    )
    fig.update_layout(xaxis_tickangle=-25)

    best_reg = _best_metric(df, "regression", "mae", ascending=True)
    best_cls = _best_metric(df, "classification", "f1_macro", ascending=False)
    cards = [
        dbc.Alert(
            "En regresión, prioriza MAE y RMSE bajos y R² alto. "
            "En clasificación, prioriza F1 macro y accuracy altos.",
            color="info",
            className="mb-3",
        ),
    ]
    if best_reg is not None:
        cards.append(_metric_card(
            "Mejor regresión",
            best_reg,
            "MAE más bajo · indica menor error promedio en μg/m³",
        ))
    if best_cls is not None:
        cards.append(_metric_card(
            "Mejor clasificación",
            best_cls,
            "F1 macro más alto · mejor balance entre precisión y recall",
        ))

    columns = [{"name": col, "id": col} for col in [
        "task_type",
        "model_name",
        "metric_name",
        "metric_value",
        "trained_at",
    ]]
    data = df[["task_type", "model_name", "metric_name", "metric_value", "trained_at"]].to_dict("records")
    return fig, data, columns, cards


def _best_metric(df: pd.DataFrame, task: str, metric: str, ascending: bool):
    subset = df[(df["task_type"] == task) & (df["metric_name"] == metric)]
    if subset.empty:
        return None
    return subset.sort_values("metric_value", ascending=ascending).iloc[0]


def _metric_card(title: str, row, subtitle: str):
    return dbc.Card(dbc.CardBody([
        html.H5(title),
        html.H3(f"{row['metric_value']:.3f}"),
        html.P(f"{row['model_name']} · {subtitle}", className="mb-0"),
    ]), className="mb-3")

