extends Control


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass


func _on_button_pressed() -> void:
	Global.generated_new_character = false
	get_tree().change_scene_to_file("res://node_2d.tscn")


func _on_generate_new_character_pressed() -> void:
	print($TextEdit.text)
	Global.generated_new_character = true
	
	# This is where we will call the scripts to generate
	
	get_tree().change_scene_to_file("res://node_2d.tscn")
