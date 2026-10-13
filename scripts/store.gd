extends Node
## In-app purchases. Loaded automatically at startup as "Store".
##
## The game is free. Everything below is optional:
##   4x speed, the Control and Toxin packs, and the Kitchen and Birthday Party
##   bonus worlds cost $0.99 each, or $2.99 for all five (store price tiers).
##
## TEST MODE: the web playtest build and editor runs grant purchases instantly,
## so the store can be tried without real money.
## PHONES: real purchases go through Apple's or Google's billing plugin
## (scripts/billing/), which phone builds include (tools/ci/fetch_plugins.sh).
## Without a plugin the store reports itself unavailable instead of giving
## items away. Prices shown come from the store (in the player's currency)
## once it answers; the prices below are only the fallback.

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
	{"id": BUNDLE_ALL, "name": "Everything Bundle", "price": "$2.99",
		"description": "All five items below for $2.99 instead of $4.95."},
	{"id": SPEED_3X, "name": "4x Speed", "price": "$0.99",
		"description": "Adds a 4x fast-forward option to every level."},
	{"id": PACK_CONTROL, "name": "Control Pack", "price": "$0.99",
		"description": "Slows, stuns and area damage. Usable in every world."},
	{"id": PACK_TOXIN, "name": "Toxin Pack", "price": "$0.99",
		"description": "Stacking, spreading poison that ignores armor. Usable in every world."},
	{"id": WORLD_KITCHEN, "name": "Kitchen Defense", "price": "$0.99",
		"description": "Bonus world: defend the cookie jar from ants, slugs, mice and roaches.",
		"warning": "POST-GAME: HARD", "warning_detail": "Harder than Galactic Siege. Best after finishing the main game."},
	{"id": WORLD_BIRTHDAY, "name": "Birthday Bash", "price": "$0.99",
		"description": "Bonus world: wind-up toys, balloons, piñatas and a clown crash the party. Protect the cake.",
		"warning": "POST-GAME: HARD", "warning_detail": "Harder than Galactic Siege. Best after finishing the main game."},
]

const SAVE_PATH := "user://purchases.json"

## True when purchases are simulated (web playtest builds and the editor).
var test_mode := OS.has_feature("web") or OS.has_feature("editor") or OS.is_debug_build()

var _owned := {}  # product id -> true
## The phone's billing plugin wrapper (GooglePlayBilling or AppStoreBilling),
## or null (web, editor, or a phone build without the plugin).
var billing: RefCounted = null

## A message for the player (a failed purchase, store unavailable...).
signal notice(text: String)


func _ready() -> void:
	_load()
	if test_mode:
		return
	var ids := PRODUCTS.map(func(item): return item.id)
	if Engine.has_singleton("GodotGooglePlayBilling"):
		use_billing(GooglePlayBilling.new(Engine.get_singleton("GodotGooglePlayBilling"), ids))
	elif Engine.has_singleton("InAppStore"):
		use_billing(AppStoreBilling.new(Engine.get_singleton("InAppStore"), ids))


## Plugs in a billing wrapper (the tests pass one with a fake plugin).
func use_billing(wrapper: RefCounted) -> void:
	billing = wrapper
	billing.owned.connect(_grant)
	billing.prices_changed.connect(func(): purchases_changed.emit())
	billing.ready_changed.connect(func(): purchases_changed.emit())
	billing.failed.connect(func(text): notice.emit(text))


func _process(_delta: float) -> void:
	# The App Store plugin queues its replies; read them every frame.
	if billing and billing.has_method("poll"):
		billing.poll()


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


## The price to show: the store's own (in the player's currency) once it has
## answered, else the fallback in PRODUCTS.
func price(product_id: String) -> String:
	if billing and billing.prices.has(product_id):
		return billing.prices[product_id]
	return product(product_id).get("price", "")


## True if the store can take purchases right now.
func is_available() -> bool:
	return test_mode or (billing != null and billing.connected)


## Starts a purchase. Emits purchases_changed when it goes through.
func buy(product_id: String) -> void:
	if owns(product_id):
		return
	if test_mode:
		_grant(product_id)
		return
	if billing == null:
		notice.emit("The store isn't available right now.")
		return
	billing.buy(product_id)  # _grant() runs when the store confirms it


## Asks the platform for everything this account already bought (required by
## Apple for any app with purchases).
func restore_purchases() -> void:
	if billing:
		billing.restore()  # each owned item comes back through _grant()
	else:
		purchases_changed.emit()


## Test mode only: forget all purchases.
func reset_test_purchases() -> void:
	if not test_mode:
		return
	_owned.clear()
	_save()
	purchases_changed.emit()


func _grant(product_id: String) -> void:
	if product(product_id).is_empty() or _owned.has(product_id):
		return  # not one of ours, or already saved
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
