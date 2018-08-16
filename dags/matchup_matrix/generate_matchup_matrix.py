"""Generate Home and Away Matrix"""

from collections import namedtuple

import pandas as pd
from PIL import Image

from ..common.render_template import render

PATH = "supporting-files/pl-logos/"
COMBINED_PATH = f"{path}/combined/"


def split_image(hometeam, awayteam, team_logo, *, create_image=True):
    """Use Pillow to split home and away image

    Args:
        - home team
    """

    # file location
    combined_img_filepath = f"{combined_path}/{hometeam}_{awayteam}.png"

    # if we have to create the image
    if create_image:
        # open images
        img_home = Image.open(f"{path}/{team_logo[hometeam]}")
        img_away = Image.open(f"{path}/{team_logo[awayteam]}")
        width, height = img_home.size

        img_combined = Image.new("RGBA", (width, height))

        # away logo, copy top half
        for x in range(width):
            for y in range(x):
                img_combined.putpixel((x, y), img_away.getpixel((x, y)))

        # home logo, copy bottom half
        for y in range(height):
            for x in range(y):
                img_combined.putpixel((x, y), img_home.getpixel((x, y)))

        # save new image
        img_combined.save(combined_img_filepath)

    return combined_img_filepath


def make_result_image(match_result, team_logo):
    """From match_results tuple, generate results image and return

    Args:
        * match_results tuple

    Output
        * image filepath
    """

    if match_result.FTHG == match_result.FTAG:
        # split_pic_diagonally
        img_file_path = split_image(
            match_result.HomeTeam, match_result.AwayTeam, team_logo
        )
    elif match_result.FTHG > match_result.FTAG:
        # show home team's logo
        img_file_path = f"{path}/{team_logo[match_result.HomeTeam]}"
    else:
        # show away team's logo
        img_file_path = f"{path}/{team_logo[match_result.AwayTeam]}"

    return img_file_path


def create_match_matrix(ds, **kwargs):
    results = pd.read_csv("/tmp/premier_league_cleaned.csv")
    teams = list(results["HomeTeam"].unique()) + list(results["AwayTeam"].unique())
    team_logo = {team: f"{team}.png" for team in teams}

    # get list of teams
    team_list = sorted(teams)

    # create dictionary of match_results
    # key: (home_team, away_team) namedtuple
    # value... date, score, results image
    match_results = {}
    matchup = namedtuple("matchup", ["home_team", "away_team"])

    # loop thru each row and generate results image
    for item in results.itertuples():
        key = matchup(home_team=item.HomeTeam, away_team=item.AwayTeam)

        # save details
        match_details = {}
        match_details["date"] = item.Date
        match_details["home_goals"] = item.FTHG
        match_details["away_goals"] = item.FTAG
        match_details["result_img"] = make_result_image(item, split_image, team_logo)

        match_results[key] = match_details

    # Create HTML visualization using Jinja2
    # pass in variables, render template, and send
    context = {"match_results": match_results, "team_list": team_list}

    html = render("supporting-files/home_away_matrix_template.html", context)

    with open("/tmp/output.html", "w") as f:
        f.write(html)
