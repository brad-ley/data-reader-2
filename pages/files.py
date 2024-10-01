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
from urllib.parse import urlparse
from pathlib import Path as P
import dash_bootstrap_components as dbc
import redis
import json
import requests
import pyrfc6266

# Initialize Redis client
# redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
redis_client = redis.Redis(host="0.0.0.0", port=6379, decode_responses=True)

register_page(
    __name__,
    path="/files",
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.SLATE],
)


layout = html.Div(
    [
        dcc.Input(
            id="url-path",
            placeholder="Copy and paste GDrive share url",
            type="text",
            # value="https://drive.google.com/file/d/10ubxTjhWxwmDM48LwRTqKs_W2eEA811m/view?usp=share_link",
            style={
                "background-color": "#272b30",
                "height": "60px",
                "width": "75%",
                "justifyContent": "center",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px 10px 0px 30px",
                "color": "#aaaaaa",
            },
        ),
        dcc.Input(
            id="log-path",
            placeholder="Copy and paste log folder",
            type="text",
            value="/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Misc./Magnet data",
            style={
                "background-color": "#272b30",
                "height": "60px",
                "width": "75%",
                "justifyContent": "center",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px 10px 0px 30px",
                "color": "#aaaaaa",
            },
        ),
        dcc.Upload(
            id="upload-file",
            children=html.Div(["Drag and drop or select .tdms file"]),
            # Allow multiple files to be uploaded
            multiple=True,
            style={
                "width": "75%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px 10px 0px 30px",
            },
        ),
        html.Div(id="output-file-upload"),
    ],
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
def delete_file(button_clicks, files):
    if len(button_clicks) < 1:
        raise PreventUpdate
    n_clicks = ctx.triggered[0]["value"]
    if not n_clicks:
        raise PreventUpdate
    button_id = ctx.triggered_id.file  # type: ignore
    del files[button_id]
    return files


@callback(
    Output("files", "data"),
    Output("upload-file", "children"),
    Output("url-path", "value"),
    Input("url-path", "value"),
    Input("upload-file", "filename"),
    Input("log-path", "value"),
    State("files", "data"),
    # prevent_initial_call=True,
)
def update_files_list(
    url_path,
    list_of_names,
    path_string,
    files,
):
    children = html.Div(["Drag and drop or select .tdms file"])
    if list_of_names is not None:
        for n in list_of_names:
            if P(n).suffix == ".tdms":
                files[n] = path_string
            else:
                children = html.Div(
                    ["Not a .tdms file"], style={"color": "indianred"}
                )

    if url_path:
        file_id = url_path.split("/")[-2]
        down_url = "https://drive.google.com/uc?export=download&id=" + file_id
        # NOTE the stream=True parameter
        r = requests.get(down_url, stream=True)
        remote_filename = pyrfc6266.requests_response_to_filename(r)
        local_filename = P(__name__).parent.joinpath("data", remote_filename)
        if P(local_filename).suffix == ".tdms":
            #     with open(local_filename, "wb") as f:
            #         for chunk in r.iter_content(chunk_size=1024):
            #             if chunk:  # filter out keep-alive new chunks
            #                 f.write(chunk)
            #                 # f.flush() commented by recommendation from J.F.Sebastian
            # files[remote_filename] = str(P(local_filename).parent)
            files[remote_filename] = down_url
        else:
            children = html.Div(
                ["Not a .tdms file"], style={"color": "indianred"}
            )

    send_files_to_reader(files)
    return files, children, ""


def send_files_to_reader(files):
    full_path_files = []
    for key in files:
        if P(files[key]).is_dir():
            full_path_files.append(str(P(files[key]).joinpath(P(key))))
        else:
            try:
                urlparse(files[key])
                full_path_files.append(files[key])
            except ValueError:  # not a valid url
                pass

    redis_client.hset(
        # name="files", key="files", value=json.dumps(full_path_files)
        name="files",
        key="dict",
        value=json.dumps(files),
    )


@callback(
    Output("output-file-upload", "children"),
    Input("files", "data"),
    # prevent_initial_call=True,
)
def update_buttons(files):
    if files:
        send_files_to_reader(files)
        buttons = []
        for file in files:
            buttons.append(parse_contents(file))
        return buttons
