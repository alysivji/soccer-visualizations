"""Transform results dataset into tidy data

https://en.wikipedia.org/wiki/Tidy_data"""

import numpy as np
import pandas as pd

# TODO figure out airflow logging
# print(f"pandas version: {pd.__version__}")
# print(f"numpy version: {np.__version__}")

divisions = {"E0": "EPL", "D1": "Bundesliga1", "I1": "SerieA", "SP1": "LaLigaPrimera"}

points = {"W": 3, "D": 1, "L": 0}


def get_result(score, score_opp):
    """Given score, calculate result
    ## http://stackoverflow.com/questions/19914937/
    ## applying-function-with-multiple-arguments-to-create-a-new-pandas-column
    """
    if score == score_opp:
        return "D"
    elif score > score_opp:
        return "W"
    else:
        return "L"


def transform_results_data(ds, **kwargs):
    """Turns results data into tidy dataset"""
    results_file = "/tmp/work/premier_league.csv"
    year = 2018
    division = "E0"

    # Loading data
    col_names = [
        "Div",
        "Date",
        "HomeTeam",
        "AwayTeam",
        "FTHG",
        "FTAG",
        "FTR",
        "HTHG",
        "HTAG",
        "HTR",
    ]

    results = pd.read_csv(
        results_file,
        usecols=[x for x in range(len(col_names))],
        names=col_names,
        skiprows=1,
        parse_dates=["Date"],
        dayfirst=True,
    )
    results = results.dropna(how="all")

    results.to_csv("/tmp/work/premier_league_cleaned.csv", index=False)

    # make data in table more readable
    results["Season"] = f"{year}-{year+1}"
    results["Div"] = divisions[division]

    # build out col so we can melt each game into a record per team
    results["H"] = results["HomeTeam"]
    results["A"] = results["AwayTeam"]
    cols_to_keep = [
        "Season",
        "Div",
        "Date",
        "HomeTeam",
        "AwayTeam",
        "FTHG",
        "FTAG",
        "FTR",
        "HTHG",
        "HTAG",
        "HTR",
    ]
    tidy_results = pd.melt(
        results,
        id_vars=cols_to_keep,
        value_vars=["H", "A"],
        var_name="HomeAway",
        value_name="Team",
    )

    # convert home/away columns (goals) into team / opponent columns
    tidy_results["Opponent"] = np.where(
        tidy_results["Team"] == tidy_results["HomeTeam"],
        tidy_results["AwayTeam"],
        tidy_results["HomeTeam"],
    )

    # full time goals
    tidy_results["Goals"] = np.where(
        tidy_results["Team"] == tidy_results["HomeTeam"],
        tidy_results["FTHG"],
        tidy_results["FTAG"],
    )
    tidy_results["Goals_Opp"] = np.where(
        tidy_results["Team"] != tidy_results["HomeTeam"],
        tidy_results["FTHG"],
        tidy_results["FTAG"],
    )
    tidy_results["Result"] = np.vectorize(get_result)(
        tidy_results["Goals"], tidy_results["Goals_Opp"]
    )
    tidy_results["Points"] = tidy_results["Result"].map(points)

    # 1st half goals
    tidy_results["H1_Goals"] = np.where(
        tidy_results["Team"] == tidy_results["HomeTeam"],
        tidy_results["HTHG"],
        tidy_results["HTAG"],
    )
    tidy_results["H1_Goals_Opp"] = np.where(
        tidy_results["Team"] != tidy_results["HomeTeam"],
        tidy_results["HTHG"],
        tidy_results["HTAG"],
    )
    tidy_results["H1_Result"] = np.vectorize(get_result)(
        tidy_results["H1_Goals"], tidy_results["H1_Goals_Opp"]
    )
    tidy_results["H1_Points"] = tidy_results["H1_Result"].map(points)

    # 2nd half goals
    tidy_results["H2_Goals"] = tidy_results["Goals"] - tidy_results["H1_Goals"]
    tidy_results["H2_Goals_Opp"] = (
        tidy_results["Goals_Opp"] - tidy_results["H1_Goals_Opp"]
    )
    tidy_results["H2_Result"] = np.vectorize(get_result)(
        tidy_results["H2_Goals"], tidy_results["H2_Goals_Opp"]
    )
    tidy_results["H2_Points"] = tidy_results["H2_Result"].map(points)

    # drop extra columns
    tidy_results = tidy_results.drop(
        ["HomeTeam", "AwayTeam", "FTR", "FTHG", "FTAG", "HTHG", "HTAG", "HTR"], axis=1
    )

    # rename colmns
    team_results_cols = [
        "Season",
        "Division",
        "Date",
        "HomeAway",
        "Team",
        "Opponent",
        "Goals",
        "Goals_Opp",
        "Result",
        "Points",
        "H1_Goals",
        "H1_Goals_Opp",
        "H1_Result",
        "H1_Points",
        "H2_Goals",
        "H2_Goals_Opp",
        "H2_Result",
        "H2_Points",
    ]

    tidy_results.columns = team_results_cols

    # TODO this is what is stored in our database
    # postgres connector
    tidy_results.to_csv("/tmp/work/premier_league_tidy.csv", index=False)
