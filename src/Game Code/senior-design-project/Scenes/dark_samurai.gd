extends CharacterBody2D


const SPEED = 300.0
const JUMP_VELOCITY = -450.0
const DAMAGE_AMOUNT = 20

@onready var samurai = $Sprite2D
@onready var sword_area = $SwordArea

var max_health: int = 100
var current_health: int = 100
var is_dead: bool = false

var is_attacking: bool = false
var is_hurt: bool = false

func _ready() -> void:
	samurai.animation_finished.connect(_on_animation_finished)
	add_to_group("player")
	sword_area.monitoring = false

func _physics_process(delta: float) -> void:
	# If the player is dead then stop all movement
	if is_dead:
		if not is_on_floor():
			velocity += get_gravity() * delta
		move_and_slide()
		return
	
	# Add the gravity
	if not is_on_floor():
		velocity += get_gravity() * delta
	
	if is_hurt:
		move_and_slide()
		return

	# Handle jump.
	if Input.is_action_just_pressed("ui_accept") and is_on_floor():
		velocity.y = JUMP_VELOCITY

	# Get the input direction and handle the movement/deceleration.
	# As good practice, you should replace UI actions with custom gameplay actions.
	var direction := Input.get_axis("move_right", "move_left")
	
	if Input.is_action_just_pressed("attack1") and is_on_floor() and not is_attacking:
		start_attack("attack1")
	elif Input.is_action_just_pressed("attack2") and is_on_floor() and not is_attacking:
		start_attack("attack2")
	
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
		# Flip the sprite
		samurai.flip_h = (direction < 0)
		
		# Flip the Hitbox too!
		# If facing Left (-1), move hitbox to the left side
		if direction < 0:
			sword_area.scale.x = -1
		else:
			sword_area.scale.x = 1
		
	move_and_slide()

func start_attack(anim_name):
	is_attacking = true
	velocity.x = 0
	samurai.play(anim_name)
	
	# Turn ON the sword hitbox
	sword_area.monitoring = true

func _on_sword_area_body_entered(body):
	# If we hit an Enemy (Layer 3)
	if body.has_method("take_damage"):
		body.take_damage(DAMAGE_AMOUNT)
		print("Hit enemy!")

func _on_animation_finished() -> void:
	var current_animation = samurai.animation
	
	if current_animation == "attack1" or current_animation == "attack2":
		is_attacking = false
		# Turn OFF the sword hitbox when attack ends
		sword_area.monitoring = false
	
	if current_animation == "hit":
		is_hurt = false

func take_damage(amount: int):
	# If the character is already dead, then don't do anything
	if is_dead:
		return
	
	current_health -= amount
	
	if current_health <= 0:
		die()
	else:
		is_hurt = true
		is_attacking = false
		velocity.x = 0
		samurai.play("hit")

func die():
	is_dead = true
	velocity.x = 0
	samurai.play("die")
	
	await samurai.animation_finished
	
	get_tree().paused = true
	print("Game Over - Engine Paused")
