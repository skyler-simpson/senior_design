extends CharacterBody2D

enum State {
	IDLE,
	CHASE,
	ATTACKING,
	COOLDOWN,
	HURT,
	DEAD
}

var current_state = State.IDLE

const SPEED = 120.0
const GRAVITY = 980.0
const DAMAGE = 15

var max_health = 50
var current_health = 50

var player_target = null

@onready var anim_sprite = $AnimatedSprite2D
@onready var aggro_range = $AggroRange
@onready var attack_range = $AttackRange
@onready var sword_hitbox = $SwordHitbox
@onready var cooldown_timer = $AttackCooldownTimer

func _ready():
	aggro_range.body_entered.connect(_on_aggro_range_body_entered)
	aggro_range.body_exited.connect(_on_aggro_range_body_exited)
	attack_range.body_entered.connect(_on_attack_range_body_entered)
	
	anim_sprite.animation_finished.connect(_on_animation_finished)
	
	cooldown_timer.timeout.connect(_on_cooldown_timeout)
	

func _physics_process(delta: float) -> void:
	# Add the gravity.
	if not is_on_floor():
		velocity.y += GRAVITY * delta

	match current_state:
		State.IDLE:
			velocity.x = 0
			anim_sprite.play("idle")
		
		State.CHASE: 
			if player_target and is_instance_valid(player_target) and not player_target.is_dead:
				var direction = global_position.direction_to(player_target.global_position)
				velocity.x = direction.x * SPEED
				anim_sprite.play("run")
				face_direction(direction.x)
			else:
				# Player died or moved out of aggro range
				current_state = State.IDLE
		
		State.ATTACKING:
			velocity.x = 0 # Stop moving and attack the player
			
		State.COOLDOWN:
			velocity.x = 0
			anim_sprite.play("idle")
			
			if player_target and is_instance_valid(player_target):
				var direction = global_position.direction_to(player_target.global_position)
				face_direction(direction.x)
		
		State.HURT:
			velocity.x = 0
			anim_sprite.play("hit")
		
		State.DEAD:
			velocity.x = 0
			anim_sprite.play("die")
	
	move_and_slide()

func _process(_delta):
	if current_state == State.ATTACKING and sword_hitbox.monitoring:
		# If the player is touching the sword hitbox, then they are hit
		var overlapping_bodies = sword_hitbox.get_overlapping_bodies()
		for body in overlapping_bodies:
			if body.is_in_group("player"):
				# The player will take damage
				body.take_damage(DAMAGE)
				sword_hitbox.monitoring = false

func take_damage(amount):
	if current_state == State.DEAD:
		return
	
	current_health -= amount
	
	if current_health <= 0:
		die()
	else:
		current_state = State.HURT

func die():
	current_state = State.DEAD
	
	set_collision_layer_value(3, false) 
	set_collision_mask_value(2, false)
	
	sword_hitbox.monitoring = false
	anim_sprite.play("die")

func face_direction(dir_x):
	if dir_x > 0:
		anim_sprite.flip_h = false
		attack_range.scale.x = 1
		sword_hitbox.scale.x = 1
	elif dir_x < 0:
		anim_sprite.flip_h = true
		attack_range.scale.x = -1
		sword_hitbox.scale.x = -1

func start_attack():
	current_state = State.ATTACKING
	anim_sprite.play("attack")
	sword_hitbox.monitoring = true

func _on_aggro_range_body_entered(body):
	if body.is_in_group("player"):
		player_target = body
		if current_state == State.IDLE:
			current_state = State.CHASE

func _on_aggro_range_body_exited(body):
	if body == player_target:
		player_target = null
		if current_state != State.ATTACKING and current_state != State.COOLDOWN:
			current_state = State.IDLE

func _on_attack_range_body_entered(body):
	if body == player_target and current_state == State.CHASE:
		start_attack()

func _on_animation_finished():
	if anim_sprite.animation == "attack":
		current_state = State.COOLDOWN
		sword_hitbox.monitoring = false
		cooldown_timer.start(2.0)
	elif anim_sprite.animation == "hit":
		if current_state != State.DEAD:
			current_state = State.CHASE
	elif anim_sprite.animation == "die":
		queue_free()

func _on_cooldown_timeout():
	if current_state == State.DEAD:
		return

	current_state = State.CHASE
	
	var is_overlapping = attack_range.overlaps_body(player_target)
	
	if player_target and attack_range.overlaps_body(player_target):
		start_attack()
