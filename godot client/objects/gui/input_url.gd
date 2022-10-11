extends Control


onready var text=$container/Panel/VBoxContainer/HBoxContainer/LineEdit


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass


func _on_Button_pressed():
	DroneManager.addDrone(text.text)
	
	get_parent().remove_child(self)
	
	pass # Replace with function body.


func _on_abort():
	
	get_parent().remove_child(self)
	
	pass # Replace with function body.
