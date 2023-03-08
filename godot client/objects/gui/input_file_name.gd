extends Control


onready var text=$container/Panel/VBoxContainer/HBoxContainer/LineEdit


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


func _on_enter_name_pressed():
	
	var file=File.new()
	file.open(self.text.text,File.WRITE_READ)
	
	file.store_line(JSON.print(SelectionManager.objectSelected.generate_route()))
	file.close()
	
	get_parent().remove_child(self)
	


func _on_abort_pressed():	
	get_parent().remove_child(self)
	
