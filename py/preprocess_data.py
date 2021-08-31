import pandas as pd

responses = pd.read_csv("data/responses.csv")
polls = pd.read_csv("data/polls.csv")
pollsters = pd.read_csv("data/pollsters.csv")
favorability = pd.read_csv("data/favorability.csv")
questions = pd.read_csv("data/questions.csv")
xtab_order = pd.read_csv("data/xtab_order.csv")

# convert val_order to int
xtab_order["val_order"] = xtab_order["val_order"].astype(int)

# Columns to group each poll responses to.
IDS = [
    "poll_id",
    "question_id",
    "xtab1_var",
    "xtab1_val",
    "xtab2_var",
    "xtab2_val",
]

total_by_poll = (
    responses.groupby(IDS)
    .pct.sum()
    .reset_index()
    .rename(columns={"pct": "total_percentage"})
)
# merge total_by_poll and responses, create new normalized percentage column
responses = responses.merge(total_by_poll, on=IDS)
responses["percent_norm"] = responses.pct / responses.total_percentage
responses = responses.merge(favorability, on=["question_id", "response"])
responses["pct_fav"] = responses.favorability * responses.pct
# Also merge to poll table.
responses.poll_id = responses.poll_id.astype(float)
responses = responses.merge(polls, on="poll_id")
# Make sample_size numeric, treat missing sample sizes as zero.
# added data validation to spreadsheet
# responses2.sample_size = pd.to_numeric(
#     responses2.sample_size.str.replace(",", ""), errors="coerce"
# )
# Merge to get question text.
responses = responses.merge(questions, on="question_id")
# merge to get val_order
responses = responses.merge(xtab_order, on=["xtab1_var", "xtab1_val"], how="left")
# fill missing val order with 0
responses.val_order.fillna(0, inplace=True)
# convert data column to yyyy-mm-dd format
responses["date"] = pd.to_datetime(responses.date, format="%Y-%m-%d")

# set poll_id, vall_order as int
responses[["poll_id", "val_order"]] = responses[["poll_id", "val_order"]].astype(int)
# Wrap question text and pollster
def plotly_wrap(x, length=30):
    return x.str.wrap(length).apply(lambda x: x.replace("\n", "<br>"))


responses["question_text_wrap"] = plotly_wrap(responses.question_text)
responses["pollster_wrap"] = plotly_wrap(responses.pollster, 20)

responses.to_csv("data/responses_merged.csv", index=False)
