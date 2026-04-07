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

@export var DAMAGE = 15

var max_health = 50
var current_health = 50

var player_target = null

var has_damaged_player = false

@onready var anim_sprite = $AnimatedSprite2D
@onready var aggro_range = $AggroRange
@onready var attack_range = $AttackRange
@onready var sword_hitbox = $SwordHitbox
@onready var cooldown_timer = $AttackCooldownTimer
@onready var health_bar = $HealthBar

func _ready():
	add_to_group("enemies")
	aggro_range.body_entered.connect(_on_aggro_range_body_entered)
	aggro_range.body_exited.connect(_on_aggro_range_body_exited)
	attack_range.body_entered.connect(_on_attack_range_body_entered)
	
	anim_sprite.animation_finished.connect(_on_animation_finished)
	anim_sprite.frame_changed.connect(_on_frame_changed)
	
	cooldown_timer.timeout.connect(_on_cooldown_timeout)
	
	sword_hitbox.body_entered.connect(_on_sword_hitbox_body_entered)
	
	health_bar.max_value = max_health
	health_bar.value = current_health
	

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

func take_damage(amount):
	if current_state == State.DEAD:
		return
	
	current_health -= amount
	
	if health_bar:
		health_bar.value = current_health
		print("Enenmy health bar value set to: ", health_bar.value)
	
	if current_health <= 0:
		health_bar.hide()
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
	sword_hitbox.monitoring = false
	has_damaged_player = false

func _on_frame_changed():
	if anim_sprite.animation == "attack":
		if anim_sprite.frame == 3 or anim_sprite.frame == 4 or anim_sprite.frame == 5:
			sword_hitbox.set_deferred("monitoring", true)
		else:
			sword_hitbox.set_deferred("monitoring", false)

func _on_aggro_range_body_entered(body):
	if body.is_in_group("player"):
		player_target = body
		if current_state == State.IDLE:
			current_state = State.CHASE

func _on_aggro_range_body_exited(body):
	if body == player_target:
		player_target = null
		
		# Check to see if the enemy is dieing
		if current_state == State.DEAD:
			return
			
		if current_state != State.ATTACKING and current_state != State.COOLDOWN:
			current_state = State.IDLE

func _on_attack_range_body_entered(body):
	if current_state == State.DEAD: 
		return
	
	if body == player_target and current_state == State.CHASE:
		start_attack()

func _on_animation_finished():
	if anim_sprite.animation == "attack":
		current_state = State.COOLDOWN
		sword_hitbox.monitoring = false
		cooldown_timer.start(1.0)
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
		
func _on_sword_hitbox_body_entered(body):
	if current_state == State.ATTACKING and not has_damaged_player:
		if body.is_in_group("player"):
			body.take_damage(DAMAGE)
			has_damaged_player = true
			sword_hitbox.set_deferred("monitoring", false)
		
