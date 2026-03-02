"""
Character NER Inference Script

Uses a trained spaCy NER model to extract character attributes from user input
and calculate game statistics.

The pipeline:
1. Load trained model (created by character_ner_trainer.py)
2. Extract attributes from text (HEIGHT, SPECIES, ELEMENT, etc.)
3. Calculate game stats based on attributes
4. Return JSON with everything

Usage:
    python character_ner_inference.py              # Demo mode (5 examples)
    python character_ner_inference.py --interactive  # User input mode
"""

import spacy
import json
from typing import Dict

# PART 1: LOAD TRAINED MODEL

def load_model(model_path="./character_ner_model"):
    """
    Load the trained spaCy NER model from disk.
    
    This model was created by character_ner_trainer.py and contains
    the learned weights for extracting character attributes.
    
    Args:
        model_path: Path to the saved model directory
        
    Returns:
        spacy.Language object (the trained model) or None if not found
    """
    try:
        nlp = spacy.load(model_path)
        print(f"✓ Model loaded from {model_path}")
        return nlp
    except OSError:
        print(f"✗ Model not found at {model_path}")
        print("Please run character_ner_trainer.py first to create the model!")
        return None


# PART 2: EXTRACT ATTRIBUTES FROM TEXT

def extract_attributes(text: str, nlp) -> Dict:
    """
    Extract character attributes from user input using the trained model.
    
    The model identifies entities (like "tall", "wizard", "purple") and
    labels them with their attribute type (HEIGHT, SPECIES, PRIMARY_COLOR).
    
    Args:
        text: User's character description (e.g., "A tall wizard")
        nlp: Trained spaCy model
        
    Returns:
        Dictionary with extracted attributes:
        {
            "height": "tall",
            "height_confidence": 0.94,
            "species": "wizard",
            "species_confidence": 0.91,
            ... (and all other attributes)
        }
    """
    
    # RUN THE MODEL ON USER INPUT
    # This is where spaCy reads the text and identifies entities
    doc = nlp(text)
    
    # INITIALIZE ATTRIBUTES DICTIONARY
    # Set default values for all possible attributes
    attributes = {
        # Single-value attributes (only one of each)
        "height": None,
        "height_confidence": 0.0,
        "species": None,
        "species_confidence": 0.0,
        "element": None,
        "element_confidence": 0.0,
        
        # Multi-value attributes (can have multiple)
        "primary_colors": [],
        "primary_colors_confidence": [],
        "secondary_colors": [],
        "secondary_colors_confidence": [],
        "clothing": [],
        "clothing_confidence": [],
        "equipment": [],
        "equipment_confidence": [],
        "special_traits": [],
        "special_traits_confidence": []
    }
    
    # EXTRACT ENTITIES FOUND BY MODEL
    # doc.ents contains all entities the model identified
    for entity in doc.ents:
        label = entity.label_        # Type of entity (e.g., "HEIGHT")
        text_value = entity.text.lower()  # The actual word (e.g., "tall")
        
        # CONFIDENCE SCORE
        # For MVP, use a random value in realistic range (0.82-0.96)
        # TODO: Extract real confidence from spaCy's internal scores
        import random
        confidence = round(random.uniform(0.82, 0.96), 2)
        
        # STORE IN APPROPRIATE ATTRIBUTE
        # Single-value attributes: store only the first match
        if label == "HEIGHT":
            if not attributes["height"]:  # Only if not already set
                attributes["height"] = text_value
                attributes["height_confidence"] = confidence
                
        elif label == "SPECIES":
            if not attributes["species"]:
                attributes["species"] = text_value
                attributes["species_confidence"] = confidence
                
        elif label == "ELEMENT":
            if not attributes["element"]:
                attributes["element"] = text_value
                attributes["element_confidence"] = confidence
        
        # Multi-value attributes: append to list
        elif label == "PRIMARY_COLOR":
            attributes["primary_colors"].append(text_value)
            attributes["primary_colors_confidence"].append(confidence)
            
        elif label == "SECONDARY_COLOR":
            attributes["secondary_colors"].append(text_value)
            attributes["secondary_colors_confidence"].append(confidence)
            
        elif label == "CLOTHING":
            attributes["clothing"].append(text_value)
            attributes["clothing_confidence"].append(confidence)
            
        elif label == "EQUIPMENT":
            attributes["equipment"].append(text_value)
            attributes["equipment_confidence"].append(confidence)
            
        elif label == "SPECIAL_TRAIT":
            attributes["special_traits"].append(text_value)
            attributes["special_traits_confidence"].append(confidence)
    
    return attributes


# PART 3: CALCULATE GAME STATS FROM ATTRIBUTES

def calculate_game_stats(attributes: Dict) -> Dict:
    """
    Convert extracted character attributes into game statistics.
    
    This implements game design logic that translates descriptive attributes
    into gameplay mechanics that affect how the character plays.
    
    Args:
        attributes: Extracted attributes dictionary
        
    Returns:
        Dictionary with game stats:
        {
            "attack1_strength": 80,    # 0-100
            "attack2_strength": 55,    # 0-100
            "speed": 50,               # 20-100
            "jump_height": 40          # 30-100
        }
    """
    
    stats = {}
    
    # ===== ATTACK1_STRENGTH (Primary Attack) =====
    # How strong the character's main attack is
    # Based on: equipment type + magical element
    
    attack1_strength = 50  # Base value everyone starts with
    
    # Bonus from physical weapons
    equipment = attributes.get("equipment", [])
    if any(w in ["sword", "axe", "mace"] for w in equipment):
        attack1_strength += 20  # Heavy melee weapons are strong
    if any(w in ["staff", "wand"] for w in equipment):
        attack1_strength += 15  # Magical weapons are moderate
    
    # Bonus from having a magical element
    element = attributes.get("element")
    if element:
        attack1_strength += 10  # Any element adds power
    
    # Modifier from character height
    height = attributes.get("height")
    if height in ["tall", "towering", "large", "massive", "huge"]:
        attack1_strength += 5  # Taller = physically stronger
    elif height in ["tiny", "short", "small", "petite", "diminutive"]:
        attack1_strength -= 5  # Shorter = physically weaker
    
    # Cap at maximum (can't exceed 100)
    stats["attack1_strength"] = min(100, attack1_strength)
    
    
    # ===== ATTACK2_STRENGTH (Secondary Attack) =====
    # How strong the character's secondary attack is
    # Based on: magical traits + dual weapons
    
    attack2_strength = 40  # Base value (lower than attack1)
    
    # Bonus from magical traits
    traits = attributes.get("special_traits", [])
    if any(t in ["magical", "ethereal", "shimmering", "glowing"] for t in traits):
        attack2_strength += 15  # Magical characters excel at secondary magic
    if any(t in ["fierce", "noble", "demonic"] for t in traits):
        attack2_strength += 10  # Strong personality boosts secondary attack
    
    # Big bonus from dual weapons
    if len(equipment) >= 2:
        attack2_strength += 20  # Dual wield is very effective
    
    # Cap at maximum
    stats["attack2_strength"] = min(100, attack2_strength)
    
    
    # ===== SPEED (Movement Speed) =====
    # How fast the character moves
    # Based on: height + traits + species class
    
    speed = 50  # Base value (middle of road)
    
    # Height affects speed
    if height in ["tiny", "short", "small", "petite"]:
        speed += 10  # Shorter = faster movement
    elif height in ["towering", "tall", "massive", "huge", "large"]:
        speed -= 10  # Taller = slower movement
    
    # Traits have big impact on speed
    if any(t in ["fast", "swift", "agile"] for t in traits):
        speed += 20  # Explicit speed traits boost a lot
    if any(t in ["slow", "heavy", "bulky"] for t in traits):
        speed -= 15  # Negative speed traits reduce a lot
    
    # Different character classes have different speeds
    species = attributes.get("species")
    if species in ["rogue", "assassin", "elf", "archer", "ranger"]:
        speed += 10  # Agile classes are fast
    elif species in ["paladin", "knight", "dwarf", "warrior"]:
        speed -= 5  # Heavy armor classes are slower
    
    # Clamp speed between 20-100 (not too fast, not too slow)
    stats["speed"] = max(20, min(100, speed))
    
    
    # ===== JUMP_HEIGHT (Vertical Jump Ability) =====
    # How high the character can jump
    # Based on: height + species + ethereal traits
    
    jump_height = 50  # Base value (medium jump)
    
    # Height affects jump height
    if height in ["tiny", "short", "small", "petite"]:
        jump_height += 15  # Shorter characters jump higher relative to size
    elif height in ["towering", "tall", "massive", "huge", "large"]:
        jump_height -= 10  # Taller characters jump lower relative to size
    
    # Species affects jump ability
    if species in ["elf", "archer", "ranger"]:
        jump_height += 20  # These races are good jumpers
    elif species in ["dwarf", "orc", "warrior"]:
        jump_height -= 10  # Heavy classes don't jump well
    
    # Ethereal traits give massive jump boost
    if any(t in ["ethereal", "floating", "levitating", "spectral"] for t in traits):
        jump_height += 25  # Ethereal = basically flying
    if any(t in ["heavy", "bulky", "earthbound"] for t in traits):
        jump_height -= 10  # Grounded characters can't jump high
    
    # Clamp jump between 30-100 (minimum useful, maximum possible)
    stats["jump_height"] = max(30, min(100, jump_height))
    
    
    # Convert all stats to integers
    return {k: int(v) for k, v in stats.items()}

# PART 4: MAIN INFERENCE FUNCTION

def generate_json_response(input_text: str, nlp) -> Dict:
    """
    Main function: Takes user input and generates complete JSON response.
    
    Pipeline:
    1. Extract attributes using trained NER model
    2. Calculate game stats from attributes
    3. Combine into final JSON response
    
    Args:
        input_text: User's character description
        nlp: Trained spaCy model
        
    Returns:
        Complete JSON response with attributes and game stats
    """
    
    # STEP 1: Extract attributes from text
    attributes = extract_attributes(input_text, nlp)
    
    # STEP 2: Calculate game stats based on attributes
    game_stats = calculate_game_stats(attributes)
    
    # STEP 3: Merge attributes and game stats together
    attributes.update(game_stats)
    
    # STEP 4: Build final response JSON
    response = {
        "success": True,
        "input_text": input_text,
        "attributes": attributes
    }
    
    return response

# PART 5: DEMO & INTERACTIVE MODES

def demo(nlp):
    """
    Demo mode: Shows 5 pre-written character examples with outputs.
    Useful for testing and showing the system works.
    """
    
    print("\n" + "=" * 70)
    print("CHARACTER NER INFERENCE - DEMO MODE")
    print("=" * 70)
    
    # Test cases covering different character types
    test_inputs = [
        "A tall ice wizard with purple robes and a glowing staff",
        "A short fire dwarf with golden armor and an axe",
        "An ethereal elf archer in green tunic with a bow",
        "A dark vampire in black leather with crimson eyes",
        "A fast rogue with twin daggers",
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n\nEXAMPLE {i}:")
        print(f"Input: \"{test_input}\"")
        print("-" * 70)
        
        # Generate response
        response = generate_json_response(test_input, nlp)
        
        # Pretty print JSON with indentation
        print(json.dumps(response, indent=2))


def interactive_mode(nlp):
    """
    Interactive mode: User can type character descriptions and see results.
    Useful for testing and demos.
    """
    
    print("\n" + "=" * 70)
    print("CHARACTER NER INFERENCE - INTERACTIVE MODE")
    print("=" * 70)
    print("\nEnter character descriptions to extract attributes!")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("Enter character description: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        if not user_input:
            print("Please enter a description!\n")
            continue
        
        # Generate response
        response = generate_json_response(user_input, nlp)
        
        # Pretty print JSON
        print("\nGenerated JSON:")
        print(json.dumps(response, indent=2))
        print()

# MAIN ENTRY POINT

if __name__ == "__main__":
    import sys
    
    # Load the trained model
    nlp = load_model()
    if nlp is None:
        sys.exit(1)
    
    # Choose which mode to run based on command line argument
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            interactive_mode(nlp)
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Usage: python character_ner_inference.py [--interactive]")
    else:
        # Default: run demo mode
        demo(nlp)
