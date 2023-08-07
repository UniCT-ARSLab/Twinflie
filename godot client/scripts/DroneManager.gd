extends Node
signal drone_collided
onready var droni=preload("res://objects/TouchObject.tscn")
onready var loading=preload("res://objects/gui/loading_screen.tscn")
var num=0

var current_url=""

func _ready():
	pass # Replace with function body.




func addDrone(url):
	var http=HTTPRequest.new()
	
	get_tree().get_root().get_node("World").add_child(http)
	http.connect("request_completed", self, "_http_request_completed")
	var caricamento=loading.instance()
	get_tree().get_root().add_child(caricamento)
	var httpError = http.request("http://localhost:5000/connect_to/url/"+url)
	current_url=url.replace("_","/")
	print(httpError)
	if httpError != OK :
		push_error("Errore in http")

func _http_request_completed(result, response_code, headers, body):
	
	print("test:",body.get_string_from_utf8())
	if(body.get_string_from_utf8().find("failed")!=-1):
		
		get_tree().get_root().remove_child(get_tree().get_root().get_node("Loading_screen"))
		GuiManager.create_alert("non è stato possibile connetersi al drone richiesto verificare l'url inserito e che il drone sia acceso","connection error")
		return
	else:
		var drone=droni.instance()
		drone.set_objectName(current_url)
		get_tree().get_root().get_node("World/Drones").add_child(drone)
		get_tree().get_root().remove_child(get_tree().get_root().get_node("Loading_screen"))
		if num==0:
			var caricamento=loading.instance()
			get_tree().get_root().add_child(caricamento)
			get_tree().get_root().get_node("World/AnchorContainer").make_req()
		else:
			get_tree().get_root().remove_child(get_tree().get_root().get_node("Loading_screen"))
		
		num=num+1
