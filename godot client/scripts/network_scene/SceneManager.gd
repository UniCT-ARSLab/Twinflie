extends Node

var URL_SERVER = ""
var droneScene = preload("res://objects/network_test/NetworkDrone.tscn")
var httpClient : HTTPRequest
var timerRequest : Timer
var connected = false
var droneListNodes = {}
var requesting = false



func _ready():
	httpClient = HTTPRequest.new()
	
	timerRequest = Timer.new()
	add_child(httpClient)
	add_child(timerRequest)

func _process(delta):
	if(!connected) :
		return
	self.sendRequest()

func disconnectHttp():
	httpClient.disconnect("request_completed", self, "_on_request_completed")
	self.connected = false

func connectHttp(urlPort):
	self.URL_SERVER = urlPort if (urlPort != null && urlPort!="") else "localhost:8080"
	httpClient.connect("request_completed", self, "_on_request_completed")
	self.connected = true
	
func sendRequest():
	if !requesting:
		requesting=true
		httpClient.request("http://"+self.URL_SERVER+"/agentlist")

func _on_request_completed(result, response_code, headers, body):
	requesting = false
	var json = JSON.parse(body.get_string_from_utf8())
	if json and len(json.result)>0 :
		for droneInfo in json.result:
			if not droneListNodes.has(droneInfo.name):
				droneListNodes[droneInfo.name] = droneScene.instance()
				get_tree().root.get_node("World/Drones").add_child(droneListNodes[droneInfo.name], true)
			
			droneListNodes[droneInfo.name].move(droneInfo.x / 10, droneInfo.y/ 10, droneInfo.z/ 10)
