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


def list_options(lst, format_string=None):
    # returns a list of dicts with keys "label" and "value" that set options in dash components
    if format_string:
        return [
            {"label": format_string.format(x), "value": x}
            if x != "-"
            else {"label": "None", "value": x}
            for x in lst
        ]
    else:
        return [
            {"label": x, "value": x}
            if x != "-"
            else {"label": "None", "value": x}
            for x in lst
        ]


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

app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-0SYCS50FQ0"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());

            gtag('config', 'G-0SYCS50FQ0');
        </script>

        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

# ------------ create cards to contain charts ------------ #

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
                            options=list_options(countries),
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
                            # to be selected by user in dropdown
                            options=list_options(xtab1_vars),
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
                            # to be selected by user in dropdown
                            options=list_options(xtab1_vals),
                        ),
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
        responsive=True,
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
    dcc.Dropdown(
        # define component_id for input of app@callback function
        id="country-dropdown-2",  # ID "country-dropdown-2"
        multi=True,
        # create a list of dicts of countries and their labels
        # to be selected by user in dropdown
        options=list_options(countries),
        value=countries,
        # shrink the fontsize of the country selections to make the buble a little mroe readable
        style={"fontSize": 10},
    ),
    html.Br(),
    # ---------- filter demographics with these ---------- #
    dbc.Card(
        [
            html.H6(
                [
                    "Compare polls by demographic: ",
                    # dbc.Badge("Optional", color="light", className="mr-1"),
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
                        ["1. Choose category"],
                        id="xtab1-bubble-label",  # ID "xtab1-bubble-label"
                        style={
                            "font-weight": "bold",
                            # "text-align": "center",
                            # "color": BLUE,
                            "fontSize": 14,
                        },
                    ),
                    dcc.Dropdown(
                        # define component_id for input of app@callback function
                        id="xtab1-bubble-dropdown",  # ID         "xtab1-bubble-dropdown"
                        multi=False,
                        value="-",
                        # to be selected by user in dropdown
                        options=list_options(xtab1_vars),
                        optionHeight=25,
                    ),
                    # html.Br(),
                    html.Label(
                        ["2. Choose demographic"],
                        style={
                            "font-weight": "bold",
                            # "text-align": "center",
                            # "color": BLUE,
                            "fontSize": 14,
                        },
                    ),
                    dcc.Dropdown(
                        # define component_id for input of app@callback function
                        id="xtab1_val-bubble-dropdown",  # ID "xtab1_val-bubble-dropdown"
                        multi=False,
                        value="-",
                        # to be selected by user in dropdown
                        options=list_options(xtab1_vals),
                    ),
                ],
                id="xtab1-bubble-cardbody",  # ID "xtab1-bubble-cardbody"
            ),
        ],
        # color="info",
        outline="light",
    ),
]

bubble_big_card = dbc.Card(
    [
        dbc.CardHeader(html.H5("Compare across polls")),
        dbc.CardBody(
            [
                html.P(
                    "Hover over one of the bubbles to view question information. Click one of the polls to view more information in the drill down module. Configure the below options to filter the bubble chart.",
                    # style={"font-family": "Roboto"}
                ),
                dbc.Row(
                    [
                        # Place the filter components in a row with the bubble graph
                        dbc.Col(bubble_input_components, lg=3),
                        dbc.Col(
                            bubble_graph_component,
                            lg=9,
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
        [
            html.Label(
                ["Question text:"],
                id="question-label-heading",
                style={
                    "font-weight": "bold",
                    # "text-align": "center",
                    # "color": BLUE,
                    # "fontSize": 20,
                },
            ),
            html.Blockquote(
                ["Question:"],
                id="question-label",
            ),
        ],
        md={"width": 6, "offset": 2},
    ),
    dcc.Graph(
        id="bar-graph",  # ID "bar-graph"
        figure={},
        config={"displayModeBar": False},
    ),
]

bar_input_components = [
    html.Label(
        ["Select country:"],
        style={
            "font-weight": "bold",
            "text-align": "center",
            "color": BLUE,
            "fontSize": 16,
        },
    ),
    # TODO: show poll names instead of poll_id
    dcc.Dropdown(
        # define component_id for input of app@callback function
        id="country-dropdown",  # ID "country-dropdown"
        multi=False,
        value="USA",
        # to be selected by user in dropdown
        options=list_options(countries),
    ),
    html.Br(),
    html.Label(
        ["Select poll:"],
        style={
            "font-weight": "bold",
            "text-align": "center",
            "color": BLUE,
            "fontSize": 16,
        },
    ),
    # TODO: show poll names instead of poll_id
    dcc.Dropdown(
        # define component_id for input of app@callback function
        id="poll-dropdown",  # ID "poll-dropdown"
        multi=False,
        value=29,
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
            "fontSize": 16,
        },
    ),
    dcc.RadioItems(
        # define component_id for input of app@callback function
        id="question-dropdown",  # ID "question-dropdown"\
        value=26,
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
        inputStyle={"margin-right": "5px"},
    ),
    html.Br(),
    html.Label(
        ["Break down results by:"],
        id="xtab1-label",  # ID "x-tab1-label"
        style={
            "font-weight": "bold",
            "text-align": "center",
            "color": BLUE,
            "fontSize": 16,
        },
    ),
    dcc.RadioItems(
        # define component_id for input of app@callback function
        id="xtab1-dropdown",  # ID "x-tab1-dropdown"
        # multi=False,
        value="-",
        # to be selected by user in dropdown
        options=list_options(xtab1_vars),
        # try addding a right mark to the question text
        inputStyle={"margin-right": "5px", "margin-left": "5px"},
    ),
]


bar_big_card = dbc.Card(
    [
        dbc.CardHeader(html.H5("Drill down into individual polls")),
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
default_offset = 1
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
                                    src="https://raw.githubusercontent.com/UBICenter/ubicenter.org/master/assets/images/logos/wide-blue.jpg",  # LINK TO LOGO
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
                        "UBI Poll Tracker",
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
                        "Explore the state of public opinion on UBI across "
                        + str(len(poll_ids))
                        + " different polls from "
                        + str(len(countries))
                        + " countries.",
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
        # Link to contact email and github issue tracker
        dbc.Row(
            [
                dbc.Col(
                    [
                        # Create html header for general issues
                        html.H4(
                            [
                                "Questions or feedback? ",
                                "Email ",
                                html.A(
                                    "contact@ubicenter.org",
                                    href="mailto:contact@ubicenter.org",
                                    target="blank",
                                ),
                                " or file an issue at ",
                                html.A(
                                    "github.com/UBICenter/polls/issues",
                                    href="http://github.com/UBICenter/polls/issues",
                                    target="blank",
                                ),
                            ],
                            style={
                                "text-align": "left",
                                "color": "gray",
                                "fontSize": 12,
                                "font-family": "Roboto",
                            },
                        ),
                        # Create html header for submitting polls
                        html.H4(
                            [
                                "Found a poll we're missing? ",
                                "Let us know ",
                                html.A(
                                    "here",
                                    href="https://github.com/UBICenter/polls/issues/new?assignees=&labels=new-poll&template=new-poll.md&title=Add+poll+from+%5Bpollster%5D+on+%5Bdates%5D",
                                    target="blank",
                                ),
                            ],
                            style={
                                "text-align": "left",
                                "color": "gray",
                                "fontSize": 12,
                                "font-family": "Roboto",
                            },
                        ),
                    ],
                    md={"size": 8, "offset": 1},
                ),
            ]
        ),
    ]
)

# -------------------------------------------------------- #
#                     Assign Bar Graph module callbacks                     #
# --------------------------------------------------------
# update bar graph dropdown selections based on clickData from bubble-graph


@app.callback(
    Output("country-dropdown", "value"),
    Output("poll-dropdown", "value"),
    Output("question-dropdown", "value"),
    # TODO: output should include selected question
    Input("bubble-graph", "clickData"),
    Input("country-dropdown", "value"),
    Input("poll-dropdown", "value"),
    Input("question-dropdown", "value"),
    # this prevents the callback from loading when the app starts
    prevent_initial_call=True,
)
def update_bar_graph_selections_with_click(
    clickData, country_value_in, poll_value_in, question_value_in
):
    # NOTE This section is the view callback context, #TODO delete
    ctx = dash.callback_context
    prop_id = ctx.triggered[0]["prop_id"]
    if prop_id == "bubble-graph.clickData":
        # the element "customdata" is defined by an argument in the px.scatter() call in the bubble_chart() function in the visualize.py file. The order of the items in customdata is important, but the order is set arbitrarily
        country_value_out = clickData["points"][0]["customdata"][2]
        poll_value_out = clickData["points"][0]["customdata"][0]
        question_value_out = clickData["points"][0]["customdata"][1]
        return country_value_out, poll_value_out, question_value_out
    elif prop_id == "country-dropdown.value":
        country_value_out = country_value_in

        # subset polls based on selected country
        poll_ids_sorted = (
            r[r.country == country_value_in]
            .sort_values("date", ascending=False)
            .poll_id.unique()
        )
        # populate poll-dropdown value with most recent poll as default
        poll_value_out = poll_ids_sorted[0]

        # populate first question from poll as default
        question_value_out = r[
            r.poll_id == poll_value_out
        ].question_id.unique()[0]

        return country_value_out, poll_value_out, question_value_out
    elif prop_id == "poll-dropdown.value":
        country_value_out = country_value_in
        poll_value_out = poll_value_in
        question_value_out = r[
            r.poll_id == poll_value_out
        ].question_id.unique()[0]

        return country_value_out, poll_value_out, question_value_out


# NOTE this one is probabably fine as is
@app.callback(
    Output("bar-graph", "figure"),
    Input("poll-dropdown", "value"),
    Input("question-dropdown", "value"),
    Input("xtab1-dropdown", "value"),
)
def return_bar_graph(poll, question, xtab1):

    # NOTE debugging here
    # if not xtab selected then choose default value
    if (xtab1 is None) or (xtab1 == []):
        xtab1 = "-"

    bar = visualize.poll_vis(
        responses=r,
        poll_id=poll,
        question_id=question,
        crosstab_variable=xtab1,
    )

    return bar


# ------ update poll, question, crosstab options based on country dropdown ----- #
@app.callback(
    Output("poll-dropdown", "options"),
    Input("country-dropdown", "value"),
)
def update_poll_options(country_dropdown_value):
    """update poll options based on country dropdown"""
    # get list of poll_ids for selected country, sorted by newest to oldest
    poll_ids_sorted = (
        r[r.country == country_dropdown_value]
        .sort_values("date", ascending=False)
        .poll_id.unique()
    )

    poll_options = [
        {
            # shoud look like "Pew Research Center (2021-4-22)"
            "label": "{} ({})".format(
                polls.loc[id, "pollster"],
                polls.loc[id, "date"],
            ),
            "value": id,
        }
        for id in poll_ids_sorted
    ]

    return poll_options


# ------ update question options based on poll dropdown ----- #
@app.callback(
    Output("question-dropdown", "options"),
    # NOTE value is output here
    # Output("question-dropdown", "value"),
    # we want to update the default question based on the poll selected
    Input("poll-dropdown", "value"),
    # we also want to update the default question when a new country is selected
    Input("country-dropdown", "value"),
)
def update_question_options_and_value(
    poll_dropdown_value, country_dropdown_value
):

    # ---------------------------------------------------- #
    question_options = [
        # this part returns the question text based on the provided question id
        {
            "label": "{}".format(
                r.loc[r.question_id == x, "question_text"].max()
            ),
            "value": x,
        }
        # this part returns the unique question ids associated with the selected poll id in responses_merged.csv
        for x in r[r.poll_id == poll_dropdown_value].question_id.unique()
    ]

    if poll_dropdown_value is None:
        question_options = [
            {
                "label": "Please select a poll first",
                "value": "",
            }
        ]
    return question_options
    # NOTE commented out code below is only for if we still include the question-dropdown value in the column
    # default_question = question_options[0]["value"] if question_options else None
    # return question_options, default_question


# ------ update xtab1 options based on question dropdown ----- #
@app.callback(
    Output("question-label", "children"),
    Output("xtab1-dropdown", "options"),
    Output("xtab1-label", "style"),
    Output("xtab1-dropdown", "style"),
    # NOTE: deactivate second crosstab for now
    # Output(component_id="xtab2-dropdown", component_property="options"),
    Input("question-dropdown", "value"),
    Input("poll-dropdown", "value"),
)
def update_xtab1_options_and_visibility(
    question_dropdown_value, poll_dropdown_value
):
    """update xtab1 options based on question dropdown"""

    # this places the question text above the bar graph
    question_label = '"{}"'.format(
        r.loc[r.question_id == question_dropdown_value, "question_text"].max()
    )

    # replace xtab1 dropdown options with the relavent options for the selected question
    xtab1_options = list_options(
        r[
            (r.question_id == question_dropdown_value)
            & (r.poll_id == poll_dropdown_value)
        ].xtab1_var.unique()
    )

    # define the style for xtab1-label (if relevant)
    label_style = {
        "font-weight": "bold",
        "text-align": "center",
        "color": BLUE,
        "fontSize": 20,
        # "display": "block",
    }

    if len(xtab1_options) > 1:
        return question_label, xtab1_options, label_style, {"display": "block"}
    else:
        return (
            question_label,
            xtab1_options,
            {"display": "none"},
            {"display": "none"},
        )


# NOTE MAYBE couuld combine with below callback. actually no - maybe
@app.callback(
    Output("xtab1-dropdown", "value"),
    Input("country-dropdown", "value"),
    Input("poll-dropdown", "value"),
    Input("question-dropdown", "value"),
)
def set_default_xtab1_value(country, poll, question):
    """set xtab1 value to default value if country, poll, question changed"""
    return "-"


# -------------------------------------------------------- #
#                bubble chart tab callbacks                #
# -------------------------------------------------------- #


# update bubble chart based on country dropdown, crosstab variable, crosstab value
@app.callback(
    # output the relevent xtab1_val based on selected xtab1_var
    Output("xtab1-bubble-dropdown", "options"),
    # output the relevent xtab1_val based on selected xtab1_var
    Output("xtab1_val-bubble-dropdown", "options"),
    # country input will be list
    Output("bubble-graph", "figure"),
    # # this is to update xtab1_val-bubble-dropdown VALUE based on selected xtab1_var
    # Output(component_id="xtab1_val-bubble-dropdown", component_property="value"),
    Input("country-dropdown-2", "value"),
    # xtab1-bubble-dropdown input will be a string
    Input("xtab1-bubble-dropdown", "value"),
    Input("xtab1_val-bubble-dropdown", "value"),
)
def update_bubble_chart(
    countries,
    xtab1_var,
    xtab1_val,
):
    # subsets r to only include the selected countries
    r_sub = r[r.country.isin(countries)]

    # updates xtab1-bubble-dropdown options based on selected country
    xtab1_options = list_options(r_sub.xtab1_var.unique())

    # updates xtab1_val-bubble-dropdown options based on selected xtab1_var
    xtab1_val_options = list_options(
        r_sub[r_sub.xtab1_var == xtab1_var].xtab1_val.unique()
    )

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


# -------------------------------------------------------- #
#                      other callbacks                     #
# -------------------------------------------------------- #
# callback to download responses_merged.csv
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def download_button(n_clicks):
    return dcc.send_data_frame(r.to_csv, "responses.csv")


if __name__ == "__main__":
    app.run_server(debug=True, port=8060, host="127.0.0.1")
