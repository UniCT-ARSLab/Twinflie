extends Control


# Declare member variables here. Examples:
# var a = 2
# var b = "text"


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


func set_drone_name(value):
	$VBoxContainer/Label.text=value


func set_battery_value(value):
	$VBoxContainer/ProgressBar.value=value


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
