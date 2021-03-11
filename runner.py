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
		self.perk_description = {
			CITY: info[3],
			CREATURE: info[4],
		}
		self.perks = {
			CITY: eval(f"ce.{self.marks[CITY][0]}"),
			CREATURE: eval(f"ce.{self.name.lower()}"),
		}
		self.state = 0

	def __repr__(self):
		return f"{self.name}: {self.state} [{', '.join(self.get_marks())}]"

	def get_marks(self):
		return [m for marks in self.marks.values() for m in marks]

	def remove_temp_mark(self, player, mark):
		if mark in self.marks[player] and self.marks[player].index(mark) != 0:
			self.marks[player].remove(mark)

	def get_dimension(self):
		return CITY if self.state > 0 else CREATURE

class Card:
	def __init__(self, info):
		if len(info) == 4:
			self.name, self.mark, self.cost, self.description = info
			self.equip = 0

		elif len(info) == 5:
			self.name, self.equip, self.mark, self.cost, self.description = info

		if self.name.lower() in ce.equipment:
			self.perk, self.condition = ce.no_check, ce.no_check
		else:
			self.perk = eval(f"ce.{self.name.lower().strip('!').translate(ce.ttable)}")
			try:
				self.condition = eval(f"ce.{self.name.lower().strip('!').translate(ce.ttable)}_check")
			except:
				self.condition = ce.no_check			

	def __repr__(self):
		return f"{self.name.upper()}: {self.mark} {self.cost}\n\t- {self.description}"

	def short_info(self):
		return f"{self.name.upper()}: {self.mark} {self.cost}"

class Game:
	def __init__(self):
		self.winner = None
		self.players = {
			CITY: {
				"awareness": 0,
				"energy": 3,
				"pile": [Card(card) for card in game_data.CITY_CARDS],
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
		for i in range(len(self.characters)):
			if i%2 == 0:
				self.characters[i].state = CITY
			else:
				self.characters[i].state = CREATURE
		self.skip_chars = set()

		self.activity_marker = 0
		self.player = self.characters[0].state * -1

		self.equiped = [] # list of tuples (Equipment Card, Character or None)

		self.turn_phases = (
			("awareness", self.awareness_phase), 
			("action", self.action_phase), 
			("activity", self.activity_phase), 
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

	def is_equiped(self, card_name):
		for card, n in self.equiped:
			if card.name.lower() == card_name.lower():
				return (card, n)
		return False

	def remove_equipment(self, card_name):
		for n in range(len(self.equiped)):
			if self.equiped[n][0].name.lower() == card_name.lower():
				return self.equiped.pop(n)

	def print_game(self):
		print("\nnew turn".upper())
		self.print_board()
		print(f"{PLAYER_NAMES[self.player].upper()}'s turn\n")
		self.print_score()
	
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
		if self.equiped:
			print("Equiped:", end=" ")
			for card, _ in self.equiped:
				print(card.name.upper(), end=" ")
			print()

	def print_board(self):
		print()
		for n, char in enumerate(self.characters):
			if self.activity_marker == n:
				print(n, str(self.characters[n]).upper(), end=" ")
			else:
				print(n, self.characters[n], end=" ")

			if n in self.skip_chars:
				print("(skipped next time)", end=" ")
			if self.is_equiped("shotgun") and self.is_equiped("shotgun")[1] == n:
				print("(with the Shotgun)")
			print()
		print()

	def print_cards(self, player=None):
		if not player:
			player = self.player

		print("\nYOUR CARDS:")
		if self.players[player]["cards"]:
			for n, card in enumerate(self.players[player]["cards"]):
				print(f"{n}. {card}")
		else:
			print("no cards")

	def switch_player(self):
		self.player *= -1

	def request_input(self, input_s, allowed_range):
		while True:
			inp = input(f"{input_s} {'/'.join(allowed_range)}: ").lower()
			if inp == "q":
				sys.exit()
			if inp in allowed_range:
				return inp

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
			else:
				self.phases[phase_name] = True

	def awareness_phase(self):
		print("\nI. AWARENESS PHASE")
		pass

	def action_phase(self):
		print("\nII. ACTION PHASE")
		self.print_cards()
		self.check_chocolate_bars()
		print("\nChoose your action:")
		if self.players[self.player]["cards"]:
			move = self.request_int_input("1) play card, 2) prepare, 3) rest: ", [1, 2, 3])
		else:
			move = self.request_int_input("2) prepare, 3) rest: ", [2, 3])

		if move == 1:
			self.play_card(self.player)
		elif move == 2:
			self.prepare()
		elif move == 3:
			self.rest()

	def check_chocolate_bars(self):
		if self.is_equiped("chocolate bars") and self.player == CITY:
			if self.players[CREATURE]["energy"] > self.players[CITY]["energy"]:
				self.update_energy(CITY, 1)

	def play_card(self, player=None, activate=True):
		if not player:
			player = self.player

		for n, card in enumerate(self.players[player]["cards"]):
			print(f"{n} {card.short_info()}")
		card_n = self.request_int_input("Select card: ", 
			range(len(self.players[player]['cards'])))
		card = self.players[player]["cards"].pop(card_n)

		if any(card.mark in char.get_marks() for char in self.chars_in_state("shiftable")):
			mode = self.request_input("Shift marker of place symbol?", ["m", "s"])
		else:
			mode = "s"

		if mode == "m":
			self.shift_marker(card, player)
		elif mode == "s":
			self.place_symbol(card, player)

		if self.winner:
			return 

		self.licence_coupon_hose(card, player)
			
		if activate:
			self.activate_card_effect(card, player)

		if not card.equip:
			self.players[player]["discard"].append(card)

	def shift_marker(self, card, player):
		print("\nshift marker".upper())
		r = []
		for char in self.get_chars(card.mark, "shiftable"):
			n = self.characters.index(char)
			r.append(n)
			print(n, char)
		char_n = self.request_int_input("Select character: ", r)
		self.move_safety_marker(char_n, player)

	def move_safety_marker(self, char_n, n):
		new_state = self.characters[char_n].state + n
		new_state = min(5, new_state)
		new_state = max(-5, new_state)
		self.characters[char_n].state = new_state
		if self.characters[char_n].state == 0:
			self.characters[char_n].state += n
		self.winner_check()

	def place_symbol(self, card, player):
		print("\nplace symbol".upper())
		r = []
		for n, char in enumerate(self.characters):
			if card.mark not in char.get_marks():
				r.append(n)
				print(n, char)
		char_n = self.request_int_input("Select character: ", r)
		for char in self.characters:
			char.remove_temp_mark(player, card.mark)
		self.characters[char_n].marks[player].append(card.mark)

	def licence_coupon_hose(self, card, player):
		if player == CITY:
			if self.is_equiped("driving licence") and card.mark == "route":
					confirm = self.request_input("Reverse the Direction?", ["y", "n"])
					if confirm == "y":
						self.reverse_direction()

			elif self.is_equiped("coupon") and card.mark == "shop":
				self.take_cards(CITY, 1)

			elif self.is_equiped("firehose") and card.mark == "hands":
				self.update_energy(CREATURE, -1)

	def activate_card_effect(self, card, player):
		cost = self.assign_cost(card, player)
		if self.players[player]["energy"] >= cost and card.condition(self):
			print(f"\n{card.name.upper()} card's effect:")
			print(f"{card.description}\nCost: {card.cost}")
			print(f"Equipment in game: {len(self.equiped)} {'(max)' if len(self.equiped) == 3 else ''}")
			confirm = self.request_input("Activate card effect?", ["y", "n"])
			if confirm == "y":
				if card.equip:
					if len(self.equiped) == 3:
						for n, (eq, char) in enumerate(self.equiped):
							print(n, eq.name)
						equip_n = self.request_int_input("What equipment to discard? n: ", 
							range(len(self.equiped)))
						discarded_eq = self.equiped[equip_n][0]
						self.remove_equipment(discarded_eq.name)

					if card.name.lower() == "shotgun":
						self.print_board()
						char_n = self.request_int_input("What Character to equip with the Shotgun? n: ",
							range(len(self.characters)))
						self.equiped.append((card, char_n))
					else:
						self.equiped.append((card, None))
				self.update_energy(player, -cost)
				self.activate_perk(card, player)

	def assign_cost(self, card, player):
		if self.is_equiped("sedative") and player == CREATURE:
			return card.cost + 1
		return card.cost

	def activate_perk(self, card, player):
		if self.is_equiped("revolver") and player == CREATURE:
			confirm = self.request_input("Use Revolver to cancel the Creature Card effect?", ["y", "n"])
			if confirm == "y":
				self.remove_equipment("revolver")
				return
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

	def activity_phase(self):
		print("\nIII. ACTIVITY PHASE")
		active_char = self.characters[self.activity_marker]
		if active_char.state in STATES["inbetween"]:
			print(f"{active_char.name.upper()} is InBetween: nothing happens")
		else:
			print(f"{active_char.name.upper()}: {active_char.state}")

			player = active_char.get_dimension()
			print(f"{PLAYER_NAMES[player].upper()} is now active")

			self.increase_awareness(player)
			self.play_char_perk(player, active_char)	

	def increase_awareness(self, player):
		if self.players[player]["energy"] >= self.players[player]["awareness"] + 1:
			self.print_score()
			confirm = self.request_input("Increase Awareness?", ["y", "n"])
			if confirm == "y":
				self.update_awareness(player, 1)
				self.update_energy(player, -(self.players[player]["awareness"]))
		else:
			print(f"{PLAYER_NAMES[player].upper()} cannot increase their Awareness")

	def play_char_perk(self, player, char):
		if abs(char.state) > 2:
			print(f"\n{char.name.upper()}'s perk:")
			print(char.perk_description[player])
			if char.perks[player](self, char):
				print("Perk activated")
			else:
				print("Perk not activated")

	def skip_activity_phase(self):
		self.phases["activity"] = False

	def movement_phase(self):
		print("\nIV. MOVEMENT PHASE")
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
		n += self.players[player]["awareness"]
		self.players[player]["awareness"] = max(0, n)
		self.winner_check()

	def update_energy(self, player, n):
		energy = self.players[player]["energy"] + n
		energy = min(energy, 10)
		energy = max(energy, 0)
		self.players[player]["energy"] = energy
		self.print_score()

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
		return card

	def get_card_from_discard(self, player):
		if self.players[player]["discard"]:
			for n, card in enumerate(self.players[player]["discard"]):
				print(n, card)
			card_n = self.request_int_input("What card to take? ", range(len(self.players[player]["discard"])))
			card = self.players[player]["discard"].pop(card_n)
			self.players[player]["cards"].append(card)
		else:
			print("No cards in discard pile")

	def shuffle_the_deck(self, player):
		random.shuffle(self.players[player]["discard"])
		self.players[player]["pile"] = self.players[player]["discard"]
		self.players[player]["discard"] = []

	def get_neighbors(self, char):
		neighbors = []
		char_n = self.characters.index(char)
		neigh_ns = [char_n - 1, char_n + 1]
		for neigh_n in neigh_ns:
			if neigh_n < 0:
				neigh_n = len(self.characters) - 1
			elif neigh_n >= len(self.characters):
				neigh_n = 0
			neighbors.append((neigh_n, self.characters[neigh_n]))
		return neighbors

	def delete_neighbor(self):
		secured = [char for char in self.characters if char.state in STATES["secured"]]
		neighbors = [neighbor for secure in secured for neighbor in self.get_neighbors(secure)]
		for n, neighbor in neighbors:
			print(n, neighbor)
		while True:
			char_n = self.request_int_input("What neighbor to remove from the game? n: ", 
				[n for n, _ in neighbors])
			confirm = self.request_input("Are you sure?", ["y", "n"])
			if confirm == "y":
				del self.characters[char_n]
				self.winner_check()
				break

if __name__ == "__main__":
	g = Game()
	w = g.run_game()