extends Control


onready var labelName = $VBoxContainer/PanelContainer/VBoxContainer/DroneName
var objectSelected:Node = null

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


func openObject(object):
	self.objectSelected = object
	self.labelName.text = self.objectSelected.objectName
	self.visible = true;

func closeObject():
	self.visible = false;

func _on_Delete_pressed():
	self.objectSelected.get_parent().remove_child(self.objectSelected)
	self.objectSelected.queue_free()
	self.objectSelected = null
	self.closeObject()
	


func _on_Add_Points_pressed():
	SceneManager.changeState(SceneManager.STATES.adding)


func _on_EditPath_pressed():
	SceneManager.changeState(SceneManager.STATES.editing)


func _on_Deselect_pressed():
	self.objectSelected.deselectObject()
	self.closeObject()
	pass # Replace with function body.


func _on_Button_pressed():
	
	self.objectSelected.set_vel($VBoxContainer/PanelContainer/VBoxContainer/HBoxContainer/SpinBox.value)
	pass # Replace with function body.
