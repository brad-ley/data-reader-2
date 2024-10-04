import dash
import dash_daq as daq
import pandas as pd
from dash import dcc, html, Input, Output, State, callback, ctx, no_update

# from dash.exceptions import PreventUpdate
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
                            updatemode="drag",
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
        html.Div(id="plots"),
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
    Output("just-started", "data"),
    Input("files", "data"),
    Input("x_axis_slider", "value"),
    Input("normalize", "on"),
    Input("lhe", "on"),
    Input("interval-component", "n_intervals"),
    State("just-started", "data"),
    # blocking=True,
)
def import_data(files, time_start, normalize, lhe, n, just_started):
    fig = make_fig()
    # if ctx.triggered_id == "interval-component" or just_started:
    if ctx.triggered_id == "interval-component":
        filegroups = redis_read(write=True)
        # just_started = False
    else:
        filegroups = redis_read(write=False)

    if filegroups:
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
                        dat[channel.name] = channel.data
                        if normalize and ("LHe (%)" in channel.name):
                            # dat[channel.name] /= dat[channel.name].max()
                            dat[channel.name] /= 100
                            # fig = px.line(
                            #     x=dat["time"][dat["time"] > plot_start],
                            #     y=dat[channel.name][dat["time"] > plot_start],
                            # )
                        if lhe:
                            if "LHe (%)" in channel.name:
                                fig.add_scatter(
                                    x=dat["time"][dat["time"] > plot_start],
                                    y=dat[channel.name][
                                        dat["time"] > plot_start
                                    ],
                                    mode="lines+markers",
                                    name=channel.name,
                                )
                        else:
                            fig.add_scatter(
                                x=dat["time"][dat["time"] > plot_start],
                                y=dat[channel.name][dat["time"] > plot_start],
                                mode="lines+markers",
                                name=channel.name,
                            )

                    except ValueError:
                        raise Exception(f"{groups} file has issues.")
                        break

        # return fig
        return update_fig(fig), just_started
    else:
        return no_update, no_update
