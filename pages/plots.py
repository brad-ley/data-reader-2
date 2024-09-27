import dash
from dash import html

dash.register_page(__name__, path="/plots")

layout = html.Div(
    [
        html.H1("Files page"),
        html.Div("Choose .TDMS files to plot here."),
    ]
)
