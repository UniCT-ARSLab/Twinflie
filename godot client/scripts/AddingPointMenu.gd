extends Control

#questa è la Gui per aggiungere i i punti del percorso viene attivata dal gui menager

onready var labelName = $VBoxContainer/PanelContainer/VBoxContainer/DroneName
var objectSelected:Node = null

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.
	
func _process(delta):
	if self.get_rect().has_point(get_viewport().get_mouse_position()):
		SelectionManager.canPlacePoints = false
	else:
		SelectionManager.canPlacePoints = true
	#print(get_viewport().get_mouse_position())
	
	#var mouse = get_viewport().get_mouse_position()


#qunado viene premuto il tasto add point dopo aver selezionato un drone viene reso visibile questo menu
func openObject(object):
	self.objectSelected = object
	self.labelName.text = object.objectName
	self.visible = true;

#questo verra chiamato dal gui menager alla fine dell'inserimento dei punti
func closeObject():
	self.visible = false;


#queste righe non ho capito che fanno
#func _on_Add_Points_pressed():
	#SceneManager.changeState(SceneManager.STATES.selection)



func _on_DeletePoint_pressed():
	self.objectSelected.get_node("PathLine").removeLastNode()

func _on_ClearPoints_pressed():
	self.objectSelected.get_node("PathLine").clearPoints()

func _on_SavePoints_pressed():
	SelectionManager.objectSelected.get_node("PathLine").clearGhost()
	SceneManager.changeState(SceneManager.STATES.selection)

func _on_TakeoffPoint_pressed():
	self.objectSelected.addTakeoffPoint($VBoxContainer/PanelContainer/VBoxContainer/HBoxContainer/SpinBox.value)


func _on_LandingPoint_pressed():
	self.objectSelected.addLandingPoint()


func _on_AddingPointMenu_gui_input(event):
	print(event)
	pass # Replace with function body.


func _on_LandingPoint2_pressed():
	self.objectSelected.get_node("PathLine")
	pass # Replace with function body.


func _on_spinningpoint_pressed():
	self.objectSelected.addspinningpoint()


func _on_waitingpoint_pressed():
	print("adding waitng")
	self.objectSelected.addwaitingpoint($VBoxContainer/PanelContainer/VBoxContainer/HBoxContainer2/SpinBox.value)
