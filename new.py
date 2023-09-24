def play_action_phase(self):
	self.switch_current_player()
	move = self.choose_action_move()
	self.play_action_move(move)

def play_action_move(self, move):
	action = next(move)
	if action == 1:
		self.play_card(move)
	elif action == 2:
		self.prepare(move)
	else:
		self.rest()

def get_card_n(self, player, card_name):
	cards = self.players[player]["cards"]
	for n in range(len(cards)):
		if cards[n].name == card_name:
			return n

def prepare(self, move):
	player = self.current_player
	discard = next(move)

	if discard == "y":
		discard = next(move)
		for card_name in discard:
			card_n = self.get_card_n(player, card_name)
			self.discard_card(player, card_n)

	n = 5 - len(self.players[player]["cards"])
	self.take_cards(player, n)

def play_card(self, move):
	player = self.current_player

	card_name, mode = next(move)
	card_n = self.get_card_n(player, card_name)
	card = self.players[player]["cards"].pop(card_n)

	if mode == "m":
		self.shift_marker(move)
	elif mode == "s":
		self.place_symbol(move)

	activate = next(move)

	if activate == "y":
		action = next(move)
		card.perk(self, action)

	if not card.equip:
		self.players[player]["discard"].append(card)

def shift_marker(self, move):
	char_n, n = next(move)

	new_state = self.characters[char_n].state + self.current_player * n
	if new_state > 5:
		new_state = 5
	elif new_state < -5:
		new_state = -5
	elif new_state == 0:
		new_state =+ self.current_player

	self.characters[char_n].state = new_state
	self.winner_check()

def place_symbol(self, move):
	char_n, mark = next(move)
	for char in self.characters:
		char.remove_temp_mark(self.current_player, mark)
	self.characters[char_n].marks[self.current_player].append(mark)

