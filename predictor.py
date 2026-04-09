import json
import os
import math
from datetime import datetime

DATA_DIR = 'data'
PPDA_BOOST = 0.05
INJURY_PENALTY = 0.15
VALUE_THRESHOLD = 0.05

def load_json(fn):
    path = os.path.join(DATA_DIR, fn)
    return json.load(open(path)) if os.path.exists(path) else {}

def poisson(lam, k):
    return (lam**k * math.exp(-lam)) / math.factorial(min(k, 20))

def bivariate_poisson(lh, la, mg=6):
    matrix = [[poisson(lh, i) * poisson(la, j) for j in range(mg+1)] for i in range(mg+1)]
    return matrix

def calc_probabilities(matrix):
    home_win = sum(sum(matrix[i][j] for j in range(i)) for i in range(1, len(matrix)))
    draw = sum(matrix[i][i] for i in range(len(matrix)))
    away_win = sum(sum(matrix[i][j] for j in range(i+1, len(matrix[0]))) for i in range(len(matrix)))
    total = home_win + draw + away_win
    return {"1": home_win/total, "X": draw/total, "2": away_win/total} if total > 0 else {}

def calc_totals(matrix, line=2.5):
    over = sum(sum(matrix[i][j] for j in range(len(matrix[0])) if i+j > line) for i in range(len(matrix)))
    under = 1 - over
    return {"over": over, "under": under}

def get_team_stats(team, xg_data):
    for name, data in xg_data.items():
        if team.lower() in name.lower() or name.lower() in team.lower():
            return data
    return None

def get_injury_count(team, injuries):
    for name, inj_list in injuries.items():
        if team.lower() in name.lower():
            return len(inj_list)
    return 0

def predict_match(fixture, xg_data, odds_data, injuries):
    home, away = fixture['home'], fixture['away']
    h_stats = get_team_stats(home, xg_data)
    a_stats = get_team_stats(away, xg_data)
    
    if not h_stats or not a_stats:
        return None
    
    lambda_h = h_stats['xG_avg'] * 1.1
    lambda_a = a_stats['xG_avg']
    
    if h_stats.get('ppda', 10) < 9:
        lambda_h *= (1 + PPDA_BOOST)
    if a_stats.get('ppda', 10) < 9:
        lambda_a *= (1 + PPDA_BOOST)
    
    h_inj = get_injury_count(home, injuries)
    a_inj = get_injury_count(away, injuries)
    if h_inj > 2:
        lambda_h *= (1 - INJURY_PENALTY)
    if a_inj > 2:
        lambda_a *= (1 - INJURY_PENALTY)
    
    matrix = bivariate_poisson(lambda_h, lambda_a)
    probs_1x2 = calc_probabilities(matrix)
    probs_totals = calc_totals(matrix)
    
    odds_key = f"{home} vs {away}"
    odds = odds_data.get(odds_key, {})
    h2h = odds.get('h2h', {})
    
    value_bets = []
    for outcome, prob in probs_1x2.items():
        odd_val = h2h.get(home if outcome == '1' else (away if outcome == '2' else 'Draw'), 0)
        if odd_val > 1:
            implied = 1 / odd_val
            value_pct = (prob / implied - 1) * 100 if implied > 0 else 0
            if value_pct > VALUE_THRESHOLD * 100 and prob > 0.30:
                value_bets.append({"type": outcome, "value%": round(value_pct, 1), "prob": round(prob*100, 1)})
    
    confidence = 70
    if h_stats.get('form_pts', 0) > 10 and a_stats.get('form_pts', 0) > 10:
        confidence = 85
    if h_inj > 3 or a_inj > 3:
        confidence = 60
    
    return {
        "match_id": fixture['id'],
        "home": home,
        "away": away,
        "date": fixture['date'],
        "time": fixture['time'],
        "league": fixture['league'],
        "predictions": {
            "1X2": {k: round(v*100, 1) for k, v in probs_1x2.items()},
            "totals": {"over2.5": round(probs_totals['over']*100, 1), "under2.5": round(probs_totals['under']*100, 1)}
        },
        "value_bets": value_bets,
        "confidence": confidence,
        "lambda_home": round(lambda_h, 2),
        "lambda_away": round(lambda_a, 2),
        "injuries": {"home": h_inj, "away": a_inj}
    }

def run_predictions():
    fixtures = load_json('fixtures.json')
    xg_data = load_json('xg_stats.json')
    odds_data = load_json('odds.json')
    injuries = load_json('injuries.json')
    
    predictions = []
    for fix in fixtures:
        pred = predict_match(fix, xg_data, odds_data, injuries)
        if pred:
            predictions.append(pred)
    
    with open(f'{DATA_DIR}/predictions.json', 'w') as f:
        json.dump(predictions, f, indent=2, ensure_ascii=False)
    
    print(f'Generated {len(predictions)} predictions')
    print(f'Value bets found: {sum(len(p["value_bets"]) for p in predictions)}')
    return predictions

if __name__ == '__main__':
    run_predictions()
