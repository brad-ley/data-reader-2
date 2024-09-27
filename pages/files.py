from dash import dcc, html, Input, Output, State, callback, register_page
from pathlib import Path as P
import plotly.express as px
import pandas as pd

register_page(
    __name__,
    path="/",
    suppress_callback_exceptions=True,
)

layout = html.Div(
    [
        dcc.Upload(
            id="upload-file",
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
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
                    html.H5(P(file).name),
                ],
                style={
                    "display": "inline-block",
                    "margin": "10px 0px 0px 30px",
                    "width": "250px",
                },
            ),
            html.Div(
                [
                    html.Button("Clear", id="clear" + P(file).name),
                ],
                style={
                    "display": "inline-block",
                    "margin": "10px 0px 0px 30px",
                    "width": "100px",
                },
            ),
        ]
    )


@callback(
    Output("files", "data"),
    Input("upload-file", "contents"),
    State("upload-file", "filename"),
    State("upload-file", "last_modified"),
    State("files", "data"),
    # prevent_initial_call=True,
)
def update_files_list(list_of_contents, list_of_names, list_of_dates, files):
    if list_of_contents is not None:
        for c, n, d in zip(list_of_contents, list_of_names, list_of_dates):
            files[n] = c
    return files


@callback(
    Output("output-file-upload", "children"),
    Input("files", "data"),
    # prevent_initial_call=True,
)
def update_buttons(files):
    print(files)
    if files:
        for file in files:
            return parse_contents(file)
