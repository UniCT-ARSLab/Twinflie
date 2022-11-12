extends Control
 
onready var input_drone = preload("res://objects/gui/input_url.tscn")



func _ready():
	
	pass # Replace with function body.


func _on_Button_pressed():
	GuiManager.hide_point_menu()
	GuiManager.hideDroneSelected()
	
	add_child(input_drone.instance())
	
	pass # Replace with function body.
