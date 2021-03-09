import csv
import random
import card_effects as ce

def read_csv(filename):
	output = []
	with open(filename) as f:
		reader = csv.reader(f)
		next(reader)
		for line in reader:
			output.append(line)
	return output

CHARACTERS = read_csv("characters.csv")
CITY_CARDS = read_csv("city_cards.csv")
CREATURE_CARDS = read_csv("creature_cards.csv")

for card in CITY_CARDS + CREATURE_CARDS:
	for n in range(len(card)):
		try:
			card[n] = int(card[n])
		except:
			pass

EFFECTS = {
	"Move quickly!": (ce.move_quickly, ce.no_check),
	"Turn back!": (ce.turn_back, ce.no_check),
	"Preparations": (ce.preparations, ce.preparations_check),
	"Lock the door": (ce.lock_the_door, ce.no_check),
	"Night search": (ce.night_search, ce.night_search_check),
	"Regroup": (ce.regroup, ce.regroup_check),
	"Throwing stuff": (ce.throwing_stuff, ce.throwing_stuff_check),
	"Set up a barricade": (ce.barricade, ce.barricade_check),
	"Evacuation": (ce.evacuation, ce.evacuation_check),
	"We need to close this": (ce.close_this, ce.close_this_check),
	"Covering your tracks": (ce.covering_tracks, ce.covering_tracks_check),
	"Stockroom check": (ce.stockroom, ce.stockroom_check),
	"Floor it!": (ce.floor_it, ce.no_check),
	"Front page article": (ce.front_page, ce.front_page_check),
	"On the house": (ce.on_the_house, ce.on_the_house_check),
	"Risky maneuver": (ce.risky_maneuver, ce.no_check),
	"Reroute": (ce.reroute, ce.no_check),
	"Struggle": (ce.struggle, ce.struggle_check),
	"Hiding": (ce.hiding, ce.no_check),
	"Rage": (ce.rage, ce.rage_check),
	"Replacement": (ce.replacement, ce.no_check),
	"Lurking": (ce.lurking, ce.lurking_check),
	"Entrapment": (ce.entrap, ce.entrap_check),
	"Ambush": (ce.ambush, ce.ambush_check),
	}

for card in CITY_CARDS + CREATURE_CARDS:
	if card[0] in EFFECTS:
		card.extend(EFFECTS[card[0]])

for card in CREATURE_CARDS.copy():
	for _ in range(3):
		CREATURE_CARDS.append(card)

for deck in [CHARACTERS, CITY_CARDS, CREATURE_CARDS]:
	random.shuffle(deck)
