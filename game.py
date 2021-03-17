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
			CREATURE: {
				"perk": eval(f"ce.{self.name.lower()}"),
				"condition": eval(f"ce.{self.name.lower()}_check"),
			}
		}
		self.state = 0
		self.card_effects = [None, None]

	def get_marks(self):
		return [m for marks in self.marks.values() for m in marks]

	def remove_temp_mark(self, player, mark):
		if mark in self.marks[player] and self.marks[player].index(mark) != 0:
			self.marks[player].remove(mark)

	def get_dimension(self):
		return CITY if self.state > 0 else CREATURE

	def is_card_affected(self):
		return any(e for e in self.card_effects)

	def __repr__(self):
		s = f"{self.name}: {self.state} [{', '.join(self.get_marks())}]"
		if self.is_card_affected():
			for e in self.card_effects:
				if e:
					s += f" ({e})"
		return s

	def short_info(self):
		return f"{self.name}: {self.state}"

class Card:
	def __init__(self, info):
		if len(info) == 4:
			self.name, self.mark, self.cost, self.description = info
			self.equip = 0

		elif len(info) == 5:
			self.name, self.equip, self.mark, self.cost, self.description = info

		if self.equip:
			self.perk, self.condition = ce.no_check, ce.no_check

		else:
			self.perk = eval(f"ce.{self.name.lower().strip('!').translate(ce.ttable)}")
			try:
				self.condition = eval(f"ce.{self.name.lower().strip('!').translate(ce.ttable)}_check")
			except:
				self.condition = ce.no_check			

	def __repr__(self):
		return f"{self.name.upper()}: {self.mark} {self.cost}\n- {self.description}"

	def short_info(self):
		return f"{self.name.upper()}: {self.mark} {self.cost}"

class Game:
	def __init__(self, humans=1, characters=10):
		self.humans = self.set_players(humans)

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

		self.characters = [Character(info) for info in random.sample(game_data.CHARACTERS, characters)]
		for i in range(len(self.characters)):
			if i%2 == 0:
				self.characters[i].state = CITY
			else:
				self.characters[i].state = CREATURE
		self.skip_chars = set()

		self.activity_marker = 0
		self.player = self.characters[0].state * -1

		self.equiped = []

		self.turn_phases = (
			("awareness", self.awareness_phase), 
			("action", self.action_phase), 
			("activity", self.activity_phase), 
			("movement", self.movement_phase),
		)
		self.phases = {phase[0]: True for phase in self.turn_phases}

	def set_players(self, human_players):
		humans = []
		if human_players == 2:
			humans.extend((CITY, CREATURE))
		elif abs(human_players) == 1:
			humans.append(human_players)
		elif human_player == 0:
			pass
		else:
			sys.exit("Error while initiating players")
		return set(humans)

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

	def marked_in_state(self, mark, state):
		return [char for char in self.in_state(state) if mark in char.get_marks()]

	def in_state(self, state):
		return [char for char in self.characters if char.state in STATES[state]]

	def get_range_and_print_enumed(self, seq, player, exc=[], filt=[], short=False):
		chars = True if seq == self.characters else False
		s = [""]
		r = []
		for n, el in enumerate(seq):
			# comply with exceptions and filters
			if n in exc or el in exc:
				continue
			if filt and n not in filt and el not in filt:
				continue
			# formate the output
			el_s = el.short_info() if short else str(el)
			if chars and n == self.activity_marker:
				el_s = el_s.upper()
			# collect range and printable info
			s.append(f"{n} {el_s}")
			r.append(n)
		s.append("")

		if player in self.humans:
			print("\n".join(s))

		return r

	def winner_check(self):
		if len(self.characters) < 6:
			self.winner = CITY if (self.in_state('city') > self.in_state('creature')) else CREATURE

		if self.players[CITY]["awareness"] == 6 or len(self.in_state("secured")) == 3:
			self.winner = CITY
		elif self.players[CREATURE]["awareness"] == 6 or len(self.in_state("devoured")) == 3:
			self.winner = CREATURE

	def is_equiped(self, card_name):
		for card in self.equiped:
			if card.name.lower() == card_name.lower():
				return card
		return False

	def remove_equipment(self, card_name):
		for n in range(len(self.equiped)):
			if self.equiped[n].name.lower() == card_name.lower():
				if card_name.lower() == "shotgun":
					for char in self.characters:
						char.card_effects[1] = None
				print(f"{card_name.upper()} is removed.")
				return self.equiped.pop(n)

	def shotgunner(self, player):
		if self.is_equiped("shotgun") and player == CREATURE:
			for n, char in enumerate(self.characters):
				if char.card_effects[1]:
					return n
		return None

	def print_game(self):
		print("\nnew turn".upper())
		self.print_board()
		print(f"{PLAYER_NAMES[self.player].upper()}'s turn\n")
		self.print_score()
	
	def print_score(self):
		divider = "\t" * 3
		info = [""]
		info.append(divider.join([PLAYER_NAMES[i].upper() + "\t" for i in [1, -1]]))
		info.append("")
		info.append(divider.join([f"AWARENESS: {self.players[i]['awareness']}" 
			for i in [1, -1]]))
		info.append(divider.join([f"ENERGY: {self.players[i]['energy']}"
			for i in [1, -1]]))
		info.append(divider.join([f"CARDS: {len(self.players[i]['cards'])}"
			for i in [1, -1]]))
		info.append("")
		print("\n".join(info))
		if self.equiped:
			print("Equiped:", end=" ")
			for card in self.equiped:
				print(card.name.upper(), end=" ")
			print()

	def print_board(self):
		self.get_range_and_print_enumed(self.characters, self.player)

	def print_cards(self, player=None, requester=None):
		if not player:
			player = self.player
		if not requester:
			requester = player
		if requester in self.humans:
			print("\nYOUR CARDS:")
		if self.players[player]["cards"]:
			self.get_range_and_print_enumed(self.players[player]["cards"], requester)
		else:
			print("no cards")

	def switch_player(self):
		self.player *= -1

	def request_input(self, player, input_s, allowed_range):
		if player in self.humans:
			while True:
				inp = input(f"{input_s} {'/'.join(allowed_range)}: ").lower()
				if inp == "q":
					sys.exit()
				if inp in allowed_range:
					return inp
		else:
			return random.choice(allowed_range)

	def request_int_input(self, player, input_s, allowed_range):
		if player in self.humans:
			while True:
				n = input(input_s)
				if n == "q":
					sys.exit()
				try:
					n = int(n)
					if n in allowed_range:
						return n
				except: pass
		else:
			return random.choice(allowed_range)

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
		self.choose_action()

	def check_chocolate_bars(self):
		if self.is_equiped("chocolate bars") and self.player == CITY:
			if self.players[CREATURE]["energy"] > self.players[CITY]["energy"]:
				self.update_energy(CITY, 1)

	def choose_action(self):
		if self.player in self.humans:
			print("\nChoose your action:")

		if self.players[self.player]["cards"]:
			s = "1) play card, 2) prepare, 3) rest: "
			r = [1, 2, 3]
		else:
			s = "2) prepare, 3) rest: "
			r = [2, 3]

		move = self.request_int_input(self.player, s, r)

		acts = {1: "is playing a card ", 2: "is preparing", 3: "is resting"}
		print(f"{PLAYER_NAMES[self.player].title()} {acts[move]}")

		if move == 1:
			self.play_card()
		elif move == 2:
			self.prepare()
		elif move == 3:
			self.rest()

	def play_card(self, player=None, activate=True):
		if not player:
			player = self.player

		r = self.get_range_and_print_enumed(self.players[player]["cards"], player, short=True)
		card_n = self.request_int_input(player, "Select card: ", r)
		card = self.players[player]["cards"].pop(card_n)
		if player not in self.humans:
			print(card)

		if any(card.mark in char.get_marks() for char in self.in_state("shiftable")):
			mode = self.request_input(player, "Shift marker of place symbol?", ["m", "s"])
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
		exc = []
		if (gunner := self.shotgunner(player)):
			exc.append(gunner)
		r = self.get_range_and_print_enumed(self.characters, player, 
				filt=self.marked_in_state(card.mark, "shiftable"), exc=exc)
		char_n = self.request_int_input(player, "Select character: ", r)
		print(f"{PLAYER_NAMES[player].title()} shifts marker on {self.characters[char_n].name}")
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
		exc = [char for char in self.characters if card.mark in char.get_marks()]
		if (gunner := self.shotgunner(player)):
			exc.append(gunner)
		r = self.get_range_and_print_enumed(self.characters, player, exc=exc)
		char_n = self.request_int_input(player, "Select character: ", r)
		for char in self.characters:
			char.remove_temp_mark(player, card.mark)
		print(f"{PLAYER_NAMES[player].title()} places {card.mark.upper()} on {self.characters[char_n].name}")
		self.characters[char_n].marks[player].append(card.mark)

	def licence_coupon_hose(self, card, player):
		if player == CITY:
			if self.is_equiped("driving licence") and card.mark == "route":
				confirm = self.request_input(CITY, "Driving licence is equiped. Reverse the Direction?", ["y", "n"])
				if confirm == "y":
					print("City uses DRIVING LICENCE and flips the Direction.")
					self.reverse_direction()

			elif self.is_equiped("coupon") and card.mark == "shop":
				print("City uses COUPON and draws 1 card.")
				self.take_cards(CITY, 1)

			elif self.is_equiped("firehose") and card.mark == "hands":
				print("City uses FIREHOSE and lowers Creature energy by 1.")
				self.update_energy(CREATURE, -1)

	def activate_card_effect(self, card, player):
		cost = self.assign_cost(card, player)
		if self.players[player]["energy"] >= cost and card.condition(self):
			if self.player in self.humans:
				print(f"\n{card.name.upper()} card's effect:")
				print(f"{card.description}\nCost: {cost}")
				if card.equip:
					print(f"Equipment in game: {len(self.equiped)} {'(max)' if len(self.equiped) == 3 else ''}")
			confirm = self.request_input(player, "Activate card effect?", ["y", "n"])
			if confirm == "y":
				if card.equip:
					self.activate_equipment(card)
				self.update_energy(player, -cost)
				print(f"{PLAYER_NAMES[player].title()} is trying to activate {card.name}.")
				self.activate_perk(card, player)

	def assign_cost(self, card, player):
		if self.is_equiped("sedative") and player == CREATURE:
			return card.cost + 1
		return card.cost

	def activate_equipment(self, card):
		if len(self.equiped) == 3:
			r = self.get_range_and_print_enumed(self.equiped, CITY, short=True)
			n = self.request_int_input(CITY, "What equipment to remove from game? n: ", r)
			self.remove_equipment(self.equiped[n].name)

		if card.name.lower() == "shotgun":
			r = self.get_range_and_print_enumed(self.characters, CITY)
			char_n = self.request_int_input(CITY, "What Character to equip with the Shotgun? n: ", r)
			self.characters[char_n].card_effects[1] = card.name
		self.equiped.append(card)
		print(f"City activates {card.name}")

	def activate_perk(self, card, player):
		if self.is_equiped("revolver") and player == CREATURE:
			if self.player in self.humans:
				print(f"{card.description}")
			confirm = self.request_input(CITY, "Use Revolver to cancel the Creature Card effect?", ["y", "n"])
			if confirm == "y":
				print(f"City uses Revolver and cancels {card.name} effect.")
				self.remove_equipment("revolver")
				return
		print(f"{PLAYER_NAMES[player].title()} activates {card.name}.")
		card.perk(self)

	def prepare(self):
		if self.players[self.player]['cards']:
			n = self.request_int_input(self.player, "How many cards to discard? ", 
				range(len(self.players[self.player]["cards"]) + 1))
			self.lose_cards(self.player, n)

		n = 5 - len(self.players[self.player]["cards"])
		self.take_cards(self.player, n)

	def rest(self):
		n = len(self.in_state(PLAYER_NAMES[self.player]))
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
			if player in self.humans:
				self.print_score()
			confirm = self.request_input(player, "Increase Awareness?", ["y", "n"])
			if confirm == "y":
				self.update_awareness(player, 1)
				self.update_energy(player, -(self.players[player]["awareness"]))
		else:
			print(f"{PLAYER_NAMES[player].upper()} cannot increase their Awareness")

	def play_char_perk(self, player, char):
		if abs(char.state) > 2:
			if player in self.humans:
				print(f"\n{char.name.upper()}'s perk:")
				print(char.perk_description[player])

			if player == CITY:
				response = char.perks[CITY](self, char)
			elif player == CREATURE:
				if response := char.perks[CREATURE]["condition"](self, char):
					if self.check_walkie():
						response = False
					else:
						response = char.perks[CREATURE]["perk"](self, char)
			if response:
				print("Perk activated")
			else:
				print("Perk not activated")

	def check_walkie(self):
		if self.is_equiped("walkie-talkie"):
			confirm = self.request_input(CITY, "Discard Walkie-talkie to cancel this Character's effect?", 
				["y", "n"])
			if confirm == "y":
				self.remove_equipment("walkie-talkie")
				print("City uses Walkie-talkie and cancels the Character's effect.")
				return True
		return False

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
			self.characters[self.activity_marker].card_effects[0] = None
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
		if n >= len(self.players[player]['cards']):
			while self.players[player]['cards']:
				self.discard_card(player, 0)
		else:
			for _ in range(n):
				if self.players[player]["cards"]:
					r = self.get_range_and_print_enumed(self.players[player]["cards"], player)
					card_n = self.request_int_input(player, "What card to discard? n: ", r)
					self.discard_card(player, card_n)

	def discard_card(self, player, card_n):
		card = self.players[player]["cards"].pop(card_n)
		self.players[player]["discard"].append(card)
		return card

	def get_card_from_discard(self, player):
		if self.players[player]["discard"]:
			r = self.get_range_and_print_enumed(self.players[player]["discard"], player)
			card_n = self.request_int_input(player, "What card to take? ", r)
			card = self.players[player]["discard"].pop(card_n)
			self.players[player]["cards"].append(card)
		else:
			print("No cards in discard pile")

	def shuffle_the_deck(self, player):
		random.shuffle(self.players[player]["discard"])
		self.players[player]["pile"] = self.players[player]["discard"]
		self.players[player]["discard"] = []

	def get_neighbor_ns(self, char):
		char_n = self.characters.index(char)
		neigh_ns = [char_n - 1, char_n + 1]
		for n in range(2):
			if neigh_ns[n] < 0:
				neigh_ns[n] = len(self.characters) - 1
			elif neigh_ns[n] >= len(self.characters):
				neigh_ns[n] = 0
		return neigh_ns

if __name__ == "__main__":
	g = Game()
	w = g.run_game()