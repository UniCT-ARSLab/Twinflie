extends Node

enum STATES { selection, editing, adding }
export(STATES) var sceneState = STATES.selection


#questo oggetto gestisce le 3 modalita con cui si puo interaggire con la simulazione, quando la modalita combia
#questo oggetto cambiera la camera e l'interazione con il mouse ed eseguira le adeguate chiamate al GUImenger per
#cambiare la GUI visualizzata

onready var camera : Camera = get_tree().get_current_scene().get_node("Camera")
onready var topCamera : Camera = get_tree().get_current_scene().get_node("TopCamera")
onready var mousePointer = get_tree().get_current_scene().get_node("MousePointer")
# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

func changeState(state):
	self.sceneState = state
	match state:
		STATES.selection:
			self.selectionState()
		STATES.editing:
			self.editingState()
		STATES.adding:
			self.addingState()

func selectionState():
	self.camera.make_current()
	self.mousePointer.setCamera(self.camera)
	GuiManager.showBottomMenu()
	
	for object in get_tree().get_nodes_in_group("TouchObjects"):
		if !object.is_in_group("TouchPoints"):
			object.enableObject()
	SelectionManager.objectSelected.enableObject()
	SelectionManager.objectSelected.selectObject()
	GuiManager.hideAddingPointsMenu()
	GuiManager.showBottomMenu()
	pass
	
func editingState():
	pass
		
func addingState():
	self.topCamera.make_current()
	self.mousePointer.setCamera(self.topCamera)
	for object in get_tree().get_nodes_in_group("TouchObjects"):
		if !object.is_in_group("TouchPoints"):
			object.disableObject()
	SelectionManager.objectSelected.disableObject()
	GuiManager.hideBottomMenu()
	GuiManager.hide_point_menu()
	GuiManager.hideDroneSelected()
	GuiManager.showAddingPointsMenu(SelectionManager.objectSelected)
	pass
