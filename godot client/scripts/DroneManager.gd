extends Node

onready var droni=preload("res://objects/TouchObject.tscn")

func _ready():
	pass # Replace with function body.

func addDrone(url):
	
	var http=HTTPRequest.new()
	
	get_tree().get_root().get_node("World").add_child(http)
	http.connect("request_completed", self, "_http_request_completed")
	var httpError = http.request("http://localhost:5000/connect_to/url/"+url)
	if httpError != OK :
		push_error("Errore in http")

func _http_request_completed(result, response_code, headers, body):
	
	print(body)
	var drone=droni.instance()
	get_tree().get_root().get_node("World/Drones").add_child(drone)
