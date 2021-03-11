CITY, CREATURE = 1, -1
PLAYER_NAMES = {1: "city", -1: "creature"}
STATES = {
	"city": (1, 2, 3, 4, 5),
	"creature": (-1, -2, -3, -4, -5),
	"alert": (2,),
	"guarded": (3, 4),
	"secured": (5,),
	"nervous": (-2,),
	"terrified": (-3, -4),
	"devoured": (-5,),
	"shiftable": (1, -1, 2, -2, 3, -3, 4, -4),
	"inbetween": (1, -1),
	"all": tuple(n*mult for mult in [1, -1] for n in range(1, 6)),
}

CONSTS = (CITY, CREATURE, PLAYER_NAMES, STATES)

ttable = {
	ord(" "): ord("_"),
}

equipment = ["sedative", "firehose", "driving licence", "walkie-talkie", "chocolate bars", "coupon", "shotgun", "revolver"]

def no_check(game):
	return True

def move_quickly(game):
	game.action_phase()

def turn_back(game):
	game.reverse_direction()

def preparations(game):
	game.take_cards(CITY, 2)

def preparations_check(game):
	return game.players[CREATURE]["energy"] > game.players[CITY]["energy"]

def lock_the_door(game):
	game.skip_activity_phase()

def night_search(game):
	for player in game.players:
		game.lose_cards(player, len(game.players[player]["cards"]) - 2)

def night_search_check(game):
	return len(game.players[CREATURE]['cards']) > 2

def regroup(game):
	chars = len(game.get_chars("hands", "city"))
	game.lose_cards(CREATURE, chars)

def regroup_check(game):
	return len(game.get_chars("hands", "city"))

def throwing_stuff(game):
	chars = len(game.get_chars("hands", "city"))
	game.update_energy(CREATURE, -chars)

def throwing_stuff_check(game):
	return len(game.get_chars("hands", "city")) and game.players[CREATURE]["energy"] > 0

def set_up_a_barricade(game):
	for player in game.players:
		if game.players[player]["energy"] > 4:
			game.players[player]["energy"] = 4

def set_up_a_barricade_check(game):
	return game.players[CREATURE]['energy'] > 4

def evacuation(game):
	game.delete_neighbor()

def evacuation_check(game):
	return game.chars_in_state("secured")

def we_need_to_close_this(game):
	for player in game.players:
		game.update_awareness(player, -1)

def we_need_to_close_this_check(game):
	return game.players[CREATURE]['awareness'] > game.players[CITY]["awareness"]

def floor_it(game):
	for n, char in enumerate(game.characters):
		print(n, char)
	r = [n for n in range(len(game.characters))]
	r.remove(game.activity_marker)
	char_n = game.request_int_input("What character to make active? n: ", r)
	game.activity_marker = char_n

def risky_maneuver(game):
	for char in game.chars_in_state("guarded"):
		char.state = 2
	for char in game.chars_in_state("terrified"):
		char.state = -2

def covering_your_tracks(game):
	game.update_awareness(CREATURE, -1)

def covering_your_tracks_check(game):
	return game.players[CREATURE]["awareness"] > 0

def stockroom_check(game):
	game.get_card_from_discard(CITY)

def stockroom_check_check(game):
	city_shoppers = len([char for char in game.get_chars("shop", "city")])
	if city_shoppers % 2 == 0:
		return city_shoppers >= len([char for char in game.get_chars("shop", "all")]) // 2
	else:
		return city_shoppers > len([char for char in game.get_chars("shop", "all")]) // 2
def front_page_article(game):
	game.update_awareness(CITY, 1)

def front_page_article_check(game):
	return len(game.chars_in_state('creature')) > len(game.characters) // 2

def on_the_house(game):
	game.update_energy(CITY, 3)

def on_the_house_check(game):
	return len(game.players[CREATURE]["cards"]) > len(game.players[CITY]["cards"])

def reroute(game):
	skip_character(game, 'Reroute')

def struggle(game):
	game.update_energy(CITY, -1)
	game.update_energy(CREATURE, 1)

def struggle_check(game):
	return game.players[CITY]['energy'] > 0

def hiding(game):
	skip_character(game, "Hiding")

def rage(game):
	for n, (card, _) in enumerate(game.equiped):
		print(n, card)
	card_n = game.request_int_input("What equipment card to remove? n: ", range(len(game.equiped)))
	card_name = game.equiped[card_n][0].name
	game.remove_equipment(card_name)

def rage_check(game):
	return game.equiped

def replacement(game):
	r = [n for n in range(len(game.characters))]
	r.remove(game.activity_marker)
	active_char = game.characters[game.activity_marker]

	print()
	for n in r:
		print(f"{n} {game.characters[n]}")

	char_n_before = game.request_int_input("What character to move? n: ", r)
	char_n_after = game.request_int_input("Where to place them? n: ", range(len(game.characters)))
	char_being_moved = game.characters.pop(char_n_before)
	game.characters.insert(char_n_after, char_being_moved)
	game.activity_marker = game.characters.index(active_char)
	game.print_board()

def lurking(game):
	n = len(game.players[CITY]['cards']) - len(game.players[CREATURE]['cards'])
	game.take_cards(CREATURE, n) 

def lurking_check(game):
	return len(game.players[CITY]['cards']) - len(game.players[CREATURE]['cards']) > 0

def entrapment(game):
	chars = [char for char in game.chars_in_state("creature") if char.state in STATES["shiftable"]]
	r = []
	for n, char in enumerate(game.characters):
		if char in chars:
			r.append(n)
			print(n, char)
	char_n = game.request_int_input("What character to entrap? n: ", r)
	game.move_safety_marker(char_n, -1)

def entrapment_check(game):
	return [char for char in game.chars_in_state("creature") if char.state in STATES["shiftable"]]

def ambush(game):
	if game.players[CITY]['energy'] in [0, 1]:
		option = "c"
	elif len(game.players[CITY]['cards']) in [0, 1]:
		option = "e"
	else:
		game.print_score()
		option = game.request_input("What should City lose, cards or energy?", ["c", "e"])

	if option == "e":
		game.update_energy(CITY, -(game.players[CITY]["energy"] // 2))
	elif option == "c":
		game.lose_cards(CITY, len(game.players[CITY]["cards"]) // 2)
	else:
		print("Error")

def ambush_check(game):
	return game.players[CITY]['energy'] > 1 or len(game.players[CITY]['cards']) > 1

def skip_character(game, card_name):
	game.print_board()
	char_n = game.request_int_input(f"What character to put {card_name} on? n: ", 
		range(len(game.characters)))
	game.skip_chars.add(char_n)
	print(f"{game.characters[char_n]} (skipped in Activity phase)")

def police(game, char):
	neighbors = [neig for neig in game.get_neighbors(char) if neig[1].state < 0]
	if neighbors:
		if len(neighbors) > 1:
			print()
			for n, neig in neighbors:
				print(n, neig)
			n = game.request_int_input("Whose Safety marker to shift? n: ", [n for n, _ in neighbors])
		else:
			n = neighbors[0][0]
		game.move_safety_marker(n, 1)
		return True
	return False

def route(game, char):
	confirm = game.request_input("Activate this Character's effect?", ["y", "n"])
	if confirm == "y":
		space = game.request_int_input("How many spaces forward to move the Activity marker? 1/2: ", [1, 2])
		for _ in range(space):
			game.move_activity_marker()
		return True
	return False

def shop(game, char):
	game.update_energy(CITY, 2)
	game.take_cards(CITY, 1)
	return True

def hands(game, char):
	if game.players[CITY]['cards']:
		confirm = game.request_input("Activate this Character's effect?", ["y", "n"])
		if confirm == "y":
			game.play_card(CITY, False)
			return True
	return False

def bob(game, char):
	game.update_awareness(CITY, -1)
	return True

def mandi(game, char):
	borderlines = [char_n for char_n, char in enumerate(game.characters) if char.state == 1]
	if borderlines:
		if len(borderlines) < 3:
			for char_n in borderlines:
				game.move_safety_marker(char_n, -1)
		else:
			for _ in range(2):
				for char_n in borderlines:
					print(char_n, game.characters[char_n])
				char_n = game.request_int_input("What character to drag into the Creature dimension? n: ", borderlines)
				game.move_safety_marker(char_n, -1)
				borderlines.remove(char_n)
		return True
	return False

def carl(game, char):
	if game.players[CREATURE]["cards"]:
		game.print_cards(CREATURE)
		confirm = game.request_input("Activate this Character's effect?", ["y", "n"])
		if confirm == "y":
			game.play_card(CREATURE)
			return True
	return False

def rodney(game, char):
	if game.players[CITY]["cards"]:
		game.print_cards(CITY)
		card_n = game.request_int_input("What City card to discard? n: ", range(len(game.players[CITY]['cards'])))
		game.discard_card(CITY, card_n)
		return True
	return False

def timmy(game, char):
	secured = game.chars_in_state("secured")
	if secured:
		for n, s in enumerate(secured):
			print(n, s)
		n = game.request_int_input("Whose Safety marker to shift? n: ", range(len(secured)))
		char_n = game.characters.index(secured[n])
		game.move_safety_marker(char_n, -2)
		return True
	return False

def richard(game, char):
	if game.equiped:
		for n, card in enumerate(game.equiped):
			print(n, card)
		n = game.request_int_input("What Equipment to remove from the game? n:", range(len(game.equiped)))
		card_name = game.equiped[n][0].name
		card = game.remove_equipment(card_name)[0]
		game.update_energy(CREATURE, card.cost)
		return True
	return False

def jeremy(game, char):
	confirm = game.request_input("Activate this Character's effect?", ["y", "n"])
	if confirm == "y":
		game.reverse_direction()
		return True
	return False

def julie(game, char):
	game.take_cards(CREATURE, 2)
	return True

def maggie(game, char):
	upgrade_cost = (game.players[CREATURE]["awareness"] + 1) // 2
	if game.players[CREATURE]["energy"] >= upgrade_cost:
		confirm = game.request_input("Activate this Character's effect?", ["y", "n"])
		if confirm == "y":
			game.update_awareness(CREATURE, 1)
			game.update_energy(CREATURE, -upgrade_cost)
			return True
	return False

def natalie(game, char):
	neighbors = game.get_neighbors(char)
	for n, ch in neighbors:
		print(n, ch)
	char_n = game.request_int_input("Whose Safety marker to shift? n: ", [n for n, _ in neighbors])
	game.move_safety_marker(char_n, -1)
	return True

def earl(game, char):
	minions = [ch for ch in game.characters if ch.state in [-3, -4, -5] and ch.name != char.name]
	if minions:
		char_ns = [game.characters.index(minion) for minion in minions]
		for char_n, minion in zip(char_ns, minions):
			print(f"{char_n} {minion.name.upper()}: {minion.perk_description[CREATURE]}")
		confirm = game.request_input("Activate any Character's effect?", ["y", "n"])
		if confirm == "y":
			char_n = game.request_int_input("What Character's effect to use? n: ", char_ns)
			game.characters[char_n].perks[CREATURE](game, game.characters[char_n])
			return True
	return False

def scott(game, char):
	n = len([ch for ch in game.characters if ch.state < -1])
	game.update_energy(CREATURE, n)
	return True

def sam(game, char):
	if game.players[CITY]["cards"] and game.players[CITY]["energy"] > 0:
		game.print_score()
		option = game.request_input("What should City lose?", ["c", "e"])
	elif game.players[CITY]["cards"]:
		option = "c"
	elif game.players[CITY]["energy"]:
		option = "e"
	else:
		return False

	if option == "c":
		game.lose_cards(CITY, 2)
	else:
		game.update_energy(CITY, -3)
	return True

def tom(game, char):
	if game.players[CREATURE]["cards"]:
		game.print_cards(CREATURE)
		confirm = game.request_input("Activate this Character's effect?", ["y", "n"])
		if confirm == "y":
			card_n = game.request_int_input("What Card to discard for energy? n: ", range(len(game.players[CREATURE]["cards"])))
			card = game.discard_card(CREATURE, card_n)
			game.update_energy(CREATURE, card.cost * 3)
			return True
	return False

def jayme(game, char):
	if game.players[CREATURE]["cards"]:
		for card in game.players[CREATURE]["cards"]:
			print(card.short_info())
		confirm = game.request_input("Activate this Character's effect?", ["y", "n"])
		if confirm == "y":
			card_n = game.request_int_input("What Card to discard? n: ", range(len(game.players[CREATURE]["cards"])))
			card = game.discard_card(CREATURE, card_n)
			char_ns = [game.characters.index(ch) for ch in game.get_chars(card.mark, "all")]
			for char_n in char_ns:
				game.move_safety_marker(char_n, -1)
			game.print_board()
			return True
	return False

def lance(game, char):
	game.update_energy(CREATURE, 3)
	return True

def maks(game, char):
	neighbors = game.get_neighbors(char)
	for char_n, neigh in neighbors:
		print(char_n, neigh)
	confirm = game.request_input("Activate this Character's effect?", ["y", "n"])
	if confirm == "y":
		char_n = game.request_int_input("What Character to remove from game? n:", [n for n, _ in neighbors])
		del game.characters[char_n]
		game.winner_check()
		return True
	return False

def mina(game, char):
	if game.players[CREATURE]["discard"]:
		game.get_card_from_discard(CREATURE)
		return True
	return False

