import dash_bootstrap_components as dbc
import dash


pages = {"Files": "/files", "Plots": "/"}


def header(name):
    print(name)
    children = [
        f"name: {page}    " + f"link: {pages[page]}"
        for page in pages
        if name.split(".")[-1] != page.lower()
    ]
    print(children)
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink(f"{page}", href=f"{pages[page]}"))
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
