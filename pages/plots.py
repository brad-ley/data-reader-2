import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(
    __name__,
    path="/plots",
    external_stylesheets=[dbc.themes.SLATE],
)

layout = html.Div(
    [
        html.H1("Files page"),
        html.Div("Choose .TDMS files to plot here."),
    ]
)
