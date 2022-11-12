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
	$VBoxContainer/PanelContainer/VBoxContainer/meeting_container/LineEdit.text=self.objectSelected.name_meeting
	
	if(self.objectSelected.time==null):
		$VBoxContainer/PanelContainer/VBoxContainer/waiting_container/SpinBox.value=1
	else:
		$VBoxContainer/PanelContainer/VBoxContainer/waiting_container/SpinBox.value=self.objectSelected.time
	
	show_base_settings()
	
	for tipo in ["waiting","meeting","spinning"]:
		pass
	
	if object.type=="waiting":
		show_waiting_settings()
		
	if object.type=="meeting":
		show_meeting_settings()
	if object.type=="spinning":
		show_spinning_settings()
		
	$VBoxContainer/PanelContainer/VBoxContainer/meeting_container/LineEdit.text=self.objectSelected.name_meeting

	
	#$VBoxContainer/PanelContainer/VBoxContainer/Label.text+=" __"+self.objectSelected.type+"__  "
	print(self.objectSelected.global_transform.origin.x)
	self.visible = true;
	
	

#questo verra chiamato dal gui menager alla fine dell'inserimento dei punti
func closeObject():
	self.visible = false;

func _on_Button_x_pressed():
	self.objectSelected.global_transform.origin.x=$VBoxContainer/PanelContainer/VBoxContainer/HBoxContainer/SpinBox.value
	
func _on_Button_y_pressed():
	self.objectSelected.global_transform.origin.y=$VBoxContainer/PanelContainer/VBoxContainer/HBoxContainer2/SpinBox.value
	
func _on_Button_z_pressed():
	self.objectSelected.global_transform.origin.z=$VBoxContainer/PanelContainer/VBoxContainer/HBoxContainer3/SpinBox.value

func show_base_settings():
	
	$VBoxContainer/PanelContainer/VBoxContainer/meeting_container.visible=false
	$VBoxContainer/PanelContainer/VBoxContainer/waiting_container.visible=false

	$VBoxContainer/PanelContainer/VBoxContainer/check_waiting.set_pressed_no_signal(false)
	$VBoxContainer/PanelContainer/VBoxContainer/check_spinning.set_pressed_no_signal(false)
	$VBoxContainer/PanelContainer/VBoxContainer/check_meeting.set_pressed_no_signal(false)
	

	$VBoxContainer/PanelContainer/VBoxContainer/check_waiting.disabled=false
	$VBoxContainer/PanelContainer/VBoxContainer/check_spinning.disabled=false
	$VBoxContainer/PanelContainer/VBoxContainer/check_meeting.disabled=false

func show_meeting_settings():
	
	$VBoxContainer/PanelContainer/VBoxContainer/check_meeting.set_pressed_no_signal(true)
#	$VBoxContainer/PanelContainer/VBoxContainer/check_spinning.set_pressed_no_signal(false)
#	$VBoxContainer/PanelContainer/VBoxContainer/check_waiting.set_pressed_no_signal(false)
		
	$VBoxContainer/PanelContainer/VBoxContainer/check_waiting.disabled=true
	$VBoxContainer/PanelContainer/VBoxContainer/check_spinning.disabled=true
	$VBoxContainer/PanelContainer/VBoxContainer/check_meeting.disabled=false
		
	$VBoxContainer/PanelContainer/VBoxContainer/waiting_container.visible=false
	$VBoxContainer/PanelContainer/VBoxContainer/meeting_container.visible=true

func show_spinning_settings():
	
	$VBoxContainer/PanelContainer/VBoxContainer/check_spinning.set_pressed_no_signal(true)
	$VBoxContainer/PanelContainer/VBoxContainer/check_waiting.set_pressed_no_signal(false)
	$VBoxContainer/PanelContainer/VBoxContainer/check_meeting.set_pressed_no_signal(false)
		
	$VBoxContainer/PanelContainer/VBoxContainer/check_waiting.disabled=true
	$VBoxContainer/PanelContainer/VBoxContainer/check_spinning.disabled=false
	$VBoxContainer/PanelContainer/VBoxContainer/check_meeting.disabled=true
	
func show_waiting_settings():
	
	$VBoxContainer/PanelContainer/VBoxContainer/check_waiting.set_pressed_no_signal(true)
	$VBoxContainer/PanelContainer/VBoxContainer/check_spinning.set_pressed_no_signal(false)
	$VBoxContainer/PanelContainer/VBoxContainer/check_meeting.set_pressed_no_signal(false)
		
	$VBoxContainer/PanelContainer/VBoxContainer/check_waiting.disabled=false
	$VBoxContainer/PanelContainer/VBoxContainer/check_spinning.disabled=true
	$VBoxContainer/PanelContainer/VBoxContainer/check_meeting.disabled=true
		
	$VBoxContainer/PanelContainer/VBoxContainer/waiting_container.visible=true
	$VBoxContainer/PanelContainer/VBoxContainer/meeting_container.visible=false
		
		
func _on_check_waiting_toggled(button_pressed):
	if button_pressed:
		self.objectSelected.type="waiting"
		self.objectSelected.time=1
		show_waiting_settings()
		$VBoxContainer/PanelContainer/VBoxContainer/waiting_container/SpinBox.value=1
	else:
		self.objectSelected.type="base"
		self.objectSelected.time=null
		show_base_settings()


func _on_check_meeting_toggled(button_pressed):
	if button_pressed:
		self.objectSelected.type="meeting"
		show_meeting_settings()
	else:
		self.objectSelected.type="base"
		self.objectSelected.name_meeting=""
		show_base_settings()

func _on_check_spinning_toggled(button_pressed):
	if button_pressed:
		self.objectSelected.type="spinning"
		show_spinning_settings()
	else:
		self.objectSelected.type="base"
		show_base_settings()


func _on_LineEdit_meeting_text_changed(new_text):
	self.objectSelected.name_meeting=new_text

func _on_SpinBox_waiting_time_value_changed(value):
	self.objectSelected.time=value

func _on_SpinBox_x_value_changed(value):
	self.objectSelected.global_transform.origin.x=value

func _on_SpinBox_y_value_changed(value):
	self.objectSelected.global_transform.origin.y=value

func _on_SpinBox_value_changed(value):
	self.objectSelected.global_transform.origin.z=value
