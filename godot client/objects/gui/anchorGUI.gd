extends Control

var objectSelected=null

func _ready():
	pass # Replace with function body.

func openObject(object):
	self.objectSelected = object
	
	$VBoxContainer/PanelContainer/VBoxContainer/HBoxContainer/Label.text= self.objectSelected.get_name() + "settings"
	
	$VBoxContainer/PanelContainer/VBoxContainer/"x settings"/SpinBox.value=self.objectSelected.global_transform.origin.x
	$VBoxContainer/PanelContainer/VBoxContainer/"y settings"/SpinBox.value=self.objectSelected.global_transform.origin.y
	$VBoxContainer/PanelContainer/VBoxContainer/"z settings"/SpinBox.value=self.objectSelected.global_transform.origin.z

	self.visible = true;
	
	
func closeObject():
	self.visible = false;



func _on_Button_x_pressed():
	self.objectSelected.global_transform.origin.x=$VBoxContainer/PanelContainer/VBoxContainer/"x settings"/SpinBox.value
	
func _on_Button_y_pressed():
	self.objectSelected.global_transform.origin.y=$VBoxContainer/PanelContainer/VBoxContainer/"y settings"/SpinBox.value
	
func _on_Button_z_pressed():
	self.objectSelected.global_transform.origin.z=$VBoxContainer/PanelContainer/VBoxContainer/"z settings"/SpinBox.value


func _on_SpinBox_x_value_changed(value):
	self.objectSelected.global_transform.origin.x=value

func _on_SpinBox_y_value_changed(value):
	self.objectSelected.global_transform.origin.y=value

func _on_SpinBox_z_value_changed(value):
	self.objectSelected.global_transform.origin.z=value



func _on_abort_pressed():
	GuiManager.hide_anchor_menu()
