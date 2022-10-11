extends Spatial

class_name NetworkDrone

signal object_collided

#export var pathColor:Color = Color.red
export var active:bool = true
export var objectName = "No Name"

onready var outline = $Path/PathFollow/Mesh/Outline
onready var label = $Viewport/Panel/HBoxContainer/Label
onready var sprite3d = $Sprite3D
onready var pathLine = $PathLine
onready var realPath = $Path
onready var realPathFollow = $Path/PathFollow

var lastPosition

var speed = 0
var selected:bool = false


func _ready():
	self.pathLine.addPoint(self.global_transform.origin)
	self.label.text = objectName

func _process(delta):
	self.global_transform.origin = self.global_transform.origin.linear_interpolate(lastPosition, delta)
	
func addPathPoint(point):
	self.pathLine.addPoint(point)
	
func addTakeoffPoint(altitude):
	self.pathLine.addTakeOffPoint(altitude)
	
func addLandingPoint():
	self.pathLine.addLandingPoint()

func getLastPathPoint():
	return self.pathLine.getLastPoint()
	
func generatePath():
	var _curve = Curve3D.new()
	for pointNode in self.pathLine.getAllPoints():
		_curve.add_point(pointNode.transform.origin)
	self.realPath.set_curve(_curve)
	
func offsetPath(offset):
	self.realPathFollow.offset = offset
		
func getRealPath():
	return self.realPath

func move(x, y, z):
	lastPosition = Vector3(x, z, y)

func _on_CollisionArea_area_entered(area):
	self.emit_signal("object_collided")
	pass # Replace with function body.
