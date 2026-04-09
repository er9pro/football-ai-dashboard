import json
import os
import random
from datetime import datetime, timedelta

DATA_DIR = 'data'

# Demo teams for each league
TEAMS = {
    'Premier League': ['Manchester City', 'Arsenal', 'Liverpool', 'Manchester United', 'Chelsea', 'Tottenham'],
    'La Liga': ['Real Madrid', 'Barcelona', 'Atletico Madrid', 'Sevilla', 'Real Sociedad', 'Athletic Bilbao'],
    'Serie A': ['Inter Milan', 'AC Milan', 'Juventus', 'Napoli', 'Roma', 'Lazio'],
    'Bundesliga': ['Bayern Munich', 'Borussia Dortmund', 'RB Leipzig', 'Bayer Leverkusen', 'Union Berlin', 'Freiburg']
}

def generate_demo_predictions():
    """Generate demo predictions without API keys"""
    predictions = []
    
    for league, teams in TEAMS.items():
        # Generate 3-5 matches per league
        num_matches = random.randint(3, 5)
        
        for i in range(num_matches):
            # Select random home and away teams
            home, away = random.sample(teams, 2)
            
            # Generate realistic stats
            home_xg = round(random.uniform(0.8, 2.5), 2)
            away_xg = round(random.uniform(0.8, 2.5), 2)
            home_ppda = round(random.uniform(6, 12), 2)
            away_ppda = round(random.uniform(6, 12), 2)
            
            # Calculate probabilities based on xG
            total_xg = home_xg + away_xg
            home_prob = round((home_xg / total_xg) * 100, 1)
            draw_prob = round(random.uniform(20, 30), 1)
            away_prob = round(100 - home_prob - draw_prob, 1)
            
            # Generate odds (inverse of probability with bookmaker margin)
            home_odds = round(100 / home_prob * 0.9, 2)
            draw_odds = round(100 / draw_prob * 0.9, 2)
            away_odds = round(100 / away_prob * 0.9, 2)
            
            # Calculate value bets
            value_home = round((home_prob / 100) * home_odds - 1, 2)
            value_away = round((away_prob / 100) * away_odds - 1, 2)
            
            # Determine best bet
            if value_home > 0.05:
                bet_type = 'Home'
                value_pct = round(value_home * 100, 1)
            elif value_away > 0.05:
                bet_type = 'Away'
                value_pct = round(value_away * 100, 1)
            else:
                bet_type = None
                value_pct = 0
            
            # Generate match date (next 7 days)
            match_date = datetime.now() + timedelta(days=random.randint(0, 7))
            
            prediction = {
                'league': league,
                'home_team': home,
                'away_team': away,
                'match_date': match_date.strftime('%Y-%m-%d %H:%M'),
                'home_xg': home_xg,
                'away_xg': away_xg,
                'home_ppda': home_ppda,
                'away_ppda': away_ppda,
                'prob_home': home_prob,
                'prob_draw': draw_prob,
                'prob_away': away_prob,
                'odds_home': home_odds,
                'odds_draw': draw_odds,
                'odds_away': away_odds,
                'value_bet': bet_type,
                'value_pct': value_pct,
                'confidence': round(random.uniform(60, 85), 1),
                'injuries': random.choice(['None', f'{random.randint(1,3)} key players', 'Goalkeeper out']),
                'form': f'{random.choice(["W","D","L"])}{random.choice(["W","D","L"])}{random.choice(["W","D","L"])}'
            }
            
            predictions.append(prediction)
    
    return predictions

if __name__ == '__main__':
    print("Generating demo predictions...")
    
    # Create data directory
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Generate predictions
    predictions = generate_demo_predictions()
    
    # Save to file
    output_file = os.path.join(DATA_DIR, 'predictions.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(predictions, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Generated {len(predictions)} demo predictions")
    print(f"✓ Saved to {output_file}")
    print("\nDemo mode - using generated data without API keys")
