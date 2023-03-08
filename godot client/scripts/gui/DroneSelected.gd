extends Control

onready var input_file = preload("res://objects/gui/input_file_name.tscn")
onready var input_file_import_nav = preload("res://objects/gui/input_file_name_import_nav.tscn")

onready var labelName = $VBoxContainer/PanelContainer/VBoxContainer/DroneName
var objectSelected:Node = null


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


func _on_syncronyze_position_pressed():
	self.objectSelected.sync_pos()
	pass # Replace with function body.





func _on_save_nav_pressed():
	
	get_tree().get_root().add_child(input_file.instance())
	
	pass # Replace with function body.


func _on_import_nav_pressed():
	get_tree().get_root().add_child(input_file_import_nav.instance())
	pass # Replace with function body.
