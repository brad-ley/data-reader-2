import dash
import dash_daq as daq
import time
import pandas as pd
from dash import (
    dcc,
    html,
    Input,
    Output,
    callback,
)
from math import ceil
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
    colors = {"background": "#272b30", "text": "#AAAAAA"}
    fig.update_layout({"uirevision": "foo"}, overwrite=True)
    fig.update_layout(margin=margin)
    fig.update_layout(
        {
            "plot_bgcolor": colors["background"],
            "paper_bgcolor": colors["background"],
            "font": {"color": colors["text"]},
        }
    )

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
        dcc.Interval(
            id="interval-component",
            interval=1 * 1000,  # in milliseconds
            n_intervals=0,
        ),
        html.Div(
            [
                html.Div(
                    [
                        "Time window (min):",
                    ],
                    style={
                        "display": "inline-block",
                        "margin": "10px 0px 0px 30px",
                        "width": "200px",
                    },
                ),
                html.Div(
                    [
                        dcc.Slider(
                            0,
                            4,
                            # step=1,
                            id="x_axis_slider",
                            value=2,
                            marks={i: f"{10**(4-i)}" for i in range(5)},
                            tooltip={
                                "placement": "right",
                                "always_visible": True,
                                "transform": "expTime",
                            },
                            updatemode="drag",
                            persistence=True,
                        )
                    ],
                    style={
                        "width": "50%",
                        "display": "inline-block",
                        "margin": "0px 0px -25px -50px",
                    },
                ),
            ]
        ),
        html.Div(
            [
                dcc.Markdown(
                    r"Normalize LHe ($$\% \rightarrow \frac{\%}{100\%}$$): ",
                    mathjax=True,
                ),
            ],
            style={
                "display": "inline-block",
                "margin": "30px 0px 0px 30px",
                "width": "250px",
            },
        ),
        html.Div(
            [
                daq.BooleanSwitch(  # type: ignore
                    id="normalize", on=True, color="#aaaaaa", persistence=True
                ),
            ],
            style={
                "display": "inline-block",
                "margin": "0px 0px 0px -20px",
            },
        ),
    ],
)


@callback(
    Output("plotter", "figure"),
    Input("files", "data"),
    Input("x_axis_slider", "value"),
    Input("normalize", "on"),
    Input("interval-component", "n_intervals"),
)
def import_data(files, time_start, normalize, n):
    fig = make_fig()
    filegroups = redis_read()
    for groups in filegroups:  # type: ignore
        for group in groups:
            dat = pd.DataFrame()
            dat["time"] = pd.to_datetime(group.time, utc=True).tz_convert(
                "US/Pacific"
            )
            plot_start = dat["time"].iloc[-1] - pd.Timedelta(
                minutes=10 ** (4 - time_start)
            )
            for channel in group.channels:
                dat[channel.name] = channel.data
                if normalize and "LHe" in channel.name:
                    # dat[channel.name] /= dat[channel.name].max()
                    dat[channel.name] /= 100
                fig.add_scatter(
                    x=dat["time"][dat["time"] > plot_start],
                    y=dat[channel.name][dat["time"] > plot_start],
                    mode="lines+markers",
                    name=channel.name,
                )

    return update_fig(fig)
