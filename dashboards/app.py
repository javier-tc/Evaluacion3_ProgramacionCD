import os

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html

from dashboards.pages import analytical, executive, operational

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
    title="Calidad del Aire - Santiago",
)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Ejecutivo", href="/", active="exact")),
        dbc.NavItem(dbc.NavLink("Analitico", href="/analitico", active="exact")),
        dbc.NavItem(dbc.NavLink("Operacional", href="/operacional", active="exact")),
    ],
    brand="Monitoreo Calidad del Aire - Santiago",
    color="primary",
    dark=True,
    className="mb-4",
)

app.layout = html.Div([
    navbar,
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content"),
])


@callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/analitico":
        return analytical.layout()
    if pathname == "/operacional":
        return operational.layout()
    return executive.layout()


if __name__ == "__main__":
    host = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    port = int(os.getenv("DASHBOARD_PORT", "8050"))
    app.run_server(host=host, port=port, debug=False)
