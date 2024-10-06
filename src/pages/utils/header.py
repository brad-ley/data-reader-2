import dash_bootstrap_components as dbc
import dash


pages = {"Files": "/files", "Plots": "/"}
# pages = dash.page_registry.values()


def header(name):
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink(f"{page}", href=f"{pages[page]}"))
            # dbc.NavItem(
            #     dbc.NavLink(f"{page['name']}", href=f"{page['relative_path']}")
            # )
            for page in pages
            if name.split(".")[-1] != page.lower()
        ],
        brand="LoggerPlot",
        color="primary",
        dark=True,
        className="mb-2",
        fluid=True,
        sticky=True,
    )
    return navbar
