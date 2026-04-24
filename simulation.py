# =============================================================
# simulation.py — Silnik symulacji (niezależny od Colaba)
# Importowany przez app.py (Streamlit)
# =============================================================

import pandas as pd
import numpy as np


# =============================================================
# FUNKCJE POMOCNICZE
# =============================================================

def calculate_max_drawdown(series):
    if series.empty: return 0
    roll_max = series.expanding().max()
    drawdown = series - roll_max
    return round(drawdown.min(), 2)

def get_max_losing_streak(series):
    if series.empty: return 0
    is_loss = (series == 0).astype(int)
    streak = is_loss.groupby((is_loss != is_loss.shift()).cumsum()).cumsum()
    return int(streak.max())

def get_match_type(row):
    try:
        t_goals = pd.to_numeric(row['team_goals'])
        o_goals = pd.to_numeric(row['opponent_goals'])
        diff = t_goals - o_goals
        if diff == 0:   return 'DRAW'
        elif diff == 1: return 'TEAM_WIN_BY_1'
        elif diff == -1:return 'TEAM_LOSS_BY_1'
        elif diff > 0:  return 'TEAM_WIN'
        else:           return 'TEAM_LOSS'
    except:
        return 'UNKNOWN'

def parse_split(split_str):
    if pd.isna(split_str): return [100, 0]
    try:
        return [int(x) for x in str(split_str).split('/')]
    except:
        return [100, 0]

def mean_active_stake(x):
    active = x[x > 0]
    return active.mean() if not active.empty else 0

def count_active_matches(x):
    return int((x > 0).sum())


# =============================================================
# KONFIGURACJA REGUŁ (rules_config)
# =============================================================

def get_waiting_logic(event_code, odds_val):
    """Zwraca nowy, niezależny obiekt logiki 3-poziomy + WAITING."""
    return {
        "events": [event_code],
        "odds":   (odds_val, 0),
        "split":  (1.0, 0.0),
        "states": {
            "S1":      {"stake": 100, "on_win": "S1", "on_loss": "S2"},
            "S2":      {"stake": 150, "on_win": "S1", "on_loss": "S3"},
            "S3":      {"stake": 250, "on_win": "S1", "on_loss": "WAITING"},
            "WAITING": {"stake": 0,   "on_win": "S1", "on_loss": "WAITING"},
        },
        "start_state": "S1"
    }

def build_rules_config():
    """Buduje i zwraca słownik rules_config. Każde wywołanie = nowe obiekty."""
    cfg = {
        "DRAW_3LEVEL_WAITING":  get_waiting_logic("DRAW", 3.2),
        "DRAW_3LEVEL_BOTH":     get_waiting_logic("DRAW", 3.2),
        "DRAW_3LEVEL_HOME":     get_waiting_logic("DRAW", 3.2),
        "DRAW_3LEVEL_AWAY":     get_waiting_logic("DRAW", 3.2),

        "WIN1_3LEVEL_WAITING":  get_waiting_logic("TEAM_WIN_BY_1", 3.5),
        "WIN1_3LEVEL_BOTH":     get_waiting_logic("TEAM_WIN_BY_1", 3.5),
        "WIN1_3LEVEL_HOME":     get_waiting_logic("TEAM_WIN_BY_1", 3.5),
        "WIN1_3LEVEL_AWAY":     get_waiting_logic("TEAM_WIN_BY_1", 3.5),

        "LOSE1_3LEVEL_WAITING": get_waiting_logic("TEAM_LOSS_BY_1", 3.5),
        "LOSE1_3LEVEL_BOTH":    get_waiting_logic("TEAM_LOSS_BY_1", 3.5),
        "LOSE1_3LEVEL_HOME":    get_waiting_logic("TEAM_LOSS_BY_1", 3.5),
        "LOSE1_3LEVEL_AWAY":    get_waiting_logic("TEAM_LOSS_BY_1", 3.5),

        "HOME_STATE_PROGRESSION": {
            "events": ["DRAW", "TEAM_WIN_BY_1"],
            "odds":   (3.2, 3.5),
            "split":  (0.7, 0.3),
            "states": {
                "S1": {"stake": 100, "on_win": "S1", "on_loss": "S2"},
                "S2": {"stake": 150, "on_win": "S1", "on_loss": "S3"},
                "S3": {"stake": 240, "on_win": "S2", "on_loss": "S3"},
            },
            "start_state": "S1"
        },

        "DRAW_CLASSIC_PROGRESSION": {
            "events": ["DRAW"],
            "odds":   (3.2, 0),
            "split":  (1.0, 0.0),
            "states": {
                "S1": {"stake": 100, "on_win": "S1", "on_loss": "S2"},
                "S2": {"stake": 150, "on_win": "S1", "on_loss": "S3"},
                "S3": {"stake": 250, "on_win": "S1", "on_loss": "S1"},
            },
            "start_state": "S1"
        },

        "DRAW_RECOVERY_PROGRESSION": {
            "events": ["DRAW"],
            "odds":   (3.2, 0),
            "split":  (1.0, 0.0),
            "states": {
                "S1": {"stake": 100, "on_win": "S1", "on_loss": "S2"},
                "S2": {"stake": 190, "on_win": "S1", "on_loss": "S3"},
                "S3": {"stake": 350, "on_win": "S1", "on_loss": "S4"},
                "S4": {"stake": 520, "on_win": "S1", "on_loss": "S4"},
            },
            "start_state": "S1"
        },
    }

    splits_win = {
        "BALANCED": (0.7, 0.3), "40_60": (0.4, 0.6),
        "30_70":    (0.3, 0.7), "20_80": (0.2, 0.8)
    }
    for k, v in splits_win.items():
        cfg[f"DRAW_OR_WIN1_{k}"] = {
            "events": ["DRAW", "TEAM_WIN_BY_1"],
            "odds":   (3.2, 3.5), "split": v,
            "states": {
                "S1": {"stake": 100, "on_win": "S1", "on_loss": "S2"},
                "S2": {"stake": 190, "on_win": "S1", "on_loss": "S3"},
                "S3": {"stake": 350, "on_win": "S2", "on_loss": "S4"},
                "S4": {"stake": 520, "on_win": "S2", "on_loss": "S3"},
            },
            "start_state": "S1"
        }

    splits_lose = {
        "80_20": (0.8, 0.2), "70_30": (0.7, 0.3), "60_40": (0.6, 0.4),
        "40_60": (0.4, 0.6), "30_70": (0.3, 0.7), "20_80": (0.2, 0.8)
    }
    for k, v in splits_lose.items():
        cfg[f"DRAW_OR_LOSE1_{k}"] = {
            "events": ["DRAW", "TEAM_LOSS_BY_1"],
            "odds":   (3.2, 3.5), "split": v,
            "states": {
                "S1": {"stake": 100, "on_win": "S1", "on_loss": "S2"},
                "S2": {"stake": 190, "on_win": "S1", "on_loss": "S3"},
                "S3": {"stake": 350, "on_win": "S2", "on_loss": "S4"},
                "S4": {"stake": 520, "on_win": "S2", "on_loss": "S3"},
            },
            "start_state": "S1"
        }

    return cfg


# =============================================================
# WALIDACJA KONFIGURACJI
# =============================================================

def validate_rules_config(rules_df, rules_config):
    """
    Sprawdza spójność między rules.xlsx a rules_config.
    Zwraca (errors, warnings) — listy komunikatów.
    """
    errors, warnings = [], []

    active_state = rules_df[
        (rules_df['rule_type'].astype(str).str.upper() == 'STATE') &
        (rules_df['active'].astype(str).str.upper().isin(['YES', '1']))
    ]

    for _, row in active_state.iterrows():
        r_id   = str(row['rule_id']).strip()
        r_name = str(row['rule_name']).strip()
        if r_name not in rules_config:
            errors.append(
                f"❌ [{r_id}] rule_name='{r_name}' istnieje w Excelu, "
                f"ale BRAK logiki w rules_config."
            )

    used = set(active_state['rule_name'].str.strip().tolist())
    for cfg_name in rules_config:
        if cfg_name not in used:
            warnings.append(
                f"⚠️  Logika '{cfg_name}' istnieje w rules_config, "
                f"ale żadna aktywna reguła jej nie używa."
            )

    dupes = active_state[active_state.duplicated(subset=['rule_id'], keep=False)]
    if not dupes.empty:
        errors.append(
            f"❌ Zduplikowane rule_id w Excelu: "
            f"{dupes['rule_id'].unique().tolist()}"
        )

    return errors, warnings


# =============================================================
# GŁÓWNA FUNKCJA SYMULACJI
# =============================================================

def run_simulation(matches: pd.DataFrame, rules: pd.DataFrame) -> tuple:
    """
    Uruchamia pełną symulację.
    Zwraca (sim_results DataFrame, summary DataFrame).
    """
    matches = matches.copy()
    rules   = rules.copy()

    matches.columns = matches.columns.str.strip()
    rules.columns   = rules.columns.str.strip()
    matches['team_side'] = matches['team_side'].astype(str).str.strip().str.upper()

    rules_config = build_rules_config()

    # Walidacja — rzuca wyjątek tylko przy błędach krytycznych
    errors, _ = validate_rules_config(rules, rules_config)
    if errors:
        raise ValueError("\n".join(errors))

    results = []

    for _, rule in rules.iterrows():
        if str(rule.get('active', 'YES')).upper() not in ['YES', '1']:
            continue

        r_id   = str(rule['rule_id']).strip()
        r_name = str(rule['rule_name']).strip()
        r_type = str(rule.get('rule_type', 'CLASSIC')).strip().upper()
        r_side = str(rule.get('applies_to_side', 'BOTH')).strip().upper()

        running_balance = 0
        loss_streak     = 0
        state           = None
        step            = 1

        if r_type == "STATE":
            if r_name not in rules_config:
                continue
            config = rules_config[r_name]
            state  = config["start_state"]

        for _, match in matches.iterrows():
            m_side = str(match['team_side']).strip().upper()
            if r_side != "BOTH" and m_side != r_side:
                continue

            match_type = get_match_type(match)

            if r_type == "STATE":
                state_cfg = config["states"][state]
                stake     = state_cfg["stake"]
                s1, s2    = config.get("split", (1.0, 0.0))
                odds1, odds2 = config["odds"]

                h1  = int(match_type == config["events"][0])
                h2  = int(len(config["events"]) > 1 and match_type == config["events"][1])
                hit = int(h1 or h2)

                net = (stake * s1 * odds1 * h1 + stake * s2 * odds2 * h2) - stake
                running_balance += net

                results.append({
                    "match_no":        match['match_no'],
                    "rule_id":         r_id,
                    "rule_name":       r_name,
                    "side":            r_side,
                    "engine":          "STATE",
                    "state":           state,
                    "stake":           stake,
                    "match_type":      match_type,
                    "hit":             hit,
                    "net_result":      round(net, 2),
                    "running_balance": round(running_balance, 2)
                })

                if hit:
                    loss_streak = 0
                    state = state_cfg["on_win"]
                else:
                    loss_streak += 1
                    if r_name == "HOME_STATE_PROGRESSION" and state == "S0" and loss_streak >= 2:
                        state = "S1"
                    else:
                        state = state_cfg["on_loss"]

            else:
                splits = parse_split(rule.get(f'step_{int(step)}_split'))
                stake  = rule['base_stake']

                hit1 = int(match_type == rule['event_1_code'])
                hit2 = int(match_type == rule.get('event_2_code', 'NONE'))
                hit  = int(hit1 or hit2)

                net = (
                    stake * (splits[0] / 100) * rule['event_1_odds'] * hit1 +
                    stake * (splits[1] / 100) * rule.get('event_2_odds', 0) * hit2
                ) - stake
                running_balance += net

                results.append({
                    "match_no":        match['match_no'],
                    "rule_id":         r_id,
                    "rule_name":       r_name,
                    "side":            r_side,
                    "engine":          "CLASSIC",
                    "state":           f"Step {step}",
                    "stake":           stake,
                    "match_type":      match_type,
                    "hit":             hit,
                    "net_result":      round(net, 2),
                    "running_balance": round(running_balance, 2)
                })

                if hit == 1 and str(rule.get('reset_after_hit', 'YES')).upper() == 'YES':
                    step = 1
                else:
                    step = min(step + 1, int(rule.get('max_steps', 1)))

    sim_results = pd.DataFrame(results)

    if sim_results.empty:
        return sim_results, pd.DataFrame()

    summary = sim_results.groupby(['rule_id', 'rule_name', 'side', 'engine']).agg(
        matches        = ('match_no', 'count'),
        active_matches = ('stake',    count_active_matches),
        hits           = ('hit',      'sum'),
        total_profit   = ('net_result', 'sum'),
        avg_stake      = ('stake',    mean_active_stake),
        max_drawdown   = ('running_balance', calculate_max_drawdown),
        max_streak     = ('hit',      get_max_losing_streak)
    ).reset_index()

    summary['hit_rate'] = round(summary['hits'] / summary['matches'] * 100, 2)
    summary['roi'] = round(
        summary['total_profit'] /
        (summary['active_matches'] * summary['avg_stake']).replace(0, 1),
        4
    )
    summary = summary.sort_values(by='roi', ascending=False)

    return sim_results, summary
