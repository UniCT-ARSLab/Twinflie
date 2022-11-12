extends Spatial

onready var outline = $Mesh/Outline
#onready var gizmoTool = $GizmoTool
onready var lineDrawer = $LineRenderer
onready var raycast = $RayCast
var selected:bool = false


var type
var time=null
var name_meeting=""

# Called when the node enters the scene tree for the first time.
func _ready():

	pass # Replace with function body.

func selectObject():
	self.outline.visible = true
	#self.gizmoTool.active = true
	#self.gizmoTool.visible = true
	$Mesh/Outline.visible=true
	print(self.type)
	if(self.time!=null):
		print(self.time)
	self.selected = true
	
func deselectObject():
	self.outline.visible = false
	#self.gizmoTool.active = false
	#self.gizmoTool.visible = false
	$Mesh/Outline.visible=false
	self.selected = false
	
func _on_Area_input_event(camera, event, click_position, click_normal, shape_idx):
	if event is InputEventMouseButton:
		if event.button_index == BUTTON_LEFT and !event.pressed and !self.selected :
			SelectionManager.emit_signal("pointSelected", self)
	if event is InputEventScreenTouch and !self.selected:
		if event.pressed :
			SelectionManager.emit_signal("pointSelected", self)

