extends Spatial


# Declare member variables here. Examples:
# var a = 2
# var b = "text"

onready var label = $Label
onready var selected=false


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

func selectObject():
	$Label.modulate=Color(0.730469, 0.014267, 0.014267)
	selected=true
	

func deselectObject():
	$Label.modulate=Color(1, 1, 1)
	selected=false
	
func updateLabel(lab):
	label.text = lab
	
func _on_Area_input_event(camera, event, click_position, click_normal, shape_idx):
	if event is InputEventMouseButton:
		if event.button_index == BUTTON_LEFT and !event.pressed and !self.selected :
			SelectionManager.emit_signal("anchorSelected", self)
	if event is InputEventScreenTouch and !self.selected:
		if event.pressed :
			SelectionManager.emit_signal("anchorSelected", self)
	

func get_name():
	return self.label.text

# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
