import dash
import redis
from dash import html, dcc
import dash_bootstrap_components as dbc

# redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
redis_client = redis.Redis(host="0.0.0.0", port=6379, decode_responses=True)

# external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
graph_height = "325px"
margin_vert = "0px"
margin = dict(l=20, r=20, t=20, b=20)

app = dash.Dash(
    __name__,
    use_pages=True,
    # prevent_initial_callbacks=True,
    external_stylesheets=[dbc.themes.SLATE],  # type: ignore
    suppress_callback_exceptions=True,
)
app.title = "DataLogger"
app._favicon = "assets/favicon.ico"
theme = {
    "dark": True,
    "detail": "#007439",
    "primary": "#00EA64",
    "secondary": "#6E6E6E",
}


app.layout = html.Div(
    [
        dcc.Store(id="files", data={}, storage_type="local"),
        html.H1(
            "Data-logging plotter software",
            style={"margin": "20px 0px 0px 30px"},
        ),
        html.Div(
            [
                html.Div(
                    dcc.Link(
                        f"{page['name']} - {page['path']}",
                        href=page["relative_path"],
                    ),
                    style={"margin": "0px 0px 0px 30px"},
                )
                for page in dash.page_registry.values()
            ]
        ),
        dash.page_container,
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
    # app.run_server(debug=True, host="0.0.0.0")
