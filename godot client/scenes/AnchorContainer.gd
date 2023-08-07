extends Spatial

onready var anchor = preload("res://objects/Anchor.tscn")

var ancore=[]
var http

func _ready():
	pass

func make_req():
	
	http=HTTPRequest.new()
	add_child(http)
	#http.set_use_threads(true)
	#http.set_download_chunk_size(100000000)
	http.connect("request_completed", self, "_http_request_completed")
	var test=http.request("http://localhost:5000/get_anchor_pos")
	#print(test)

func _http_request_completed(result, response_code, headers, body):
	print("ok")
	var response = parse_json(body.get_string_from_utf8().replace("(","").replace(")",""))

	if response["status"]=="drone correctly connected":
		response.erase("status")
		for i in response.keys():
			var objAnchor = anchor.instance()
			add_child(objAnchor)
			objAnchor.updateLabel("Anchor "+str(i))
			ancore.append(objAnchor)
			
			objAnchor.global_transform.origin.x=float(response[i]["pos"].split(",")[0])
			objAnchor.global_transform.origin.y=float(response[i]["pos"].split(",")[2])
			objAnchor.global_transform.origin.z=float(response[i]["pos"].split(",")[1]) * -1
			
			print(i," ",float(response[str(i)]["pos"].split(",")[0])," ",float(response[str(i)]["pos"].split(",")[1])," ",float(response[str(i)]["pos"].split(",")[2]))
		
		get_tree().get_root().remove_child(get_tree().get_root().get_node("Loading_screen"))
	else:
		http.request("http://localhost:5000/get_anchor_pos")
