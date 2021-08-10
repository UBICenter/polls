from re import S
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


# SECTION Import data.
r = pd.read_csv("data/responses_merged.csv")
r.date = r.date.apply(lambda x: pd.to_datetime(x))
polls = pd.read_csv("data/polls.csv").set_index("poll_id")
poll_ids = r.poll_id.unique().astype(int)
question_ids = r.question_id.unique().astype(int)
xtab1_vars = r.xtab1_var.unique()
xtab1_vals = r.xtab1_val.unique()
xtab2_vars = r.xtab2_var.unique()
countries = r.country.unique()

# ------------ create cards to contain charts ------------ #

# default style for the chart
style = {"width": "90vh", "height": "90vh"}

# place the bar chart in a card
barcard = dbc.CardDeck(
    [
        dbc.Card(
            dcc.Graph(
                id="bar-graph",  # ID "bar-graph"
                figure={},
                config={"displayModeBar": False},
            ),
            body=True,
            color="info",
        )
    ]
)

barcard_bubble_click = dbc.CardDeck(
    [
        dbc.Card(
            dcc.Graph(
                id="bar-graph-bubble-click",  # ID "bar-graph-bubble-click"
                figure={},
                config={"displayModeBar": False},
            ),
            body=True,
            color="info",
        )
    ]
)

# create defualt bubble chart
bubble_fig = visualize.bubble_chart(
    responses=r,
)
bubblecard = dbc.Card(
    dcc.Graph(
        id="bubble-graph",  # ID "bubble-graph"
        figure=bubble_fig,
        config={"displayModeBar": False},
    ),
    body=True,
    color="info",
)

bubble_carddeck = dbc.CardDeck(
    [
        bubblecard,
        barcard_bubble_click,
    ]
)
# charts = dbc.CardDeck(
#     [
#         bubblecard,
#         barcard,
#     ]
# )


# SECTION Create the input cards
cards1 = dbc.CardDeck(
    [
        # define first card with poll selection options
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
                            id="country-dropdown",  # ID "country-dropdown"
                            multi=False,
                            value=22,
                            # create a list of dicts of states and their labels
                            # to be selected by user in dropdown
                            options=[{"label": c, "value": c} for c in countries],
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
                            id="poll-dropdown",  # ID "poll-dropdown"
                            multi=False,
                            # value=22,
                            # create a list of dicts of states and their labels
                            # to be selected by user in dropdown
                            options=[
                                {
                                    "label": "{} - {} ({})".format(
                                        polls.loc[id, "pollster"],
                                        polls.loc[id, "date"],
                                        polls.loc[id, "country"],
                                    ),
                                    "value": id,
                                }
                                for id in poll_ids
                            ],
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
                            id="question-dropdown",  # ID "question-dropdown"
                            multi=False,
                            # value=17,
                            # create a list of dicts of states and their labels
                            # to be selected by user in dropdown
                            options=[
                                {
                                    "label": "{}".format(
                                        r.loc[
                                            r.question_id == x, "question_text"
                                        ].unique()
                                    ),
                                    "value": x,
                                }
                                for x in question_ids
                            ],
                        ),
                    ]
                ),
            ],
            color="info",
            outline=False,
        ),
    ],
)

# SECTION define first card with poll selection options
xtab1_card = dbc.Card(
    [
        # ---------- select a cross-tab ---------- #
        dbc.CardBody(
            [
                html.Label(
                    ["Select cross-tab:"],
                    id="xtab1-label",  # ID "x-tab1-label"
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
                    id="xtab1-dropdown",  # ID "x-tab1-dropdown"
                    multi=False,
                    value="-",
                    # create a list of dicts of states and their labels
                    # to be selected by user in dropdown
                    options=[{"label": x, "value": x} for x in xtab1_vars],
                ),
            ],
            id="xtab1-cardbody",  # ID "xtab1-cardbody"
        ),
    ],
    id="xtab1-card",  # ID "xtab1-card"
    color="info",
    outline=False,
)
xtab2_card = dbc.Card(
    [
        # ---------- select a cross-tab ---------- #
        dbc.CardBody(
            [
                html.Label(
                    ["Select second cross-tab:"],
                    id="xtab2-label",  # ID "x-tab2-label"
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
                    id="xtab2-dropdown",  # ID "x-tab2-dropdown"
                    multi=False,
                    value="-",
                    # create a list of dicts of states and their labels
                    # to be selected by user in dropdown
                    options=[{"label": x, "value": x} for x in xtab2_vars],
                ),
            ],
            id="xtab2-cardbody",  # ID "xtab2-cardbody"
        ),
    ],
    id="xtab2-card",  # ID "xtab2-card"
    color="info",
    outline=False,
)

# -------------------------------------------------------- #
#                       tab two cards                      #
# -------------------------------------------------------- #
# Create the input cards for tab 2
cards2 = dbc.CardDeck(
    [
        # define first card with poll selection options
        dbc.Card(
            [
                # ------------- select a country ------------ #
                dbc.CardBody(
                    [
                        html.Label(
                            ["Select countries:"],
                            style={
                                "font-weight": "bold",
                                "text-align": "center",
                                "color": "white",
                                "fontSize": 20,
                            },
                        ),
                        # TODO: for the EU polls with country crosstab, have those as selectable options
                        dcc.Dropdown(
                            # define component_id for input of app@callback function
                            id="country-dropdown-2",  # ID "country-dropdown-2"
                            multi=True,
                            # create a list of dicts of countries and their labels
                            # to be selected by user in dropdown
                            options=[
                                {"label": c + str(" "), "value": c} for c in countries
                            ],
                            value=[c for c in countries],
                        ),
                    ]
                ),
            ],
            color="info",
            outline=False,
        ),
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.Label(
                            ["Select cross-tab category group:"],
                            id="xtab1-bubble-label",  # ID "xtab1-bubble-label"
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
                            id="xtab1-bubble-dropdown",  # ID         "xtab1-bubble-dropdown"
                            multi=False,
                            value="-",
                            # create a list of dicts of states and their labels
                            # to be selected by user in dropdown
                            options=[{"label": x, "value": x} for x in xtab1_vars],
                        ),
                    ],
                    id="xtab1-bubble-cardbody",  # ID "xtab1-bubble-cardbody"
                ),
            ],
            color="info",
            outline=False,
        ),
        dbc.Card(
            [
                # ---------- select a cross-tab value ---------- #
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
                            id="xtab1_val-bubble-dropdown",  # ID "xtab1_val-bubble-dropdown"
                            multi=False,
                            value="-",
                            # create a list of dicts of states and their labels
                            # to be selected by user in dropdown
                            options=[{"label": x, "value": x} for x in xtab1_vals],
                        ),
                    ],
                ),
            ],
            color="info",
            outline=False,
        ),
    ]
)
# bubblecard,


# Get base pathname from an environment variable that CS will provide.
url_base_pathname = os.environ.get("URL_BASE_PATHNAME", "/")

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.FLATLY,
        "https://fonts.googleapis.com/css2?family=Lato:wght@300;400&display=swap",  # LINK TO FONT
        "/assets/style.css",
    ],
    # Pass the url base pathname to Dash.
    url_base_pathname=url_base_pathname,
)
# used to debug the app maybe
application = app.server
# server = app.server

# -------------------------------------------------------- #
#                        app layout                        #
# -------------------------------------------------------- #
default_size = "auto"
input_width = {"size": 10, "offset": 1}
chart_width = {"size": 10, "offset": 1}
default_offset = "1"
# Design the app
app.layout = html.Div(
    [
        dbc.Navbar(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Img(
                                    src="https://blog.ubicenter.org/_static/ubi_center_logo_wide_blue.png",  # LINK TO LOGO
                                    height="30px",
                                )
                            ),
                        ],
                        align="center",
                        no_gutters=True,
                    ),
                    href="https://www.ubicenter.org",  # LINK TO WEBSITE
                    target="blank",
                ),
                dbc.NavbarToggler(id="navbar-toggler"),  # ID "navbar-toggler",
            ]
        ),
        html.Br(),
        # --------------------- place title -------------------- #
        dbc.Row(
            [
                dbc.Col(
                    html.H1(
                        "Explore the state of public opinion on UBI",
                        id="header",  # ID "header"
                        style={
                            "text-align": "center",
                            "color": "#1976D2",
                            "fontSize": 50,
                            "letter-spacing": "2px",
                            "font-weight": 300,
                        },
                    ),
                    width={"size": default_size, "offset": default_offset},
                ),
            ]
        ),
        html.Br(),
        # -------------- explanation of app -------------- #
        dbc.Row(
            [
                dbc.Col(
                    html.H4(
                        "Use the interactive below to explore different the current state of UBI's favorability accross different countries, polls, and questions.",  # REVIEW
                        style={
                            "text-align": "left",
                            "color": "black",
                            "fontSize": 25,
                        },
                    ),
                    width={"size": default_size, "offset": default_offset},
                ),
            ]
        ),
        html.Br(),
        # SECTION --------------------- tabs --------------------- #
        dcc.Tabs(
            [
                # SECTION ----------------- tab 1 ---------------- #
                dcc.Tab(
                    label="Bar Chart",
                    children=[
                        # navbar
                        dbc.Row([dbc.Col(cards1, width=input_width)]),
                        html.Div(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            xtab1_card,
                                            width=input_width,
                                        )
                                    ]
                                )
                            ],
                            style={"display": "block"},
                        ),
                        # html.Div(
                        #     [
                        #         dbc.Row(
                        #             [
                        #                 dbc.Col(
                        #                     xtab2_card,
                        #                     width=input_width,
                        #                 )
                        #             ]
                        #         )
                        #     ],
                        #     style={"display": "block"},
                        # ),
                        html.Br(),
                        # ---------------- place charts --------------- #
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
                                    width={
                                        "size": default_size,
                                        "offset": default_offset,
                                    },
                                ),
                            ]
                        ),
                        # dbc.Row([dbc.Col(text, width={"size": 6, "offset": 3})]),
                        html.Br(),
                        dbc.Row([dbc.Col(barcard, width=chart_width)]),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                    ],
                ),
                # SECTION ----------------- tab 2 ---------------- #
                dcc.Tab(
                    label="Compare Across Polls",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.H1(
                                        "Trends:",
                                        style={
                                            "text-align": "center",
                                            "color": "#1976D2",
                                            "fontSize": 30,
                                        },
                                    ),
                                    width={"size": "auto", "offset": 2},
                                ),
                            ]
                        ),
                        # dbc.Row([dbc.Col(text, width={"size": 6, "offset": 3})]),
                        html.Br(),
                        dbc.Row([dbc.Col(cards2, width=input_width)]),
                        html.Br(),
                        # ---------------- place charts --------------- #
                        dbc.Row([dbc.Col(bubble_carddeck, width=chart_width)]),
                    ],
                ),
            ]
        ),
        html.Br(),
        html.Br(),
        # add download button
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.Button("Download data as CSV", id="btn_csv"),
                            dcc.Download(id="download-dataframe-csv"),
                        ],
                    ),
                    width={"size": "auto", "offset": 1},
                ),
            ]
        ),
        # html.Div(
        #     dbc.Card(
        #         [
        #             dbc.Button("Download data as CSV", id="btn_csv"),
        #             dcc.Download(id="download-dataframe-csv"),
        #         ],
        #     )
        #     # style={"display": "none"},
        # ),
    ]
)

# -------------------------------------------------------- #
#                     Assign Tab 1 callbacks                     #
# -------------------------------------------------------- #

# TODO create most obvious way to select question first
@app.callback(
    Output(component_id="bar-graph", component_property="figure"),
    # Input(component_id="country-dropdown", component_property="value"),
    Input(component_id="poll-dropdown", component_property="value"),
    Input(component_id="question-dropdown", component_property="value"),
    Input(component_id="xtab1-dropdown", component_property="value"),
)
def test(poll, question, xtab1):

    bar = visualize.poll_vis(
        responses=r, poll_id=poll, question_id=question, crosstab_variable=xtab1
    )

    return bar


# ------ update poll, question, crosstab options based on country dropdown ----- #
@app.callback(
    Output(component_id="poll-dropdown", component_property="options"),
    # Output(component_id="bubble-graph", component_property="figure"),
    Input("country-dropdown", "value"),
)
def update(dropdown_value):
    """[summary]
    change the options of the checklist to match the selected countries
    Parameters
    ----------
    dropdown : str
        takes the input "country-dropdown" from the callback
    Returns
    -------
    populates other dropdowns with country-specific options
    """
    poll_options = [
        {
            "label": "{} - {} ({})".format(
                polls.loc[id, "pollster"],
                polls.loc[id, "date"],
                polls.loc[id, "country"],
            ),
            "value": id,
        }
        for id in r[r.country == dropdown_value]
        .sort_values("date", ascending=False)
        .poll_id.unique()
    ]

    # bubble = visualize.bubble_chart(
    #     responses=r,
    #     # poll_ids=r.poll_id.unique(),
    #     # question_ids=r.question_id.unique()
    # )

    return poll_options


# ------ update question options based on poll dropdown ----- #
@app.callback(
    Output(component_id="question-dropdown", component_property="options"),
    Output(component_id="question-dropdown", component_property="value"),
    # Output(component_id="xtab1-dropdown", component_property="options"),
    Input("poll-dropdown", "value"),
)
def update(dropdown_value):
    """[summary]
    change the options of the questions dropdown to match the selected countries
    Parameters
    ----------
    dropdown : str
        takes the input "country-dropdown" from the callback
    Returns
    -------
    populates other dropdowns with country-specific options
    """

    question_options = [
        # this part returns the question text based on the provided question id
        {
            "label": "{}".format(r.loc[r.question_id == x, "question_text"].max()),
            "value": x,
        }
        # this part returns the unique question ids associated with the selected poll id in responses_merged.csv
        for x in r[r.poll_id == dropdown_value].question_id.unique()
    ]

    default_question = question_options[0]["value"] if question_options else None
    return question_options, default_question

    # return question_options, question_options[0]["value"]


# ------ update xtab1 options based on question dropdown ----- #
@app.callback(
    Output(component_id="xtab1-dropdown", component_property="options"),
    # NOTE: deactivate second crosstab for now
    # Output(component_id="xtab2-dropdown", component_property="options"),
    Input("question-dropdown", "value"),
)
def update(dropdown_value):
    # update xtab1 options based on question dropdown

    xtab1_options = [
        {"label": x, "value": x}
        for x in r[r.question_id == dropdown_value].xtab1_var.unique()
    ]

    # NOTE: deactivate this for now
    # xtab2_options = [
    #     {"label": x, "value": x}
    #     for x in r[r.question_id == dropdown_value].xtab2_var.unique()
    # ]

    return xtab1_options
    # return xtab1_options, xtab2_options


# ------ update xtab1 options based on question dropdown ----- #
@app.callback(
    Output(component_id="xtab1-card", component_property="style"),
    Input("xtab1-dropdown", "options"),
)
def show_hide_xtab(xtab1_dropdown_options):
    if len(xtab1_dropdown_options) > 1:
        return {"display": "block"}
    else:
        return {"display": "none"}


# # ------ update xtab2 options based on question dropdown ----- #
# @app.callback(
#     Output(component_id="xtab2-card", component_property="style"),
#     Input("xtab2-dropdown", "options"),
# )
# def show_hide_xtab(xtab2_dropdown_options):
#     if len(xtab2_dropdown_options) > 1:
#         return {"display": "block"}
#     else:
#         return {"display": "none"}

# -------------------------------------------------------- #
#                bubble chart tab callbacks                #
# -------------------------------------------------------- #

# update bubble chart based on country dropdown, crosstab variable, crosstab value
@app.callback(
    # output the relevent xtab1_val based on selected xtab1_var
    Output(component_id="xtab1-bubble-dropdown", component_property="options"),
    # output the relevent xtab1_val based on selected xtab1_var
    Output(component_id="xtab1_val-bubble-dropdown", component_property="options"),
    # country input will be list
    Output(component_id="bubble-graph", component_property="figure"),
    Output(component_id="bar-graph-bubble-click", component_property="figure"),
    Input(component_id="country-dropdown-2", component_property="value"),
    # xtab1-bubble-dropdown input will be a string
    Input(component_id="xtab1-bubble-dropdown", component_property="value"),
    Input(component_id="xtab1_val-bubble-dropdown", component_property="value"),
    Input(component_id="bubble-graph", component_property="clickData"),
)
def update_bubble_chart(
    country_dropdown,
    xtab1_bubble_dropdown,
    xtab1_val_bubble_dropdown,
    clickData,
):
    # subsets r to only include the selected countries
    r_sub = r[r.country.isin(country_dropdown)]

    # updates xtab1-bubble-dropdown options based on selected country
    xtab1_options = [{"label": x, "value": x} for x in r_sub.xtab1_var.unique()]

    # updates xtab1_val-bubble-dropdown options based on selected xtab1_var
    xtab1_val_options = [
        {"label": x, "value": x}
        for x in r_sub[r_sub.xtab1_var == xtab1_bubble_dropdown].xtab1_val.unique()
    ]

    if (xtab1_bubble_dropdown in [None, "-"]) | (
        xtab1_val_bubble_dropdown in [None, "-"]
    ):
        bubble = visualize.bubble_chart(r_sub)
    else:
        bubble = visualize.bubble_chart(r_sub, xtab1_val=xtab1_val_bubble_dropdown)

    bubble.update_layout(transition_duration=300)

    print(clickData)
    # if a bubble is clicked, update the bar chart to the side. else, update the bubble chart with an empty dict
    if clickData is not None:
        poll_id = clickData["points"][0]["customdata"][0]
        question_id = clickData["points"][0]["customdata"][1]

        updated_bar = visualize.poll_vis(
            r_sub,
            poll_id=poll_id,
            question_id=question_id,
            crosstab_variable=xtab1_bubble_dropdown,
        )
    else:
        updated_bar = {}

    return xtab1_options, xtab1_val_options, bubble, updated_bar


# callback to download responses_merged.csv
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(r.to_csv, "responses.csv")


if __name__ == "__main__":
    app.run_server(debug=True, port=8050, host="127.0.0.1")
