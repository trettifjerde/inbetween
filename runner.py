import game_data
import card_effects as ce
import random
import csv
import sys

CITY, CREATURE, PLAYER_NAMES, STATES = ce.CONSTS

class Character:
	def __init__(self, info):
		self.name = info[0]
		self.marks = {
			CITY: [info[1]],
			CREATURE: [info[2]],
		}
		self.city_effect, self.creature_effect = info[3:]
		self.state = 0

	def __repr__(self):
		return f"{self.name}: {self.state} [{', '.join(self.get_marks())}]"

	def get_marks(self):
		return [m for marks in self.marks.values() for m in marks]

	def remove_temp_mark(self, player, mark):
		if mark in self.marks[player] and self.marks[player].index(mark) != 0:
			self.marks[player].remove(mark)

class Card:
	def __init__(self, info):
		self.name, self.mark, self.cost, self.description, self.perk, self.condition = info

	def __repr__(self):
		return f"{self.name.upper()}: {self.mark} {self.cost}\n\t- {self.description}"

	def short_info(self):
		return f"{self.name.upper()}: {self.mark} {self.cost}"

class CityCard(Card):
	def __init__(self, info):
		self.name, self.equip, self.mark, self.cost, self.description, self.perk, self.condition = info

class Game:

	def __init__(self):
		self.winner = None
		self.players = {
			CITY: {
				"awareness": 0,
				"energy": 3,
				"pile": [CityCard(card) for card in game_data.CITY_CARDS],
				"cards": [],
				"discard": [],
				},
			CREATURE: {
				"awareness": 0, 
				"energy": 3,
				"pile": [Card(card) for card in game_data.CREATURE_CARDS],
				"cards": [],
				"discard": [],
				},
		}

		for player in self.players:
			self.take_cards(player, 3)

		self.characters = [Character(info) for info in random.sample(game_data.CHARACTERS, 10)]
		for i in range(10):
			if i%2 == 0:
				self.characters[i].state = CITY
			else:
				self.characters[i].state = CREATURE
		self.skip_chars = set()

		self.activity_marker = 0
		self.player = self.characters[self.activity_marker].state * -1

		self.equiped = set()

		self.turn_phases = (
			("awareness", self.awareness_phase), 
			("action", self.action_phase), 
			("activation", self.activation_phase), 
			("movement", self.movement_phase),
		)
		self.phases = {phase[0]: True for phase in self.turn_phases}

	def run_game(self):
		while True:
			winner = self.play_turn()
			if winner:
				break
		print(f"{PLAYER_NAMES[winner].upper()} wins the game")
		return winner

	def play_turn(self):
		self.print_game()
		self.make_move()
		return self.winner

	def get_chars(self, mark, state):
		return [char for char in self.chars_in_state(state) if mark in char.get_marks()]

	def chars_in_state(self, state):
		return [char for char in self.characters if char.state in STATES[state]]

	def winner_check(self):
		if len(self.characters) < 6:
			self.winner = CITY if (self.chars_in_state('city') > 
				self.chars_in_state('creature')) else CREATURE

		if self.players[CITY]["awareness"] == 6 or len(self.chars_in_state("secured")) == 3:
			self.winner = CITY
		elif self.players[CREATURE]["awareness"] == 6 or len(self.chars_in_state("devoured")) == 3:
			self.winner = CREATURE

	def print_game(self):
		print("\nnew turn".upper())
		self.print_score()
		self.print_board()
		print(f"{PLAYER_NAMES[self.player].upper()}'s turn\n")
	
	def print_score(self):
		print()
		divider = "\t" * 3
		info = []
		info.append(divider.join([PLAYER_NAMES[i].upper() + "\t" for i in [1, -1]]))
		info.append("")
		info.append(divider.join([f"AWARENESS: {self.players[i]['awareness']}" 
			for i in [1, -1]]))
		info.append(divider.join([f"ENERGY: {self.players[i]['energy']}"
			for i in [1, -1]]))
		info.append(divider.join([f"CARDS: {len(self.players[i]['cards'])}"
			for i in [1, -1]]))
		s = "\n".join(info)
		print(s + "\n")

	def print_board(self):
		print()
		for n, char in enumerate(self.characters):
			if self.activity_marker == n:
				print(n, str(self.characters[n]).upper())
			else:
				print(n, self.characters[n])
		print()

	def print_cards(self):
		print("\nYOUR CARDS:")
		if self.players[self.player]["cards"]:
			for card in self.players[self.player]["cards"]:
				print(f"\t{card}")
		else:
			print("no cards")

	def switch_player(self):
		self.player *= -1

	def request_int_input(self, input_s, allowed_range):
		while True:
			n = input(input_s)
			if n == "q":
				sys.exit()
			try:
				n = int(n)
				if n in allowed_range:
					return n
			except: pass

	def make_move(self):
		for phase_name, phase_f in self.turn_phases:
			if self.phases[phase_name]:
				phase_f()
				if self.winner:
					break

	def awareness_phase(self):
		print("I. AWARENESS PHASE")
		pass

	def action_phase(self):
		print("II. ACTION PHASE")
		self.print_cards()
		print("Choose your action:")
		if self.players[self.player]["cards"]:
			move = self.request_int_input("1) play card, 2) prepare, 3) rest: ", [1, 2, 3])
		else:
			move = self.request_int_input("2) prepare, 3) rest: ", [2, 3])

		if move == 1:
			self.play_card()
		elif move == 2:
			self.prepare()
		elif move == 3:
			self.rest()

	def play_card(self):
		for n, card in enumerate(self.players[self.player]["cards"]):
			print(f"{n} {card.short_info()}")
		card_n = self.request_int_input("Select card: ", 
			range(len(self.players[self.player]['cards'])))
		card = self.players[self.player]["cards"].pop(card_n)

		mode = self.choose_mode(card)
		if mode == "m":
			self.shift_marker(card)
		elif mode == "s":
			self.place_symbol(card)

		self.activate_card_effect(card)

		if self.player == -1 or not card.equip:
			self.players[self.player]["discard"].append(card)

	def choose_mode(self, card):
		if any(card.mark in char.get_marks() for char in self.chars_in_state("shiftable")):
			while True:
				mode = input("Shift marker or place symbol? m/s: ").lower()
				if mode == "q":
					sys.exit()
				if mode == "m" or mode == "s":
					break
		else:
			mode = "s"
		return mode

	def shift_marker(self, card):
		print("shift marker".upper())
		r = []
		for char in self.get_chars(card.mark, "shiftable"):
			n = self.characters.index(char)
			r.append(n)
			print(n, char)
		char_n = self.request_int_input("Select character: ", r)
		self.move_marker(char_n, self.player)
		self.print_board()
		self.winner_check()

	def move_marker(self, char_n, n):
		self.characters[char_n].state += n
		if self.characters[char_n].state == 0:
			self.characters[char_n].state += n

	def place_symbol(self, card):
		print("place symbol".upper())
		r = []
		for n, char in enumerate(self.characters):
			if card.mark not in char.get_marks():
				r.append(n)
				print(n, char)
		char_n = self.request_int_input("Select character: ", r)
		for char in self.characters:
			char.remove_temp_mark(self.player, card.mark)
		self.characters[char_n].marks[self.player].append(card.mark)
		self.print_board()

	def activate_card_effect(self, card):
		if self.players[self.player]["energy"] >= card.cost and card.condition(self):
			print(f"{card.name.upper()} card's effect:")
			print(f"{card.description}\nCost: {card.cost}")
			while True:
				confirm = input(f"Activate card effect? y/n: ").lower()
				if confirm in ["y", "n"]:
					break
			if confirm == "y":
				self.update_energy(self.player, -card.cost)
				self.print_score()
				card.perk(self)

	def prepare(self):
		if self.players[self.player]['cards']:
			n = self.request_int_input("How many cards to discard? ", 
				range(len(self.players[self.player]["cards"]) + 1))
			self.lose_cards(self.player, n)

		n = 5 - len(self.players[self.player]["cards"])
		self.take_cards(self.player, n)

	def rest(self):
		n = len(self.chars_in_state(PLAYER_NAMES[self.player]))
		self.update_energy(self.player, n)

	def activation_phase(self):
		print("III. ACTIVITY PHASE")
		pass

	def skip_activation_phase(self):
		self.phases["activation"] = False

	def movement_phase(self):
		print("IV. MOVEMENT PHASE")
		self.move_activity_marker()
		self.switch_player()

	def move_activity_marker(self):
		self.activity_marker += 1
		if self.activity_marker == len(self.characters):
			self.activity_marker = 0
		if self.activity_marker in self.skip_chars:
			self.skip_chars.remove(self.activity_marker)
			self.move_activity_marker()

	def reverse_direction(self):
		active_char = self.characters[self.activity_marker]
		self.characters = self.characters[::-1]
		self.activity_marker = self.characters.index(active_char)

	def update_awareness(self, player, n):
		self.players[player]["awareness"] += n
		if self.players[player]["awareness"] < 0:
			self.players[player]["awareness"] = 0
		self.winner_check()

	def update_energy(self, player, n):
		energy = self.players[player]["energy"] + n
		energy = min(energy, 10)
		energy = max(energy, 0)
		self.players[player]["energy"] = energy

	def take_cards(self, player, n):
		for _ in range(n):
			if not self.players[player]["pile"]:
				self.shuffle_the_deck(player)
			self.players[player]["cards"].append(self.players[player]["pile"].pop())

	def lose_cards(self, player, n):
		if n == len(self.players[player]['cards']):
			while self.players[player]['cards']:
				self.discard_card(player, 0)
		else:
			for _ in range(n):
				if self.players[player]["cards"]:
					print()
					for n, card_info in enumerate(self.players[player]["cards"]):
						print(n, card_info)
					print()
					card_n = self.request_int_input("What card to discard? n: ", 
						range(len(self.players[player]["cards"])))
					self.discard_card(player, card_n)

	def discard_card(self, player, card_n):
		card = self.players[player]["cards"].pop(card_n)
		self.players[player]["discard"].append(card)

	def get_card_from_discard(self, player):
		r = []
		for n, card in enumerate(self.players[player]["discard"]):
			r.append(n)
			print(n, card)
		card_n = self.request_int_input("What card to take? n: ", r)
		card = self.players[player]["discard"].pop(card_n)
		self.players[player]["cards"].append(card)

	def shuffle_the_deck(self, player):
		random.shuffle(self.players[player]["discard"])
		self.players[player]["pile"] = self.players[player]["discard"]
		self.players[player]["discard"] = []

	def get_neighbors(self, char):
		neighbors = []
		char_n = self.characters.index(char)
		try:
			neighbors.append(self.characters[char_n - 1])
		except:
			neighbors.append(self.characters[len(self.characters) - 1])
		try:
			neighbors.append(self.characters[char_n + 1])
		except:
			neighbors.append(self.characters[0])
		return neighbors

	def delete_neighbor(self):
		secured = [char for char in self.characters if char.state in STATES["secured"]]
		neighbors = [neighbor for secure in secured for neighbor in self.get_neighbors(secure)]
		neighbors_n = [self.characters.index(neighbor) for neighbor in neighbors]
		for n, neighbor in zip(neighbors_n, neighbors):
			print(n, neighbor)
		while True:
			char_n = self.request_int_input("What neighbor to remove from the game? n: ", 
				neighbors_n)
			while True:
				confirm = input("Are you sure? y/n: ").lower()
				if confirm in ["y", "n"]:
					break
			if confirm == "y":
				del self.characters[char_n]
				self.winner_check()
				break

if __name__ == "__main__":
	g = Game()
	w = g.run_game()