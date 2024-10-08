import dash
import redis
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_extensions.enrich import BlockingCallbackTransform, DashProxy

redis_client = redis.Redis(
    host="red-cs11kubtq21c73ekg21g", port=6379, decode_responses=True
)
# redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
# redis_client = redis.Redis(host="0.0.0.0", port=6379, decode_responses=True)

# external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
graph_height = "325px"
margin_vert = "0px"
margin = dict(l=20, r=20, t=20, b=20)

# app = dash.Dash(
app = DashProxy(
    __name__,
    use_pages=True,
    # prevent_initial_callbacks=True,
    external_stylesheets=[dbc.themes.SLATE],  # type: ignore
    suppress_callback_exceptions=True,
    title="DataLogger",
    transforms=[BlockingCallbackTransform(timeout=10)],
)
app._favicon = "./favicon.ico"


app.layout = html.Div(
    [
        dcc.Store(id="files", data={}, storage_type="local"),
        dash.page_container,
    ]
)

if __name__ == "__main__":
    # app.run_server(
    #     # debug=True,
    #     dev_tools_ui=False,
    #     dev_tools_props_check=False,
    # )
    print("Running at http://localhost:8050/files")
    app.run_server(
        debug=False,
        host="0.0.0.0",
        dev_tools_ui=False,
        dev_tools_props_check=False,
    )
    server = app.server
