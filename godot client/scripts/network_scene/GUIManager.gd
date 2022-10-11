extends Control


onready var httpDialog : WindowDialog = $HttpDialog
onready var connectButton : Button = $MainMenu/PanelContainer/HBoxContainer/ConnectButton
onready var disconnectButton : Button = $MainMenu/PanelContainer/HBoxContainer/DisconnectButton
onready var inputIpPort : LineEdit = $HttpDialog/VBoxContainer/HBoxContainer/LineEdit


func _ready():
	pass


func _on_ConnectButton_pressed():
	httpDialog.popup_centered()


func _on_ConnectDialogButton_pressed():
	httpDialog.visible = false
	disconnectButton.visible = true
	connectButton.visible = false
	SceneManagerNetwork.connectHttp(inputIpPort.text)


func _on_DisconnectButton_pressed():
	disconnectButton.visible = false
	connectButton.visible = true
	SceneManagerNetwork.disconnectHttp()
