extends Control

@onready var sprite_preview = $MarginContainer/VBoxContainer/ScrollContainer/CenterContainer/SpritePreview
@onready var file_dialog = $FileDialog

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	# Connect file dialog to file loading function
	file_dialog.file_selected.connect(_on_file_selected)

func _on_file_selected(path: String):
	# Use load from file
	var image = Image.load_from_file(path)
	if image:
		var texture = ImageTexture.create_from_image(image)
		sprite_preview.texture = texture
		
		# Update the global state
		Global.custom_skin_path = path
		Global.generated_new_character = true
		
		# grab the corresponding values based on the sprite timestamp and put them into the existing JSON file

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass


func _on_play_button_pressed() -> void:
	if sprite_preview.texture == null:
		print("Please select a sprite sheet first.")
		return
	
	get_tree().change_scene_to_file("res://node_2d.tscn")


func _on_menu_button_pressed() -> void:
	get_tree().change_scene_to_file("res://Scenes/main_menu.tscn")


func _on_load_button_pressed() -> void:
	var path = "res://Characters/TestingSprites/Old Characters"
	file_dialog.current_dir = path
	file_dialog.popup_centered()
