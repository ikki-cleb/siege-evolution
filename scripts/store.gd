extends Node
## In-app purchases. Loaded automatically at startup as "Store".
##
## The game is free. Everything below is optional:
##   3x speed, the Control and Toxin packs, and the Kitchen and Birthday Party
##   bonus worlds cost $1 each, or $3 for all five.
##
## TEST MODE: the web playtest build and editor runs grant purchases instantly,
## so the store can be tried without real money. Real purchases on phones need
## Apple's and Google's billing plugins (see the TODO in buy()); until those
## are added, phone builds report the store as unavailable instead of giving
## items away.

signal purchases_changed

const SPEED_3X := "speed_3x"
const PACK_CONTROL := "pack_control"
const PACK_TOXIN := "pack_toxin"
const WORLD_KITCHEN := "world_kitchen"
const WORLD_BIRTHDAY := "world_birthday"
const BUNDLE_ALL := "bundle_all"

## Everything for sale, in the order the Store screen lists it. These ids
## must match the product ids set up in App Store Connect / Google Play Console.
const PRODUCTS: Array[Dictionary] = [
	{"id": BUNDLE_ALL, "name": "Everything Bundle", "price": "$3.00",
		"description": "All five items below for $3 instead of $5."},
	{"id": SPEED_3X, "name": "3x Speed", "price": "$1.00",
		"description": "Adds a 3x fast-forward option to every level."},
	{"id": PACK_CONTROL, "name": "Control Pack", "price": "$1.00",
		"description": "Slows, stuns and area damage. Usable in every world."},
	{"id": PACK_TOXIN, "name": "Toxin Pack", "price": "$1.00",
		"description": "Stacking, spreading poison that ignores armor. Usable in every world."},
	{"id": WORLD_KITCHEN, "name": "Kitchen Defense", "price": "$1.00",
		"description": "Bonus world: defend the cookie jar from ants, slugs, mice and roaches.",
		"warning": "POST-GAME: HARD", "warning_detail": "Harder than Galactic Siege. Best after finishing the main game."},
	{"id": WORLD_BIRTHDAY, "name": "Birthday Bash", "price": "$1.00",
		"description": "Bonus world: wind-up toys, balloons, piñatas and a clown crash the party. Protect the cake.",
		"warning": "POST-GAME: HARD", "warning_detail": "Harder than Galactic Siege. Best after finishing the main game."},
]

const SAVE_PATH := "user://purchases.json"

## True when purchases are simulated (web playtest builds and the editor).
var test_mode := OS.has_feature("web") or OS.has_feature("editor") or OS.is_debug_build()

var _owned := {}  # product id -> true


func _ready() -> void:
	_load()


## True if the player owns this item (or the bundle that includes it).
## An empty id means "free", which is always owned.
func owns(product_id: String) -> bool:
	if product_id == "":
		return true
	if _owned.has(product_id):
		return true
	return product_id != BUNDLE_ALL and _owned.has(BUNDLE_ALL)


func product(product_id: String) -> Dictionary:
	for item in PRODUCTS:
		if item.id == product_id:
			return item
	return {}


func price(product_id: String) -> String:
	return product(product_id).get("price", "")


## True if the store can take purchases right now.
func is_available() -> bool:
	return test_mode


## Starts a purchase. Emits purchases_changed when it goes through.
func buy(product_id: String) -> void:
	if owns(product_id):
		return
	if test_mode:
		_grant(product_id)
		return
	# TODO (phone builds): hand off to the platform billing plugin here, and
	# call _grant() from its "purchase succeeded" callback.
	#   Android: Godot Google Play Billing plugin
	#   iOS:     Godot StoreKit plugin
	push_warning("Store: no billing plugin connected; purchase of %s ignored." % product_id)


## Asks the platform for everything this account already bought (required by
## Apple for any app with purchases).
func restore_purchases() -> void:
	# TODO (phone builds): ask the billing plugin, then _grant() each item.
	purchases_changed.emit()


## Test mode only: forget all purchases.
func reset_test_purchases() -> void:
	if not test_mode:
		return
	_owned.clear()
	_save()
	purchases_changed.emit()


func _grant(product_id: String) -> void:
	_owned[product_id] = true
	_save()
	purchases_changed.emit()


func _load() -> void:
	if not FileAccess.file_exists(SAVE_PATH):
		return
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH))
	if parsed is Array:
		for product_id in parsed:
			_owned[str(product_id)] = true


func _save() -> void:
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(_owned.keys()))
