extends Control


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
var objectSelected=null

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


func openObject(object):
	self.objectSelected = object
	$VBoxContainer/PanelContainer/VBoxContainer/HBoxContainer/SpinBox.value=self.objectSelected.global_transform.origin.x
	$VBoxContainer/PanelContainer/VBoxContainer/HBoxContainer2/SpinBox.value=self.objectSelected.global_transform.origin.y
	$VBoxContainer/PanelContainer/VBoxContainer/HBoxContainer3/SpinBox.value=self.objectSelected.global_transform.origin.z
	
	$VBoxContainer/PanelContainer/VBoxContainer/VBoxContainer2/LineEdit.text=self.objectSelected.name_meeting

	#$VBoxContainer/PanelContainer/VBoxContainer/Label.text+=" __"+self.objectSelected.type+"__  "
	print(self.objectSelected.global_transform.origin.x)
	self.visible = true;
	
	

#questo verra chiamato dal gui menager alla fine dell'inserimento dei punti
func closeObject():
	self.visible = false;


func _on_Button_add_meeting_point_pressed():
	
	if(self.objectSelected.type=="base"):
		self.objectSelected.type="meeting"
		self.objectSelected.name_meeting=$VBoxContainer/PanelContainer/VBoxContainer/VBoxContainer/LineEdit.text
	else:
		print("the selected node is not a base point")		


func _on_Button_x_pressed():
	self.objectSelected.global_transform.origin.x=$VBoxContainer/PanelContainer/VBoxContainer/HBoxContainer/SpinBox.value
	
	

func _on_Button_y_pressed():
	self.objectSelected.global_transform.origin.y=$VBoxContainer/PanelContainer/VBoxContainer/HBoxContainer2/SpinBox.value
	

func _on_Button_z_pressed():
	self.objectSelected.global_transform.origin.z=$VBoxContainer/PanelContainer/VBoxContainer/HBoxContainer3/SpinBox.value


func _on_Button_change_meeting_pressed():
	if(self.objectSelected.type!="meeting"):
		$VBoxContainer/PanelContainer/VBoxContainer/VBoxContainer2/LineEdit.text="not a meeting point"
		print("not a meeting point")
	else:
		self.objectSelected.name_meeting=$VBoxContainer/PanelContainer/VBoxContainer/VBoxContainer2/LineEdit.text
			


func _on_Button_set_time_pressed():
	if(self.objectSelected.type!="waiting"):
		
		print("it was not a waiting point")
		
#		if (self.objectSelected.type=="meeting"):
#			self.objectSelected.name_meeting=null
#			
#		self.objectSelected.type="waiting"
#		self.objectSelected.time=$VBoxContainer/PanelContainer/VBoxContainer/HBoxContainer4/SpinBox.value

	else:
		self.objectSelected.time=$VBoxContainer/PanelContainer/VBoxContainer/HBoxContainer4/SpinBox.value


func _on_Button_set_as_base_pressed():
	
	self.objectSelected.type="base"
	self.objectSelected.time=null
	self.objectSelected.name_meeting=null
	
	pass # Replace with function body.
