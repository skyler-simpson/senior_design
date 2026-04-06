extends Node

# This will determine if the user generates a new character or not
var generated_new_character: bool = false
var last_prompt: String = ""
var custom_skin_path: String = ""

# Custom character stats loaded from companion JSON file
var has_custom_stats: bool = false
var custom_speed: float = 300.0
var custom_jump_velocity: float = -450.0
var custom_damage_amount: float = 20.0
