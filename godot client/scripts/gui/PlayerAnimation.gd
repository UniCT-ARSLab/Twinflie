extends Control

onready var slider = $VBoxContainer/HBoxContainer/Slider
onready var progress = $VBoxContainer/HBoxContainer/ProgressBar

var playing = false
var objects = null
var time = 0
var PathLenght = 0
var route={}

var http
var counter_time=0

# Called when the node enters the scene tree for the first time.
func _ready():
	objects = []
	DroneManager.connect("drone_collided", self, "_on_Drones_object_collided")
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.

func _process(delta):
	
	if self.playing:
		counter_time=counter_time+delta
		$VBoxContainer/HBoxContainer/LineEdit.text=str(counter_time)
		var offsetAmount=0
		for object in self.objects:
			offsetAmount+=object.get_offset()
			
		if offsetAmount >= self.PathLenght:
			
			end_simulation(true)
			
		for object in self.objects:
			if !self.playing:
				
				pass
			else:
				self.slider.value = offsetAmount
				self.progress.value = offsetAmount
				

func end_simulation(flag):
	self.playing = false
	self.time = 0
	self.slider.value = 0
	self.progress.value = 0
	for object in self.objects:
		if !self.playing:
			object.playing=false
			object.enableObject()
			if flag:
				object.set_offset(0)
			
	self.objects=[]
	
	
func _on_PlayButton_pressed():
	GuiManager.hide_point_menu()
	GuiManager.hideDroneSelected()
	var counter=0
	self.objects.empty()
	for object in get_tree().get_nodes_in_group("TouchObjects"):
		if !object.is_in_group("TouchPoints"):
			self.objects.append(object)
			
			var json =object.generate_route()
			route[object.objectName]=json[object.objectName]
			
			
			object.generatePath()
			object.deselectObject()
			object.disableObject()
			object.set_offset(0)
			var lenght = object.getRealPath().get_curve().get_baked_length()
			counter+=lenght
			#object.disableObject()
			
			
	var http=HTTPRequest.new()
	add_child(http)
			
	var headers = ["Content-Type: application/json"]
	http.request("http://localhost:5000/route", headers, false, HTTPClient.METHOD_POST, JSON.print(route))
	yield(http, "request_completed")
	remove_child(http)
					
	self.progress.set_max(counter)
	self.slider.set_max(counter)
	self.PathLenght=counter
	counter_time=0
	self.playing = true
	
	# Noogi was here.


func _on_Slider_value_changed(value):
	return
	for object in get_tree().get_nodes_in_group("TouchObjects"):
		if !object.is_in_group("TouchPoints"):
			object.generatePath()
			object.deselectObject()
			if self.PathLenght < object.getRealPath().get_curve().get_baked_length():
				self.PathLenght = object.getRealPath().get_curve().get_baked_length()
				self.progress.set_max(self.PathLenght)
				self.slider.set_max(self.PathLenght)
			object.offsetPath(value)




func _on_Drones_object_collided():
	
	end_simulation(false)
	print("collisioneanimation")
	
	pass # Replace with function body.



func _http_request_completed(result, response_code, headers, body):

	pass
	
func _on_Button_start_real_pressed():
	
	for object in get_tree().get_nodes_in_group("TouchObjects"):
		if !object.is_in_group("TouchPoints"):
			self.objects.append(object)
			
			var json =object.generate_route()
			route[object.objectName]=json[object.objectName]


	var http=HTTPRequest.new()
	add_child(http)
			
	var headers = ["Content-Type: application/json"]
	http.request("http://localhost:5000/route", headers, false, HTTPClient.METHOD_POST, JSON.print(route))
	yield(http, "request_completed")
	remove_child(http)
	
	http=HTTPRequest.new()
	add_child(http)
	http.connect("request_completed", self, "_http_request_completed")
	var test=http.request("http://localhost:5000/falli_partire")



func _on_set_floor_pressed():
	var my_y=1000
	
	for object in get_tree().get_nodes_in_group("TouchObjects"):
		if !object.is_in_group("TouchPoints"):
			object.sync_pos()
			if my_y>object.fantasma.global_transform.origin.y:
				my_y=object.fantasma.global_transform.origin.y
				
	get_tree().get_root().get_node("World/Floor").global_transform.origin.y=my_y-0.1
	
	
	pass # Replace with function body.


func _on_set_anchor_pressed():
	
	 
	
	var position={}
	
	for object in get_tree().get_nodes_in_group("anchor"):
		var id=object.label.text.replace("Anchor ","")
		position[id]={x=object.global_transform.origin.x,y=object.global_transform.origin.y,z=object.global_transform.origin.z*-1}
		
		object.deselectObject();
		
	print(position)
	
	var http=HTTPRequest.new()
	add_child(http)
	var headers = ["Content-Type: application/json"]
	print(JSON.print(route))
	http.request("http://localhost:5000/set_anchor_pos", headers, false, HTTPClient.METHOD_POST, JSON.print(position))
	yield(http, "request_completed")
	remove_child(http)
	


func _on_stop_test_pressed():
	end_simulation(false)
