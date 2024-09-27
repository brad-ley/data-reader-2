import dash
from dash import html, dcc

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
graph_height = "325px"
margin_vert = "0px"
margin = dict(l=20, r=20, t=20, b=20)

app = dash.Dash(
    __name__,
    use_pages=True,
    prevent_initial_callbacks=True,
    external_stylesheets=external_stylesheets,  # type: ignore
    # suppress_callback_exceptions=True,
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
        dcc.Store(id="files", data={}, storage_type="session"),
        html.H1("Multi-page app with Dash Pages"),
        html.Div(
            [
                html.Div(
                    dcc.Link(
                        f"{page['name']} - {page['path']}",
                        href=page["relative_path"],
                    )
                )
                for page in dash.page_registry.values()
            ]
        ),
        dash.page_container,
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
