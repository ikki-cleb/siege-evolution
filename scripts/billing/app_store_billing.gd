class_name AppStoreBilling
extends RefCounted
## Real purchases on iPhone, through Godot's StoreKit plugin (the "InAppStore"
## singleton from godot-ios-plugins; tools/ci/fetch_plugins.sh adds it to
## phone builds). The Store script talks to this; this talks to the plugin.
##
## The plugin doesn't use signals: it queues "events" (Dictionaries with a
## "type" and a "result") that we read every frame with poll().

signal ready_changed
signal owned(product_id: String)
signal prices_changed
signal failed(message: String)

var plugin: Object
var product_ids: Array = []
var connected := true  ## StoreKit needs no connection step
var prices := {}


func _init(p_plugin: Object, p_product_ids: Array) -> void:
	plugin = p_plugin
	product_ids = p_product_ids
	# Finish each transaction as soon as it's reported, so Apple stops
	# re-sending it (we save what was bought ourselves).
	if plugin.has_method("set_auto_finish_transaction"):
		plugin.set_auto_finish_transaction(true)
	plugin.request_product_info({"product_ids": PackedStringArray(product_ids)})


func buy(product_id: String) -> void:
	plugin.purchase({"product_id": product_id})


## Asks Apple for everything this Apple ID already bought (required for any
## app with purchases: the Store screen has a Restore Purchases button).
func restore() -> void:
	plugin.restore_purchases()


## Reads the plugin's queued events. The Store calls this every frame.
func poll() -> void:
	while plugin.get_pending_event_count() > 0:
		_handle(plugin.pop_pending_event())


func _handle(event: Dictionary) -> void:
	var ok: bool = event.get("result", "") == "ok"
	match event.get("type", ""):
		"product_info":
			if ok:
				var ids: Array = event.get("ids", [])
				var texts: Array = event.get("localized_prices", event.get("prices", []))
				for i in mini(ids.size(), texts.size()):
					prices[str(ids[i])] = str(texts[i])
				prices_changed.emit()
		"purchase", "restore":
			if ok:
				owned.emit(str(event.get("product_id", "")))
			elif event.get("result", "") == "error":
				failed.emit("Purchase didn't go through. %s" % event.get("error", ""))
