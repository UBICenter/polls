# import ubicenter
import plotly.express as px
import plotly.graph_objects as go
from py import preprocess_data as ppd
import ubicenter
import numpy as np

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
variable_mapping_inverse["pct_fav"] = "% favorability"

# function to replicate ubicenter's format_fig function enough for dash
def format_fig(fig,show=True):
    CONFIG = {"displayModeBar": False}
    ubicenter.add_ubi_center_logo(fig)
    fig.update_xaxes(
        title_font=dict(size=16, color="black"), tickfont={"size": 14}
    )
    fig.update_yaxes(
        title_font=dict(size=16, color="black"), tickfont={"size": 14}
    )
    fig.update_layout(
        hoverlabel_align="right",
        font_family="Roboto",
        title_font_size=20,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    if show:
        fig.show(config=CONFIG)
    else:
        return fig

# alternative version of the above function, with a different means of making plots
def poll_vis(responses, poll_id, question_id=None, crosstab_variable="-"):
    # --------------- copied from visualize.py --------------- #
    if question_id is None:
        target_questions = responses[responses.poll_id == poll_id].question_id.unique()
        # check if there's only one question for the poll, if there's more than 1 --
        # tell the user that's not supported
        assert target_questions.size == 1, "Please select a question:"
        # + target_questions -- have the assert statement include a list of the question options
        question_id = target_questions[0]
    target_responses = responses[
        (responses.poll_id == poll_id)
        & (responses.question_id == question_id)
        & (responses.xtab1_var == crosstab_variable)
    ]

    # target_responses["question_text_wrap"] = ppd.plotly_wrap(target_responses.question_text.copy(),130)
    # # question_text=target_responses["question_text_wrap"].iloc[0] 
    # question_text=target_responses["question_text_wrap"].unique()[0] if target_responses.shape[0] > 0 else "No question text"

    # ------------------ copied from plotly ------------------ #
    #
    response_set_df=target_responses[["response","response_order"]]

    # response set in order
    response_set = target_responses[["response","response_order"]].sort_values(by=["response_order"]).response.unique()
    # create a list comprehsion to get the response labels in the same order as the response order
    top_labels = [x.replace(" ","<br>") for x in target_responses.sort_values(by=["response_order"]).response.unique()]
    # find the line length of the longest in top_labels
    max_line_length = max([x.count("a") for x in top_labels])

    # Define UBI Center colors
    BLUE = "#1976D2"
    DARK_BLUE = "#1565C0"
    LIGHT_BLUE = "#90CAF9"
    GRAY = "#BDBDBD"
    BARELY_BLUE = "#E3F2FD"
    # Define other colors
    SUPER_DARK_GRAY = "#222222"
    VERY_DARK_GRAY = "#333333"
    DARK_GRAY = "#444444"
    BLACK = "#000000"

    colors=[
        DARK_BLUE, 
        BLUE, 
        LIGHT_BLUE, 
        BARELY_BLUE,
        GRAY, 
        ]

    colors = colors[::-1]

    #lighter grays, darker blues
    colors = ["#494848", "#636363" ,"#B4B4B4", BLUE, DARK_BLUE]
    # VERY_DARK_GRAY to VERY_LIGHT_GRAY
    colors = [VERY_DARK_GRAY, DARK_GRAY, "#B4B4B4", BLUE, DARK_BLUE]
    if len(top_labels) == 5:
        colors = [VERY_DARK_GRAY, DARK_GRAY, GRAY, BLUE, DARK_BLUE]
    elif len(top_labels) == 4:
        colors = [VERY_DARK_GRAY, DARK_GRAY, BLUE, DARK_BLUE]
    elif len(top_labels) == 3:
        colors = [DARK_GRAY, GRAY, BLUE]
    elif len(top_labels) == 2:
        colors = [DARK_GRAY, BLUE]
    
    TEXTCOLORS = ['rgb(248, 248, 255)','rgb(248, 248, 255)','rgb(248, 248, 255)','rgb(248, 248, 255)','rgb(248, 248, 255)']

    # create list of lists of the percent_norm of each response in order of response_order
    x_data = [[x for x in target_responses[target_responses.xtab1_val==val].sort_values(by=["response_order"]).percent_norm.values] for val in target_responses.xtab1_val.unique()]


    # create list of y_data corresponding to the xtab1_val
    y_data = [y for y in target_responses.xtab1_val.unique()]


    fig = go.Figure()

    # this is likely an artifact from constructing the dataset in the plotly example
    for i in range(0, len(x_data[0])):
        for xd, yd in zip(x_data, y_data):
            fig.add_trace(go.Bar(
                x=[xd[i]], y=[yd],
                orientation='h',
                marker=dict(
                    color=colors[i],
                    line=dict(color='rgb(248, 248, 249)', width=1)
                )
            ))

    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
            domain=[0.15, 1]
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
        barmode='stack',
        paper_bgcolor='rgb(248, 248, 255)',
        plot_bgcolor='rgb(248, 248, 255)',
        margin=dict(l=120, r=10, t=140, b=80),
        showlegend=False,
    )

    annotations = []

    for yd, xd in zip(y_data, x_data):
        # labeling the y-axis
        annotations.append(dict(xref='paper', yref='y',
                                x=0.14, y=yd,
                                xanchor='right',
                                text=str(yd),
                                font=dict(family='Arial', size=14,
                                        color='rgb(67, 67, 67)'),
                                showarrow=False, align='right'))
        # labeling the first percentage of each bar (x_axis)
        annotations.append(dict(xref='x', yref='y',
                                x=xd[0] / 2, y=yd,
                                text = '{:.0%}'.format(xd[0]),
                                # text=str(xd[0]) + '%',
                                font=dict(family='Arial', size=14,
                                        color='rgb(248, 248, 255)'),
                                showarrow=False))
        # labeling the first Likert scale (on the top)
        if yd == y_data[-1]:
            annotations.append(dict(xref='x', yref='paper',
                                    x=xd[0] / 2, y=1.1,
                                    text=top_labels[0],
                                    font=dict(family='Arial', size=14,
                                            color='rgb(67, 67, 67)'),
                                    showarrow=False))
        space = xd[0]
        for i in range(1, len(xd)):
                # labeling the rest of percentages for each bar (x_axis)
                annotations.append(dict(xref='x', yref='y',
                                        x=space + (xd[i]/2), y=yd,
                                        text = '{:.0%}'.format(xd[i]),
                                        # text=str(xd[i]) + '%',
                                        font=dict(family='Arial', size=14,
                                                color=TEXTCOLORS[i]),
                                        showarrow=False))
                # labeling the Likert scale
                if yd == y_data[-1]:
                    annotations.append(dict(xref='x', yref='paper',
                                            x=space + (xd[i]/2), y=1.1,
                                            text=top_labels[i],
                                            font=dict(family='Arial', size=14,
                                                    color='rgb(67, 67, 67)'),
                                            showarrow=False))
                space += xd[i]

    fig.update_layout(
        annotations=annotations,
        margin=dict(l=10, r=10, t=80, b=80),
        )
    fig.update_yaxes(automargin=True)
    fig.update_xaxes(automargin=True)

    # fig.show()
    # NOTE: use format_fig as defined above instead of ubicenter.format_fig
    return format_fig(fig,show=False)   



# Function to create a bubble chart for % favorability across a set of poll/question pairs.
def bubble_chart(responses, poll_ids=None, question_ids=None,  xtab1_val="-"):
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
    target_data = responses[(responses.xtab1_val == xtab1_val)&(responses.xtab2_val=="-")]
    # Only subset by xtab1_val if we're not splitting by it.
    xtab_split = (xtab1_val != "-")
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
        "country"
    ]
    # add xtab1_var and xtab1_val if we're \ splitting by it.
    if xtab_split:
        GROUPBY += ["xtab1_var","xtab1_val","xtab2_var","xtab2_val"]
    poll_question = target_data.groupby(GROUPBY).pct_fav.sum().reset_index()
    # filter poll_ids and question_ids if specified
    if poll_ids is not None:
        poll_question = poll_question[poll_question.poll_id.isin(poll_ids)]
    if question_ids is not None:
        poll_question = poll_question[poll_question.question_id.isin(question_ids)]
    # return poll_question
    # Visualize as a scatter chart.
    size=(poll_question.sample_size+1)**0.3
    size_max=20

    if xtab_split:
        variable_mapping_inverse_tmp = variable_mapping_inverse.copy()
        variable_mapping_inverse_tmp["xtab1_val"] = xtab1_val
        fig = px.scatter(
            poll_question,
            x="date",
            y="pct_fav",
            color="country", 
            text="pollster_wrap",
            # size=np.log(poll_question.sample_size+1),
            size="sample_size",
            # size_max=size_max,
            hover_data=["poll_id","question_id","sample_size"],
            labels=variable_mapping_inverse_tmp,
        )
        
        # add title based on xtab1_val
        fig.update_layout(title=xtab1_val)
        # fig.add_hline(y=0, line_color="red")        
        
        
    else:
        fig = px.scatter(
            poll_question,
            x="date",
            y="pct_fav",
            color="country",
            # text="pollster_wrap",
            # size=np.log(poll_question.sample_size+1),
            size=size,
            size_max=size_max,
            hover_data=["poll_id","question_id","sample_size",],
            labels=variable_mapping_inverse,
            trendline='ols'
        )
    
    fig.update_layout(clickmode="event+select",)
    
    return format_fig(fig,show=False)   
    # FIXME: this breaks the size of the bubble chart.     
    # return ubicenter.format_fig(fig,show=False)
