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
	Global.generated_new_character = true
	var user_prompt = %TextEdit.text 
	Global.last_prompt = user_prompt
	
	# Translate BOTH paths for the operating system
	var script_path = ProjectSettings.globalize_path("res://generator.py")
	var save_path = ProjectSettings.globalize_path("res://Characters/TestingSprites/custom_skin.png")
	
	var project_dir=ProjectSettings.globalize_path("res://")
	var python_exe = project_dir.path_join("../../../.venv/bin/python").simplify_path()
	print(python_exe)
	
	# Pass the prompt AND the save path to Python
	var arguments = [script_path, user_prompt, save_path]
	var python_output = [] 
	
	print("Running Python...")
	OS.execute(python_exe, arguments, python_output)
	
	if python_output.size() > 0:
		print("Python Output: ", python_output[0])
		
	get_tree().change_scene_to_file("res://Scenes/preview_sprite.tscn")


func _on_load_existing_sprite_pressed() -> void:
	# Move to the load sprite scene
	get_tree().change_scene_to_file("res://Scenes/load_sprite.tscn")
