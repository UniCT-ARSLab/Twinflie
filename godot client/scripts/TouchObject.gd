extends Spatial

class_name TouchObject


#export var pathColor:Color = Color.red
export var active:bool = true
export var objectName = "No Name"

onready var outline = $Path/PathFollow/Mesh/Outline
onready var upper_lay= $Path/PathFollow/Viewport/drone_upper_lay
onready var sprite3d = $Path/PathFollow/Sprite3D
onready var gizmoTool = $Path/PathFollow/GizmoTool
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

var passed_point=[]

var playing=false
var waiting=0
var speed = 1
var wait_meeting=false
var selected:bool = false
var waiting_list=[]

var sync_timer=10
var sync_flag=false
var counter_point=0

func _process(delta):
	
	if not sync_flag:
		if sync_timer>0 :
			sync_timer=sync_timer-delta
		elif sync_timer>-0.1:
			self.sync_pos()
			sync_flag=true
			
	var pos=Vector3(pos_x,pos_y,pos_z)
		
	self.fantasma.global_transform= self.fantasma.global_transform.interpolate_with(Transform(Vector3(1,0,0),Vector3(0,1,0),Vector3(0,0,1),pos),delta)

	if udp.get_available_packet_count()>0:
		
		var array_bytes = udp.get_packet()
		dict=JSON.parse(array_bytes.get_string_from_ascii().replace("'",'"').replace("(","").replace(")","")).result
		
		if dict[objectName]["status"]!="connected":
			print ("remove self")
			get_parent().remove_child(self)
			GuiManager.create_alert(self.objectName+"cannot be reached","error on"+self.objectName)
			
		pos_x=float(dict[objectName]["position"].split(",")[0])
		pos_y=float(dict[objectName]["position"].split(",")[2])
		pos_z=float(dict[objectName]["position"].split(",")[1])*-1
		
		#print(float(dict[objectName]["battery"])*1000)
		upper_lay.set_battery_value(float(dict[objectName]["battery"])*1000)
		
	if self.waiting>0:
		waiting-=delta
		return
		
	if self.wait_meeting:
		for elem in self.waiting_list:
				if not elem[0] in elem[1].passed_point:
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
		#self.realPathFollow.look_at(self.pathLine.getAllPoints()[self.iter].global_transform.origin,self.pathLine.getAllPoints()[self.iter].global_transform.origin)
		self.realPathFollow.rotation_degrees.x=0
		self.realPathFollow.rotation_degrees.z=0
		
		if(self.dist>=self.item.global_transform.origin.distance_to(self.pathLine.getAllPoints()[self.iter].global_transform.origin)):
			self.dist=self.item.global_transform.origin.distance_to(self.pathLine.getAllPoints()[self.iter].global_transform.origin)
		else:
			self.passed_point.append(self.pathLine.getAllPoints()[self.iter])
			#if(self.pathLine.getAllPoints()[self.iter].type=="base"):
				#print("base")
			
			#if(self.pathLine.getAllPoints()[self.iter].type=="takeoff"):
				#print("takeoff")
			
			#if(self.pathLine.getAllPoints()[self.iter].type=="landing"):
				#print("landing")
			
			if(self.pathLine.getAllPoints()[self.iter].type=="waiting"):
				self.waiting=self.pathLine.getAllPoints()[self.iter].time
				#print("waiting")
			
			if(self.pathLine.getAllPoints()[self.iter].type=="spinning"):
				self.spinning=self.realPathFollow.rotation_degrees.y
				self.state_spinning=true
				#print("spinning")
			
			if(self.pathLine.getAllPoints()[self.iter].type=="meeting"):
				
				for drone in get_tree().get_nodes_in_group("TouchObjects"):
					if !drone.is_in_group("TouchPoints"):
						if drone.playing and drone!=self:
							for point in drone.pathLine.getAllPoints():
								if point.type=="meeting" and point.name_meeting==self.pathLine.getAllPoints()[self.iter].name_meeting:
									self.waiting_list.append([point,drone])
									if !self.wait_meeting:
										self.wait_meeting=true
										
			
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
	#objectName="drone_"+str(DroneManager.num)
	self.pathLine.addPoint(self.global_transform.origin)
	self.upper_lay.set_drone_name(objectName)
	udp.set_dest_address("127.0.0.1", 20003)
	udp.put_packet("subscribe".to_ascii())
	
	udp.wait()
	
	var array_bytes = udp.get_packet()
	dict=JSON.parse(array_bytes.get_string_from_ascii().replace("'",'"').replace("(","").replace(")","")).result
	#print("dizionario")
	#print(dict)
	pos_x=float(dict[objectName]["position"].split(",")[0])
	pos_y=float(dict[objectName]["position"].split(",")[2])
	pos_z=float(dict[objectName]["position"].split(",")[1])*-1
	
	self.global_transform.origin.x=pos_x
	self.global_transform.origin.y=pos_y
	self.global_transform.origin.z=pos_z
	
	sync_timer=10

func set_objectName(name):
	
	self.objectName=name

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
	
	
func generate_route():
	var punti=pathLine.getAllPoints()
	
	var json={}
	json[objectName]=[]
	var i=0
	for punto in punti:
		
		var point_origin=punto.global_transform.origin
		point_origin.z=point_origin.z*-1
		json[objectName].append({"name":"punto_"+str(i),"coordinate":(point_origin),"type":punto.type,"meeting_name":punto.name_meeting,"pause_time":punto.time})
		
		i+=1
	#print(json)
	return json
	
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


func sync_pos():

	self.realPathFollow.global_transform.origin=self.fantasma.global_transform.origin
	
	pathLine.getAllPoints()[0].global_transform.origin=self.realPathFollow.global_transform.origin
	
	"""
	self.realPathFollow.global_transform.origin.x=pos_x
	self.realPathFollow.global_transform.origin.y=pos_y
	self.realPathFollow.global_transform.origin.z=pos_z"""
	
	
	
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
	self.passed_point=[]
	self.waiting_list=[]
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
	print("collisione")
	if self.playing:
		print("collisione2")
		
		DroneManager.emit_signal("drone_collided")
	
	pass # Replace with function body.

func import_route(route):
	
	var json=JSON.parse(route).result
	self.get_node("PathLine").clearPoints()
	for point in json[self.objectName]:
		
		if point["name"]=="punto_0":
			continue
			
		var cord=point["coordinate"]
		#print(cord)
		cord=cord.replace("(","").replace(")","").replace(" ","")
		cord=cord.split(",")
		#print(typeof(cord[0]))
		
		self.pathLine.copy_point(Vector3(float(cord[0]),float(cord[1]),float(cord[2])*-1))
		
		
		self.pathLine.getLastPoint().type=point["type"]
		self.pathLine.getLastPoint().time=point["pause_time"]
		self.pathLine.getLastPoint().name_meeting=point["meeting_name"]
		
	pass
	

