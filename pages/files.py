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
from dash.exceptions import PreventUpdate
from pathlib import Path as P
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

register_page(
    __name__,
    path="/",
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.SLATE],
)

layout = html.Div(
    [
        dcc.Upload(
            id="upload-file",
            children=html.Div(
                ["Drag and drop or ", html.A("select .tdms file")]
            ),
            style={
                "width": "30%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px 10px 0px 30px",
            },
            # Allow multiple files to be uploaded
            multiple=True,
        ),
        html.Div(id="output-file-upload"),
    ]
)


def parse_contents(file):
    return html.Div(
        [
            html.Div(
                [
                    html.Button(
                        "Remove",
                        id={
                            "type": "pattern-matched-button",
                            "file": P(file).name,
                            # "index": 1,
                        },
                    )  # for file in files
                ],
                style={
                    "display": "inline-block",
                    "margin": "10px 10px 0px 30px",
                    "width": "50px",
                },
            ),
            html.Div(
                [
                    html.H5(P(file).name)  # for file in files
                ],
                style={
                    "display": "inline-block",
                    "margin": "10px 0px 0px 30px",
                    "width": "350px",
                },
            ),
        ]
    )


@callback(
    Output("files", "data", allow_duplicate=True),
    Input({"type": "pattern-matched-button", "file": ALL}, "n_clicks"),
    State("files", "data"),
    prevent_initial_call=True,
)
def display_output(button_clicks, files):
    if len(button_clicks) < 1:
        raise PreventUpdate
    n_clicks = ctx.triggered[0]["value"]
    if not n_clicks:
        raise PreventUpdate
    # print([key for key in files])
    button_id = ctx.triggered_id.file  # type: ignore
    print("->", button_id, n_clicks)
    del files[button_id]
    return files


@callback(
    Output("files", "data"),
    Output("upload-file", "children"),
    Input("upload-file", "contents"),
    State("upload-file", "filename"),
    State("upload-file", "last_modified"),
    State("files", "data"),
    # prevent_initial_call=True,
)
def update_files_list(list_of_contents, list_of_names, list_of_dates, files):
    children = html.Div(["Drag and drop or ", html.A("select .tdms file")])
    if list_of_contents is not None:
        for c, n, d in zip(list_of_contents, list_of_names, list_of_dates):
            if P(n).suffix == ".tdms":
                files[n] = c
            else:
                children = html.Div(
                    ["Not a .tdms file"], style={"color": "indianred"}
                )

    return files, children


@callback(
    Output("output-file-upload", "children"),
    Input("files", "data"),
    # prevent_initial_call=True,
)
def update_buttons(files):
    if files:
        buttons = []
        for file in files:
            print(file)
            buttons.append(parse_contents(file))
        return buttons
