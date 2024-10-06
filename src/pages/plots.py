import dash
import dash_daq as daq
import pandas as pd
from dash import dcc, html, Input, Output, State, callback, ctx, no_update, ALL

# from dash.exceptions import PreventUpdate
import plotly.express as px

from pages.reader.data_read import redis_read
from pages.utils.header import header
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


def add_switch(item):
    return html.Div(
        [
            # html.Div(
            #     [f"{item}:"],
            #     style={
            #         "display": "inline-block",
            #         # "margin": "10px 10px 15px 10px",
            #         # "width": "120px",
            #     },
            # ),
            # for item in items
            html.Div(
                [
                    daq.BooleanSwitch(  # type: ignore
                        id={
                            "type": "pattern-switch",
                            "plot": item,
                        },
                        on=True,
                        color="#aaaaaa",
                        persistence=True,
                        persistence_type="local",
                        label=item,
                    )
                ],
                style={
                    "display": "inline-block",
                    "margin": "0px -10px 0px 5px",
                    # "width": "100px",
                },
            ),
        ],
        style={
            "display": "inline-block",
            "margin": "0px 0px 15px 30px",
            # "width": "120px",
        },
    )


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
        header(__name__),
        html.Div(
            # [dcc.Graph(id="plotter", figure=fig, style={"height": graph_height})],
            [dcc.Graph(id="plotter", figure=fig)],
            style={
                "horizontal-align": "middle",
            },
        ),
        dcc.Interval(
            id="interval-component",
            interval=60 * 1000,  # in milliseconds
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
                        "margin": "10px 0px 10px 30px",
                        "width": "200px",
                    },
                ),
                html.Div(
                    [
                        dcc.Slider(
                            0,
                            5,
                            # step=1,
                            id="x_axis_slider",
                            value=1,
                            marks={i: f"1e+{(5-i)}" for i in range(6)},
                            tooltip={
                                "placement": "right",
                                "always_visible": True,
                                "transform": "expTime",
                            },
                            updatemode="mouseup",
                            persistence=True,
                        )
                    ],
                    style={
                        "width": "50%",
                        "display": "inline-block",
                        "margin": "0px 0px -15px -50px",
                    },
                ),
            ]
        ),
        html.Div(id="plots-on"),
        dcc.Store(id="plots-shown-dict", storage_type="memory"),
        dcc.Store(id="just-started", data=True, storage_type="memory"),
        # html.Div(
        #     [
        #         html.Div(
        #             [
        #                 dcc.Markdown(
        #                     r"Plot LHe only:",
        #                     mathjax=True,
        #                 ),
        #             ],
        #             style={
        #                 "display": "inline-block",
        #                 "margin": "20px 5px 0px 30px",
        #                 "width": "140px",
        #             },
        #         ),
        #         html.Div(
        #             [
        #                 daq.BooleanSwitch(  # type: ignore
        #                     id="lhe",
        #                     on=True,
        #                     color="#aaaaaa",
        #                     persistence=True,
        #                 ),
        #             ],
        #             style={
        #                 "display": "inline-block",
        #                 "margin": "15px 20px 0px -20px",
        #             },
        #         ),
        #         html.Div(
        #             [
        #                 dcc.Markdown(
        #                     r"Normalize LHe ($$\% \rightarrow \frac{\%}{100\%}$$): ",
        #                     mathjax=True,
        #                 ),
        #             ],
        #             style={
        #                 "display": "inline-block",
        #                 "margin": "20px 0px 0px 30px",
        #                 "width": "250px",
        #             },
        #         ),
        #         html.Div(
        #             [
        #                 daq.BooleanSwitch(  # type: ignore
        #                     id="normalize",
        #                     on=True,
        #                     color="#aaaaaa",
        #                     persistence=True,
        #                 ),
        #             ],
        #             style={
        #                 "display": "inline-block",
        #                 "margin": "15px 0px 0px -20px",
        #             },
        #         ),
        #     ],
        # ),
    ],
)


@callback(
    Output("plotter", "figure"),
    Input("plots-shown-dict", "data"),
    Input("x_axis_slider", "value"),
    # prevent_initial_call=True,
)
def show_data(plots_on, time_start):
    fig = make_fig()
    filegroups = redis_read(write=False)
    if plots_on and filegroups:
        for groups in filegroups:  # type: ignore
            for group in groups:
                dat = pd.DataFrame()
                dat["time"] = pd.to_datetime(group.time, utc=True).tz_convert(
                    "US/Pacific"
                )
                plot_start = dat["time"].iloc[-1] - pd.Timedelta(
                    minutes=10 ** (5 - time_start)
                )
                for channel in group.channels:
                    try:
                        if "Level (%)" in channel.name:
                            channel.name = "LHe (%)"
                        if plots_on:
                            if plots_on[channel.name]:
                                dat[channel.name] = channel.data
                                fig.add_scatter(
                                    x=dat["time"][dat["time"] > plot_start],
                                    y=dat[channel.name][
                                        dat["time"] > plot_start
                                    ],
                                    mode="lines+markers",
                                    name=channel.name,
                                )
                        else:
                            dat[channel.name] = channel.data
                            fig.add_scatter(
                                x=dat["time"][dat["time"] > plot_start],
                                y=dat[channel.name][dat["time"] > plot_start],
                                mode="lines+markers",
                                name=channel.name,
                            )

                    except ValueError:
                        raise Exception(f"{groups} file has issues.")
                        break

        return update_fig(fig)
    else:
        return no_update


# @callback(Output("navbar", "children"), Input("files", "data"))
# def init(_):
#     return [dbc.NavItem(dbc.NavLink("Files", href="/files"))]


@callback(
    Output("plots-shown-dict", "data"),
    Input("plots-on", "children"),
)
def get_switch_values(allplots):
    plots_on = {}
    if allplots:
        plots_on = dict(
            [
                (
                    ii["props"]["children"][0]["props"]["children"][0][
                        "props"
                    ]["id"]["plot"],
                    ii["props"]["children"][0]["props"]["children"][0][
                        "props"
                    ]["on"],
                )
                for ii in allplots[0]["props"]["children"]
            ],
        )

    return plots_on
    # return plots_on


@callback(
    # Output("plotter", "figure"),
    # Output("just-started", "data"),
    Output("plots-on", "children"),
    Input({"type": "pattern-switch", "plot": ALL}, "on"),
    Input("interval-component", "n_intervals"),
    Input("x_axis_slider", "value"),
    # Input("just-started", "data"),
    State("files", "data"),
    State("plots-on", "children"),
)
def make_switches(plot_switched, n, time_start, files, allplots):
    switches = set()
    if ctx.triggered_id == "interval-component":
        filegroups = redis_read(write=True)
        # filegroups = redis_read(write=False)
    else:
        filegroups = redis_read(write=False)

    if filegroups:
        for groups in filegroups:  # type: ignore
            for group in groups:
                for channel in group.channels:
                    try:
                        if "Level (%)" in channel.name:
                            channel.name = "LHe (%)"
                        switches.add(channel.name)
                    except ValueError:
                        raise Exception(f"{groups} file has issues.")
                        break

        switches_out = (
            html.Div(
                [add_switch(switch) for switch in sorted(list(switches))],
                style={
                    "display": "inline-block",
                },
            ),
        )
        return switches_out

    return no_update
