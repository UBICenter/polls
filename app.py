import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import microdf as mdf
import os
from py import visualize

# Import data.
r = pd.read_csv("data/responses_merged.csv")
polls = pd.read_csv("data/polls.csv").set_index("poll_id")
poll_ids = r.poll_id.unique().astype(int)
question_ids = r.question_id.unique().astype(int)
xtab1_vars = r.xtab1_var.unique()
xtab2_vars = r.xtab2_var.unique()
countries = r.country.unique()

# Create the input cards
cards = dbc.CardDeck(
    [
        # define first card with state-dropdown component
        dbc.Card(
            [
                # ------------- select a country ------------ #
                dbc.CardBody(
                    [
                        html.Label(
                            ["Select country:"],
                            style={
                                "font-weight": "bold",
                                "text-align": "center",
                                "color": "white",
                                "fontSize": 20,
                            },
                        ),
                        # TODO: show poll names instead of poll_id
                        dcc.Dropdown(
                            # define component_id for input of app@callback function
                            id="country-dropdown",
                            multi=False,
                            value=22,
                            # create a list of dicts of states and their labels
                            # to be selected by user in dropdown
                            options=[{"label": c,
                                      "value": c} for c in countries],
                        ),
                    ]
                ),
                # ------------- select a poll ------------ #
                dbc.CardBody(
                    [
                        html.Label(
                            ["Select poll:"],
                            style={
                                "font-weight": "bold",
                                "text-align": "center",
                                "color": "white",
                                "fontSize": 20,
                            },
                        ),
                        # TODO: show poll names instead of poll_id
                        dcc.Dropdown(
                            # define component_id for input of app@callback function
                            id="poll-dropdown",
                            multi=False,
                            value=22,
                            # create a list of dicts of states and their labels
                            # to be selected by user in dropdown
                            options=[{"label": "{} - {} ({})".format(polls.loc[id, "pollster"], 
                                                                     polls.loc[id, "date"], 
                                                                     polls.loc[id, "country"]),
                                      "value": id} for id in poll_ids],
                        ),
                    ]
                ),
                # ----------- select a question ---------- #
                dbc.CardBody(
                    [
                        html.Label(
                            ["Select question:"],
                            style={
                                "font-weight": "bold",
                                "text-align": "center",
                                "color": "white",
                                "fontSize": 20,
                            },
                        ),
                        # TODO: show question names instead of question_id
                        # TODO: dynamically update dropdown options based on poll-dropdown`s value
                        dcc.Dropdown(
                            # define component_id for input of app@callback function
                            id="question-dropdown",
                            multi=False,
                            value=17,
                            # create a list of dicts of states and their labels
                            # to be selected by user in dropdown
                            options=[{"label": "{}".format(r.loc[r.question_id==x, "question_text"].unique()), "value": x} for x in question_ids],
                        ),
                    ]
                ),
                # ---------- select a cross-tab ---------- #
                dbc.CardBody(
                    [
                        html.Label(
                            ["Select cross-tab:"],
                            style={
                                "font-weight": "bold",
                                "text-align": "center",
                                "color": "white",
                                "fontSize": 20,
                            },
                        ),
                        # TODO: show question names instead of question_id
                        dcc.Dropdown(
                            # define component_id for input of app@callback function
                            id="xtab1-dropdown",
                            multi=False,
                            value="-",
                            # create a list of dicts of states and their labels
                            # to be selected by user in dropdown
                            options=[{"label": x, "value": x} for x in xtab1_vars],
                        ),
                    ]
                ),
            ],
            color="info",
            outline=False,
        ),
    ],
)

charts = dbc.CardDeck(
    [
        dbc.Card(
            dcc.Graph(id="bar-graph", figure={}),
            body=True,
            color="info",
        ),
        # dbc.Card(
        #     dcc.Graph(id="bubble-graph", figure={}),
        #     body=True,
        #     color="info",
        # ),
    ]
)


# Get base pathname from an environment variable that CS will provide.
url_base_pathname = os.environ.get("URL_BASE_PATHNAME", "/")

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.FLATLY,
        "https://fonts.googleapis.com/css2?family=Lato:wght@300;400&display=swap",
        "/assets/style.css",
    ],
    # Pass the url base pathname to Dash.
    url_base_pathname=url_base_pathname,
)
# used to debug the app maybe 
application = app.server
# server = app.server

# Design the app
app.layout = html.Div(
    [
        # navbar
        dbc.Navbar(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Img(
                                    src="https://blog.ubicenter.org/_static/ubi_center_logo_wide_blue.png",
                                    height="30px",
                                )
                            ),
                        ],
                        align="center",
                        no_gutters=True,
                    ),
                    href="https://www.ubicenter.org",
                    target="blank",
                ),
                dbc.NavbarToggler(id="navbar-toggler"),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    html.H1(
                        "Explore funding mechanisms of UBI",
                        id="header",
                        style={
                            "text-align": "center",
                            "color": "#1976D2",
                            "fontSize": 50,
                            "letter-spacing": "2px",
                            "font-weight": 300,
                        },
                    ),
                    width={"size": 8, "offset": 2},
                ),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    html.H4(
                        "Use the interactive below to explore different funding mechanisms for a UBI and their impact. You may choose between repealing benefits or adding new taxes.  When a benefit is repealed or a new tax is added, the new revenue automatically funds a UBI to all people equally to ensure each plan is budget neutral.",
                        style={
                            "text-align": "left",
                            "color": "black",
                            "fontSize": 25,
                        },
                    ),
                    width={"size": 8, "offset": 2},
                ),
            ]
        ),
        html.Br(),
        dbc.Row([dbc.Col(cards, width={"size": 10, "offset": 1})]),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    html.H1(
                        "Poll results:",
                        style={
                            "text-align": "center",
                            "color": "#1976D2",
                            "fontSize": 30,
                        },
                    ),
                    width={"size": 8, "offset": 2},
                ),
            ]
        ),
        # dbc.Row([dbc.Col(text, width={"size": 6, "offset": 3})]),
        html.Br(),
        dbc.Row([dbc.Col(charts, width={"size": 10, "offset": 1})]),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
    ]
)

# -------------------------------------------------------- #
#                     Assign callbacks                     #
# -------------------------------------------------------- #


@app.callback(
    Output(component_id="bar-graph", component_property="figure"),
    # Input(component_id="country-dropdown", component_property="value"),
    Input(component_id="poll-dropdown", component_property="value"),
    Input(component_id="question-dropdown", component_property="value"),
    Input(component_id="xtab1-dropdown", component_property="value"),
)
def test(poll, question, xtab1):
    return visualize.poll_vis(responses=r, poll_id=poll, question_id=question, crosstab_variable=xtab1)

# ------ update selections based on country dropdown ----- #
@app.callback(
    Output(component_id="poll-dropdown", component_property="options"),
    Output(component_id="question-dropdown", component_property="options"),
    Output(component_id="xtab1-dropdown", component_property="options"),
    Input("country-dropdown", "value"),
)
def update(dropdown_value):
    """[summary]
    change the options of the checklist to match the selected countryes
    Parameters
    ----------
    checklist : list
        takes the input "country-dropdown" from the callback
    Returns
    -------
    populates other checklist with country-specific options
    """
    poll_options = [
        {
            "label": "{} - {} ({})".format(
                polls.loc[id, "pollster"], polls.loc[id, "date"], polls.loc[id, "country"]
            ),
            "value": id,
        }
        for id in r[r.country == dropdown_value].poll_id.unique()
    ]
    question_options = [
        {
            "label": "{}".format(r.loc[r.question_id == x, "question_text"].unique()),
            "value": x,
        }
        for x in r[r.country == dropdown_value].question_id.unique()[0]
    ]
    xtab1_options = [
        {"label": x, "value": x} for x in r[r.country == dropdown_value].xtab1_var.unique()
    ]
    
    return poll_options, question_options, xtab1_options

if __name__ == "__main__":
    app.run_server(debug=True, port=8000, host="127.0.0.1")
