import csv
import random
import card_effects as ce

CITY, CREATURE, PLAYER_NAMES, STATES = ce.CONSTS

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

# Make 3 more copies of every Creature card
for card in CREATURE_CARDS.copy():
	for _ in range(3):
		CREATURE_CARDS.append(card)

# Randomise the card order
for deck in [CHARACTERS, CITY_CARDS, CREATURE_CARDS]:
	random.shuffle(deck)
