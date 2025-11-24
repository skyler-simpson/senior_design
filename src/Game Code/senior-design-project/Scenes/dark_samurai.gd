extends CharacterBody2D


const SPEED = 300.0
const JUMP_VELOCITY = -400.0
@onready var samurai = $Sprite2D

var is_attacking: bool = false

func _ready() -> void:
	samurai.animation_finished.connect(_on_animation_finished)

func _physics_process(delta: float) -> void:
	# Add the gravity
	if not is_on_floor():
		velocity += get_gravity() * delta

	# Handle jump.
	if Input.is_action_just_pressed("ui_accept") and is_on_floor():
		velocity.y = JUMP_VELOCITY

	# Get the input direction and handle the movement/deceleration.
	# As good practice, you should replace UI actions with custom gameplay actions.
	var direction := Input.get_axis("move_right", "move_left")
	
	# Attacking animations
	if Input.is_action_just_pressed("attack1") and is_on_floor() and not is_attacking:
		is_attacking = true
		velocity.x = 0
		samurai.play("attack1")
	elif Input.is_action_just_pressed("attack2") and is_on_floor() and not is_attacking:
		is_attacking = true
		velocity.x = 0
		samurai.play("attack2")
	
	# Moving animations
	if not is_attacking:
		if direction:
			velocity.x = direction * SPEED
		else:
			velocity.x = move_toward(velocity.x, 0, SPEED)
			
		if is_on_floor():
			if velocity.x == 0:
				samurai.play("idle")
			else:
				samurai.play("running")
		else:
			if velocity.y < 0:
				samurai.play("jumping")
			else:
				samurai.play("falling")
			
	if direction != 0:
		samurai.flip_h = (direction < 0)
		
	move_and_slide()
	
func _on_animation_finished() -> void:
	var current_animation = samurai.animation
		
	if current_animation == "attack1" or current_animation == "attack2":
		is_attacking = false
