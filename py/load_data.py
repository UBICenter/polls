import pandas as pd

VARIABLE_MAPPING = {
    "Poll ID": "poll_id",
    "Question ID": "question_id",
    "Cross-tab variable 1": "xtab1_var",
    "Cross-tab value 1": "xtab1_val",
    "Cross-tab variable 2": "xtab2_var",
    "Cross-tab value 2": "xtab2_val",
    "Sample size": "sample_size",
    "Question text": "question_text",
    "percentage": "pct",
    "Response": "response",
    "Favorability": "favorability",
    "Date": "date",
    "Pollster": "pollster",
    "Notes": "notes",
}


def get_data(gid, f):
    temp = (
        pd.read_csv(
            "https://docs.google.com/spreadsheets/d/"
            + "1ulqohI6YLYFsz3wm8f5j6BS_JVelu2Ea8SXXa-wwkhQ"
            + "/export?gid="
            + str(gid)
            + "&format=csv",
            # Set first column as rownames in data frame
            index_col=0,
        )
        .reset_index()
        .rename(columns=VARIABLE_MAPPING)
    )
    # strip any whitespace from the text
    temp.columns = temp.columns.str.strip()
    temp.to_csv("data/" + f + ".csv", index=False)


get_data(0, "responses")
get_data(1080881848, "polls")
get_data(1983382452, "pollsters")
get_data(109990425, "questions")
get_data(1152857355, "favorability")
get_data(935642594, "xtab_order")
