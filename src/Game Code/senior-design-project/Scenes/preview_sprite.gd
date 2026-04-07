extends Control

@onready var sprite_preview = $MarginContainer/VBoxContainer/ScrollContainer/CenterContainer/SpritePreview
@onready var title_label = $MarginContainer/VBoxContainer/TitleLabel

@onready var confirm_button = $MarginContainer/VBoxContainer/HBoxContainer/ConfirmButton
@onready var retry_button = $MarginContainer/VBoxContainer/HBoxContainer/RetryButton

# Stat sliders
@onready var speed_slider = $MarginContainer/VBoxContainer/StatsPanel/MarginStats/StatsVBox/SpeedRow/SpeedSlider
@onready var speed_value = $MarginContainer/VBoxContainer/StatsPanel/MarginStats/StatsVBox/SpeedRow/SpeedValue
@onready var jump_slider = $MarginContainer/VBoxContainer/StatsPanel/MarginStats/StatsVBox/JumpRow/JumpSlider
@onready var jump_value = $MarginContainer/VBoxContainer/StatsPanel/MarginStats/StatsVBox/JumpRow/JumpValue
@onready var damage_slider = $MarginContainer/VBoxContainer/StatsPanel/MarginStats/StatsVBox/DamageRow/DamageSlider
@onready var damage_value = $MarginContainer/VBoxContainer/StatsPanel/MarginStats/StatsVBox/DamageRow/DamageValue

# NLP-extracted attributes (saved for JSON rewrite)
var _nlp_attributes: Dictionary = {}
var _nlp_input_text: String = ""

# Path to the sprite and its companion JSON
var _sprite_path: String = ""
var _json_path: String = ""


func _ready() -> void:
	# Resolve the sprite path
	if Global.custom_skin_path != "":
		_sprite_path = Global.custom_skin_path
	else:
		_sprite_path = "res://Characters/TestingSprites/custom_skin.png"

	_json_path = _sprite_path.replace(".png", ".json")

	_load_sprite_preview()
	_load_stats_from_json()


func _load_sprite_preview() -> void:
	if FileAccess.file_exists(_sprite_path):
		var img = Image.load_from_file(_sprite_path)
		var tex = ImageTexture.create_from_image(img)

		sprite_preview.texture = tex
		sprite_preview.texture_filter = TextureFilter.TEXTURE_FILTER_NEAREST
		sprite_preview.custom_minimum_size = Vector2(tex.get_width(), tex.get_height())

		print("Preview loaded. Size: ", tex.get_size())
	else:
		title_label.text = "Error: No sprite sheet found!"
		print("Error: Preview image not found at ", _sprite_path)


func _load_stats_from_json() -> void:
	"""Load NLP attributes and game stats from companion JSON file."""
	if FileAccess.file_exists(_json_path):
		var file = FileAccess.open(_json_path, FileAccess.READ)
		var content = file.get_as_text()
		file.close()

		var json = JSON.new()
		var parse_result = json.parse(content)

		if parse_result == OK:
			var data = json.get_data()
			if data is Dictionary:
				# Store NLP data for later rewrite
				_nlp_attributes = data.get("attributes", {})
				_nlp_input_text = data.get("input_text", "")

				# Load game stats into sliders
				var stats = data.get("game_stats", {})
				var speed = stats.get("speed", 50)
				var jump = stats.get("jump_velocity", 50)
				var damage = stats.get("damage_amount", 50)

				# Enforce minimum jump of 40 so characters can always clear obstacles
				if jump < 40:
					jump = 40

				_set_slider_values(speed, jump, damage)
				print("Loaded stats from JSON: SPEED=", speed, " JUMP=", jump, " DMG=", damage)
				return

	# Fallback: no JSON found, use defaults
	print("No companion JSON found. Using default stat values (50/50/50).")
	_set_slider_values(50, 50, 50)


func _set_slider_values(speed: int, jump: int, damage: int) -> void:
	speed_slider.value = clamp(speed, 0, 100)
	jump_slider.value = clamp(jump, 40, 100)
	damage_slider.value = clamp(damage, 0, 100)
	_update_value_labels()


func _update_value_labels() -> void:
	speed_value.text = str(int(speed_slider.value))
	jump_value.text = str(int(jump_slider.value))
	damage_value.text = str(int(damage_slider.value))


func _save_stats_to_json() -> void:
	"""Rewrite the JSON file with user-modified slider values."""
	var speed = int(speed_slider.value)
	var jump = int(jump_slider.value)
	var damage = int(damage_slider.value)

	var data = {
		"attributes": _nlp_attributes,
		"game_stats": {
			"speed": speed,
			"jump_velocity": jump,
			"damage_amount": damage
		},
		"input_text": _nlp_input_text,
		"user_modified": not _nlp_attributes.is_empty()  # True if user changed sliders
	}

	var json_string = JSON.stringify(data, "\t")

	# Write back to the JSON file
	var file = FileAccess.open(_json_path, FileAccess.WRITE)
	if file:
		file.store_string(json_string)
		file.close()
		print("Stats saved to JSON: SPEED=", speed, " JUMP=", jump, " DMG=", damage)
	else:
		print("Warning: Could not save modified stats to ", _json_path)


func _on_speed_slider_changed(value: float) -> void:
	_update_value_labels()


func _on_jump_slider_changed(value: float) -> void:
	_update_value_labels()


func _on_damage_slider_changed(value: float) -> void:
	_update_value_labels()


func _on_confirm_button_pressed() -> void:
	# Save user-modified stats to JSON
	_save_stats_to_json()

	# Pass stats to Global for the game scene
	Global.has_custom_stats = true
	Global.custom_speed = speed_slider.value
	Global.custom_jump_velocity = jump_slider.value
	Global.custom_damage_amount = damage_slider.value

	print("Confirming with stats — SPEED: ", speed_slider.value,
		  ", JUMP: ", jump_slider.value,
		  ", DMG: ", damage_slider.value)

	# Proceed to the game screen
	get_tree().change_scene_to_file("res://node_2d.tscn")


func _on_retry_button_pressed() -> void:
	# Update UI to show that a new sprite sheet is being generated
	title_label.text = "Regenerating Your Character..."

	# Disable the buttons
	confirm_button.disabled = true
	retry_button.disabled = true

	# Wait so the label updates on the screen
	await get_tree().create_timer(0.1).timeout

	_run_python_generation(Global.last_prompt)

	# Reload the scene
	get_tree().reload_current_scene()


func _run_python_generation(prompt_text: String) -> void:
	var script_path = ProjectSettings.globalize_path("res://generator.py")
	var save_path = ProjectSettings.globalize_path("res://Characters/TestingSprites/custom_skin.png")

	var project_dir = ProjectSettings.globalize_path("res://")
	var python_exe = project_dir.path_join("../../../.venv/bin/python").simplify_path()
	print(python_exe)

	var arguments = [script_path, prompt_text, save_path, "--reuse-prompt"]
	var python_output = []

	print("Python is regenerating with prompt: ", prompt_text)
	OS.execute(python_exe, arguments, python_output)
