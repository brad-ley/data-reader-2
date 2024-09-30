import dash
import pandas as pd
from dash import (
    ctx,
    dcc,
    html,
    Input,
    Output,
    State,
    callback,
    register_page,
    ALL,
)
import plotly.express as px

from pages.reader.data_read import redis_read
import dash_bootstrap_components as dbc


dash.register_page(
    __name__,
    path="/",
    external_stylesheets=[dbc.themes.SLATE],
)

# graph_height = "325px"
margin_vert = "0px"
margin = dict(l=40, r=40, t=20, b=20)


def make_fig():
    return px.line()


def update_fig(fig):
    colors = {
        'background': '#272b30',
        'text': '#AAAAAA'
    }
    fig.update_layout({"uirevision": "foo"}, overwrite=True)
    fig.update_layout(margin=margin)
    fig.update_layout({
        'plot_bgcolor': colors['background'],
        'paper_bgcolor': colors['background'],
        'font': {
            'color': colors['text']
        }})

    return fig


fig = update_fig(make_fig())


layout = html.Div(
    [
        html.Div(
            # [dcc.Graph(id="plotter", figure=fig, style={"height": graph_height})],
            [dcc.Graph(id="plotter", figure=fig)],
            style={
                "horizontal-align": "middle",
            },
        ),
    ],
)


@callback(
    Output("plotter", "figure"),
    Input("files", "data"),
)
def import_data(files):
    fig = make_fig()
    filegroups = redis_read()
    for groups in filegroups:  # type: ignore
        for group in groups:
            dat = pd.DataFrame()
            dat['time'] = group.time
            for channel in group.channels:
                dat[channel.name] = channel.data
                fig.add_scatter(x=dat['time'], y=dat[channel.name], mode='lines', name=channel.name)

    return update_fig(fig)
