import game_data as gd

CITY, CREATURE = 1, -1
PLAYER_NAMES = {1: "city", -1: "creature"}

STATES = {
	CITY: (1, 2, 3, 4, 5),
	CREATURE: (-1, -2, -3, -4, -5),
	"alert": (2,),
	"guarded": (3, 4),
	"secured": (5,),
	"nervous": (-2,),
	"terrified": (-3, -4),
	"devoured": (-5,),
	"shiftable": (1, -1, 2, -2, 3, -3, 4, -4),
	"inbetween": (1, -1),
	"city_border": (1,),
	"creature_border": (-1,),
	"creature_shiftable": (-1, -2, -3, -4),
	"all": tuple(n*mult for mult in [1, -1] for n in range(1, 6)),
}
mark_names = ["hands", "shop", "police", "route", "eye", "pistol", "cloud", "claw", "bars", "scratch", "crack"]

MARK_IDS = {name: n for n, name in zip((n for n in range(1, len(mark_names) + 1)), mark_names)}
MARK_NAMES = {n: name for name, n in MARK_IDS.items()}
CARD_IDS = {card[0]: card[-1] for card in gd.CITY_CARDS + gd.CREATURE_CARDS}
CARD_NAMES = {card_id: card_name for card_name, card_id in CARD_IDS.items()}

CONSTS = (CITY, CREATURE, PLAYER_NAMES, STATES, MARK_IDS, MARK_NAMES, CARD_IDS, CARD_NAMES)

ttable = {
	ord(" "): ord("_"),
}

CARD_ACTS_CHOOSABLE = [
	"evacuation", 
	"floor_it", 
	"stockroom_check", 
	"hiding",
	"reroute", 
	"rage", 
	"replacement",
	"entrapment",
	"ambush"]

def card_act_options(game, card_name):
	name = card_name.lower().strip("!").translate(ttable)
	if name not in CARD_ACT_OPTS:
		return [""]
	return CARD_ACT_OPTS[name](game)

def no_check(game):
	return True

def denied(game):
	return False

def move_quickly(game):
	game.extra_move = True

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
	chars = len(game.marked_in_state(MARK_IDS["hands"], CITY))
	game.lose_cards(CREATURE, chars)

def regroup_check(game):
	return len(game.marked_in_state(MARK_IDS["hands"], CITY)) and game.players[CREATURE]["cards"]

def throwing_stuff(game):
	chars = len(game.marked_in_state(MARK_IDS["hands"], CITY))
	game.update_energy(CREATURE, -chars)

def throwing_stuff_check(game):
	return len(game.marked_in_state(MARK_IDS["hands"], CITY)) and game.players[CREATURE]["energy"]

def set_up_a_barricade(game):
	for player in game.players:
		if game.players[player]["energy"] > 4:
			game.players[player]["energy"] = 4

def set_up_a_barricade_check(game):
	return game.players[CREATURE]['energy'] > 4

def evacuation(game, option):
	active_char, marker = game.get_active_char(), game.activity_marker
	del game.characters[option]
	if active_char in game.characters:
		game.activity_marker = game.characters.index(active_char)
	elif marker < len(game.characters):
		game.activity_marker = marker
	else:
		game.activity_marker = 0
	game.winner_check()

def evacuation_check(game):
	return game.in_state("secured")

def evacuation_options(game):
	secured = [char for char in game.characters if char.state in STATES["secured"]]
	return [n for secure in secured for n in game.get_neighbor_ns(secure)]

def we_need_to_close_this(game):
	for player in game.players:
		game.update_awareness(player, -1)

def we_need_to_close_this_check(game):
	return game.players[CREATURE]["awareness"] > 0 and game.players[CREATURE]['awareness'] >= game.players[CITY]["awareness"]

def floor_it(game, option):
	game.activity_marker = option

def floor_it_options(game):
	return [n for n in range(len(game.characters)) if n != game.activity_marker]

def risky_maneuver(game):
	for char in game.in_state("guarded"):
		char.state = 2
	for char in game.in_state("terrified"):
		char.state = -2

def risky_maneuver_check(game):
	return game.in_state("terrified") and len(game.in_state("terrified")) >= len(game.in_state("guarded"))

def covering_your_tracks(game):
	game.update_awareness(CREATURE, -1)

def covering_your_tracks_check(game):
	return game.players[CREATURE]["awareness"] > 0

def stockroom_check(game, option):
	game.get_card_from_discard(CITY, option)

def stockroom_check_check(game):
	if game.players[CITY]["discard"]:
		city_shoppers = len([char for char in game.marked_in_state(MARK_IDS["shop"], CITY)])
		if city_shoppers % 2 == 0:
			return city_shoppers >= len([char for char in game.marked_in_state(MARK_IDS["shop"], "all")]) // 2
		else:
			return city_shoppers > len([char for char in game.marked_in_state(MARK_IDS["shop"], "all")]) // 2
	else:
		return False

def stockroom_check_options(game):
	return set(card.id for card in game.players[CITY]["discard"])

def front_page_article(game):
	game.update_awareness(CITY, 1)

def front_page_article_check(game):
	return len(game.in_state(CREATURE)) > len(game.characters) // 2

def on_the_house(game):
	game.update_energy(CITY, 3)

def on_the_house_check(game):
	return len(game.players[CREATURE]["cards"]) > len(game.players[CITY]["cards"])

def reroute(game, option):
	skip_character(game, option, CARD_IDS["Reroute"])

def reroute_options(game):
	return skip_character_options(game)

def struggle(game):
	game.update_energy(CITY, -1)
	game.update_energy(CREATURE, 1)

def struggle_check(game):
	return game.players[CITY]['energy'] > 0

def hiding(game, option):
	skip_character(game, option, CARD_IDS["Hiding"])

def hiding_options(game):
	return skip_character_options(game)

def rage(game, option):
	game.remove_equipment(game.equiped[option].name)

def rage_check(game):
	return game.equiped

def rage_options(game):
	return [n for n in game.equiped]

def replacement(game, option):
	whom, where = option
	active_char = game.characters[game.activity_marker]

	whom = game.characters.pop(whom)
	game.characters.insert(where, whom)
	game.activity_marker = game.characters.index(active_char)

def replacement_options(game):
	chars = range(len(game.characters))
	marker = game.activity_marker

	return [(whom, where) 
		for whom in chars if whom != marker 
		for where in chars if where != whom]

def lurking(game):
	n = len(game.players[CITY]['cards']) - len(game.players[CREATURE]['cards'])
	game.take_cards(CREATURE, n) 

def lurking_check(game):
	return len(game.players[CITY]['cards']) - len(game.players[CREATURE]['cards']) > 0

def entrapment(game, option):
	move = iter(((option, CREATURE),))
	game.shift_marker(move)

def entrapment_check(game):
	return [char for char in game.in_state("creature_shiftable")]

def entrapment_options(game):
	return [n for n in game.n_in_state("creature_shiftable")]

def ambush(game, option):
	city = game.players[CITY]
	if option == "e":
		game.update_energy(CITY, -(city["energy"] // 2))
	elif option == "c":
		game.lose_cards(CITY, len(city["cards"]) // 2)
	else:
		print("Error")

def ambush_check(game):
	return game.players[CITY]['energy'] > 1 or len(game.players[CITY]['cards']) > 1

def ambush_options(game):
	city = game.players[CITY]
	if city["energy"] < 2:
		return ["c"]
	elif len(city["cards"]) < 2:
		return ["e"]
	else:
		return ["c", "e"]

def skip_character(game, option, card_id):
	game.skip_chars.add(option)
	game.characters[option].card_effects[0] = card_id

def skip_character_options(game):
	return [n for n in range(len(game.characters)) if n not in game.skip_chars]

def police(game, char):
	neighbors = [n for n in game.get_neighbor_ns(char) 
	if game.characters[n] in game.in_state(CREATURE) and
	game.characters[n] in game.in_state("shiftable")]
	if neighbors:
		if len(neighbors) > 1:
			r = game.get_range_and_print_enumed(game.characters, CITY, filt=neighbors)
			n = game.request_int_input(CITY, "Whose Safety marker to shift? n: ", r)
		else:
			n = neighbors[0]
		game.move_safety_marker(n, CITY)
		return True
	return False

def route(game, char):
	confirm = game.request_input(CITY, "Activate this Character's effect?", ["y", "n"])
	if confirm == "y":
		space = game.request_int_input(CITY, "How many spaces forward to move the Activity marker? 1/2: ", [1, 2])
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
		game.print_cards(CITY)
		confirm = game.request_input(CITY, "Activate this Character's effect?", ["y", "n"])
		if confirm == "y":
			game.play_card(CITY, False)
			return True
	return False

def bob(game, char):
	game.update_awareness(CITY, -1)
	return True

def bob_check(game, char):
	return game.players[CITY]["awareness"] > 0

def mandi(game, char):
	r = game.get_range_and_print_enumed(game.characters, CREATURE, filt=game.in_state("city_border"))
	for _ in range(2):
		if r:
			n = game.request_int_input(CREATURE, "What character to drag into the Creature dimension? n: ", r)
			game.move_safety_marker(n, CREATURE)
			r.remove(n)
	return True

def mandi_check(game, char):
	return game.in_state("city_border")

def carl(game, char):
	game.print_cards(CREATURE)
	confirm = game.request_input(CREATURE, "Activate this Character's effect?", ["y", "n"])
	if confirm == "y":
		game.play_card(CREATURE)
		return True
	return False

def carl_check(game, char):
	return game.players[CREATURE]["cards"]

def rodney(game, char):
	game.print_cards(CITY, CREATURE)
	r = game.get_range_and_print_enumed(game.players[CITY]['cards'], CREATURE)
	n = game.request_int_input(CREATURE, "What City card to discard? n: ", r)
	game.discard_card(CITY, n)
	return True

def rodney_check(game, char):
	return game.players[CITY]["cards"]

def timmy(game, char):
	r = game.get_range_and_print_enumed(game.characters, CREATURE, filt=game.in_state("secured"))
	n = game.request_int_input(CREATURE, "Whose Safety marker to shift? n: ", r)
	game.move_safety_marker(n, -2)
	return True

def timmy_check(game, char):
	return game.in_state("secured")

def richard(game, char):
	r = game.get_range_and_print_enumed(game.equiped, CREATURE)
	n = game.request_int_input(CREATURE, "What Equipment to remove from the game? n:", r)
	card = game.remove_equipment(game.equiped[n].name)
	print(f"{card.name} is unequiped")
	game.update_energy(CREATURE, card.cost)
	return True

def richard_check(game, char):
	return game.equiped

def jeremy(game, char):
	confirm = game.request_input(CREATURE, "Activate this Character's effect?", ["y", "n"])
	if confirm == "y":
		game.reverse_direction()
		return True
	return False

def jeremy_check(game, char):
	return True

def julie(game, char):
	game.take_cards(CREATURE, 2)
	return True

def julie_check(game, char):
	return True

def maggie(game, char):
	upgrade_cost = (game.players[CREATURE]["awareness"] + 1) // 2
	confirm = game.request_input(CREATURE, "Activate this Character's effect?", ["y", "n"])
	if confirm == "y":
		game.update_awareness(CREATURE, 1)
		game.update_energy(CREATURE, -upgrade_cost)
		return True
	return False

def maggie_check(game, char):
	upgrade_cost = (game.players[CREATURE]["awareness"] + 1) // 2
	return game.players[CREATURE]["energy"] >= upgrade_cost

def natalie(game, char):
	shiftable_neigh_ns = [n for n in game.get_neighbor_ns(char) 
				if game.characters[n].state in STATES["shiftable"]]
	r = game.get_range_and_print_enumed(game.characters, CREATURE, filt=shiftable_neigh_ns)
	n = game.request_int_input(CREATURE, "Whose Safety marker to shift? n: ", r)
	game.move_safety_marker(n, CREATURE)
	return True

def natalie_check(game, char):
	return any(game.characters[n].state in STATES["shiftable"] for n in game.get_neighbor_ns(char))

def earl(game, char):
	minions = [ch for ch in game.characters 
		if ch.name != char.name and ch.state in [-3, -4, -5] and ch.perks[CREATURE]["condition"](game, ch)]
	char_ns = [game.characters.index(minion) for minion in minions]
	for char_n, minion in zip(char_ns, minions):
		print(f"{char_n} {minion.name.upper()}: {minion.perk_description[CREATURE]}")
	confirm = game.request_input(CREATURE, "Activate any Character's effect?", ["y", "n"])
	if confirm == "y":
		if len(char_ns) == 1:
			n = char_ns[0]
		else:
			n = game.request_int_input(CREATURE, "What Character's effect to use? n: ", char_ns)
		game.characters[n].perks[CREATURE]["perk"](game, game.characters[n])
		return True
	return False

def earl_check(game, char):
	return [ch for ch in game.characters 
		if ch.state in [-3, -4, -5] and ch.name != char.name and ch.perks[CREATURE]["condition"](game, ch)]

def scott(game, char):
	n = len([ch for ch in game.characters if ch.state < -1])
	game.update_energy(CREATURE, n)
	return True

def scott_check(game, char):
	return game.in_state(CREATURE) and game.players[CREATURE]["energy"] < 10

def sam(game, char):
	if game.players[CITY]["cards"] and game.players[CITY]["energy"] > 0:
		game.print_score()
		option = game.request_input(CREATURE, "What should City lose?", ["c", "e"])
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

def sam_check(game, char):
	return game.players[CITY]["cards"] or game.players[CITY]["energy"]

def tom(game, char):
	r = game.get_range_and_print_enumed(game.players[CREATURE]["cards"], CREATURE)
	confirm = game.request_input(CREATURE, "Activate this Character's effect?", ["y", "n"])
	if confirm == "y":
		n = game.request_int_input(CREATURE, "What Card to discard for triple amount of energy? n: ", r)
		card = game.discard_card(CREATURE, n)
		game.update_energy(CREATURE, card.cost * 3)
		return True
	return False

def tom_check(game, char):
	return game.players[CREATURE]["cards"]

def jayme(game, char):
	game.print_board()
	r = game.get_range_and_print_enumed(game.players[CREATURE]["cards"], CREATURE, short=True)
	confirm = game.request_input(CREATURE, "Activate this Character's effect?", ["y", "n"])
	if confirm == "y":
		n = game.request_int_input(CREATURE, "What Card to discard? n: ", r)
		card = game.discard_card(CREATURE, n)
		chars_marked = game.get_range_and_print_enumed(game.characters, CREATURE, 
			filt=game.marked_in_state(card.mark, "shiftable"))
		for n in chars_marked:
			game.move_safety_marker(n, CREATURE)
		game.print_board()
		return True
	return False

def jayme_check(game, char):
	return any(game.marked_in_state(card.mark, "shiftable") for card in game.players[CREATURE]["cards"])

def lance(game, char):
	game.update_energy(CREATURE, 3)
	return True

def lance_check(game, char):
	return game.players[CREATURE]["energy"] < 10

def maks(game, char):
	r = game.get_range_and_print_enumed(game.characters, CREATURE, filt=game.get_neighbor_ns(char))
	confirm = game.request_input(CREATURE, "Activate this Character's effect?", ["y", "n"])
	if confirm == "y":
		n = game.request_int_input(CREATURE, "What Character to remove from game? n:", r)
		del game.characters[n]
		game.winner_check()
		return True
	return False

def maks_check(game, char):
	return True

def mina(game, char):
	raise NotImplementedError

def mina_check(game, char):
	return game.players[CREATURE]["discard"]

CARD_ACT_OPTS = {name: eval(f"{name}_options") for name in CARD_ACTS_CHOOSABLE}