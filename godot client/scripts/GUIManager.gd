extends Node

#questo oggetto gestira la GUI della simulazione nelle aperture dei vari menu.

onready var GUI_CONTAINER = get_tree().get_current_scene().get_node("GUIContainer")


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

func showDroneSelected(drone):
	self.GUI_CONTAINER.get_node("DroneSelected").openObject(drone)
	
func hideDroneSelected():
	GUI_CONTAINER.get_node("DroneSelected").closeObject()

#da questa chiamata verra mostrata la schermata per l'aggiunta dei punti 
func showAddingPointsMenu(drone):
	self.GUI_CONTAINER.get_node("AddingPointMenu").openObject(drone)
	
func hideAddingPointsMenu():
	GUI_CONTAINER.get_node("AddingPointMenu").closeObject()

func show_point_menu(point):
	GUI_CONTAINER.get_node("point menu").closeObject()
	self.GUI_CONTAINER.get_node("point menu").openObject(point)
	
func hide_point_menu():
	GUI_CONTAINER.get_node("point menu").closeObject()



func hideBottomMenu():
	GUI_CONTAINER.get_node("MainMenu").visible = false
	
func showBottomMenu():
	GUI_CONTAINER.get_node("MainMenu").visible = true
	
	
