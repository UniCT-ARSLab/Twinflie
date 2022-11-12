extends Spatial

class_name MousePointer
export(NodePath) var objectsNodes
export(NodePath) var cameraPath

export var drawEnabled : bool = true
onready var camera = get_node(cameraPath)

#questo oggeto gestisce l'interazione tra il puntatore del mouse e la scena corrente valutando lo stato della scena

var http

var touchObjects
var point:Vector3
var oldPoint:Vector3
var dragging = false
var count = 0
var hit = null
var objectsFiltered = []

func _ready():
	touchObjects = get_node_or_null(objectsNodes)
	objectsFiltered = touchObjects.get_children()
	SelectionManager.connect("objectSelected",self, "on_object_selected")

func _physics_process(delta):
	_updateMousePosition()

func on_object_selected(obj):
	count = 0
	


func _input(event):
	if(event is InputEventMouseButton && event.button_index == 1 && event.pressed && !event.is_echo() && !dragging):
		if(hit != null and !hit.empty() && hit.collider.is_in_group("gizmo")):
			
				self.hit.collider.get_parent()._input_event(camera, event, self.hit.position, null, null)
				dragging = true
		else:
			if SelectionManager.objectSelected != null and SelectionManager.canPlacePoints :
				if SceneManager.sceneState == SceneManager.STATES.adding:
					#print("Metto un nuovo punto")
					if self.hit != null:
						GuiManager.hide_point_menu()
						SelectionManager.objectSelected.get_node("PathLine").addPoint(point)
			
			

	if(event is InputEventMouseButton && event.button_index == 1 && !event.pressed && !event.is_echo() && dragging):
		dragging = false
		
	

func _updateMousePosition():

	oldPoint = point
	var mouse = get_viewport().get_mouse_position()
	var from = camera.project_ray_origin(mouse)
	var to = from + camera.project_ray_normal(mouse) * 2000

	var space_state = get_world().get_direct_space_state()
	var hitted = space_state.intersect_ray(from, to, [objectsFiltered])
	self.hit = hitted
	if self.hit.size() != 0:
		point = self.hit.position
		self.set_translation(self.hit.position)
	else:
		self.hit = null
		
		
	if SceneManager.sceneState == SceneManager.STATES.adding and point != null and SelectionManager.canPlacePoints:
		SelectionManager.objectSelected.get_node("PathLine").renderGhostLine(point)
	elif SceneManager.sceneState == SceneManager.STATES.adding and point != null and !SelectionManager.canPlacePoints:
		SelectionManager.objectSelected.get_node("PathLine").clearGhostLine()


func setCamera(camera):
	self.camera = camera


func _on_reset_estimation_pressed():
	
	http=HTTPRequest.new()
	add_child(http)
	#http.set_use_threads(true)
	#http.set_download_chunk_size(100000000)
	http.connect("request_completed", self, "_http_request_completed")
	var test=http.request("http://localhost:5000/reset_estimation")
	#print(test)

func _http_request_completed(result, response_code, headers, body):
	print("ok")
