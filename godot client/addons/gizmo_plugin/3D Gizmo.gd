extends Spatial

export var scaling = 200
export var active = true
var selected_object = null

onready var collisions = [
	$X_Rotate/StaticBody/CollisionShape,
	$X_Translate/StaticBody/CollisionShape,
	$Y_Rotate/StaticBody/CollisionShape,
	$Y_Translate/StaticBody2/CollisionShape,
	$Z_Rotate/StaticBody/CollisionShape,
	$Z_Translate/StaticBody2/CollisionShape
]

func _process(delta):
	return
	if get_viewport().get_camera() != null:
		var size = get_viewport().get_camera().size / scaling
		scale = Vector3(size, size, size)
		

func activeGizmo():
	self.active = true
	self.visible = true
	for collision in self.collisions:
		collision.disabled = false
		
func disableGizmo():
	self.active = false
	self.visible = false
	for collision in self.collisions:
		collision.disabled = true
