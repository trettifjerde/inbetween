import csv
import random

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

# Convert all number-fields from string to int
for card in CITY_CARDS + CREATURE_CARDS:
	for n in range(len(card)):
		try:
			card[n] = int(card[n])
		except:
			pass

# Add card ids
for n, card in enumerate(CHARACTERS + CITY_CARDS + CREATURE_CARDS, 1):
	card.append(n)

# Make 3 more copies of every Creature card
for card in CREATURE_CARDS.copy():
	for _ in range(3):
		CREATURE_CARDS.append(card)

# Make 3 more copies of Move quickly
for card in CITY_CARDS:
	if card[0] == "Move quickly!":
		move_quickly = card
for _ in range(3):
	CITY_CARDS.append(move_quickly)

# Randomise the card order
#for deck in [CHARACTERS, CITY_CARDS, CREATURE_CARDS]:
	#random.shuffle(deck)
