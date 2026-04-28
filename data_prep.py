import pandas as pd
import os

DATA_PATH = "matches.csv"

import os
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "matches.csv")
if not os.path.exists(DATA_PATH):
    DATA_PATH = "matches.csv"

def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("matches.csv not found in data/ folder.")
    df = pd.read_csv(DATA_PATH)
    return df


def filter_by_season(df, season):
    if season != "all":
        df = df[df["season"].astype(str) == str(season)]
    return df


def get_all_seasons():
    df = load_data()
    return sorted(df["season"].unique(), reverse=True)


def get_wins_per_team(season="all"):
    df = load_data()
    df = filter_by_season(df, season)
    df = df[df["winner"].notna()]
    wins = df["winner"].value_counts().reset_index()
    wins.columns = ["team", "wins"]
    wins = wins.sort_values("wins", ascending=True)
    return wins


def get_season_standings(season="all"):
    df = load_data()
    df = filter_by_season(df, season)

    team1_matches = df.groupby("team1").size().reset_index(name="m1")
    team2_matches = df.groupby("team2").size().reset_index(name="m2")
    team1_matches.columns = ["team", "m1"]
    team2_matches.columns = ["team", "m2"]
    total_matches = pd.merge(team1_matches, team2_matches, on="team", how="outer").fillna(0)
    total_matches["matches"] = (total_matches["m1"] + total_matches["m2"]).astype(int)

    wins = df[df["winner"].notna()]["winner"].value_counts().reset_index()
    wins.columns = ["team", "wins"]

    standings = pd.merge(total_matches[["team", "matches"]], wins, on="team", how="left").fillna(0)
    standings["wins"] = standings["wins"].astype(int)
    standings["losses"] = standings["matches"] - standings["wins"]
    standings["win_%"] = (standings["wins"] / standings["matches"] * 100).round(1)
    standings["points"] = standings["wins"] * 2
    standings = standings.sort_values("points", ascending=False).reset_index(drop=True)
    standings.index += 1
    standings = standings.reset_index().rename(columns={"index": "rank"})
    standings.columns = [c.replace("_", " ").title() for c in standings.columns]
    return standings


def get_toss_win_match_win(season="all"):
    df = load_data()
    df = filter_by_season(df, season)
    df = df[df["winner"].notna()]
    toss_win = df[df["toss_winner"] == df["winner"]]
    toss_data = toss_win.groupby("toss_decision").size().reset_index(name="wins")
    return toss_data


def get_home_away_performance(season="all"):
    df = load_data()
    df = filter_by_season(df, season)
    df = df[df["winner"].notna()]

    home_wins = df[df["winner"] == df["team1"]].groupby("team1").size().reset_index()
    home_wins.columns = ["team", "wins"]
    home_wins["type"] = "Home"

    away_wins = df[df["winner"] == df["team2"]].groupby("team2").size().reset_index()
    away_wins.columns = ["team", "wins"]
    away_wins["type"] = "Away"

    combined = pd.concat([home_wins, away_wins])
    top_teams = df["winner"].value_counts().head(8).index.tolist()
    combined = combined[combined["team"].isin(top_teams)]
    return combined


def get_top_teams_by_season():
    df = load_data()
    df = df[df["winner"].notna()]
    season_wins = df.groupby(["season", "winner"]).size().reset_index(name="wins")
    season_wins.columns = ["season", "team", "wins"]
    top_teams = df["winner"].value_counts().head(6).index.tolist()
    season_wins = season_wins[season_wins["team"].isin(top_teams)]
    return season_wins
