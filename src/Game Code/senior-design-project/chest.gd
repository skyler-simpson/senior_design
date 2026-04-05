extends StaticBody2D

@onready var sprite = $AnimatedSprite2D

var is_open = false

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	add_to_group("chest")
	sprite.frame = 0
	sprite.stop()
	pass


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass
		
func take_damage(amount):
	print("hit")
	if not is_open:
		is_open = true
		get_tree().get_nodes_in_group("enemies").map(func(e): e.die())
		start_animation()
		
func start_animation():
	sprite.play("default")
	await sprite.animation_finished
	get_node("/root/Node2D/EndScreen").show_end_screen(true)
