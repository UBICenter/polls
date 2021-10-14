# import ubicenter
from inspect import trace
from dash_html_components.Label import Label
import plotly.express as px
import plotly.graph_objects as go
import ubicenter
import numpy as np
import textwrap
from datetime import datetime, timedelta
import pandas as pd
import itertools

# Define UBI Center colors
BLUE = "#1976D2"
DARK_BLUE = "#1565C0"
LIGHT_BLUE = "#90CAF9"
GRAY = "#BDBDBD"
BARELY_BLUE = "#E3F2FD"
# Define other colors
VERY_DARK_GRAY = "#333333"
DARK_GRAY = "#444444"
DARK_GRAY = "#A9A9A9"
LIGHT_GRAY = "#999999"
VERY_LIGHT_GRAY = "#CCCCCC"
BLACK = "#000000"
WHITE_SMOKE = "#F5F5F5"
SILVER = "#C0C0C0"

VARIABLE_MAPPING = {
    "Poll ID": "poll_id",
    "Question ID": "question_id",
    "Cross-tab variable 1": "xtab1_var",
    "Cross-tab value 1": "xtab1_val",
    "Cross-tab variable 2": "xtab2_var",
    "Cross-tab value 2": "xtab2_val",
    "Sample size": "sample_size",
    "Question text": "question_text",
    "Percentage": "pct",
    "Response": "response",
    "Favorability": "favorability",
    "Date": "date",
    "Pollster": "pollster",
    "Notes": "notes",
}

variable_mapping_inverse = {v: k for k, v in VARIABLE_MAPPING.items()}
variable_mapping_inverse["question_text_wrap"] = "Question"
variable_mapping_inverse["pollster_wrap"] = "Pollster"
variable_mapping_inverse["pct_fav"] = "Net favorability"

# function to replicate ubicenter's format_fig function enough for dash


def format_fig(fig, show=True):
    CONFIG = {"displayModeBar": False}
    fig.update_xaxes(
        title_font=dict(size=16, color="black"), tickfont={"size": 14}
    )
    fig.update_yaxes(
        title_font=dict(size=16, color="black"), tickfont={"size": 14}
    )
    fig.update_layout(
        hoverlabel_align="right",
        # font_family="Arial",
        title_font_size=20,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    if show:
        fig.show(config=CONFIG)
    else:
        return fig


def poll_vis(responses, poll_id, question_id=None, crosstab_variable="-"):
    """returns bar graph"""
    # ------------------ subset the data ----------------- #
    if question_id is None:
        target_questions = responses[
            responses.poll_id == poll_id
        ].question_id.unique()
        # check if there's only one question for the poll, if there's more than 1 --
        # tell the user that's not supported
        assert target_questions.size == 1, "Please select a question:"
        # + target_questions -- have the assert statement include a list of the question options
        question_id = target_questions[0]
    target_responses = responses[
        (responses.poll_id == poll_id)
        & (responses.question_id == question_id)
        & (responses.xtab1_var == crosstab_variable)
        # make sure that we're not including any responses for the first cross-tab variable that have a second cross-tab variable
        & (responses.xtab2_var == "-")
    ]

    # create a list comprehsion to get the response labels in the same order as the response order

    top_labels = target_responses.sort_values(
        by=["response_order"]
    ).response_shortened.unique()

    resp_df = target_responses.sort_values(by=["response_order"])[
        [
            "response_shortened",
            "percent_norm",
            "favorability",
            "response_order",
            "pct_fav",
        ]
    ]

    def wrap_string(text, n):
        """add plotly-compliant linebreaks to a string without breaking words across lines

        Parameters
        ----------
        text : str
            a string that you want to format
        n : int
            number of characters after which you want to add a linebreak

        Returns
        -------
        string
            formatted string
        """
        return "<br>".join(textwrap.wrap(str(text), n, break_long_words=False))

    # wrap top_labels to a manageable width
    def wrap_labels(labels, n):
        """wraps each string in a list to a given length without breaking words across lines using plotly-compliant line breaks

        Parameters
        ----------
        labels : list
            list of strings to format
        n : int
            number of characters after which you want to add a linebreak

        Returns
        -------
        list
            list of formatted strings
        """
        return [wrap_string(label, n) for label in labels]

    # ---------------------- colors ---------------------- #
    STRONG_OPP = "#777777"
    WEAK_OPP = "#A9A9A9"
    NUETRAL = "#F5F5F5"
    WEAK_SUP = "#4998E2"
    STRONG_SUP = "#1565C0"

    if len(top_labels) == 6:
        colors = [STRONG_OPP, WEAK_OPP, NUETRAL, NUETRAL, WEAK_SUP, STRONG_SUP]
        top_labels = wrap_labels(top_labels, 7)
    elif len(top_labels) == 5:
        colors = [STRONG_OPP, WEAK_OPP, NUETRAL, WEAK_SUP, STRONG_SUP]
        top_labels = wrap_labels(top_labels, 7)
    elif len(top_labels) == 4:
        colors = [STRONG_OPP, WEAK_OPP, WEAK_SUP, STRONG_SUP]
        top_labels = wrap_labels(top_labels, 10)
    elif len(top_labels) == 3:
        colors = [STRONG_OPP, NUETRAL, STRONG_SUP]
        top_labels = wrap_labels(top_labels, 15)

    elif len(top_labels) == 2:
        colors = [STRONG_OPP, STRONG_SUP]
        top_labels = wrap_labels(top_labels, 15)

    # ------------------ prepare inputs ------------------ #
    # create list of unique xtab1_vals ordered by val_order
    xtab1_vals = target_responses.sort_values(
        by=["val_order"], ascending=False
    ).xtab1_val.unique()
    # create list of lists of the percent_norm of each response in order of response_order
    # eg. [0.27 0.12 0.06 0.23 0.32]
    x_data = [
        target_responses[target_responses.xtab1_val == val]
        .sort_values(by=["response_order"])
        .percent_norm.values
        for val in xtab1_vals
    ]

    # create list of y_data that is used to label the bars eg. ["Black", "Hispanic", "White"]
    y_data = xtab1_vals

    net_fav_df = target_responses.groupby(["xtab1_val"])["pct_fav"].sum()

    # NOTE this updates the figure with an empty fig so the function plays nice with the callbacks
    if len(x_data) < 1:
        return {}

    # ---------------------------------------------------- #
    #                 actual graph creation                #
    # ---------------------------------------------------- #
    fig = go.Figure()

    # example: if there is a 5-point response scale, than we would iterate through [0, 1, 2, 3, 4]
    for i in range(0, len(x_data[0])):
        for xd, yd in zip(x_data, y_data):
            # NOTE: this is tricky, the traces are drawn from the bottom left corner up
            fig.add_trace(
                go.Bar(
                    x=[xd[i]],
                    y=[yd],
                    orientation="h",
                    text=["{:.0%}".format(xd[i])],
                    textposition="inside",
                    name=top_labels[i],
                    insidetextanchor="middle",
                    insidetextfont=dict(
                        family="Arial",
                        size=20,
                    ),
                    marker=dict(
                        color=colors[i],
                        line=dict(color="rgb(248, 248, 249)", width=1),
                    ),
                    width=0.4 if len(y_data) == 1 else (),
                    hoverinfo="skip",
                    showlegend=True,
                )
            )

    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
            domain=[0.15, 1],
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
        paper_bgcolor="rgb(248, 248, 255)",
        plot_bgcolor="rgb(248, 248, 255)",
        margin=dict(l=120, r=10, t=140, b=80),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            traceorder="normal",
            xanchor="left",
            x=0.15,
            y=1.02,
        ),
        barmode="stack",
    )
    # ex. if there are 3 horizontal bars with 5-point response scale, then len(fig.data) will be 15
    for i in range(1, len(fig.data)):
        # eg. check if trace is
        if i % len(y_data) != 0:
            fig.data[i].showlegend = False
    # ---------------------------------------------------- #
    #                 Label the bar graphs                 #
    # ---------------------------------------------------- #
    annotations = []
    for yd, xd in zip(y_data, x_data):
        # labeling the y-axis
        annotations.append(
            dict(
                xref="paper",
                yref="y",
                x=0.14,
                y=yd,
                xanchor="right",
                text=wrap_string(str(yd), 15) if yd != "-" else "All",
                font=dict(family="Arial", size=14, color="rgb(67, 67, 67)"),
                showarrow=False,
                align="right",
            )
        )
        # add the net favorability for each bar
        # add a trace to the end to display the net favorability
        fig.add_trace(
            go.Bar(
                x=[0.10],
                y=[yd],
                orientation="h",
                text="<b>{fav:+.0f}</b>".format(
                    fav=net_fav_df[yd]
                ),  # NOTE test if we can do auto text to label the graphs
                textposition="inside",  # NOTE test if we can do auto text to label the graphs
                insidetextanchor="middle",
                insidetextfont=dict(
                    family="Arial",
                    size=20,
                ),
                marker=dict(color="white", line=dict(color="white", width=1)),
                hoverinfo="skip",
                showlegend=False,
            ),
        )

    fig.update_layout(
        annotations=annotations,
        margin=dict(l=10, r=20, t=60, b=80),
    )

    fig.update_yaxes(automargin=True)
    fig.update_xaxes(automargin=True)

    # -------- format source information at bottom ------- #
    pollster = target_responses.loc[:, ["pollster"]].values[0][0]
    xtab1_var = target_responses.loc[:, ["xtab1_var"]].values[0][0]
    date = target_responses.loc[:, ["date"]].values[0][0]
    date = pd.to_datetime(date).strftime("%B %Y")
    url = target_responses.loc[:, ["Link"]].values[0][0]
    country = target_responses.loc[:, ["country"]].values[0][0]
    demographic = target_responses.loc[:, ["demographic"]].values[0][0]

    try:
        sample_size = int(
            target_responses.loc[:, ["sample_size"]].values[0][0]
        )
        sample_size = "{:,}".format(sample_size)
    except:
        sample_size = ""

    # Change source text depending on whether this is actually the Swiss Referendum
    if poll_id == 3:
        source_text = "Results of 2016 Swiss referendum in which 2,494,848 votes were cast."
    else:
        source_text = "Survey of {sample_size} {demographic}, {country} by {pollster}, {date}. Retrieved from ".format(
            sample_size=sample_size,
            demographic=demographic,
            pollster=pollster,
            country=country,
            date=date,
        )

    # ---------------------------------------------------- #
    source_url = "<br><a target='blank' href='{}'>{}</a>".format(url, url)

    source = wrap_string(source_text, 100) + source_url

    # add annotation for data source
    fig.add_annotation(
        xref="paper",
        yref="paper",
        xanchor="left",
        x=0.15,
        y=-0.25,
        text=source,
        font=dict(family="Arial", size=12, color="rgb(67, 67, 67)"),
        align="left",
        showarrow=False,
    )

    ubicenter.add_ubi_center_logo(fig, y=-0.2)

    # NOTE: use format_fig as defined above instead of ubicenter.format_fig
    return format_fig(fig, show=False).update_layout(autosize=True)


# Function to create a bubble chart for % favorability across a set of poll/question pairs.
def bubble_chart(responses, poll_ids=None, question_ids=None, xtab1_val="-"):
    """[summary]

    Parameters
    ----------
    responses : [type]
        [description]
    poll_ids : [type], optional
        [description], by default None
    question_ids : [type], optional
        [description], by default None
    xtab1_var : str, optional
        [description], by default "-"
    xtab1_val : str, optional
        [description], by default "-"
    """
    # TODO (ideas):
    # 1) Add the line to zero for a "stem" chart (also add a zero hline)
    # 2) xtab2_var and xtab2_val
    # 3) Formal function docstring.
    # 4) Set color palettes for ordinal xtabs (also something for gender?)
    # Subset the data per the specifications.
    target_data = responses[
        (responses.xtab1_val == xtab1_val) & (responses.xtab2_val == "-")
    ]
    # Only subset by xtab1_val if we're not splitting by it.
    xtab_split = xtab1_val != "-"
    if not xtab_split:
        target_data = target_data[target_data.xtab1_val == xtab1_val]
    # Summarize to the poll/question level.
    GROUPBY = [
        "poll_id",
        "question_id",
        "question_text_wrap",
        "date",
        "pollster_wrap",
        "sample_size",
        "country",
        "short_question",
    ]
    # add xtab1_var and xtab1_val if we're \ splitting by it.
    if xtab_split:
        GROUPBY += ["xtab1_var", "xtab1_val", "xtab2_var", "xtab2_val"]
    poll_question = target_data.groupby(GROUPBY).pct_fav.sum().reset_index()
    # filter poll_ids and question_ids if specified
    if poll_ids is not None:
        poll_question = poll_question[poll_question.poll_id.isin(poll_ids)]
    if question_ids is not None:
        poll_question = poll_question[
            poll_question.question_id.isin(question_ids)
        ]

    # Set arguments that are common across figures conditionally created by the xtab_split
    opacity = 0.5
    custom_data = [
        "poll_id",
        "question_id",
        "country",
        "short_question",
        "sample_size",
        "pollster_wrap",
        "date",
    ]

    if xtab_split:
        variable_mapping_inverse_tmp = variable_mapping_inverse.copy()
        variable_mapping_inverse_tmp["xtab1_val"] = xtab1_val
        fig = px.scatter(
            poll_question,
            x="date",
            y="pct_fav",
            color="country",
            # text="pollster_wrap",
            opacity=opacity,
            hover_data=custom_data,
            labels=variable_mapping_inverse_tmp,
        )

        # add title based on xtab1_val
        fig.update_layout(title=xtab1_val)

    # this is our default map when you first run the script
    else:
        fig = px.scatter(
            poll_question,
            x="date",
            y="pct_fav",
            color="country",
            opacity=opacity,
            custom_data=custom_data,
            labels=variable_mapping_inverse,
        )

    fig.update_traces(
        # set size of bubbles,
        marker_size=8,
        # Add hover text, which will display instead of custom_data. Custom data is still available to the click event that updates the bar graph
        hovertemplate="<br>".join(
            [
                "<b>%{customdata[3]}</b>",
                "%{customdata[2]}",
                "Net favorability: %{y:+.0f}",
                "%{customdata[5]}, %{x}",
                "<extra></extra>",
            ]
        ),
        hoverlabel_align="left",
    )

    # add a Range slider to the graph
    fig.update_xaxes(rangeslider_visible=True)

    # get the date of the most recent poll, and add one month to it
    date_range_max = (poll_question.date.max() + timedelta(days=60)).strftime(
        "%Y-%m-%d"
    )

    initial_range = ["2016-01-01", date_range_max]

    fig.update_layout(
        # update default xaxis range
        xaxis_range=initial_range,
        clickmode="event+select",
        xaxis=dict(
            title=None,  # date self-explanatory
        ),
        legend_title_text=None,  # country self-explanatory
        autosize=True,
        # define hoverlabel characteristics
        hoverlabel=dict(bgcolor="white", font_size=16, font_family="Arial"),
    )

    # add line for zero net fav
    fig.add_hline(
        y=0,
        line_width=3,
        line_dash="dot",
        line_color=GRAY,
    )

    # add annotation for net fav
    net_fav_explanation = "<br>".join(
        textwrap.wrap(
            str(
                'Net favorability refers to the difference between the percentage of those surveyed expressing agreement/support towards the more "pro-UBI" position, and those that expressed disagreement/opposition.'
            ),
            70,
            break_long_words=False,
        )
    )

    fig.add_annotation(
        xref="paper",
        yref="paper",
        xanchor="left",
        x=0.0,
        y=-0.55,
        text=net_fav_explanation,
        font=dict(family="Arial", size=10, color="rgb(67, 67, 67)"),
        align="left",
        showarrow=False,
    )

    ubicenter.add_ubi_center_logo(fig, x=1.15, y=-0.16)

    return format_fig(fig, show=False)
