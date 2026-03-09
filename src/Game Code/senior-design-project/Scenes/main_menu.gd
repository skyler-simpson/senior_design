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
	# FIXED: This now perfectly matches the variable in your global.gd file!
	Global.generated_new_character = true
	var user_prompt = %TextEdit.text 
	
	# Translate BOTH paths for the operating system
	var script_path = ProjectSettings.globalize_path("res://generator.py")
	var save_path = ProjectSettings.globalize_path("user://custom_skin.png")
	
	# Pass the prompt AND the save path to Python
	var arguments = [script_path, user_prompt, save_path]
	var python_output = [] 
	
	print("Running Python...")
	OS.execute("python", arguments, python_output, true)
	
	if python_output.size() > 0:
		print("Python Output: ", python_output[0])
		
	get_tree().change_scene_to_file("res://node_2d.tscn")
