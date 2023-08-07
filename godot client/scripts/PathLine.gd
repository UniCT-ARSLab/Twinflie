extends Spatial


onready var points = $Points
onready var lineDrawer = $LineRenderer
onready var lineDrawerGhost = $LineRendererGhost

onready var pointScene = preload("res://objects/PathPoint.tscn")
var counter_point=0

# Called when the node enters the scene tree for the first time.
func _ready():
	self.lineDrawer.points.clear()
	self.lineDrawerGhost.points.clear()
	self.renderLine()
	
func renderLine():
	self.lineDrawer.points.clear()
	for point in self.points.get_children():
		self.lineDrawer.points.append(point.global_transform.origin)
	self.lineDrawerGhost.render()
	self.lineDrawer.render()
	
func renderGhostLine(pointer):
	self.lineDrawerGhost.points.clear()
	var startPoint:Node = self.getLastPoint()
	self.lineDrawerGhost.points.append(startPoint.global_transform.origin)
	self.lineDrawerGhost.points.append(pointer)
	self.lineDrawerGhost.render()

func clearGhostLine():
	self.lineDrawerGhost.points.clear()
	self.lineDrawerGhost.clearLine()
	self.lineDrawerGhost.render()
	
	
func clearPoints():
	self.counter_point=0
	var first = self.lineDrawer.points.pop_front()
	self.lineDrawerGhost.points.clear()
	self.lineDrawer.points.clear()
	for n in self.points.get_children():
		self.points.remove_child(n)
		n.queue_free()
	self.lineDrawerGhost.clearLine()
	self.lineDrawer.clearLine()
	self.addPoint(first)
	
	self.getAllPoints()[0].global_transform.origin=get_parent().realPathFollow.global_transform.origin
	

func makeTransparent():
	var material = SpatialMaterial.new()
	material.albedo_color = Color8(117, 117, 117, 120)
	material.flags_unshaded = true
	material.flags_transparent = true
	self.lineDrawer.set_material_override(material)
	self.points.visible = false
	pass

func makeVisisble():
	var material = SpatialMaterial.new()
	material.albedo_color = Color8(107, 220, 21, 255)
	material.flags_unshaded = true
	self.lineDrawer.set_material_override(material)
	self.points.visible = true
	pass
	
func addPoint(coords):
	var newPoint = self.pointScene.instance()
	var prevNode = self.getLastPoint()
	self.points.add_child(newPoint)
	if prevNode != null:
		newPoint.global_transform.origin = Vector3(coords.x, prevNode.global_transform.origin.y, coords.z)	
	else:
		newPoint.global_transform.origin = Vector3(coords.x, get_parent().global_transform.origin.y, coords.z)	
	newPoint.type="base"
	newPoint.type="meeting"
	newPoint.name_meeting="Meet_"+str(self.counter_point)
	self.counter_point+=1
	
	newPoint.deselectObject()
	
	self.renderLine()

func copy_point(coords):
	var newPoint = self.pointScene.instance()
	var prevNode = self.getLastPoint()
	self.points.add_child(newPoint)
	newPoint.global_transform.origin = Vector3(coords.x,coords.y, coords.z)	
	newPoint.type="base"
	newPoint.deselectObject()
	self.renderLine()



func addspinningpoint():
	var prevNode = self.getLastPoint()
	prevNode.type="spinning"
	self.renderLine()

func addwaitingpoint(time):
	var prevNode = self.getLastPoint()
	print("pathline waitng")
	prevNode.time=time
	prevNode.type="waiting"
	self.renderLine()


func addTakeOffPoint(altitude):
	var newPoint = self.pointScene.instance()
	var prevNode = self.getLastPoint()
	self.points.add_child(newPoint)
	var coords = prevNode.global_transform.origin
	coords.y += altitude
	newPoint.global_transform.origin = coords
	newPoint.type="takeoff"
	newPoint.deselectObject()
	self.renderLine()
	
func addLandingPoint():
	var newPoint = self.pointScene.instance()
	var prevNode = self.getLastPoint()
	self.points.add_child(newPoint)
	var ray : RayCast = prevNode.get_node("RayCast")
	ray.enabled = true
	ray.force_raycast_update()
	var point = ray.get_collision_point()
	var floorPoint : Spatial = get_parent().get_node("FloorPoint")
	point.y -= floorPoint.translation.y
	newPoint.type="landing"
	newPoint.global_transform.origin = point
	newPoint.deselectObject()
	ray.enabled = false
	self.renderLine()
	
	
func removeLastNode():
	if self.points.get_child_count() < 2:
		return
	self.lineDrawer.points.pop_back()
	var node = self.points.get_child(self.points.get_child_count() - 1)
	self.points.remove_child(node)
	self.counter_point-=1
	self.renderLine()
	node.queue_free()
	
func clearGhost():
	self.lineDrawerGhost.clearLine()
	self.lineDrawerGhost.points.clear()
	
func getLastPoint():
	if self.points.get_child_count() > 0:
		return self.points.get_child(self.points.get_child_count() - 1)
	else:
		 return null
	
func getAllPoints():
	return self.points.get_children()
	
func _process(delta):
	#rallentare
	self.renderLine()
