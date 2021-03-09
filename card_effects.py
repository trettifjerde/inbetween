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
	"unmarked": (1, -1),
	"shiftable": (1, -1, 2, -2, 3, -3, 4, -4),
	"all": tuple(n*mult for mult in [1, -1] for n in range(1, 6)),
}

CONSTS = (CITY, CREATURE, PLAYER_NAMES, STATES)

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
	game.skip_activation_phase()

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
	return len(game.get_chars("hands", "city"))

def barricade(game):
	for player in game.players:
		if game.players[player]["energy"] > 4:
			game.players[player]["energy"] = 4

def barricade_check(game):
	return game.players[CREATURE]['energy'] > 4

def evacuation(game):
	game.delete_neighbor()

def evacuation_check(game):
	return game.chars_in_state("secured")

def close_this(game):
	for player in game.players:
		game.update_awareness(player, -1)

def close_this_check(game):
	return game.players[CREATURE]['awareness'] > 0

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

def covering_tracks(game):
	game.update_awareness(CREATURE, -1)

def covering_tracks_check(game):
	return game.players[CREATURE]["awareness"] > 0

def stockroom(game):
	game.get_card_from_discard(CITY)

def stockroom_check(game):
	return len(game.get_chars('shop', 'city')) >= len(game.get_chars('shop', 'all')) // 2

def front_page(game):
	game.update_awareness(CITY, 1)

def front_page_check(game):
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
	card_n = game.request_int_input("What equipment card to remove? n: ", range(len(game.equiped)))
	game.equiped.pop(card_n)

def rage_check(game):
	return game.equiped

def replacement(game):
	r = [n for n in range(len(game.characters))]
	r.remove(game.activity_marker)
	active_char = game.characters[game.activity_marker]
	game.print_board()
	char_n_before = game.request_int_input("What character to move? n: ", r)
	char_n_after = game.request_int_input("Where to place them? n: ", range(len(game.characters)))
	char_being_moved = game.characters.pop(char_n_before)
	game.characters.insert(char_n_after, char_being_moved)
	game.activity_marker = game.characters.index(active_char)

def lurking(game):
	n = len(game.players[CITY]['cards']) - len(game.players[CREATURE]['cards'])
	game.take_cards(CREATURE, n) 

def lurking_check(game):
	return len(game.players[CITY]['cards']) - len(game.players[CREATURE]['cards']) > 0

def entrap(game):
	chars = [char for char in game.chars_in_state("creature") if char.state in STATES["shiftable"]]
	r = []
	for n, char in enumerate(game.characters):
		if char in chars:
			r.append(n)
			print(n, char)
	char_n = game.request_int_input("What character to entrap? n: ", r)
	game.move_marker(char_n, -1)

def entrap_check(game):
	return [char for char in game.chars_in_state("creature") if char.state in STATES["shiftable"]]

def ambush(game):
	if game.players[CITY]['energy'] in [0, 1]:
		option = "c"
	elif len(game.players[CITY]['cards']) in [0, 1]:
		option = "e"
	else:
		while True:
			option = input("What should City lose, cards or energy? c/e: ")
			if option in ["c", "e"]:
				break
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