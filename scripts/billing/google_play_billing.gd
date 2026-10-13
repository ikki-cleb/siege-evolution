class_name GooglePlayBilling
extends RefCounted
## Real purchases on Android, through Godot's Google Play Billing plugin
## (the "GodotGooglePlayBilling" singleton; tools/ci/fetch_plugins.sh adds it
## to phone builds). The Store script talks to this; this talks to the plugin.
##
## The plugin renamed its methods between versions (startConnection ->
## start_connection, querySkuDetails -> query_product_details...), so every
## call below tries both names, and replies are read with either key name.
## Google refunds purchases that aren't "acknowledged" within 3 days, so
## every owned item is acknowledged as soon as we see it.

signal ready_changed  ## connected to (or disconnected from) Google Play
signal owned(product_id: String)  ## a purchase or restore went through
signal prices_changed  ## localized prices arrived
signal failed(message: String)

const PURCHASED := 1  ## Google's purchase state for a completed purchase

var plugin: Object
var product_ids: Array = []
var connected := false
var prices := {}  ## product id -> localized price text, e.g. "0,99 €"


func _init(p_plugin: Object, p_product_ids: Array) -> void:
	plugin = p_plugin
	product_ids = p_product_ids
	# Connect whichever signals this plugin version has.
	_listen(["connected"], _on_connected)
	_listen(["disconnected"], _on_disconnected)
	_listen(["connect_error"], _on_connect_error)
	_listen(["query_product_details_response", "sku_details_query_completed"], _on_details)
	_listen(["on_purchase_updated", "purchases_updated"], _on_purchases)
	_listen(["query_purchases_response"], _on_purchases)
	_listen(["purchase_error"], _on_purchase_error)
	_call(["start_connection", "startConnection"], [])


func buy(product_id: String) -> void:
	if not connected:
		failed.emit("Google Play isn't connected yet. Please try again in a moment.")
		return
	_call(["purchase"], [product_id])


## Looks up everything this Google account already owns (restore).
func restore() -> void:
	if connected:
		_call(["query_purchases", "queryPurchases"], ["inapp"])


# --- Plugin replies -----------------------------------------------------------

func _on_connected() -> void:
	connected = true
	ready_changed.emit()
	_call(["query_product_details", "querySkuDetails"], [product_ids, "inapp"])
	restore()  # anything bought on another phone, or never acknowledged


func _on_connect_error(_code = 0, message = "") -> void:
	failed.emit("Couldn't reach Google Play. %s" % message)


func _on_purchase_error(_code = 0, message = "") -> void:
	failed.emit("Purchase failed. %s" % message)


func _on_disconnected() -> void:
	connected = false
	ready_changed.emit()


## Prices: a Dictionary with "product_details" (new) or an Array of
## {"sku", "price"} (old).
func _on_details(reply) -> void:
	var items: Array = reply.get("product_details", []) if reply is Dictionary else reply
	for item in items:
		var id: String = item.get("product_id", item.get("sku", ""))
		var offer: Dictionary = item.get("one_time_purchase_offer_details", {})
		var text: String = offer.get("formatted_price", item.get("price", ""))
		if id != "" and text != "":
			prices[id] = text
	prices_changed.emit()


## Purchases (new or restored): a Dictionary with "purchases" (new or old
## query reply) or a plain Array of purchases (old purchases_updated).
func _on_purchases(reply) -> void:
	var list: Array = reply.get("purchases", []) if reply is Dictionary else reply
	for purchase in list:
		if int(purchase.get("purchase_state", PURCHASED)) != PURCHASED:
			continue  # pending (e.g. paying with cash); it arrives again once paid
		var ids: Array = purchase.get("product_ids", purchase.get("skus", []))
		if ids.is_empty() and purchase.has("sku"):
			ids = [purchase.sku]
		for id in ids:
			owned.emit(str(id))
		if not purchase.get("is_acknowledged", false):
			_call(["acknowledge_purchase", "acknowledgePurchase"], [purchase.get("purchase_token", "")])


# --- Helpers ------------------------------------------------------------------

func _listen(names: Array, callback: Callable) -> void:
	for name in names:
		if plugin.has_signal(name):
			plugin.connect(name, callback)


func _call(names: Array, args: Array) -> void:
	for name in names:
		if plugin.has_method(name):
			plugin.callv(name, args)
			return
	push_warning("Google Play Billing plugin has none of: %s" % ", ".join(names))
