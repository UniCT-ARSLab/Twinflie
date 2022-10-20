extends Spatial

class_name TouchObject

signal object_collided

#export var pathColor:Color = Color.red
export var active:bool = true
export var objectName = "No Name"

onready var outline = $Path/PathFollow/Mesh/Outline
onready var label = $Viewport/Panel/HBoxContainer/Label
onready var sprite3d = $Sprite3D
onready var gizmoTool = $GizmoTool
onready var pathLine = $PathLine
onready var realPath = $Path
onready var realPathFollow = $Path/PathFollow
onready var item=$Path/PathFollow/Area
onready var mesh=$Path/PathFollow/Mesh
onready var fantasma=$Fantasma


var extimated_pos_x=0
var extimated_pos_y=0
var extimated_pos_z=0

var udp := PacketPeerUDP.new()
var connected = false

var dict
var pos_x=0
var pos_y=0
var pos_z=0

var dist=100
var iter=1
var count=0
var spinning=0
var state_spinning=false
var current_rotation=0

var playing=false
var waiting=0
var speed = 1

var selected:bool = false

func _process(delta):
	
	var pos=Vector3(pos_x,pos_y,pos_z)
		
	self.fantasma.global_transform= self.fantasma.global_transform.interpolate_with(Transform(Vector3(1,0,0),Vector3(0,1,0),Vector3(0,0,1),pos),delta)


	
	if udp.get_available_packet_count()>0:
		var array_bytes = udp.get_packet()
		dict=JSON.parse(array_bytes.get_string_from_ascii().replace("'",'"').replace("(","").replace(")","")).result
		
		pos_x=float(dict["drone_0"].split(",")[0])
		pos_y=float(dict["drone_0"].split(",")[2])
		pos_z=float(dict["drone_0"].split(",")[1])
		
		
		
	if self.waiting>0:
		waiting-=delta
		return
	if state_spinning and current_rotation<360:
		current_rotation+=1
		self.realPathFollow.rotation_degrees.y+=1
		return
		
	if current_rotation==360:
		current_rotation=0
		self.state_spinning=false
		return
	if self.playing:
		if(self.iter==self.pathLine.getAllPoints().size()):
			self.playing=false
			return
	
		self.realPathFollow.offset += delta*self.speed
		self.realPathFollow.look_at(self.pathLine.getAllPoints()[self.iter].global_transform.origin,self.pathLine.getAllPoints()[self.iter].global_transform.origin)
		self.realPathFollow.rotation_degrees.x=0
		self.realPathFollow.rotation_degrees.z=0
		
		if(self.dist>=self.item.global_transform.origin.distance_to(self.pathLine.getAllPoints()[self.iter].global_transform.origin)):
			self.dist=self.item.global_transform.origin.distance_to(self.pathLine.getAllPoints()[self.iter].global_transform.origin)
		else:
			if(self.pathLine.getAllPoints()[self.iter].type=="base"):
				print("base")
			
			if(self.pathLine.getAllPoints()[self.iter].type=="takeoff"):
				print("takeoff")
			
			if(self.pathLine.getAllPoints()[self.iter].type=="landing"):
				print("landing")
			
			if(self.pathLine.getAllPoints()[self.iter].type=="waiting"):
				self.waiting=self.pathLine.getAllPoints()[self.iter].time
				print("waiting")
			
			if(self.pathLine.getAllPoints()[self.iter].type=="spinning"):
				self.spinning=self.realPathFollow.rotation_degrees.y
				self.state_spinning=true
				print("spinning")
			
			self.iter=self.iter+1
			self.dist=100
		
	

		"""
		self.global_transform.origin.x=pos_x
		self.global_transform.origin.y=pos_y
		self.global_transform.origin.z=pos_z"""
	
		
		"""self.realPathFollow.global_transform.origin.x=pos_x
		self.realPathFollow.global_transform.origin.y=pos_y
		self.realPathFollow.global_transform.origin.z=pos_z"""
		
		
func _ready():
	print("drone")
	self.pathLine.addPoint(self.global_transform.origin)
	self.label.text = objectName
	udp.set_dest_address("127.0.0.1", 20003)
	udp.put_packet("subscribe".to_ascii())
	
	udp.wait()
	
	var array_bytes = udp.get_packet()
	dict=JSON.parse(array_bytes.get_string_from_ascii().replace("'",'"').replace("(","").replace(")","")).result
	print(dict)
	pos_x=float(dict["drone_0"].split(",")[0])
	pos_y=float(dict["drone_0"].split(",")[2])
	pos_z=float(dict["drone_0"].split(",")[1])

	self.global_transform.origin.x=pos_x
	self.global_transform.origin.y=pos_y
	self.global_transform.origin.z=pos_z
	



func selectObject():
	#self.pathLine.visible = true
	self.pathLine.makeVisisble()
	self.outline.visible = true
	self.gizmoTool.activeGizmo()
	self.selected = true
	
func deselectObject():
	#self.pathLine.visible = false
	self.pathLine.makeTransparent()
	self.outline.visible = false
	self.gizmoTool.disableGizmo()
	self.selected = false
	
	
	
func addPathPoint(point):
	self.pathLine.addPoint(point)
	
func addTakeoffPoint(altitude):
	self.pathLine.addTakeOffPoint(altitude)
	
func addLandingPoint():
	self.pathLine.addLandingPoint()

func getLastPathPoint():
	return self.pathLine.getLastPoint()

func addspinningpoint():
	return self.pathLine.addspinningpoint()
	
func addwaitingpoint(time):
	print("obj waiting")
	return self.pathLine.addwaitingpoint(time)




func disableObject():
	self.active = false
	self.gizmoTool.disableGizmo()
	self.get_node("Path/PathFollow/Area/CollisionShape").disabled = true
	
func enableObject():
	self.active = true
	self.get_node("Path/PathFollow/Area/CollisionShape").disabled = false
	
func generatePath():
	var _curve = Curve3D.new()
	for pointNode in self.pathLine.getAllPoints():
		_curve.add_point(pointNode.transform.origin)
		
	self.dist=100
	self.iter=1
	self.realPath.set_curve(_curve)
	self.playing=true
	self.waiting=0
	#self.realPathFollow.set_rotation_mode(PathFollow.ROTATION_XYZ)
	

	
	
		
func getRealPath():
	return self.realPath
	
func get_offset(): 
	return self.realPathFollow.offset

func set_offset(offset): 
	self.realPathFollow.offset=offset
	
func _on_Area_input_event(camera, event, click_position, click_normal, shape_idx):
	if self.active:
		if event is InputEventMouseButton:
			if event.button_index == BUTTON_LEFT and !event.pressed and !self.selected :
				SelectionManager.emit_signal("objectSelected", self)
		if event is InputEventScreenTouch and !self.selected:
			if event.pressed :
				SelectionManager.emit_signal("objectSelected", self)

func _on_Area_mouse_entered():
	SelectionManager.canPlacePoints = false
	sprite3d.visible = true

func _on_Area_mouse_exited():
	SelectionManager.canPlacePoints = true
	sprite3d.visible = false

func set_vel(new_vel):
	self.speed=new_vel

func _on_CollisionArea_area_entered(area):
	self.emit_signal("object_collided")
	pass # Replace with function body.
