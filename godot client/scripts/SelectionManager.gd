extends Node

signal objectSelected (obj)
signal pointSelected (obj)

var objectSelected  = null
var pointSelected  = null
var canPlacePoints : bool = false

#questo oggetto gestira il drone o il punto selezionato

# Called when the node enters the scene tree for the first time.
func _ready():
	
	self.connect("objectSelected", self, "on_object_selected")
	self.connect("pointSelected", self, "on_point_selected")
	pass # Replace with function body.


func on_object_selected(obj):
	objectSelected = obj
	for object in get_tree().get_nodes_in_group("TouchObjects"):
		if object != obj :
			object.deselectObject();
			
	GuiManager.hide_point_menu()
	GuiManager.showDroneSelected(objectSelected)
	objectSelected.selectObject();
	
func on_point_selected(obj):
	pointSelected = obj
	for object in get_tree().get_nodes_in_group("TouchPoints"):
		if object != obj :
			object.deselectObject();
			
	GuiManager.hide_point_menu()
	GuiManager.show_point_menu(pointSelected)
	pointSelected.selectObject();



# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
