extends CanvasLayer

@onready var title_label = $VBoxContainer/Title
@onready var subtitle_label = $VBoxContainer/Subtitle

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	# Allows this node to ignore the pause state
	process_mode = Node.PROCESS_MODE_ALWAYS


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	if visible and Input.is_key_pressed(KEY_ENTER):
		get_tree().paused = false
		get_tree().change_scene_to_file("res://Scenes/main_menu.tscn")

func show_end_screen(won: bool):
	title_label.text = "YOU WIN" if won else "YOU LOSE"
	subtitle_label.text = "PRESS ENTER TO RETURN TO MENU"
	visible = true
