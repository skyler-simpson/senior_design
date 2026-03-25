extends Control

@onready var sprite_preview = $MarginContainer/VBoxContainer/ScrollContainer/CenterContainer/SpritePreview
@onready var label = $MarginContainer/VBoxContainer/Label

@onready var confirmButton = $MarginContainer/VBoxContainer/HBoxContainer/ConfirmButton
@onready var retryButton = $MarginContainer/VBoxContainer/HBoxContainer/RetryButton

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	var path = "res://Characters/TestingSprites/custom_skin.png"
	
	if FileAccess.file_exists(path):
		var img = Image.load_from_file(path)
		var tex = ImageTexture.create_from_image(img)
		
		# 1. Apply the texture
		sprite_preview.texture = tex
		sprite_preview.texture_filter = TextureFilter.TEXTURE_FILTER_NEAREST
		
		# 2. FORCE the TextureRect to match the image size
		# This is what triggers the ScrollContainer to show scrollbars
		sprite_preview.custom_minimum_size = Vector2(tex.get_width(), tex.get_height())
		
		print("Preview loaded. Size: ", tex.get_size())
	else:
		print("Error: Preview image not found!")


func _on_confirm_button_pressed() -> void:
	# Proceed to the game screen
	get_tree().change_scene_to_file("res://node_2d.tscn")


func _on_retry_button_pressed() -> void:
	# Update UI to show that a new sprite sheet is being generated
	label.text = "Regenerating Your Character."
	
	# Disable the buttons
	confirmButton.disabled = true
	retryButton.disabled = true
	
	# Wait so the label updates on the screen
	await get_tree().create_timer(0.1).timeout
	
	_run_python_generation(Global.last_prompt)
	
	# Reload the scene
	get_tree().reload_current_scene()
	
func _run_python_generation(prompt_text: String) -> void:
	var script_path = ProjectSettings.globalize_path("res://generator.py")
	var save_path = ProjectSettings.globalize_path("res://Characters/TestingSprites/custom_skin.png")
	
	var arguments = [script_path, prompt_text, save_path]
	var output = []
	
	print("Python is regenerating with prompt: ", prompt_text)
	OS.execute("python", arguments, output, true)
