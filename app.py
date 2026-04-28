import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
from data_prep import (
    get_wins_per_team, get_season_standings, get_toss_win_match_win,
    get_home_away_performance, get_top_teams_by_season, get_all_seasons
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "IPL Team Performance Dashboard"

seasons = get_all_seasons()

app.layout = dbc.Container([
    html.Div([
        html.H1("🏏 IPL Team Performance Dashboard", className="text-center my-4",
                style={"color": "#f4a700", "fontWeight": "bold", "letterSpacing": "1px"}),
        html.P("Explore team stats, standings & trends across IPL seasons",
               className="text-center text-muted mb-4"),
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Select Season:", style={"color": "#f4a700"}),
            dcc.Dropdown(
                id="season-dropdown",
                options=[{"label": "All Seasons", "value": "all"}] +
                        [{"label": str(s), "value": s} for s in seasons],
                value="all",
                clearable=False,
                style={"backgroundColor": "#222", "color": "#000"}
            )
        ], width=4)
    ], className="mb-4"),

    dbc.Row(id="kpi-cards", className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Total Wins per Team", style={"color": "#f4a700"}),
                dbc.CardBody(dcc.Graph(id="wins-bar"))
            ], className="mb-4", style={"backgroundColor": "#1a1a2e"})
        ], width=7),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Win % by Toss Decision", style={"color": "#f4a700"}),
                dbc.CardBody(dcc.Graph(id="toss-pie"))
            ], className="mb-4", style={"backgroundColor": "#1a1a2e"})
        ], width=5),
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Home vs Away Performance", style={"color": "#f4a700"}),
                dbc.CardBody(dcc.Graph(id="home-away-bar"))
            ], className="mb-4", style={"backgroundColor": "#1a1a2e"})
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Season-wise Top Teams (Wins)", style={"color": "#f4a700"}),
                dbc.CardBody(dcc.Graph(id="season-line"))
            ], className="mb-4", style={"backgroundColor": "#1a1a2e"})
        ], width=6),
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Points Table", style={"color": "#f4a700"}),
                dbc.CardBody(html.Div(id="standings-table"))
            ], style={"backgroundColor": "#1a1a2e"})
        ])
    ], className="mb-4"),

    html.Footer(
        html.P("Data Source: Kaggle IPL Dataset | Built with Dash & Plotly",
               className="text-center text-muted mt-4")
    )
], fluid=True, style={"backgroundColor": "#0d0d1a", "minHeight": "100vh"})


@app.callback(
    [Output("kpi-cards", "children"),
     Output("wins-bar", "figure"),
     Output("toss-pie", "figure"),
     Output("home-away-bar", "figure"),
     Output("season-line", "figure"),
     Output("standings-table", "children")],
    Input("season-dropdown", "value")
)
def update_dashboard(season):
    wins_df = get_wins_per_team(season)
    toss_df = get_toss_win_match_win(season)
    home_away_df = get_home_away_performance(season)
    season_df = get_top_teams_by_season()
    standings_df = get_season_standings(season)

    # Use title-cased column names since we title-case them in data_prep
    matches_col = [c for c in standings_df.columns if c.lower() == "matches"][0]
    wins_col = [c for c in standings_df.columns if c.lower() == "wins"][0]
    team_col = [c for c in standings_df.columns if c.lower() == "team"][0]

    total_matches = standings_df[matches_col].sum() if not standings_df.empty else 0
    total_teams = len(standings_df)
    top_team = wins_df.iloc[0]["team"] if not wins_df.empty else "N/A"
    top_wins = wins_df.iloc[0]["wins"] if not wins_df.empty else 0

    kpi_cards = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([html.H4("Total Matches", className="card-title text-muted"),
                          html.H2(str(total_matches), style={"color": "#f4a700"})])
        ], style={"backgroundColor": "#1a1a2e", "textAlign": "center"})),
        dbc.Col(dbc.Card([
            dbc.CardBody([html.H4("Teams", className="card-title text-muted"),
                          html.H2(str(total_teams), style={"color": "#4ecdc4"})])
        ], style={"backgroundColor": "#1a1a2e", "textAlign": "center"})),
        dbc.Col(dbc.Card([
            dbc.CardBody([html.H4("Top Team", className="card-title text-muted"),
                          html.H2(top_team, style={"color": "#ff6b6b", "fontSize": "1.2rem"})])
        ], style={"backgroundColor": "#1a1a2e", "textAlign": "center"})),
        dbc.Col(dbc.Card([
            dbc.CardBody([html.H4("Most Wins", className="card-title text-muted"),
                          html.H2(str(top_wins), style={"color": "#a29bfe"})])
        ], style={"backgroundColor": "#1a1a2e", "textAlign": "center"})),
    ])

    fig_wins = px.bar(wins_df, x="wins", y="team", orientation="h",
                      color="wins", color_continuous_scale="YlOrRd",
                      template="plotly_dark")
    fig_wins.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#1a1a2e",
                           showlegend=False, coloraxis_showscale=False,
                           margin=dict(l=10, r=10, t=10, b=10))

    fig_toss = px.pie(toss_df, names="toss_decision", values="wins",
                      color_discrete_sequence=["#f4a700", "#4ecdc4"],
                      template="plotly_dark")
    fig_toss.update_layout(paper_bgcolor="#1a1a2e", margin=dict(l=10, r=10, t=10, b=10))

    fig_ha = px.bar(home_away_df, x="team", y="wins", color="type",
                    barmode="group", color_discrete_map={"Home": "#4ecdc4", "Away": "#ff6b6b"},
                    template="plotly_dark")
    fig_ha.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#1a1a2e",
                          margin=dict(l=10, r=10, t=10, b=10),
                          xaxis_tickangle=-45)

    fig_season = px.line(season_df, x="season", y="wins", color="team",
                         template="plotly_dark", markers=True)
    fig_season.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#1a1a2e",
                               margin=dict(l=10, r=10, t=10, b=10))

    table = dbc.Table.from_dataframe(
        standings_df, striped=True, bordered=True, hover=True,
        className="text-center"
    )

    return kpi_cards, fig_wins, fig_toss, fig_ha, fig_season, table


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=False)
