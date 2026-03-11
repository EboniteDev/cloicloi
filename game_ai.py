import random

# Scores simplified yaku (winning combinations) for a card list
def score(cards):
    counts = {'bright':0, 'animal':0, 'ribbon':0, 'chaff':0}
    for c in cards: counts[c['type']] += 1
    points=0
    if counts['bright']>=3: points+=20
    if counts['animal']>=5: points+=10
    if counts['ribbon']>=5: points+=5
    if counts['chaff']>=10: points+=1
    return points

# Advanced AI selects card to maximize future scoring potential with simple look ahead
def select_card(hand, table, collected, draw_pile):
    def potential_score(cards):
        # Heuristic: current score plus potential from having matching table/draw cards
        base = score(cards)
        months_on_table = set(c['month'] for c in table)
        future_matches = sum(1 for c in draw_pile if c['month'] in months_on_table)
        return base + future_matches  
    best_card = None
    best_val = -1
    for card in hand:
        temp_collected = collected + [card]
        val = potential_score(temp_collected)
        if val > best_val:
            best_val = val
            best_card = card
    # If no best found, pick random
    return best_card or random.choice(hand)
