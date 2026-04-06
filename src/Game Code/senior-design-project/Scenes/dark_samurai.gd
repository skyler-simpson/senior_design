extends CharacterBody2D


# Default stats — overridden by JSON if a companion file exists
var SPEED = 300.0
var JUMP_VELOCITY = -450.0
var DAMAGE_AMOUNT = 20
const FALL_DEATH_Y = 1000.0
const TARGET_PIXEL_HEIGHT = 100.0

@onready var samurai = $Sprite2D
@onready var sword_area = $SwordArea
@onready var health_bar = $HealthBar

var max_health: int = 100
var current_health: int = 100
var is_dead: bool = false

var is_attacking: bool = false
var is_hurt: bool = false

func _ready() -> void:
	var path_to_load = ""

	if Global.custom_skin_path != "":
		path_to_load = Global.custom_skin_path
	else:
		path_to_load = "res://Characters/TestingSprites/custom_skin.png"

	# Always try to load custom_skin.png first (works for both new generation
	# and "Play with Current Character" replays)
	if FileAccess.file_exists(path_to_load):
		var custom_image = Image.new()
		var err = custom_image.load(path_to_load)

		if err == OK:
			var custom_texture = ImageTexture.create_from_image(custom_image)
			apply_new_spritesheet(custom_texture)
			print("Success: Loaded custom sprite sheet from: ", path_to_load)
			scale_generated_sprite()
			_try_load_stats_from_json(path_to_load)
		else:
			print("Found custom_skin.png but failed to load it. Code: ", err)
			_load_default_sprite()
	else:
		print("No custom sprite found. Loading default sprite.")
		_load_default_sprite()

	# Initializing health bar
	health_bar.max_value = max_health
	health_bar.value = current_health

	samurai.animation_finished.connect(_on_animation_finished)
	add_to_group("player")
	sword_area.monitoring = false

func _load_default_sprite():
	print("No custom skin found. Loading current sprite.")
	var default_texture = load("res://Characters/TestingSprites/custom_skin.png")
	apply_new_spritesheet(default_texture)

func apply_new_spritesheet(new_texture: Texture2D):
	var frames = samurai.sprite_frames
	if not frames:
		return
		
	var new_cell_size = 192
	
	for anim_name in frames.get_animation_names():
		# Find which row this animation should live on (0-5)
		var row = _get_row_index_for_animation(anim_name)
		
		for i in range(frames.get_frame_count(anim_name)):
			var frame_tex = frames.get_frame_texture(anim_name, i)
			
			if frame_tex is AtlasTexture:
				# CRITICAL: Make the resource unique so it doesn't 
				# overwrite other animations sharing this frame index
				var unique_frame = frame_tex.duplicate()
				
				# 1. Swap the image
				unique_frame.atlas = new_texture
				
				# New code right here
				var column_index = i
				if anim_name.to_lower() == "falling":
					column_index = i + 3
				
				# 2. Set the Region to the correct 192px "Bucket"
				# Column = frame index, Row = determined by animation name
				unique_frame.region = Rect2(
					column_index * new_cell_size, 
					row * new_cell_size, 
					new_cell_size, 
					new_cell_size
				)
				
				# 3. Push the unique, corrected frame back into the SpriteFrames
				frames.set_frame(anim_name, i, unique_frame)

# function to accurately get the animation on each row
func _get_row_index_for_animation(anim_name: String) -> int:
	var n = anim_name.to_lower()
	if "idle" in n: return 0
	if "run" in n or "walk" in n: return 1
	if "jump" in n or "fall" in n: return 2
	if "attack" in n: return 3
	if "hit" in n or "hurt" in n: return 4
	if "death" in n or "die" in n: return 5
	return 0

func _physics_process(delta: float) -> void:
	if global_position.y > FALL_DEATH_Y and not is_dead:
		print(global_position)
		die()
		return
		
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
	
	if current_animation == "attack1":
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
	
	print("You were hit!")
	
	# Update health bar
	if health_bar:
		health_bar.value = current_health
		print("Set health bar value to: ", health_bar.value)
	
	if current_health <= 0:
		# Hide health bar when dead
		health_bar.hide()
		die()
	else:
		is_hurt = true
		is_attacking = false
		velocity.x = 0
		samurai.play("hit")

func die():
	# Prevent function from calling multiple times
	if is_dead: return
	
	is_dead = true
	set_physics_process(false)
	
	is_attacking = false
	is_hurt = false
	velocity = Vector2.ZERO
	
	samurai.stop()
	samurai.play("die")
	
	await samurai.animation_finished
	
	get_tree().paused = true
	print("Game Over - Engine Paused")
	get_node("/root/Node2D/EndScreen").show_end_screen(false)

func scale_generated_sprite():
	var frame_height = 0.0

	# Scenario A: You are using an AnimatedSprite2D with SpriteFrames
	if samurai is AnimatedSprite2D and samurai.sprite_frames:
		var frame_texture = samurai.sprite_frames.get_frame_texture("idle", 0)
		if frame_texture:
			frame_height = float(frame_texture.get_height())

	# Scenario B: You are using a standard Sprite2D with a raw Texture
	elif samurai is Sprite2D and samurai.texture:
		# We divide the total height by vframes in case it's a grid sprite sheet
		frame_height = float(samurai.texture.get_height()) / float(samurai.vframes)

	# Apply the scale if we successfully found the height
	if frame_height > 0:
		var scale_factor = TARGET_PIXEL_HEIGHT / frame_height
		samurai.scale = Vector2(scale_factor, scale_factor)
		print("Successfully scaled sprite to: ", samurai.scale)


func _try_load_stats_from_json(png_path: String) -> void:
	"""Load companion JSON file and apply game_stats to character vars."""
	var json_path = png_path.replace(".png", ".json")

	# Also check Global path override
	if json_path.begins_with("res://"):
		json_path = ProjectSettings.globalize_path(json_path)

	if not FileAccess.file_exists(json_path):
		print("No companion JSON found at: ", json_path)
		print("Using default stats: SPEED=", SPEED, ", JUMP=", JUMP_VELOCITY, ", DMG=", DAMAGE_AMOUNT)
		return

	var file = FileAccess.open(json_path, FileAccess.READ)
	var content = file.get_as_text()
	file.close()

	var json = JSON.new()
	var parse_result = json.parse(content)

	if parse_result != OK:
		print("Failed to parse JSON stats: ", json.get_error_message())
		return

	var data = json.get_data()
	if not data is Dictionary or not data.has("game_stats"):
		print("JSON missing game_stats key")
		return

	var stats = data["game_stats"]

	# Map NLP 0-100 scale to Godot scale
	# SPEED: NLP 0-100 → Godot 150-450 (base 300, +/- 150)
	if stats.has("speed"):
		SPEED = 150.0 + (stats["speed"] / 100.0) * 300.0

	# JUMP_VELOCITY: NLP 0-100 → Godot -250 to -550 (base -450)
	if stats.has("jump_velocity"):
		JUMP_VELOCITY = -250.0 - (stats["jump_velocity"] / 100.0) * 300.0

	# DAMAGE_AMOUNT: NLP 0-100 → Godot 5-45 (base 20, +/- 20)
	if stats.has("damage_amount"):
		DAMAGE_AMOUNT = 5.0 + (stats["damage_amount"] / 100.0) * 40.0

	print("Loaded JSON stats: SPEED=", SPEED, ", JUMP=", JUMP_VELOCITY, ", DMG=", DAMAGE_AMOUNT)
