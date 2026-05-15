"""Ball-by-ball simulation dashboard integrated into Data Storytelling Dash."""

from collections import Counter
from functools import lru_cache
import logging
import math

import dash
from dash import Input, Output, State, callback, dcc, html, no_update
import plotly.graph_objects as go

from .config import DASHBOARD_CONFIG
from ..theme import BRICK_EMBER, DEEP_TEAL, PRUSSIAN_BLUE, apply_chart_theme
from ...src.models.team_profile import TeamProfile
from ...src.services.data_loader import DataLoadError, get_available_teams, load_ipl_data
from ...src.services.feature_store import WeightedFeatureStore
from ...src.services.simulation_engine import ChaseStateSnapshot, PreparedSimulationContext, SimulationEngine

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_dataset():
    return load_ipl_data()


def _empty_figure(title: str, message: str):
    fig = go.Figure()
    apply_chart_theme(fig, title=title, height=460)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 0.5,
                "showarrow": False,
                "font": {"size": 14, "color": PRUSSIAN_BLUE},
            }
        ]
    )
    return fig


def _flatten_deliveries(sim_data):
    deliveries = []
    for innings in sim_data.get("innings", []):
        innings_no = innings.get("innings_number", 0)
        team = innings.get("batting_team", "Unknown")
        for ball in innings.get("balls", []):
            deliveries.append({"innings_number": innings_no, "batting_team": team, **ball})
    return deliveries


def _teams_options():
    try:
        teams = get_available_teams(_load_dataset())
    except Exception:
        logger.exception("Failed to load teams for dashboard controls")
        teams = []
    return [{"label": team, "value": team} for team in teams]


@lru_cache(maxsize=1)
def _stadium_options():
    try:
        venues = WeightedFeatureStore().get_available_stadiums()
    except Exception:
        logger.exception("Failed to load stadium options")
        venues = []
    return [{"label": "All Stadiums", "value": ""}] + [{"label": v, "value": v} for v in venues]


def _stadium_options_for_filters(team_a, team_b, last_n_matches, recency_bias):
    options = [{"label": "All Stadiums", "value": ""}]
    teams = [t for t in [team_a, team_b] if t]
    if len(teams) < 2:
        return options

    try:
        window = int(last_n_matches if last_n_matches is not None else 120)
        bias = float(recency_bias if recency_bias is not None else 0.5)
        window = max(1, window)
        frame = WeightedFeatureStore().weighted_features(
            bias,
            last_n_matches=window,
            teams=teams,
            stadium=None,
        )
        venues = (
            frame["venue"]
            .dropna()
            .astype(str)
            .str.strip()
        )
        venues = sorted(set(v for v in venues.tolist() if v))
        options.extend([{"label": v, "value": v} for v in venues])
        return options
    except Exception:
        logger.exception("Failed to derive stadium options for selected filters")
        return options


def _diagnostics_component(sim_data):
    metadata = sim_data.get("metadata", {}) if sim_data else {}
    diagnostics = metadata.get("diagnostics", {})
    context_usage = diagnostics.get("context_usage", {})
    ess_avg = diagnostics.get("effective_sample_size_avg", 0.0)
    if not context_usage:
        return html.Div("Diagnostics unavailable for this run.")

    total = max(1, sum(context_usage.values()))
    rows = []
    for level, count in sorted(context_usage.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total) * 100.0
        rows.append(html.Li(f"{level}: {count} balls ({pct:.1f}%)"))

    return html.Div(
        [
            html.P(f"Average effective sample size: {ess_avg:.2f}"),
            html.Ul(rows),
        ]
    )


def _overs_from_balls(ball_count: int) -> str:
    return f"{ball_count // 6}.{ball_count % 6}"


def _team_short_code(team: str) -> str:
    words = [w for w in str(team or "").split() if w]
    if not words:
        return "UNK"
    if len(words) == 1:
        return words[0][:3].upper()
    return "".join(w[0] for w in words[:4]).upper()


def _player_initials(player: str) -> str:
    words = [w for w in str(player or "").split() if w]
    if not words:
        return "NA"
    if len(words) == 1:
        return words[0][:2].upper()
    return f"{words[0][0]}{words[-1][0]}".upper()


def _coded_team_label(team: str) -> str:
    code = _team_short_code(team)
    return f"{code} ({team})"


def _wicket_points(balls: list[dict]):
    batter_runs = {}
    wicket_x = []
    wicket_y = []
    wicket_text = []
    wicket_customdata = []

    for ball in balls:
        batter = str(ball.get("batter", "Unknown"))
        runs = int(ball.get("runs", 0))
        is_extra = bool(ball.get("is_extra", False))
        if not is_extra:
            batter_runs[batter] = batter_runs.get(batter, 0) + runs

        if bool(ball.get("is_wicket", False)):
            batter_score = int(batter_runs.get(batter, 0))
            wicket_x.append(int(ball.get("ball_number", 0)))
            wicket_y.append(int(ball.get("cumulative_score", 0)))
            wicket_text.append(f"{_player_initials(batter)} {batter_score}")
            wicket_customdata.append(
                [
                    batter,
                    batter_score,
                    int(ball.get("cumulative_score", 0)),
                    int(ball.get("cumulative_wickets", 0)),
                    str(ball.get("wicket_type", "out")),
                ]
            )

    return wicket_x, wicket_y, wicket_text, wicket_customdata


def _add_wicket_trace(fig: go.Figure, balls: list[dict], team: str, line_color: str):
    wicket_x, wicket_y, wicket_text, wicket_customdata = _wicket_points(balls)
    if not wicket_x:
        return

    fig.add_trace(
        go.Scatter(
            x=wicket_x,
            y=wicket_y,
            mode="markers+text",
            name=f"{_team_short_code(team)} Wkts",
            text=wicket_text,
            textposition="middle center",
            textfont={"size": 9, "color": line_color},
            customdata=wicket_customdata,
            marker={
                "size": 24,
                "symbol": "circle",
                "color": "#ffffff",
                "line": {"color": line_color, "width": 2},
            },
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Batter score %{customdata[1]}<br>"
                "Team score %{customdata[2]}/%{customdata[3]}<br>"
                "Dismissal %{customdata[4]}"
                "<extra></extra>"
            ),
        )
    )


def _broadcast_replay_banner(event: dict, event_index: int, total_events: int, chase_target: int | None = None):
    innings_no = int(event.get("innings_number", 0))
    team = str(event.get("batting_team", "Unknown"))
    team_code = _team_short_code(team)
    runs = int(event.get("runs", 0))
    score = int(event.get("cumulative_score", 0))
    wkts = int(event.get("cumulative_wickets", 0))
    legal_ball = int(event.get("legal_ball_number", 0))
    over_display = _overs_from_balls(max(0, legal_ball))
    current_rr = (score * 6.0 / legal_ball) if legal_ball > 0 else 0.0
    striker = str(event.get("batter", "-"))
    non_striker = str(event.get("non_striker", "-"))
    bowler = str(event.get("bowler", "-"))
    runs_needed = None
    balls_remaining = None
    display_req_rr = None
    if chase_target is not None and innings_no == 2:
        runs_needed = max(0, int(chase_target) - score)
        balls_remaining = max(0, 120 - legal_ball)
        display_req_rr = (runs_needed * 6.0 / balls_remaining) if balls_remaining > 0 else 0.0

    req_rr_display = f"{display_req_rr:.2f}" if display_req_rr is not None else "-"
    runs_needed_display = str(runs_needed) if runs_needed is not None else "-"
    balls_remaining_display = str(balls_remaining) if balls_remaining is not None else "-"
    pressure = str(event.get("pressure_band", "medium")).upper()
    partnership = int(event.get("partnership_runs", 0))
    context = str(event.get("context_level_used", "-"))
    ess = float(event.get("effective_sample_size", 0.0))
    event_type = str(event.get("event_type", "legal")).replace("_", " ").upper()
    is_wicket = bool(event.get("is_wicket"))

    event_chip_bg = BRICK_EMBER if is_wicket else DEEP_TEAL
    event_chip_label = "WICKET" if is_wicket else f"+{runs}"

    panel_style = {
        "borderRadius": "10px",
        "overflow": "hidden",
        "border": f"1px solid {PRUSSIAN_BLUE}",
        "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
    }
    top_strip_style = {
        "display": "grid",
        "gridTemplateColumns": "2.2fr 2.8fr 2.2fr 1.2fr",
        "gap": "0",
        "alignItems": "stretch",
        "background": f"linear-gradient(90deg, {PRUSSIAN_BLUE} 0%, {DEEP_TEAL} 65%, {PRUSSIAN_BLUE} 100%)",
        "color": "#ffffff",
    }
    block_style = {"padding": "10px 12px", "borderRight": "1px solid rgba(255,255,255,0.24)"}

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(f"{team_code} {score}/{wkts}", style={"fontSize": "26px", "fontWeight": "800", "lineHeight": "1.1"}),
                            html.Div(
                                f"OVER {over_display} | RR {current_rr:.2f} | INN {innings_no}",
                                style={"fontSize": "12px", "opacity": "0.9", "letterSpacing": "0.4px"},
                            ),
                        ],
                        style=block_style,
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("STRIKER ", style={"opacity": "0.8", "fontSize": "11px"}),
                                    html.Span(striker, style={"fontWeight": "700"}),
                                ],
                                style={"fontSize": "15px"},
                            ),
                            html.Div(
                                [
                                    html.Span("NON-STRIKER ", style={"opacity": "0.8", "fontSize": "11px"}),
                                    html.Span(non_striker, style={"fontWeight": "700"}),
                                ],
                                style={"fontSize": "15px", "marginTop": "2px"},
                            ),
                        ],
                        style=block_style,
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("BOWLER ", style={"opacity": "0.8", "fontSize": "11px"}),
                                    html.Span(bowler, style={"fontWeight": "700"}),
                                ],
                                style={"fontSize": "15px"},
                            ),
                            html.Div(
                                [
                                    html.Span("REQ RR ", style={"opacity": "0.8", "fontSize": "11px"}),
                                    html.Span(req_rr_display, style={"fontWeight": "700"}),
                                    html.Span("  |  "),
                                    html.Span("NEED ", style={"opacity": "0.8", "fontSize": "11px"}),
                                    html.Span(runs_needed_display, style={"fontWeight": "700"}),
                                    html.Span("  |  "),
                                    html.Span("BALLS ", style={"opacity": "0.8", "fontSize": "11px"}),
                                    html.Span(balls_remaining_display, style={"fontWeight": "700"}),
                                    html.Span("  |  "),
                                    html.Span("PRESSURE ", style={"opacity": "0.8", "fontSize": "11px"}),
                                    html.Span(pressure, style={"fontWeight": "700"}),
                                ],
                                style={"fontSize": "13px", "marginTop": "2px"},
                            ),
                        ],
                        style=block_style,
                    ),
                    html.Div(
                        [
                            html.Div(
                                event_chip_label,
                                style={
                                    "background": event_chip_bg,
                                    "display": "inline-block",
                                    "padding": "6px 10px",
                                    "borderRadius": "999px",
                                    "fontWeight": "800",
                                    "fontSize": "16px",
                                    "letterSpacing": "0.5px",
                                    "textAlign": "center",
                                    "minWidth": "62px",
                                },
                            ),
                            html.Div(event_type, style={"fontSize": "11px", "marginTop": "6px", "opacity": "0.9"}),
                        ],
                        style={**block_style, "borderRight": "none", "display": "flex", "flexDirection": "column", "justifyContent": "center", "alignItems": "center"},
                    ),
                ],
                style=top_strip_style,
            ),
            html.Div(
                [
                    html.Span(f"EVENT {event_index}/{total_events}"),
                    html.Span("  |  "),
                    html.Span(f"PARTNERSHIP {partnership}"),
                    html.Span("  |  "),
                    html.Span(f"LEGAL BALL {legal_ball}"),
                    html.Span("  |  "),
                    html.Span(f"MODEL {context}"),
                    html.Span("  |  "),
                    html.Span(f"ESS {ess:.1f}"),
                ],
                style={
                    "background": "#f2f5f8",
                    "color": PRUSSIAN_BLUE,
                    "fontSize": "12px",
                    "padding": "8px 12px",
                    "fontWeight": "600",
                },
            ),
        ],
        style=panel_style,
    )


def _match_summary_component(sim_data: dict):
    innings = sim_data.get("innings", [])
    result = sim_data.get("result", "")
    if not innings:
        return result

    score_lines = []
    for idx, inn in enumerate(innings, start=1):
        team = inn.get("batting_team", f"Innings {idx}")
        coded_team = _coded_team_label(str(team))
        score_lines.append(
            html.Li(
                f"{coded_team}: {inn.get('total_runs', 0)}/{inn.get('wickets_lost', 0)} "
                f"({inn.get('overs_completed', 0.0)} overs)"
            )
        )

    return html.Div(
        [
            html.Div(result, className="fw-semibold mb-1"),
            html.Ul(score_lines, className="mb-0"),
        ]
    )


def _build_scorecard_for_innings(innings: dict, lineup: list | None):
    balls = innings.get("balls", [])
    batting_team = innings.get("batting_team", "Unknown")
    coded_team = _coded_team_label(str(batting_team))

    batting = {}
    wickets = []
    extras_runs = 0

    for ball in balls:
        batter = ball.get("batter", "Unknown")
        bowler = ball.get("bowler", "Unknown")
        runs = int(ball.get("runs", 0))
        is_wicket = bool(ball.get("is_wicket", False))
        is_extra = bool(ball.get("is_extra", False))
        extra_type = ball.get("extra_type", "")
        ball_no = int(ball.get("legal_ball_number", ball.get("ball_number", 0)))
        score = int(ball.get("cumulative_score", 0))
        wkt_count = int(ball.get("cumulative_wickets", 0))

        if batter not in batting:
            batting[batter] = {
                "runs": 0,
                "balls": 0,
                "4s": 0,
                "6s": 0,
                "status": "not out",
            }
        batting[batter]["runs"] += runs
        batting[batter]["balls"] += 1
        batting[batter]["4s"] += 1 if runs == 4 else 0
        batting[batter]["6s"] += 1 if runs == 6 else 0

        if is_extra:
            extras_runs += int(ball.get("extra_runs", runs))

        if is_wicket:
            batting[batter]["status"] = f"{ball.get('wicket_type', 'out')} b {bowler}"
            wickets.append(f"{score}/{wkt_count} ({batter}, {_overs_from_balls(ball_no)})")

    table_style = {
        "width": "100%",
        "marginBottom": "12px",
        "tableLayout": "fixed",
        "borderCollapse": "collapse",
    }
    text_col_left = {"textAlign": "left", "padding": "6px 4px"}
    num_col_right = {"textAlign": "right", "padding": "6px 4px", "whiteSpace": "nowrap"}
    batter_col = {**text_col_left, "width": "24%"}
    dismissal_col = {**text_col_left, "width": "34%"}
    num_col = {**num_col_right, "width": "7%"}
    sr_col = {**num_col_right, "width": "9%"}

    batting_rows = []
    for name, st in batting.items():
        sr = (st["runs"] * 100.0 / st["balls"]) if st["balls"] else 0.0
        batting_rows.append(
            html.Tr(
                [
                    html.Td(name, style=batter_col),
                    html.Td(st["status"], style=dismissal_col),
                    html.Td(st["runs"], style=num_col_right),
                    html.Td(st["balls"], style=num_col_right),
                    html.Td(st["4s"], style=num_col_right),
                    html.Td(st["6s"], style=num_col_right),
                    html.Td(f"{sr:.2f}", style=num_col_right),
                ]
            )
        )

    bowling = {}
    for ball in balls:
        bowler = ball.get("bowler", "Unknown")
        runs = int(ball.get("runs", 0))
        is_wicket = bool(ball.get("is_wicket", False))
        wicket_type = str(ball.get("wicket_type", "")).lower()
        legal = bool(ball.get("is_legal_delivery", True))
        over_idx = (int(ball.get("legal_ball_number", ball.get("ball_number", 1))) - 1) // 6

        if bowler not in bowling:
            bowling[bowler] = {
                "balls": 0,
                "runs": 0,
                "wkts": 0,
                "by_over_runs": {},
                "by_over_balls": {},
            }
        bowling[bowler]["runs"] += runs
        # Run outs are not credited to the bowler in bowling figures.
        bowling[bowler]["wkts"] += 1 if (is_wicket and wicket_type != "run_out") else 0
        bowling[bowler]["by_over_runs"].setdefault(over_idx, 0)
        bowling[bowler]["by_over_balls"].setdefault(over_idx, 0)
        bowling[bowler]["by_over_runs"][over_idx] += runs
        bowling[bowler]["by_over_balls"][over_idx] += 1
        if legal:
            bowling[bowler]["balls"] += 1

    bowling_rows = []
    for name, st in bowling.items():
        overs_float = st["balls"] / 6.0 if st["balls"] else 0.0
        econ = st["runs"] / overs_float if overs_float > 0 else 0.0
        maidens = sum(
            1
            for ov, ov_runs in st["by_over_runs"].items()
            if ov_runs == 0 and st["by_over_balls"].get(ov, 0) == 6
        )
        bowling_rows.append(
            html.Tr(
                [
                    html.Td(name, style={**text_col_left, "width": "40%"}),
                    html.Td(_overs_from_balls(st["balls"]), style=num_col_right),
                    html.Td(maidens, style=num_col_right),
                    html.Td(st["runs"], style=num_col_right),
                    html.Td(st["wkts"], style=num_col_right),
                    html.Td(f"{econ:.2f}", style=num_col_right),
                ]
            )
        )

    batting_order = lineup or []
    appeared = set(batting.keys())
    yet_to_bat = [p for p in batting_order if p not in appeared]

    innings_total = innings.get("total_runs", 0)
    innings_wkts = innings.get("wickets_lost", 0)
    innings_overs = innings.get("overs_completed", 0.0)

    return html.Div(
        [
            html.H4(coded_team, style={"marginTop": "18px"}),
            html.H5("Batting"),
            html.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Batter", style=batter_col),
                                html.Th("Dismissal", style=dismissal_col),
                                html.Th("R", style=num_col),
                                html.Th("B", style=num_col),
                                html.Th("4s", style=num_col),
                                html.Th("6s", style=num_col),
                                html.Th("S/R", style=sr_col),
                            ]
                        )
                    ),
                    html.Tbody(batting_rows),
                ],
                className="table table-sm",
                style=table_style,
            ),
            html.Div(f"Extras: {extras_runs}"),
            html.Div(f"Total: {innings_total}/{innings_wkts} ({innings_overs} overs)", style={"marginBottom": "10px"}),
            html.Div("Yet to bat: " + (", ".join(yet_to_bat) if yet_to_bat else "-"), style={"marginBottom": "10px"}),
            html.Div("Fall of wickets: " + (" · ".join(wickets) if wickets else "-"), style={"marginBottom": "10px"}),
            html.H5("Bowling"),
            html.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Bowler", style={**text_col_left, "width": "40%"}),
                                html.Th("O", style=num_col),
                                html.Th("M", style=num_col),
                                html.Th("R", style=num_col),
                                html.Th("W", style=num_col),
                                html.Th("Econ", style=sr_col),
                            ]
                        )
                    ),
                    html.Tbody(bowling_rows),
                ],
                className="table table-sm",
                style={**table_style, "marginBottom": "0"},
            ),
            html.Hr(),
        ]
    )


def _simulation_error_styles():
    error_style = {
        "display": "block",
        "marginBottom": "14px",
    }
    hidden_error_style = {**error_style, "display": "none"}
    return error_style, hidden_error_style


def _validate_simulation_inputs(team_a, team_b, recency_bias, last_n_matches, random_seed, max_fallback):
    if not team_a or not team_b:
        return None, "Please select both teams."
    if team_a == team_b:
        return None, "Please choose two different teams."

    try:
        window = int(last_n_matches if last_n_matches is not None else 120)
        recency_bias_value = float(recency_bias if recency_bias is not None else 0.5)
        seed = int(random_seed if random_seed is not None else 42)
        fallback_level = int(max_fallback if max_fallback is not None else 6)
    except (TypeError, ValueError):
        return None, "Invalid simulation inputs. Please check all numeric fields."

    if window < 1:
        return None, "Last N matches must be a positive integer."
    if recency_bias_value < 0.0 or recency_bias_value > 1.0:
        return None, "Recency bias must be between 0.0 and 1.0."
    if seed < 0:
        return None, "Random seed must be a non-negative integer."
    if fallback_level < 0 or fallback_level > 6:
        return None, "Max fallback level must be between 0 and 6."

    return {
        "window": window,
        "recency_bias_value": recency_bias_value,
        "seed": seed,
        "fallback_level": fallback_level,
    }, ""


def _simulate_match_payload(
    engine: SimulationEngine,
    *,
    team_a: str,
    team_b: str,
    team_a_profile: TeamProfile,
    team_b_profile: TeamProfile,
    recency_bias: float,
    random_seed: int,
    max_fallback_level: int,
    last_n_matches: int,
    stadium: str | None,
    prepared_context: PreparedSimulationContext | None = None,
    collect_chase_snapshots: bool = False,
):
    match = engine.simulate_match(
        team_a=team_a,
        team_b=team_b,
        team_a_profile=team_a_profile,
        team_b_profile=team_b_profile,
        recency_bias=recency_bias,
        random_seed=random_seed,
        model_depth="full_context",
        max_fallback_level=max_fallback_level,
        lineup_sampling_seed=random_seed,
        last_n_matches=last_n_matches,
        realism_version="enhanced_v1",
        stadium=stadium,
        prepared_context=prepared_context,
        collect_chase_snapshots=collect_chase_snapshots,
    )
    payload = match.to_dict()
    low_confidence = team_a_profile.total_matches < 3 or team_b_profile.total_matches < 3
    payload["low_confidence_warning"] = (
        "Low-confidence simulation: one or both teams have fewer than 3 historical matches."
        if low_confidence
        else ""
    )
    return payload


def _multi_run_result_row(run_number: int, seed: int, sim_payload: dict):
    innings = sim_payload.get("innings", [])
    if len(innings) < 2:
        return {
            "run": run_number,
            "seed": seed,
            "team_a_runs": None,
            "team_b_runs": None,
            "run_diff": None,
            "team_a_score": "-",
            "team_b_score": "-",
            "winner": "Incomplete",
            "margin": "-",
            "result": sim_payload.get("result", "Incomplete"),
        }

    innings_a = innings[0]
    innings_b = innings[1]
    team_a = str(sim_payload.get("team_a", "Team A"))
    team_b = str(sim_payload.get("team_b", "Team B"))
    a_runs = int(innings_a.get("total_runs", 0))
    a_wkts = int(innings_a.get("wickets_lost", 0))
    b_runs = int(innings_b.get("total_runs", 0))
    b_wkts = int(innings_b.get("wickets_lost", 0))

    if a_runs > b_runs:
        winner = team_a
        margin = f"{a_runs - b_runs} runs"
    elif b_runs > a_runs:
        winner = team_b
        margin = f"{max(0, 10 - b_wkts)} wickets"
    else:
        winner = "Tie"
        margin = "Tie"

    return {
        "run": run_number,
        "seed": seed,
        "team_a_runs": a_runs,
        "team_b_runs": b_runs,
        "run_diff": a_runs - b_runs,
        "team_a_score": f"{a_runs}/{a_wkts}",
        "team_b_score": f"{b_runs}/{b_wkts}",
        "winner": winner,
        "margin": margin,
        "result": sim_payload.get("result", ""),
    }


def _multi_run_summary_component(rows: list[dict], team_a: str, team_b: str):
    if not rows:
        return html.Div("No simulations completed.", className="text-muted")

    winner_counts = Counter(row.get("winner", "") for row in rows)
    total = len(rows)
    team_a_wins = int(winner_counts.get(team_a, 0))
    team_b_wins = int(winner_counts.get(team_b, 0))
    ties = int(winner_counts.get("Tie", 0))

    return html.Div(
        [
            html.Div(f"Total runs: {total}", className="fw-semibold"),
            html.Div(f"{team_a}: {team_a_wins} wins ({(team_a_wins * 100.0 / total):.1f}%)"),
            html.Div(f"{team_b}: {team_b_wins} wins ({(team_b_wins * 100.0 / total):.1f}%)"),
            html.Div(f"Ties: {ties} ({(ties * 100.0 / total):.1f}%)"),
        ],
        className="mb-2",
    )


def _multi_run_table_component(rows: list[dict], team_a: str, team_b: str):
    if not rows:
        return html.Div("Run N simulations to see tabular outcomes.", className="text-muted")

    header_style = {"textAlign": "left", "whiteSpace": "nowrap"}
    return html.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Run", style=header_style),
                        html.Th("Seed", style=header_style),
                        html.Th(f"{_team_short_code(team_a)} Score", style=header_style),
                        html.Th(f"{_team_short_code(team_b)} Score", style=header_style),
                        html.Th("Winner", style=header_style),
                        html.Th("Margin", style=header_style),
                        html.Th("Result", style=header_style),
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(row["run"]),
                            html.Td(row["seed"]),
                            html.Td(row["team_a_score"]),
                            html.Td(row["team_b_score"]),
                            html.Td(row["winner"]),
                            html.Td(row["margin"]),
                            html.Td(row["result"]),
                        ]
                    )
                    for row in rows
                ]
            ),
        ],
        className="table table-sm table-striped table-hover",
    )


def _extract_cumulative_points(sim_payload: dict, team_a: str, team_b: str, run_id: int):
    innings = sim_payload.get("innings", [])
    points = []
    if len(innings) < 2:
        return points

    innings_map = [(team_a, innings[0]), (team_b, innings[1])]
    for team_label, innings_data in innings_map:
        for ball in innings_data.get("balls", []):
            if not bool(ball.get("is_legal_delivery", True)):
                continue
            legal_ball = int(ball.get("legal_ball_number", 0))
            if legal_ball < 1:
                continue
            points.append(
                {
                    "run_id": int(run_id),
                    "team": team_label,
                    "ball": legal_ball,
                    "score": int(ball.get("cumulative_score", 0)),
                }
            )
    return points


def _extract_wicket_fall_points(sim_payload: dict, team_a: str, team_b: str):
    innings = sim_payload.get("innings", [])
    points = []
    if len(innings) < 2:
        return points

    innings_map = [(team_a, innings[0]), (team_b, innings[1])]
    for team_label, innings_data in innings_map:
        wicket_count = 0
        for ball in innings_data.get("balls", []):
            if not bool(ball.get("is_wicket", False)):
                continue
            if not bool(ball.get("is_legal_delivery", True)):
                continue
            legal_ball = int(ball.get("legal_ball_number", 0))
            if legal_ball < 1:
                continue
            wicket_count += 1
            points.append(
                {
                    "team": team_label,
                    "wicket_number": wicket_count,
                    "ball": legal_ball,
                }
            )
    return points


def _extract_chase_snapshots(sim_payload: dict, run_id: int):
    metadata = sim_payload.get("metadata", {}) if sim_payload else {}
    counterfactual = metadata.get("counterfactual", {}) if isinstance(metadata, dict) else {}
    snapshots = counterfactual.get("chase_snapshots", []) if isinstance(counterfactual, dict) else []
    rows = []
    for raw in snapshots:
        if not isinstance(raw, dict):
            continue
        row = dict(raw)
        row["run_id"] = int(run_id)
        rows.append(row)
    return rows


def _state_cluster_key(snapshot: dict):
    legal_ball = int(snapshot.get("legal_ball", snapshot.get("ball", 0)))
    runs_needed = max(0, int(snapshot.get("runs_needed", 0)))
    wickets_in_hand = max(0, int(snapshot.get("wickets_in_hand", 0)))
    balls_in_over = max(0, int(snapshot.get("balls_in_over", 0)))
    # "Near-identical" clustering: small runs-needed bucket + wickets + within-over position.
    return (
        legal_ball,
        runs_needed // 2,
        wickets_in_hand,
        balls_in_over,
    )


def _stable_state_hash(snapshot: dict) -> int:
    parts = [
        str(int(snapshot.get("legal_ball", snapshot.get("ball", 0)))),
        str(int(snapshot.get("score", 0))),
        str(int(snapshot.get("wickets_lost", 0))),
        str(int(snapshot.get("runs_needed", 0))),
        str(int(snapshot.get("balls_left", 0))),
        str(int(snapshot.get("wickets_in_hand", 0))),
        str(int(snapshot.get("striker_idx", 0))),
        str(int(snapshot.get("non_striker_idx", 1))),
        str(int(snapshot.get("next_batter_idx", 2))),
        str(int(snapshot.get("balls_in_over", 0))),
        str(snapshot.get("current_bowler", "")),
    ]
    text = "|".join(parts)
    value = 0
    for ch in text:
        value = (value * 131 + ord(ch)) % 2_147_483_647
    return int(value)


def _select_counterfactual_snapshots(chase_snapshots: list[dict], max_states_per_ball: int, max_total_states: int):
    grouped: dict[int, dict[tuple, dict]] = {}
    for snapshot in chase_snapshots:
        legal_ball = int(snapshot.get("legal_ball", snapshot.get("ball", 0)))
        if legal_ball < 1:
            continue
        cluster_key = _state_cluster_key(snapshot)
        per_ball = grouped.setdefault(legal_ball, {})
        if cluster_key in per_ball:
            continue
        per_ball[cluster_key] = snapshot

    total_unique_states = sum(len(per_ball) for per_ball in grouped.values())
    if total_unique_states == 0:
        return [], {"total_unique_states": 0, "selected_states": 0, "truncated_states": 0}

    selected: list[dict] = []
    # First pass: ensure breadth across legal balls, prioritizing later balls.
    for legal_ball in sorted(grouped.keys(), reverse=True):
        states = list(grouped[legal_ball].values())
        states.sort(key=lambda row: (int(row.get("run_id", 0)), _stable_state_hash(row)))
        if not states:
            continue
        selected.append(states[0])
        if len(selected) >= max_total_states:
            break

    # Second pass: fill remaining budget up to per-ball cap (still late-ball first).
    if len(selected) < max_total_states:
        selected_keys = {(_state_cluster_key(row), int(row.get("run_id", 0))) for row in selected}
        for legal_ball in sorted(grouped.keys(), reverse=True):
            states = list(grouped[legal_ball].values())
            states.sort(key=lambda row: (int(row.get("run_id", 0)), _stable_state_hash(row)))
            added_for_ball = 1 if states else 0
            for row in states[1:]:
                if added_for_ball >= max_states_per_ball:
                    break
                state_key = (_state_cluster_key(row), int(row.get("run_id", 0)))
                if state_key in selected_keys:
                    continue
                selected.append(row)
                selected_keys.add(state_key)
                added_for_ball += 1
                if len(selected) >= max_total_states:
                    break
            if len(selected) >= max_total_states:
                break

    truncated = max(0, total_unique_states - len(selected))
    return selected, {
        "total_unique_states": total_unique_states,
        "selected_states": len(selected),
        "truncated_states": truncated,
    }


def _estimate_counterfactual_winprob_points(
    *,
    chase_snapshots: list[dict],
    engine: SimulationEngine,
    prepared_context: PreparedSimulationContext,
    base_seed: int,
    rollouts_per_state: int,
    max_states_per_ball: int,
    max_total_states: int,
):
    selected_snapshots, selection_meta = _select_counterfactual_snapshots(
        chase_snapshots=chase_snapshots,
        max_states_per_ball=max_states_per_ball,
        max_total_states=max_total_states,
    )
    points = []
    for row in selected_snapshots:
        legal_ball = int(row.get("legal_ball", row.get("ball", 0)))
        if legal_ball < 1:
            continue
        run_id = int(row.get("run_id", 0))
        state_hash = _stable_state_hash(row)
        seed = int(base_seed) + (run_id * 1009) + (state_hash % 1_000_000)
        snapshot = ChaseStateSnapshot.from_dict(row)
        win_prob = engine.estimate_chase_win_probability_from_snapshot(
            snapshot,
            context=prepared_context,
            rollouts=rollouts_per_state,
            random_seed=seed,
        )
        points.append({"ball": legal_ball, "win_prob": float(win_prob)})
    return points, selection_meta


def _multi_run_density_figure(rows: list[dict], team_a: str, team_b: str):
    fig = go.Figure()
    team_a_totals = [row["team_a_runs"] for row in rows if row.get("team_a_runs") is not None]
    team_b_totals = [row["team_b_runs"] for row in rows if row.get("team_b_runs") is not None]

    if not team_a_totals and not team_b_totals:
        return _empty_figure("Total Runs Density", "No complete simulations available for density plot.")

    fig.add_trace(
        go.Histogram(
            x=team_a_totals,
            name=_team_short_code(team_a),
            opacity=0.55,
            nbinsx=24,
            histnorm="probability density",
            marker={"color": PRUSSIAN_BLUE},
        )
    )
    fig.add_trace(
        go.Histogram(
            x=team_b_totals,
            name=_team_short_code(team_b),
            opacity=0.55,
            nbinsx=24,
            histnorm="probability density",
            marker={"color": DEEP_TEAL},
        )
    )
    apply_chart_theme(
        fig,
        title="Total Runs Density Across Simulations",
        xaxis_title="Total Runs",
        yaxis_title="Density",
        height=420,
    )
    fig.update_layout(barmode="overlay")
    return fig


def _multi_run_cumulative_box_figure(cumulative_points: list[dict], team_a: str, team_b: str):
    if not cumulative_points:
        return _empty_figure("Cumulative Score Difference by Ball", "No complete simulations available for confidence interval chart.")

    # Pair cumulative scores by (run_id, legal_ball) to compute score differences per simulation.
    paired_scores: dict[tuple[int, int], dict[str, int]] = {}
    for point in cumulative_points:
        run_id = int(point.get("run_id", 0))
        legal_ball = int(point.get("ball", 0))
        team = str(point.get("team", ""))
        score = int(point.get("score", 0))
        if run_id < 1 or legal_ball < 1:
            continue
        key = (run_id, legal_ball)
        if key not in paired_scores:
            paired_scores[key] = {}
        paired_scores[key][team] = score

    diff_by_ball: dict[int, list[int]] = {}
    for (_run_id, legal_ball), score_map in paired_scores.items():
        if team_a not in score_map or team_b not in score_map:
            continue
        diff_by_ball.setdefault(legal_ball, []).append(score_map[team_a] - score_map[team_b])

    if not diff_by_ball:
        return _empty_figure(
            "Cumulative Score Difference by Ball",
            "No paired legal-ball points available to compute score differences.",
        )

    legal_balls = sorted(diff_by_ball.keys())
    means = []
    ci_lowers = []
    ci_uppers = []
    sample_sizes = []
    for legal_ball in legal_balls:
        samples = diff_by_ball[legal_ball]
        n = len(samples)
        sample_sizes.append(n)
        mean_diff = sum(samples) / n
        means.append(mean_diff)
        if n > 1:
            variance = sum((value - mean_diff) ** 2 for value in samples) / (n - 1)
            sem = math.sqrt(variance / n)
            ci_half_width = 1.96 * sem
        else:
            ci_half_width = 0.0
        ci_lowers.append(mean_diff - ci_half_width)
        ci_uppers.append(mean_diff + ci_half_width)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=legal_balls,
            y=ci_lowers,
            mode="lines",
            line={"color": PRUSSIAN_BLUE, "width": 1, "dash": "dot"},
            name="95% CI",
            legendgroup="score_diff",
            showlegend=True,
            hovertemplate=(
                f"<b>{team_a} - {team_b}</b><br>"
                "Ball %{x}<br>"
                "Lower 95% CI %{y:.1f}<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=legal_balls,
            y=means,
            mode="lines",
            line={"color": BRICK_EMBER, "width": 2.5},
            name="Mean Difference",
            legendgroup="score_diff",
            showlegend=True,
            customdata=sample_sizes,
            hovertemplate=(
                f"<b>{team_a} - {team_b}</b><br>"
                "Ball %{x}<br>"
                "Mean %{y:.1f}<br>"
                "Samples %{customdata}<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=legal_balls,
            y=ci_uppers,
            mode="lines",
            line={"color": PRUSSIAN_BLUE, "width": 1, "dash": "dot"},
            name="95% CI",
            legendgroup="score_diff",
            showlegend=False,
            hovertemplate=(
                f"<b>{team_a} - {team_b}</b><br>"
                "Ball %{x}<br>"
                "Upper 95% CI %{y:.1f}<extra></extra>"
            ),
        )
    )

    apply_chart_theme(
        fig,
        title="Cumulative Score Difference Mean and 95% CI by Legal Ball",
        xaxis_title="Legal Ball Number",
        yaxis_title=f"Run Difference ({_team_short_code(team_a)} - {_team_short_code(team_b)})",
        height=440,
    )
    fig.add_hline(y=0, line_width=1.5, line_dash="dash", line_color=DEEP_TEAL)
    return fig


def _multi_run_chase_win_prob_figure(chase_points: list[dict], team_b: str, rollouts_per_state: int, truncated_states: int):
    if not chase_points:
        return _empty_figure("Chase Win Probability by Ball", "No counterfactual state points available across simulations.")

    grouped: dict[int, list[float]] = {}
    for point in chase_points:
        legal_ball = int(point.get("ball", 0))
        win_prob = float(point.get("win_prob", 0.0))
        if legal_ball < 1:
            continue
        grouped.setdefault(legal_ball, []).append(win_prob)

    if not grouped:
        return _empty_figure("Chase Win Probability by Ball", "No legal-ball counterfactual state points available.")

    legal_balls = sorted(grouped.keys())
    means = []
    ci_lowers = []
    ci_uppers = []
    sample_sizes = []
    for legal_ball in legal_balls:
        samples = grouped[legal_ball]
        n = len(samples)
        sample_sizes.append(n)
        mean_prob = sum(samples) / n
        means.append(mean_prob)
        if n > 1:
            variance = sum((value - mean_prob) ** 2 for value in samples) / (n - 1)
            sem = math.sqrt(variance / n)
            ci_half_width = 1.96 * sem
        else:
            ci_half_width = 0.0
        ci_lowers.append(max(0.0, mean_prob - ci_half_width))
        ci_uppers.append(min(1.0, mean_prob + ci_half_width))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=legal_balls,
            y=ci_lowers,
            mode="lines",
            line={"color": DEEP_TEAL, "width": 1, "dash": "dot"},
            name="95% CI",
            legendgroup="chase-win-prob",
            showlegend=True,
            hovertemplate=(
                f"<b>{team_b}</b><br>"
                "Ball %{x}<br>"
                "Lower 95% CI %{y:.3f}<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=legal_balls,
            y=means,
            mode="lines",
            line={"color": BRICK_EMBER, "width": 2.5},
            name=f"{_team_short_code(team_b)} Win Prob (Mean)",
            legendgroup="chase-win-prob",
            showlegend=True,
            customdata=sample_sizes,
            hovertemplate=(
                f"<b>{team_b}</b><br>"
                "Ball %{x}<br>"
                "Counterfactual Win Prob %{y:.3f}<br>"
                "States %{customdata}<br>"
                f"Rollouts/state {int(rollouts_per_state)}<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=legal_balls,
            y=ci_uppers,
            mode="lines",
            line={"color": DEEP_TEAL, "width": 1, "dash": "dot"},
            name="95% CI",
            legendgroup="chase-win-prob",
            showlegend=False,
            hovertemplate=(
                f"<b>{team_b}</b><br>"
                "Ball %{x}<br>"
                "Upper 95% CI %{y:.3f}<extra></extra>"
            ),
        )
    )

    apply_chart_theme(
        fig,
        title=f"{_team_short_code(team_b)} Counterfactual From-State Win Probability by Legal Ball",
        xaxis_title="Legal Ball Number (Innings 2)",
        yaxis_title=f"P({_team_short_code(team_b)} Win)",
        height=380,
    )
    fig.update_yaxes(range=[0.0, 1.0], tickformat=".0%")
    fig.add_hline(y=0.5, line_width=1.5, line_dash="dash", line_color=PRUSSIAN_BLUE)
    if truncated_states > 0:
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.99,
            y=1.12,
            showarrow=False,
            align="right",
            text=f"State cap applied: {int(truncated_states)} states skipped",
            font={"size": 12, "color": PRUSSIAN_BLUE},
        )
    return fig


def _multi_run_outcome_figure(rows: list[dict], team_a: str, team_b: str):
    if not rows:
        return _empty_figure("Outcome Breakdown", "No simulations completed.")

    winner_counts = Counter(row.get("winner", "") for row in rows)
    categories = [team_a, team_b, "Tie"]
    values = [winner_counts.get(team_a, 0), winner_counts.get(team_b, 0), winner_counts.get("Tie", 0)]
    colors = [PRUSSIAN_BLUE, DEEP_TEAL, BRICK_EMBER]

    fig = go.Figure(
        data=[
            go.Bar(
                x=[_team_short_code(c) if c != "Tie" else c for c in categories],
                y=values,
                marker={"color": colors},
                text=values,
                textposition="outside",
            )
        ]
    )
    apply_chart_theme(
        fig,
        title="Win Outcomes Across N Simulations",
        xaxis_title="Outcome",
        yaxis_title="Count",
        height=360,
    )
    fig.update_yaxes(rangemode="tozero")
    return fig


def _multi_run_margin_figure(rows: list[dict], team_a: str):
    run_diffs = [row.get("run_diff") for row in rows if row.get("run_diff") is not None]
    if not run_diffs:
        return _empty_figure("Run Differential", "No complete simulations available.")

    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=run_diffs,
            nbinsx=24,
            marker={"color": PRUSSIAN_BLUE},
            opacity=0.85,
            name=f"{_team_short_code(team_a)} - Opponent",
        )
    )
    fig.add_vline(x=0, line_width=2, line_dash="dash", line_color=BRICK_EMBER)
    apply_chart_theme(
        fig,
        title="Run Differential Distribution",
        xaxis_title=f"Run Differential ({_team_short_code(team_a)} minus Opponent)",
        yaxis_title="Frequency",
        height=360,
    )
    return fig


def _multi_run_wicket_timing_figure(wicket_points: list[dict], team_a: str, team_b: str):
    if not wicket_points:
        return _empty_figure("Wicket Timing (Mean ± 95% CI)", "No wicket events available across simulations.")

    fig = go.Figure()
    has_trace = False
    team_specs = [(team_a, PRUSSIAN_BLUE), (team_b, DEEP_TEAL)]

    for team_label, color in team_specs:
        grouped: dict[int, list[int]] = {}
        for point in wicket_points:
            if point.get("team") != team_label:
                continue
            wicket_number = int(point.get("wicket_number", 0))
            ball = int(point.get("ball", 0))
            if wicket_number < 1 or ball < 1:
                continue
            grouped.setdefault(wicket_number, []).append(ball)

        if not grouped:
            continue

        wicket_numbers = sorted(grouped.keys())
        means = []
        ci_half_widths = []
        sample_sizes = []
        for wicket_number in wicket_numbers:
            samples = grouped[wicket_number]
            n = len(samples)
            sample_sizes.append(n)
            mean_ball = sum(samples) / n
            means.append(mean_ball)
            if n > 1:
                variance = sum((value - mean_ball) ** 2 for value in samples) / (n - 1)
                sem = math.sqrt(variance / n)
                ci_half_widths.append(1.96 * sem)
            else:
                ci_half_widths.append(0.0)

        fig.add_trace(
            go.Scatter(
                x=wicket_numbers,
                y=means,
                mode="lines+markers",
                name=_team_short_code(team_label),
                line={"color": color, "width": 2},
                marker={"color": color, "size": 8},
                error_y={"type": "data", "array": ci_half_widths, "visible": True},
                customdata=sample_sizes,
                hovertemplate=(
                    f"<b>{team_label}</b><br>"
                    "Wicket #%{x}<br>"
                    "Mean legal ball %{y:.1f}<br>"
                    "Samples %{customdata}"
                    "<extra></extra>"
                ),
            )
        )
        has_trace = True

    if not has_trace:
        return _empty_figure("Wicket Timing (Mean ± 95% CI)", "No legal-delivery wicket events available.")

    apply_chart_theme(
        fig,
        title="Mean Ball for Each Wicket (95% CI)",
        xaxis_title="Wicket Number",
        yaxis_title="Legal Ball Number of Wicket Fall",
        height=380,
    )
    fig.update_xaxes(dtick=1, range=[0.5, 10.5], tickmode="linear")
    fig.update_yaxes(range=[0, 120])
    return fig


def layout():
    options = _teams_options()
    stadium_options = _stadium_options()
    return html.Div(
        [
            html.H1(DASHBOARD_CONFIG["title"], className="display-6"),
            html.P(DASHBOARD_CONFIG["description"], className="text-muted"),
            html.Div(
                id="bbs-error",
                className="alert alert-danger",
                style={
                    "display": "none",
                    "marginBottom": "14px",
                },
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Team A (Batting First)"),
                            dcc.Dropdown(id="bbs-team-a", options=options, placeholder="Select Team A", className="mb-2"),
                        ],
                        className="col-12 col-lg-5",
                    ),
                    html.Div(
                        [
                            html.Label("Swap", style={"visibility": "hidden"}),
                            html.Button(
                                "Swap Teams",
                                id="bbs-swap-teams",
                                n_clicks=0,
                                className="btn btn-outline-secondary w-100 mb-2",
                            ),
                        ],
                        className="col-12 col-lg-2 d-flex align-items-end",
                    ),
                    html.Div(
                        [
                            html.Label("Team B (Chasing)"),
                            dcc.Dropdown(id="bbs-team-b", options=options, placeholder="Select Team B", className="mb-2"),
                        ],
                        className="col-12 col-lg-5",
                    ),
                    html.Div(
                        [
                            html.Label("Stadium"),
                            dcc.Dropdown(
                                id="bbs-stadium",
                                options=stadium_options,
                                value="",
                                placeholder="Select Stadium",
                                className="mb-2",
                            ),
                        ],
                        className="col-12 col-lg-6",
                    ),
                ],
                className="row g-3 mb-2",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Recency Bias (0 = full history, 1 = strongest recent bias)"),
                            dcc.Slider(
                                id="bbs-recency-bias",
                                min=0.0,
                                max=1.0,
                                step=0.05,
                                value=0.5,
                                marks={0.0: "0.0", 0.5: "0.5", 1.0: "1.0"},
                            ),
                        ],
                        className="col-12",
                    ),
                    html.Div(
                        [
                            html.Label("Last N Matches"),
                            dcc.Input(id="bbs-last-n-matches", type="number", min=1, step=1, value=120, className="form-control"),
                        ],
                        className="col-12 col-md-4",
                    ),
                    html.Div(
                        [
                            html.Label("Random Seed"),
                            dcc.Input(id="bbs-random-seed", type="number", min=0, step=1, value=42, className="form-control"),
                        ],
                        className="col-12 col-md-4",
                    ),
                    html.Div(
                        [
                            html.Label("Max Fallback Level"),
                            dcc.Input(id="bbs-max-fallback", type="number", min=0, max=6, step=1, value=6, className="form-control"),
                        ],
                        className="col-12 col-md-4",
                    ),
                ],
                className="row g-3 mb-3",
            ),
            dcc.Tabs(
                id="bbs-mode-tabs",
                value="simulate-match",
                className="mb-3",
                children=[
                    dcc.Tab(label="Simulate Match", value="simulate-match"),
                    dcc.Tab(label="Run N Simulations", value="run-n-simulations"),
                ],
            ),
            dcc.Store(id="bbs-simulation-data"),
            html.Div(
                [
                    html.Button("Simulate Match", id="bbs-simulate", n_clicks=0, className="btn btn-primary"),
                    html.Div(id="bbs-status", className="mt-2 text-success"),
                    dcc.Loading(
                        id="bbs-loading-overlay",
                        type="circle",
                        color=DEEP_TEAL,
                        fullscreen=True,
                        children=html.Div(id="bbs-loading-proxy", style={"display": "none"}),
                    ),
                    html.H3("Match Summary", className="mt-4"),
                    html.Div(id="bbs-match-result", className="mb-2"),
                    html.Div(
                        id="bbs-warning",
                        className="alert alert-warning",
                        style={
                            "display": "none",
                            "marginTop": "10px",
                        },
                    ),
                    html.H3("Ball-by-Ball Progression", className="mt-4"),
                    dcc.Graph(id="bbs-main-chart", figure=_empty_figure("Score Progression", "Run a simulation to view results.")),
                    html.H3("Scorecards", className="mt-4"),
                    html.Div(id="bbs-innings-summary"),
                    html.H3("Model Diagnostics", className="mt-4"),
                    html.Div(id="bbs-diagnostics"),
                    html.H3("Ball-by-Ball Replay", className="mt-4"),
                    html.Div(
                        [
                            html.Button("Play", id="bbs-replay-play", n_clicks=0, className="btn btn-outline-primary"),
                            html.Button("Reset", id="bbs-replay-reset", n_clicks=0, className="btn btn-outline-secondary ms-2"),
                        ],
                        className="mb-2",
                    ),
                    dcc.Interval(id="bbs-replay-interval", interval=700, n_intervals=0, disabled=True),
                    dcc.Slider(id="bbs-replay-slider", min=0, max=0, value=0, step=1, marks={}),
                    html.Div(id="bbs-replay-event", className="my-2"),
                    dcc.Graph(id="bbs-replay-chart", figure=_empty_figure("Replay", "Move the slider after running a simulation.")),
                    dcc.Graph(
                        id="bbs-replay-run-rate-chart",
                        figure=_empty_figure("Run Rate Timeline", "Run rate appears after legal deliveries."),
                    ),
                ],
                id="bbs-simulate-tab-content",
                style={"display": "block"},
            ),
            html.Div(
                [
                    html.H3("N-Run Simulation", className="mt-2"),
                    html.P(
                        "Run multiple simulations with incrementing seeds from the base Random Seed to see outcome spread.",
                        className="text-muted mb-2",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label("Number of Runs (N)"),
                                    dcc.Input(
                                        id="bbs-n-runs",
                                        type="number",
                                        min=1,
                                        max=DASHBOARD_CONFIG["n_runs_max"],
                                        step=1,
                                        value=DASHBOARD_CONFIG["n_runs_default"],
                                        className="form-control",
                                    ),
                                ],
                                className="col-12 col-md-3",
                            ),
                            html.Div(
                                [
                                    
                                    dcc.Checklist(
                                        id="bbs-enable-counterfactual",
                                        options=[
                                            {
                                                "label": "Enable from-state Monte Carlo",
                                                "value": "on",
                                            }
                                        ],
                                        value=[],
                                        inputStyle={"marginRight": "10px"},
                                        labelStyle={
                                            "display": "flex",
                                            "alignItems": "center",
                                            "marginBottom": "0",
                                            "whiteSpace": "nowrap",
                                            "fontSize": "16px",
                                        },
                                        style={
                                            "border": "1px solid #d0d7de",
                                            "borderRadius": "8px",
                                            "padding": "10px 12px",
                                            "backgroundColor": "#f8fafc",
                                        },
                                    ),
                                ],
                                className="col-12 col-md-5 d-flex align-items-end",
                            ),
                            html.Div(
                                [
                                    html.Label(" "),
                                    dcc.Loading(
                                        type="default",
                                        color=DEEP_TEAL,
                                        children=html.Div(
                                            [
                                                html.Button(
                                                    "Run N Simulations",
                                                    id="bbs-run-n",
                                                    n_clicks=0,
                                                    className="btn btn-outline-primary w-100",
                                                ),
                                                html.Div(id="bbs-nruns-status", className="text-success mt-2"),
                                            ]
                                        ),
                                    ),
                                ],
                                className="col-12 col-md-3 d-flex align-items-end",
                            ),
                        ],
                        className="row g-3 mb-2",
                    ),
                    html.Div(
                        id="bbs-nruns-error",
                        className="alert alert-danger",
                        style={
                            "display": "none",
                            "marginBottom": "14px",
                        },
                    ),
                    html.Div(
                        [
                            html.Div(id="bbs-nruns-summary", className="mb-2"),
                            html.Div(
                                [
                                    dcc.Graph(
                                        id="bbs-nruns-density-chart",
                                        figure=_empty_figure("Total Runs Density", "Run N simulations to view density."),
                                    ),
                                    dcc.Graph(
                                        id="bbs-nruns-cumulative-box-chart",
                                        figure=_empty_figure(
                                            "Cumulative Score Difference by Ball",
                                            "Run N simulations to view score-difference mean and 95% CI lines.",
                                        ),
                                    ),
                                ],
                                className="mt-3",
                            ),
                            html.Div(
                                [
                                    dcc.Graph(
                                        id="bbs-nruns-winprob-chart",
                                        figure=_empty_figure(
                                            "Chase Win Probability by Ball",
                                            "Run N simulations to view counterfactual from-state win probability over legal balls.",
                                        ),
                                    )
                                ],
                                className="mt-2",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        dcc.Graph(
                                            id="bbs-nruns-outcome-chart",
                                            figure=_empty_figure("Outcome Breakdown", "Run N simulations to view outcomes."),
                                        ),
                                        className="col-12 col-xl-6",
                                    ),
                                    html.Div(
                                        dcc.Graph(
                                            id="bbs-nruns-margin-chart",
                                            figure=_empty_figure("Run Differential", "Run N simulations to view margin distribution."),
                                        ),
                                        className="col-12 col-xl-6",
                                    ),
                                ],
                                className="row g-3 mt-1",
                            ),
                            html.Div(
                                [
                                    dcc.Graph(
                                        id="bbs-nruns-wicket-timing-chart",
                                        figure=_empty_figure(
                                            "Wicket Timing (Mean ± 95% CI)",
                                            "Run N simulations to view wicket timing confidence intervals.",
                                        ),
                                    )
                                ],
                                className="mt-2",
                            ),
                            html.Div(id="bbs-nruns-table", className="mt-3"),
                        ]
                    ),
                ],
                id="bbs-nruns-tab-content",
                style={"display": "none"},
            ),
        ],
        className="container-fluid py-4",
    )


@callback(
    Output("bbs-stadium", "options"),
    Output("bbs-stadium", "value"),
    Input("bbs-team-a", "value"),
    Input("bbs-team-b", "value"),
    Input("bbs-last-n-matches", "value"),
    Input("bbs-recency-bias", "value"),
    State("bbs-stadium", "value"),
)
def refresh_stadium_options(team_a, team_b, last_n_matches, recency_bias, current_stadium):
    options = _stadium_options_for_filters(team_a, team_b, last_n_matches, recency_bias)
    valid_values = {opt["value"] for opt in options}
    if current_stadium in valid_values:
        return options, current_stadium
    return options, ""


@callback(
    Output("bbs-team-a", "value"),
    Output("bbs-team-b", "value"),
    Input("bbs-swap-teams", "n_clicks"),
    State("bbs-team-a", "value"),
    State("bbs-team-b", "value"),
    prevent_initial_call=True,
)
def swap_teams(_n_clicks, team_a, team_b):
    if not team_a and not team_b:
        return no_update, no_update
    return team_b, team_a


@callback(
    Output("bbs-simulate-tab-content", "style"),
    Output("bbs-nruns-tab-content", "style"),
    Input("bbs-mode-tabs", "value"),
)
def toggle_simulation_mode_tab(tab_value):
    if tab_value == "run-n-simulations":
        return {"display": "none"}, {"display": "block"}
    return {"display": "block"}, {"display": "none"}


@callback(
    Output("bbs-simulation-data", "data"),
    Output("bbs-status", "children"),
    Output("bbs-error", "children"),
    Output("bbs-error", "style"),
    Output("bbs-loading-proxy", "children"),
    Input("bbs-simulate", "n_clicks"),
    State("bbs-team-a", "value"),
    State("bbs-team-b", "value"),
    State("bbs-stadium", "value"),
    State("bbs-recency-bias", "value"),
    State("bbs-last-n-matches", "value"),
    State("bbs-random-seed", "value"),
    State("bbs-max-fallback", "value"),
)
def run_simulation(n_clicks, team_a, team_b, stadium, recency_bias, last_n_matches, random_seed, max_fallback):
    if not n_clicks:
        return no_update, no_update, no_update, no_update, no_update

    error_style, hidden_error_style = _simulation_error_styles()

    try:
        parsed, validation_error = _validate_simulation_inputs(
            team_a=team_a,
            team_b=team_b,
            recency_bias=recency_bias,
            last_n_matches=last_n_matches,
            random_seed=random_seed,
            max_fallback=max_fallback,
        )
        if parsed is None:
            return no_update, "Validation failed.", validation_error, error_style, f"validation-{n_clicks}"

        df = _load_dataset()
        team_a_profile = TeamProfile.from_dataframe(df, team_a)
        team_b_profile = TeamProfile.from_dataframe(df, team_b)

        seed = int(parsed["seed"])
        window = int(parsed["window"])
        recency_bias_value = float(parsed["recency_bias_value"])
        fallback_level = int(parsed["fallback_level"])
        selected_stadium = str(stadium).strip() if stadium else None
        payload = _simulate_match_payload(
            engine=SimulationEngine(),
            team_a=team_a,
            team_b=team_b,
            team_a_profile=team_a_profile,
            team_b_profile=team_b_profile,
            recency_bias=recency_bias_value,
            random_seed=seed,
            max_fallback_level=fallback_level,
            last_n_matches=window,
            stadium=selected_stadium,
        )
        venue_label = selected_stadium or "All Stadiums"
        return payload, f"Simulation complete. Seed: {seed} | Window: last {window} matches | Recency: {recency_bias_value:.2f} | Stadium: {venue_label}", "", hidden_error_style, f"done-{n_clicks}"
    except DataLoadError as exc:
        return no_update, "Data load failed.", str(exc), error_style, f"error-{n_clicks}"
    except Exception as exc:
        logger.exception("Simulation callback failed")
        return no_update, "Simulation failed.", str(exc), error_style, f"error-{n_clicks}"


@callback(
    Output("bbs-nruns-summary", "children"),
    Output("bbs-nruns-table", "children"),
    Output("bbs-nruns-density-chart", "figure"),
    Output("bbs-nruns-cumulative-box-chart", "figure"),
    Output("bbs-nruns-winprob-chart", "figure"),
    Output("bbs-nruns-outcome-chart", "figure"),
    Output("bbs-nruns-margin-chart", "figure"),
    Output("bbs-nruns-wicket-timing-chart", "figure"),
    Output("bbs-nruns-status", "children"),
    Output("bbs-nruns-error", "children"),
    Output("bbs-nruns-error", "style"),
    Input("bbs-run-n", "n_clicks"),
    State("bbs-team-a", "value"),
    State("bbs-team-b", "value"),
    State("bbs-stadium", "value"),
    State("bbs-recency-bias", "value"),
    State("bbs-last-n-matches", "value"),
    State("bbs-random-seed", "value"),
    State("bbs-max-fallback", "value"),
    State("bbs-n-runs", "value"),
    State("bbs-enable-counterfactual", "value"),
)
def run_n_simulations(
    n_clicks,
    team_a,
    team_b,
    stadium,
    recency_bias,
    last_n_matches,
    random_seed,
    max_fallback,
    n_runs,
    enable_counterfactual_value,
):
    if not n_clicks:
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update

    error_style, hidden_error_style = _simulation_error_styles()

    try:
        parsed, validation_error = _validate_simulation_inputs(
            team_a=team_a,
            team_b=team_b,
            recency_bias=recency_bias,
            last_n_matches=last_n_matches,
            random_seed=random_seed,
            max_fallback=max_fallback,
        )
        if parsed is None:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "Validation failed.", validation_error, error_style

        try:
            n_runs_value = int(n_runs if n_runs is not None else DASHBOARD_CONFIG["n_runs_default"])
        except (TypeError, ValueError):
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "Validation failed.", "Number of runs (N) must be a positive integer.", error_style

        if n_runs_value < 1:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "Validation failed.", "Number of runs (N) must be a positive integer.", error_style
        if n_runs_value > int(DASHBOARD_CONFIG["n_runs_max"]):
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                "Validation failed.",
                f"Number of runs (N) cannot exceed {DASHBOARD_CONFIG['n_runs_max']}.",
                error_style,
            )

        df = _load_dataset()
        team_a_profile = TeamProfile.from_dataframe(df, team_a)
        team_b_profile = TeamProfile.from_dataframe(df, team_b)

        base_seed = int(parsed["seed"])
        window = int(parsed["window"])
        recency_bias_value = float(parsed["recency_bias_value"])
        fallback_level = int(parsed["fallback_level"])
        selected_stadium = str(stadium).strip() if stadium else None
        enable_counterfactual = bool(enable_counterfactual_value and "on" in enable_counterfactual_value)
        rollouts_per_state = max(1, int(DASHBOARD_CONFIG.get("winprob_rollouts_per_state", 32)))
        max_states_per_ball = max(1, int(DASHBOARD_CONFIG.get("winprob_max_states_per_ball", 8)))
        max_total_states = max(1, int(DASHBOARD_CONFIG.get("winprob_max_total_states", 240)))

        engine = SimulationEngine()
        prepared_context = engine.prepare_match_context(
            team_a=team_a,
            team_b=team_b,
            recency_bias=recency_bias_value,
            max_fallback_level=fallback_level,
            last_n_matches=window,
            stadium=selected_stadium,
        )
        rows = []
        cumulative_points = []
        chase_snapshots = []
        wicket_points = []
        for run_index in range(n_runs_value):
            seed = base_seed + run_index
            payload = _simulate_match_payload(
                engine=engine,
                team_a=team_a,
                team_b=team_b,
                team_a_profile=team_a_profile,
                team_b_profile=team_b_profile,
                recency_bias=recency_bias_value,
                random_seed=seed,
                max_fallback_level=fallback_level,
                last_n_matches=window,
                stadium=selected_stadium,
                prepared_context=prepared_context,
                collect_chase_snapshots=enable_counterfactual,
            )
            row = _multi_run_result_row(run_index + 1, seed, payload)
            rows.append(row)
            cumulative_points.extend(_extract_cumulative_points(payload, team_a=team_a, team_b=team_b, run_id=run_index + 1))
            if enable_counterfactual:
                chase_snapshots.extend(_extract_chase_snapshots(payload, run_id=run_index + 1))
            wicket_points.extend(_extract_wicket_fall_points(payload, team_a=team_a, team_b=team_b))

        if enable_counterfactual:
            chase_winprob_points, chase_winprob_meta = _estimate_counterfactual_winprob_points(
                chase_snapshots=chase_snapshots,
                engine=engine,
                prepared_context=prepared_context,
                base_seed=base_seed,
                rollouts_per_state=rollouts_per_state,
                max_states_per_ball=max_states_per_ball,
                max_total_states=max_total_states,
            )
        else:
            chase_winprob_points, chase_winprob_meta = [], {"truncated_states": 0, "selected_states": 0, "total_unique_states": 0}

        summary = _multi_run_summary_component(rows, team_a=team_a, team_b=team_b)
        table = _multi_run_table_component(rows, team_a=team_a, team_b=team_b)
        density_fig = _multi_run_density_figure(rows, team_a=team_a, team_b=team_b)
        cumulative_box_fig = _multi_run_cumulative_box_figure(cumulative_points, team_a=team_a, team_b=team_b)
        if enable_counterfactual:
            chase_win_prob_fig = _multi_run_chase_win_prob_figure(
                chase_winprob_points,
                team_b=team_b,
                rollouts_per_state=rollouts_per_state,
                truncated_states=int(chase_winprob_meta.get("truncated_states", 0)),
            )
        else:
            chase_win_prob_fig = _empty_figure(
                "Chase Win Probability by Ball",
                "Counterfactual is disabled. Enable the checkbox near Number of Runs (N) to compute this chart.",
            )
        outcome_fig = _multi_run_outcome_figure(rows, team_a=team_a, team_b=team_b)
        margin_fig = _multi_run_margin_figure(rows, team_a=team_a)
        wicket_timing_fig = _multi_run_wicket_timing_figure(wicket_points, team_a=team_a, team_b=team_b)
        venue_label = selected_stadium or "All Stadiums"
        truncated_states = int(chase_winprob_meta.get("truncated_states", 0))
        selected_states = int(chase_winprob_meta.get("selected_states", 0))
        total_unique_states = int(chase_winprob_meta.get("total_unique_states", 0))
        counterfactual_note = ""
        if truncated_states > 0:
            counterfactual_note = f" | WinProb states used {selected_states}/{total_unique_states} (late-ball priority cap)"
        status = (
            f"Completed {n_runs_value} simulations. Seeds {base_seed} to {base_seed + n_runs_value - 1} | "
            f"Window: last {window} matches | Recency: {recency_bias_value:.2f} | Stadium: {venue_label}"
            f"{counterfactual_note}"
        )
        if not enable_counterfactual:
            status = f"{status} | Counterfactual: off"
        return summary, table, density_fig, cumulative_box_fig, chase_win_prob_fig, outcome_fig, margin_fig, wicket_timing_fig, status, "", hidden_error_style
    except DataLoadError as exc:
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "Data load failed.", str(exc), error_style
    except Exception as exc:
        logger.exception("N-run simulation callback failed")
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "Simulation failed.", str(exc), error_style


@callback(
    Output("bbs-replay-interval", "disabled"),
    Output("bbs-replay-play", "children"),
    Input("bbs-replay-play", "n_clicks"),
    Input("bbs-replay-reset", "n_clicks"),
    Input("bbs-simulation-data", "data"),
    State("bbs-replay-interval", "disabled"),
)
def toggle_replay_interval(play_clicks, reset_clicks, sim_data, interval_disabled):
    trigger = dash.ctx.triggered_id
    if not sim_data:
        return True, "Play"

    if trigger == "bbs-replay-play":
        next_disabled = not bool(interval_disabled)
        return next_disabled, ("Play" if next_disabled else "Pause")

    # Reset or fresh simulation load: stop replay and reset button label.
    return True, "Play"


@callback(
    Output("bbs-replay-slider", "value"),
    Input("bbs-replay-interval", "n_intervals"),
    Input("bbs-replay-reset", "n_clicks"),
    Input("bbs-simulation-data", "data"),
    State("bbs-replay-slider", "value"),
    State("bbs-replay-slider", "max"),
)
def advance_replay_slider(_n_intervals, _reset_clicks, _sim_data, current_value, max_value):
    trigger = dash.ctx.triggered_id
    if trigger in {"bbs-replay-reset", "bbs-simulation-data"}:
        return 0
    if max_value is None:
        return 0
    current = int(current_value or 0)
    max_idx = int(max_value)
    return min(max_idx, current + 1)


@callback(
    Output("bbs-main-chart", "figure"),
    Output("bbs-match-result", "children"),
    Output("bbs-innings-summary", "children"),
    Output("bbs-warning", "children"),
    Output("bbs-warning", "style"),
    Output("bbs-replay-slider", "max"),
    Output("bbs-replay-slider", "marks"),
    Output("bbs-diagnostics", "children"),
    Input("bbs-simulation-data", "data"),
)
def render_simulation(sim_data):
    warning_hidden = {
        "display": "none",
        "marginTop": "10px",
    }
    if not sim_data or not sim_data.get("innings"):
        return (
            _empty_figure("Score Progression", "Run a simulation to view results."),
            "",
            "",
            "",
            warning_hidden,
            0,
            {},
            html.Div("Diagnostics unavailable for this run."),
        )

    fig = go.Figure()
    colors = [PRUSSIAN_BLUE, DEEP_TEAL]
    scorecards = []
    lineups = sim_data.get("metadata", {}).get("lineups", {})

    for idx, innings in enumerate(sim_data.get("innings", [])):
        balls = innings.get("balls", [])
        x = [ball.get("ball_number", 0) for ball in balls]
        y = [ball.get("cumulative_score", 0) for ball in balls]
        customdata = [[ball.get("runs", 0), ball.get("cumulative_wickets", 0), ball.get("event_type", "legal")] for ball in balls]
        team = innings.get("batting_team", f"Innings {idx + 1}")
        team_code = _team_short_code(str(team))
        color = colors[idx % len(colors)]
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                customdata=customdata,
                mode="lines+markers",
                name=team_code,
                line={"color": color, "width": 2},
                marker={"size": 5},
                hovertemplate=(
                    f"<b>{team}</b><br>"
                    "Event %{x}<br>"
                    "Score %{y}/%{customdata[1]}<br>"
                    "Runs this event %{customdata[0]}<br>"
                    "Event %{customdata[2]}"
                    "<extra></extra>"
                ),
            )
        )
        _add_wicket_trace(fig=fig, balls=balls, team=str(team), line_color=color)
        scorecards.append(
            _build_scorecard_for_innings(
                innings=innings,
                lineup=lineups.get(team),
            )
        )

    apply_chart_theme(
        fig,
        title="Ball-by-Ball Score Progression",
        xaxis_title="Event Number",
        yaxis_title="Cumulative Score",
        height=460,
    )
    max_event = max((len(inn.get("balls", [])) for inn in sim_data.get("innings", [])), default=120)
    fig.update_xaxes(range=[0, max(120, max_event)])
    fig.update_layout(hovermode="x unified")
    fig.update_xaxes(showspikes=True, spikemode="across", spikesnap="cursor", spikethickness=1)

    warning = sim_data.get("low_confidence_warning", "")
    warning_style = {**warning_hidden, "display": "block"} if warning else warning_hidden

    flat = _flatten_deliveries(sim_data)
    slider_max = max(0, len(flat) - 1)
    step = max(1, len(flat) // 8) if flat else 1
    marks = {i: str(i + 1) for i in range(0, slider_max + 1, step)}
    if slider_max not in marks:
        marks[slider_max] = str(slider_max + 1)

    diagnostics = _diagnostics_component(sim_data)

    return (
        fig,
        _match_summary_component(sim_data),
        html.Div(scorecards),
        warning,
        warning_style,
        slider_max,
        marks,
        diagnostics,
    )


@callback(
    Output("bbs-replay-event", "children"),
    Output("bbs-replay-chart", "figure"),
    Output("bbs-replay-run-rate-chart", "figure"),
    Input("bbs-replay-slider", "value"),
    Input("bbs-simulation-data", "data"),
)
def render_replay(ball_index, sim_data):
    if not sim_data:
        return (
            html.Div("Run a simulation to begin replay.", className="text-muted"),
            _empty_figure("Replay", "Run a simulation to begin replay."),
            _empty_figure("Run Rate Timeline", "Run a simulation to begin replay."),
        )

    deliveries = _flatten_deliveries(sim_data)
    if not deliveries:
        return (
            html.Div("No deliveries available.", className="text-muted"),
            _empty_figure("Replay", "No replay data available."),
            _empty_figure("Run Rate Timeline", "No replay data available."),
        )

    idx = int(ball_index or 0)
    idx = max(0, min(idx, len(deliveries) - 1))
    event = deliveries[idx]

    innings_list = sim_data.get("innings", [])
    chase_target = None
    if len(innings_list) >= 1:
        chase_target = int(innings_list[0].get("total_runs", 0)) + 1
    event_text = _broadcast_replay_banner(event, idx + 1, len(deliveries), chase_target=chase_target)

    fig = go.Figure()
    run_rate_fig = go.Figure()

    selected_x = int(event.get("ball_number", 0))
    selected_x = int(event.get("ball_number", selected_x))
    selected_score = event.get("cumulative_score", 0)
    selected_rr = 0.0
    selected_legal_ball = int(event.get("legal_ball_number", 0) or 0)
    if selected_legal_ball > 0:
        selected_rr = (float(selected_score) * 6.0) / float(selected_legal_ball)
    colors = [PRUSSIAN_BLUE, DEEP_TEAL]

    # Reveal only what has been "played" up to current replay position.
    current_innings_no = int(event.get("innings_number", 1))
    current_ball_no = int(event.get("ball_number", 0))

    for i, inn in enumerate(innings_list):
        balls = inn.get("balls", [])
        inn_no = int(inn.get("innings_number", i + 1))
        team_name = inn.get("batting_team", f"Innings {i + 1}")
        team_code = _team_short_code(str(team_name))
        color = colors[i % len(colors)]

        if inn_no < current_innings_no:
            visible_balls = balls
        elif inn_no == current_innings_no:
            visible_balls = [b for b in balls if int(b.get("ball_number", 0)) <= current_ball_no]
        else:
            visible_balls = []

        x = [int(ball.get("ball_number", 0)) for ball in visible_balls]
        y = [ball.get("cumulative_score", 0) for ball in visible_balls]
        if x:
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="lines+markers",
                    name=team_code,
                    line={"color": color, "width": 2},
                    marker={"size": 5},
                    hovertemplate=(
                        f"<b>{team_name}</b><br>"
                        "Event %{x}<br>"
                        "Score %{y}<extra></extra>"
                    ),
                )
            )
            _add_wicket_trace(fig=fig, balls=visible_balls, team=str(team_name), line_color=color)

        run_rate_points = []
        for ball in visible_balls:
            legal_ball_no = int(ball.get("legal_ball_number", 0) or 0)
            if legal_ball_no <= 0:
                continue
            run_rate_points.append(
                (
                    int(ball.get("ball_number", 0)),
                    (float(ball.get("cumulative_score", 0)) * 6.0) / float(legal_ball_no),
                    legal_ball_no,
                )
            )
        if run_rate_points:
            rr_x = [point[0] for point in run_rate_points]
            rr_y = [point[1] for point in run_rate_points]
            rr_legal = [point[2] for point in run_rate_points]
            run_rate_fig.add_trace(
                go.Scatter(
                    x=rr_x,
                    y=rr_y,
                    mode="lines+markers",
                    name=team_code,
                    line={"color": color, "width": 2},
                    marker={"size": 5},
                    customdata=rr_legal,
                    hovertemplate=(
                        f"<b>{team_name}</b><br>"
                        "Event %{x}<br>"
                        "Run Rate %{y:.2f}<br>"
                        "Legal Ball %{customdata}<extra></extra>"
                    ),
                )
            )

    fig.add_trace(
        go.Scatter(
            x=[selected_x],
            y=[selected_score],
            mode="markers",
            name="Current Ball",
            marker={"size": 12, "color": BRICK_EMBER, "symbol": "diamond"},
        )
    )
    if selected_legal_ball > 0:
        run_rate_fig.add_trace(
            go.Scatter(
                x=[selected_x],
                y=[selected_rr],
                mode="markers",
                name="Current Ball",
                marker={"size": 12, "color": BRICK_EMBER, "symbol": "diamond"},
            )
        )
    apply_chart_theme(
        fig,
        title="Replay: Both Innings (Event Timeline)",
        xaxis_title="Event Number",
        yaxis_title="Cumulative Score",
        height=420,
    )
    apply_chart_theme(
        run_rate_fig,
        title="Replay: Run Rate Timeline",
        xaxis_title="Event Number",
        yaxis_title="Run Rate",
        height=360,
    )
    max_event = max((len(inn.get("balls", [])) for inn in innings_list), default=120)
    fig.update_xaxes(range=[0, max(120, max_event)])
    run_rate_fig.update_xaxes(range=[0, max(120, max_event)])
    run_rate_fig.update_layout(hovermode="x unified")
    return event_text, fig, run_rate_fig


dash.register_page(
    __name__,
    path=DASHBOARD_CONFIG.get("page_path", "/ball-by-ball-simulation"),
    name=DASHBOARD_CONFIG.get("title", "Ball-by-Ball Match Simulation"),
    title=DASHBOARD_CONFIG.get("title", "Ball-by-Ball Match Simulation"),
    description=DASHBOARD_CONFIG.get("description", ""),
    order=DASHBOARD_CONFIG.get("nav_order", 2),
    dashboard_title=DASHBOARD_CONFIG.get("title", "Ball-by-Ball Match Simulation"),
    dashboard_description=DASHBOARD_CONFIG.get("description", ""),
    dashboard_visible=DASHBOARD_CONFIG.get("is_visible", True),
    layout=layout,
)


