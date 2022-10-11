extends Control

onready var slider = $VBoxContainer/HBoxContainer/Slider
onready var progress = $VBoxContainer/HBoxContainer/ProgressBar

var playing = false
var objects = null
var time = 0
var PathLenght = 0

# Called when the node enters the scene tree for the first time.
func _ready():
	objects = []
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.

func _process(delta):
	
	if self.playing:
		
		var offsetAmount=0
		for object in self.objects:
			offsetAmount+=object.get_offset()
			
		if offsetAmount >= self.PathLenght:
			self.playing = false
			self.time = 0
			self.slider.value = 0
			self.progress.value = 0
			for object in self.objects:
				if !self.playing:
					object.set_offset(0)
					object.enableObject()
			self.objects=[]

		for object in self.objects:
			if !self.playing:
				pass
			else:
				self.slider.value = offsetAmount
				self.progress.value = offsetAmount
				


func _on_PlayButton_pressed():
	var counter=0
	for object in get_tree().get_nodes_in_group("TouchObjects"):
		if !object.is_in_group("TouchPoints"):
			self.objects.append(object)
			
			object.generatePath()
			object.deselectObject()
			object.disableObject()
			var lenght = object.getRealPath().get_curve().get_baked_length()
			counter+=lenght
			#object.disableObject()
	self.progress.set_max(counter)
	self.slider.set_max(counter)
	self.PathLenght=counter
	self.playing = true
	
	# Noogi was here.


func _on_Slider_value_changed(value):
	return
	for object in get_tree().get_nodes_in_group("TouchObjects"):
		if !object.is_in_group("TouchPoints"):
			object.generatePath()
			object.deselectObject()
			if self.PathLenght < object.getRealPath().get_curve().get_baked_length():
				self.PathLenght = object.getRealPath().get_curve().get_baked_length()
				self.progress.set_max(self.PathLenght)
				self.slider.set_max(self.PathLenght)
			object.offsetPath(value)
