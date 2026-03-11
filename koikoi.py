import random, sys, time, json, os
from cards import CARDS
#      _       _      _       _
#  ___| | ___ (_) ___| | ___ (_)
# / __| |/ _ \| |/ __| |/ _ \| |
#| (__| | (_) | | (__| | (_) | |
# \___|_|\___/|_|\___|_|\___/|_|
#
# Main game loop script for cloicloi, a terminal based koi-koi game for Linux systems coded in python.

def load_language(lang_code):
    try:
        with open(f"./translations/{lang_code}.json", encoding="utf-16") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {lang_code} translations: {e}")
        sys.exit(1)

def tr(key):
    return current_language.get(key, f"[{key}]")

def build_deck():
    deck = []
    for month in range(1, 13):
        entries = [c for c in CARDS if c[0] == month]
        for i, (m, _, t, a) in enumerate(entries):
            name = tr(f"card_{month}_{i+1}")
            deck.append({'month': m, 'name': name, 'type': t, 'ascii': a})
    return deck

def print_cards(cards, label):
    print(f"\n{label}:")
    for i in range(3):
        print(' '.join(c['ascii'][i] for c in cards))

def matches(table, card):
    return [c for c in table if c['month'] == card['month']]

def score(cards):
    counts = {'bright':0,'animal':0,'ribbon':0,'chaff':0}
    for c in cards: counts[c['type']] += 1
    pts, det = 0, []
    if counts['bright']>=3: pts+=20; det.append("Bright x3+") # Crane, Curtain, Bridge, Moon, Ono, Phoenix
    if counts['animal']>=5: pts+=10; det.append("Animal x5+") # Wrabler, Cuckoo, Butterflies, Boar, Geese, Sake, Deer, Swallow
    if counts['ribbon']>=5: pts+=5;  det.append("Ribbon x5+")
    if counts['chaff']>=10:  pts+=1;  det.append("Chaff x10+")
    return pts, det

def input_select(cards, prompt):
    while True:
        for i, c in enumerate(cards,1): print(f"{i}. {c['name']} ({c['month']}) [{c['type']}]")
        s = input(prompt)
        if s.lower() == 'q': sys.exit(tr("exit_message"))
        if s.isdigit() and 1 <= int(s) <= len(cards): return cards[int(s)-1]
        print(tr("invalid_choice"))

def select_card(hand, table, collected, draw):
    def potential_score(cards_):
        base, _ = score(cards_)
        months = set(c['month'] for c in table)
        future = sum(1 for c in draw if c['month'] in months)
        return base + future
    best, best_val = None, -1
    for card in hand:
        val = potential_score(collected+[card])
        if val > best_val:
            best_val, best = val, card
    return best or random.choice(hand)

def computer_select(hand, table, collected, diff, draw):
    if diff == 'easy':
        return random.choice(hand)
    if diff == 'medium':
        match_cards = [c for c in hand if matches(table,c)]
        return random.choice(match_cards) if match_cards else random.choice(hand)
    return select_card(hand, table, collected, draw)

def clear(): print("\033c", end="")

def select_language():
    files = [f for f in os.listdir('.') if f.startswith('translations_') and f.endswith('.json')]
    langs = [f[len('translations_'):-len('.json')] for f in files]
    if not langs:
        print("No translation files found, exiting."); sys.exit(1)
    print("Select language:")
    for i, l in enumerate(langs,1): print(f"{i}. {l}")
    while True:
        choice = input("Choose language: ")
        if choice.isdigit() and 1 <= int(choice) <= len(langs):
            return langs[int(choice)-1]
        print("Invalid choice.")

def koikoi():
    global current_language
    lang_code = select_language()
    current_language = load_language(lang_code)

    deck = build_deck()
    random.shuffle(deck)
    p_hand, c_hand, table, draw = deck[:8], deck[8:16], deck[16:28], deck[28:]
    p_collected, c_collected = [], []

    print(tr("select_ai"))
    while True:
        diff = input(tr("difficulty_prompt")).lower()
        if diff in ['easy','medium','hard']: break
        print(tr("invalid_choice"))

    turn = 0
    while (p_hand or c_hand) and draw:
        clear()
        print("------ Koikoi! ------")
        print_cards(table, tr("table_cards"))
        if turn == 0:
            print_cards(p_hand, tr("your_hand"))
            card = input_select(p_hand, tr("choose_card"))
            p_hand.remove(card)
        else:
            card = computer_select(c_hand, table, c_collected, diff, draw)
            c_hand.remove(card)
            print(f"{tr('computer_plays')}: {card['name']} ({card['month']})")
            time.sleep(1)

        mt = matches(table, card)
        if len(mt) == 1:
            table.remove(mt[0])
            (p_collected if turn == 0 else c_collected).extend([card, mt[0]])
            print(tr("match_collected"))
            if draw:
                d = draw.pop()
                print(f"{tr('drawn_card')} {d['name']} ({d['month']})")
                dt = matches(table, d)
                if len(dt) == 1:
                    table.remove(dt[0])
                    (p_collected if turn == 0 else c_collected).extend([d, dt[0]])
                    print(tr("draw_match"))
                else: table.append(d)
            else: print(tr("draw_empty"))
        else:
            table.append(card)
            if draw:
                d = draw.pop()
                print(f"{tr('drawn_card')} {d['name']} ({d['month']})")
                table.append(d)
            else: print(tr("draw_empty"))

        if turn == 0:
            pts, det = score(p_collected)
            if pts:
                print(tr("scored_pts").format(pts=pts, details=', '.join(det)))
                if input(tr("score_prompt")) == 'f':
                    print(tr("you_fold"))
                    break
        else:
            pts, det = score(c_collected)
            if pts and random.random() < {'easy':0.1,'medium':0.3,'hard':0.6}[diff]:
                print(tr("computer_ends").format(pts=pts, details=', '.join(det)))
                break

        turn = 1 - turn
        input(tr("press_enter"))

    p_pts, p_det = score(p_collected)
    c_pts, c_det = score(c_collected)

    print(f"\n{tr('round_over')}\nYou: {p_pts} pts {'('+', '.join(p_det)+')' if p_det else ''}\nComputer: {c_pts} pts {'('+', '.join(c_det)+')' if c_det else ''}")
    if p_pts > c_pts: print(tr("you_win"))
    elif c_pts > p_pts: print(tr("computer_win"))
    else: print(tr("draw"))

if __name__ == "__main__":
    koikoi()
