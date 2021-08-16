from re import S
from dash_bootstrap_components._components.CardHeader import CardHeader
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import microdf as mdf
import os
from py import visualize
import json
from textwrap import dedent as d

# Define UBI Center colors
BLUE = "#1976D2"
DARK_BLUE = "#1565C0"
LIGHT_BLUE = "#90CAF9"
GRAY = "#BDBDBD"
BARELY_BLUE = "#E3F2FD"

# SECTION Import data.
r = pd.read_csv("data/responses_merged.csv")
r.date = r.date.apply(lambda x: pd.to_datetime(x))
polls = pd.read_csv("data/polls.csv").set_index("poll_id")
poll_ids = r.poll_id.unique().astype(int)
question_ids = r.question_id.unique().astype(int)
xtab1_vars = r.xtab1_var.unique()
xtab1_vals = r.xtab1_val.unique()
xtab2_vars = r.xtab2_var.unique()
countries = sorted(r.country.unique().tolist())


def get_unique(df, col, sorted=False):
    if sorted:
        return sorted(df[col].unique())
    else:
        return df[col].unique()


def dash_options(df, col):
    return [{"label": i, "value": i} for i in df[col].unique()]


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

# ------------ create cards to contain charts ------------ #
barcard_bubble_click = dbc.Card(
    dcc.Graph(
        id="bar-graph-bubble-click",  # ID "bar-graph-bubble-click"
        figure={},
        config={"displayModeBar": False},
    ),
    body=True,
    color="info",
)

# create defualt bubble chart
bubble_fig = visualize.bubble_chart(
    responses=r,
)

bubble_dropdown_deck = dbc.CardDeck(
    [
        # define first card with poll selection options
        dbc.Card(
            [
                # ------------- select a country ------------ #
                dbc.CardBody(
                    [
                        html.Label(
                            ["Filter countries:"],
                            style={
                                "font-weight": "bold",
                                "text-align": "center",
                                "color": BLUE,
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
                            options=[{"label": c, "value": c} for c in countries],
                            value=countries,
                        ),
                    ],
                    # style={"height": "100px"},
                ),
            ],
            # color="info",
            outline=True,
        ),
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.Label(
                            ["Filter demographics based on:"],
                            id="xtab1-bubble-label",  # ID "xtab1-bubble-label"
                            style={
                                "font-weight": "bold",
                                "text-align": "center",
                                "color": BLUE,
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
                        html.Br(),
                        html.Label(
                            ["Select demographic:"],
                            style={
                                "font-weight": "bold",
                                "text-align": "center",
                                "color": BLUE,
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
                        # dbc.Button(
                        #     "Apply demographic filter",
                        #     color="primary",
                        #     outline=True,
                        #     block=True
                        # )
                    ],
                    id="xtab1-bubble-cardbody",  # ID "xtab1-bubble-cardbody"
                ),
            ],
            # color="info",
            outline=False,
        ),
    ],
)

bubble_graph_component = (
    dcc.Graph(
        id="bubble-graph",  # ID "bubble-graph"
        figure=bubble_fig,
        config={"displayModeBar": False},
    ),
)

bubble_input_components = [
    # ------ filter countries with these components ------ #
    html.Label(
        ["Filter polls by country:"],
        style={
            "font-weight": "bold",
            "text-align": "left",
            "color": BLUE,
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
        options=[{"label": c, "value": c} for c in countries],
        value=countries,
        # shrink the fontsize of the country selections to make the buble a little mroe readable
        style={"fontSize": 10},
    ),
    html.Br(),
    # ---------- filter demographics with these ---------- #
    dbc.Card(
        [
            # create a header for the card that indicates that the two dropdown options work together as a group
            # dbc.CardHeader(
            #     html.H6(
            #         [
            #             "Compare polls across selected demographic ",
            #             dbc.Badge("Optional", color="secondary", className="mr-1"),
            #         ]
            #     )
            # ),
            html.H6(
                    [
                        "Compare polls across selected demographic: ",
                        dbc.Badge("Optional", color="light", className="mr-1"),
                    ],
            style={
                            "font-weight": "bold",
                            # "text-align": "center",
                            "color": BLUE,
                            "fontSize": 20,
                        },
            ),
            dbc.CardBody(
                [
                    html.Label(
                        ["1. Choose a category"],
                        id="xtab1-bubble-label",  # ID "xtab1-bubble-label"
                        style={
                            "font-weight": "bold",
                            # "text-align": "center",
                            # "color": BLUE,
                            # "fontSize": 20,
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
                    html.Br(),
                    html.Label(
                        ["2. Select demographic:"],
                        style={
                            "font-weight": "bold",
                            # "text-align": "center",
                            # "color": BLUE,
                            # "fontSize": 20,
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
                    # dbc.Button(
                    #     "Apply demographic filter",
                    #     color="primary",
                    #     outline=True,
                    #     block=True
                    # )
                ],
                id="xtab1-bubble-cardbody",  # ID "xtab1-bubble-cardbody"
            ),
        ],
        # color="info",
        outline=False,
    ),
]

bubble_big_card = dbc.Card(
    [
        dbc.CardHeader(html.H5("Compare Across Polls")),
        dbc.CardBody(
            [
                html.P("Configure the below options to filter the bubble chart:"),
                dbc.Row(
                    [
                        dbc.Col(bubble_input_components, md=3),
                        dbc.Col(
                            bubble_graph_component,
                            md=9,
                        ),
                    ],
                    no_gutters=True,
                ),
            ]
        ),
    ]
)

bar_col_components = [
    dbc.Col(
        html.Label(
            ["Question:"],
            id="question-label",
            style={
                # "font-weight": "bold",
                # "text-align": "center",
                # "color": BLUE,
                "fontSize": 12,
            },
        ),
        md={"width": 6, "offset": 3},
    ),
    dcc.Graph(
        id="bar-graph",  # ID "bar-graph"
        figure={},
        config={"displayModeBar": False},
    ),
    # TODO: show question names instead of question_id
    # TODO: dynamically update dropdown options based on poll-dropdown`s value
]

bar_input_components = [
    html.Label(
        ["Select country:"],
        style={
            "font-weight": "bold",
            "text-align": "center",
            "color": BLUE,
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
        # make persistent
        persistence=True,
    ),
    html.Br(),
    html.Label(
        ["Select poll:"],
        style={
            "font-weight": "bold",
            "text-align": "center",
            "color": BLUE,
            "fontSize": 20,
        },
    ),
    # TODO: show poll names instead of poll_id
    dcc.Dropdown(
        # define component_id for input of app@callback function
        id="poll-dropdown",  # ID "poll-dropdown"
        multi=False,
        style={
            "fontSize": 14,
        },
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
    html.Br(),
    html.Label(
        ["  Select question:"],
        style={
            "font-weight": "bold",
            "text-align": "center",
            "color": BLUE,
            "fontSize": 20,
        },
    ),
    dcc.RadioItems(
        # define component_id for input of app@callback function
        id="question-dropdown",  # ID "question-dropdown"\
        options=[
            {
                "label": "{}".format(
                    r.loc[r.question_id == x, "question_text"].unique()
                ),
                "value": x,
            }
            for x in question_ids
        ],
        # try addding a right mark to the question text
        inputStyle={"margin-right": "10px"},
    ),
    html.Br(),
    html.Label(
        ["Select cross-tab:"],
        id="xtab1-label",  # ID "x-tab1-label"
        style={
            "font-weight": "bold",
            "text-align": "center",
            "color": BLUE,
            "fontSize": 20,
        },
    ),
    dcc.RadioItems(
        # define component_id for input of app@callback function
        id="xtab1-dropdown",  # ID "x-tab1-dropdown"
        # multi=False,
        value="-",
        # to be selected by user in dropdown
        options=[{"label": x, "value": x} for x in xtab1_vars],
        # try addding a right mark to the question text
        inputStyle={"margin-right": "10px"},
    ),
]


bar_big_card = dbc.Card(
    [
        dbc.CardHeader(html.H5("Drill down on individual polls")),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(bar_input_components, md=3),
                        dbc.Col(bar_col_components, md=9),
                    ],
                    no_gutters=True,
                ),
            ]
        ),
    ]
)

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
                            "color": BLUE,
                            "fontSize": 50,
                            "letter-spacing": "2px",
                            "font-weight": 300,
                        },
                    ),
                    md={"size": default_size, "offset": default_offset},
                ),
            ]
        ),
        html.Br(),
        # -------------- explanation of app -------------- #
        dbc.Row(
            [
                dbc.Col(
                    html.H4(
                        "Use the interactive below to explore different the current state of UBI's favorability from "
                        + str(len(poll_ids))
                        + " different polls across "
                        + str(len(countries))
                        + " countries.",  # REVIEW
                        style={
                            "text-align": "left",
                            "color": "black",
                            "fontSize": 25,
                        },
                    ),
                    md={"size": default_size, "offset": default_offset},
                ),
            ]
        ),
        html.Br(),
        # ---------------- place big cards --------------- #
        dbc.Row([dbc.Col(bubble_big_card, md=chart_width)]),
        dbc.Row([dbc.Col(bar_big_card, md=chart_width)]),
        html.Br(),
        # --------------- download button --------------- #
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.Button("Download data as CSV", id="btn_csv"),
                            dcc.Download(id="download-dataframe-csv"),
                        ],
                    ),
                    md={"size": "auto", "offset": 1},
                ),
            ]
        ),
        html.Br(),
        # link to contact email and github issue tracker
        dbc.Row(
            [
                dbc.Col(
                    html.H4(
                        [
                            "Questions or feedback? ",
                            "Email ",
                            html.A(
                                "contact@ubicenter.org",
                                href="mailto:contact@ubicenter.org",
                            ),
                            " or file an issue at ",
                            html.A(
                                "github.com/UBICenter/polls/issues",
                                href="http://github.com/UBICenter/polls/issues",
                            ),
                        ],
                        style={
                            "text-align": "left",
                            "color": "gray",
                            "fontSize": 12,
                            "font-family": "Roboto",
                        },
                    ),
                    width={
                        "size": "auto",
                        # "offset": 2
                    },
                    md={"size": 8, "offset": 1},
                ),
            ]
        ),
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


# update question-label above bar-graph based on question-dropdown selection
@app.callback(
    Output(component_id="question-label", component_property="children"),
    Input(component_id="question-dropdown", component_property="value"),
)
def update_question_label(question_dropdown_value):
    question = "{}".format(
        r.loc[r.question_id == question_dropdown_value, "question_text"].max()
    )
    return "Question text: " + str(question)


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
    Output(component_id="xtab1-label", component_property="style"),
    Output(component_id="xtab1-dropdown", component_property="style"),
    # Output(component_id="xtab1-dropdown", component_property="value"),
    Input("xtab1-dropdown", "options"),
)
def show_hide_xtab(xtab1_dropdown_options):
    # change visibilty of xtab1-dropdown based on xtab1-card
    if len(xtab1_dropdown_options) > 1:
        return {"display": "block"}, {"display": "block"}
    else:
        return {"display": "none"}, {"display": "none"}


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
    # # this is to update xtab1_val-bubble-dropdown VALUE based on selected xtab1_var
    # Output(component_id="xtab1_val-bubble-dropdown", component_property="value"),
    Input(component_id="country-dropdown-2", component_property="value"),
    # xtab1-bubble-dropdown input will be a string
    Input(component_id="xtab1-bubble-dropdown", component_property="value"),
    Input(component_id="xtab1_val-bubble-dropdown", component_property="value"),
)
def update_bubble_chart(
    countries,
    xtab1_var,
    xtab1_val,
):
    # subsets r to only include the selected countries
    r_sub = r[r.country.isin(countries)]

    # updates xtab1-bubble-dropdown options based on selected country
    xtab1_options = [{"label": x, "value": x} for x in r_sub.xtab1_var.unique()]

    # updates xtab1_val-bubble-dropdown options based on selected xtab1_var
    xtab1_val_options = [
        {"label": x, "value": x}
        for x in r_sub[r_sub.xtab1_var == xtab1_var].xtab1_val.unique()
    ]

    # if (xtab1_var in [None, "-"]) & (xtab1_val in [None, "-"]):
    #     bubble = visualize.bubble_chart(r_sub)

    if xtab1_var in [None, "-"]:
        bubble = visualize.bubble_chart(r_sub)

    # elif (xtab1_var not in [None, "-"]) & (
    #     xtab1_val in [None, "-"]
    # ):
    #     bubble = visualize.bubble_chart(r_sub[r_sub.xtab1_var == xtab1_var])

    else:
        bubble = visualize.bubble_chart(r_sub, xtab1_val=xtab1_val)

    bubble.update_layout(transition_duration=200)

    return xtab1_options, xtab1_val_options, bubble


# update bar-bubble-graph-click based on clickData from bubble-graph
@app.callback(
    Output(component_id="country-dropdown", component_property="value"),
    Output(component_id="poll-dropdown", component_property="value"),
    Input(component_id="bubble-graph", component_property="clickData"),
    # this prevents the callback from loading when the app starts
    prevent_initial_call=True,
)
def update_bar_graph_bubble_click(clickData):
    print(
        clickData,
    )
    # if a bubble is clicked, update the bar chart to the side. else, update the bubble chart with an empty dict
    if clickData is None:
        # raise PreventUpdate
        pass
    else:
        poll_id = clickData["points"][0]["customdata"][0]
        # country = r.loc[r.poll_id == poll_id, "country"].max()
        country = clickData["points"][0]["customdata"][2]
        return country, poll_id


# ----------- rewrite callbacks for bubble tab ----------- #

# callback to download responses_merged.csv
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(r.to_csv, "responses.csv")


if __name__ == "__main__":
    app.run_server(debug=True, port=8060, host="127.0.0.1")
