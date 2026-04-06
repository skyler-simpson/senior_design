import sys
import os
import json
import system_prompts
from google import genai
from google.genai import types
from dotenv import load_dotenv

from PIL import Image
from io import BytesIO

import shutil
from datetime import datetime

# ---------------------------------------------------------------------------
# Import NLP pipeline — add the NLP Model directory to the import path
# ---------------------------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_SCRIPT_DIR)          # senior-design-project/
_SRC_DIR     = os.path.dirname(_PROJECT_DIR)          # src/
NLP_DIR      = os.path.join(_SRC_DIR, "NLP Model")
sys.path.insert(0, NLP_DIR)
from character_ner_inference import load_model, generate_json_response

load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')

# Load the NLP model once at module import time
_nlp = load_model()

# ---------------------------------------------------------------------------
# Image-prompt builder — defaults when NLP cannot extract a field
# ---------------------------------------------------------------------------
_DEFAULTS = {
    "height":    "average height",
    "element":   "fire",
    "species":   "character",
    "colors":    ["red"],
    "clothing":  ["robes"],
    "equipment": ["sword"],
}


def _count_detected(attributes: dict) -> int:
    """Count how many core attributes are non-null / non-empty."""
    count = 0
    if attributes.get("height"):
        count += 1
    if attributes.get("species"):
        count += 1
    if attributes.get("element"):
        count += 1
    if attributes.get("primary_colors"):
        count += 1
    if attributes.get("clothing"):
        count += 1
    if attributes.get("equipment"):
        count += 1
    return count


def _build_image_prompt(attributes: dict, raw_input: str) -> str:
    """Combine structured NLP attributes with the raw user description.

    Only uses the structured core prompt if more than 4 attributes
    were detected; otherwise falls back to the raw description only.
    """
    detected = _count_detected(attributes)

    if detected > 4:
        height    = attributes.get("height")        or _DEFAULTS["height"]
        species   = attributes.get("species")       or _DEFAULTS["species"]
        element   = attributes.get("element")       or _DEFAULTS["element"]
        primary   = attributes.get("primary_colors") or _DEFAULTS["colors"]
        clothing  = attributes.get("clothing")       or _DEFAULTS["clothing"]
        equipment = attributes.get("equipment")      or _DEFAULTS["equipment"]

        core = (
            f"A {height} {element} {species} wearing {primary[0]} {clothing[0]} "
            f"wielding a {equipment[0]}"
        )
        return system_prompts.prepend_prompt() + core + ". " + raw_input + ". " + system_prompts.append_prompt()
    else:
        # Fallback: raw description only (NLP didn't find enough attributes)
        return system_prompts.prepend_prompt() + raw_input + ". " + system_prompts.append_prompt()


def generate_sprite_sheet(description, save_path, prompt_override=None):
    """Generate a sprite sheet from a character description.

    Args:
        description: Raw user text (used for NLP and JSON output).
        save_path: Where to save the sprite sheet PNG.
        prompt_override: If provided, skip NLP and use this exact prompt
            for Gemini. Used for retry from the preview screen.
    """
    # --- 1. Determine the prompt and run NLP ---
    if prompt_override is not None:
        # Retry path: skip NLP entirely, reuse the already-built prompt
        print(f"Retrying with pre-built prompt (skipping NLP).")
        prompt = prompt_override
        attributes = {}
        game_stats = {}
    else:
        # First-generation path: run NLP pipeline
        print(f"Generating character based on: {description}")

        if _nlp is None:
            print("Warning: NLP model not loaded. Using raw description only.")
            attributes = {}
            game_stats = {}
        else:
            result = generate_json_response(description, _nlp)
            attributes = result["attributes"]
            game_stats = result["game_stats"]
            print("\n=== NLP Attributes ===")
            print(json.dumps(attributes, indent=2))
            print("\n=== Game Stats ===")
            print(json.dumps(game_stats, indent=2))

        # --- 2. Build structured image prompt ---
        prompt = _build_image_prompt(attributes, description)

    print(f"\n=== Image Prompt ===\n{prompt}\n")

    # --- 3. Save the prompt so retries can reuse it ---
    prompt_path = save_path.replace(".png", "_prompt.txt")
    with open(prompt_path, "w") as f:
        f.write(prompt)
    print(f"Prompt saved to: {prompt_path}")

    # --- 4. Call Gemini ---
    client = genai.Client(api_key=gemini_api_key)

    print("Prompt ready, sending to Gemini...")

    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"]
            )
        )

        try:
            for part in response.parts:
                if part.inline_data is not None:
                    raw_image = Image.open(BytesIO(part.inline_data.data))
                    clean_image = raw_image.convert("RGBA")

                    # Refining and resizing the image logic
                    img_w, img_h = clean_image.size
                    grid_cols, grid_rows = 5, 6

                    # Increase the target cell size to 192x192 to ensure that it can get the full image
                    target_cell_size = 192

                    src_cell_w = img_w / grid_cols
                    src_cell_h = img_h / grid_rows

                    # Create the larger final canvas
                    final_sheet = Image.new("RGBA", (grid_cols * target_cell_size, grid_rows * target_cell_size), (0, 0, 0, 0))

                    print(f"Original resolution: {img_w}x{img_h}. Processing frames at {target_cell_size}px...")

                    for row in range(grid_rows):
                        for col in range(grid_cols):
                            # Calculate exact boundaries
                            left = int(round(col * src_cell_w))
                            top = int(round(row * src_cell_h))
                            right = int(round((col + 1) * src_cell_w))
                            bottom = int(round((row + 1) * src_cell_h))

                            tile = clean_image.crop((left, top, right, bottom))

                            # If there is a border around the image then it needs to be deleted
                            tw, th = tile.size
                            if tw > 6 and th > 6:  # Safety check
                                tile = tile.crop((3, 3, tw - 3, th - 3))

                            # Background Removal (Green Screen)
                            datas = tile.getdata()
                            new_data = []
                            for r, g, b, a in datas:
                                if g > r + 45 and g > b + 45:
                                    new_data.append((0, 0, 0, 0))
                                else:
                                    new_data.append((r, g, b, 255))
                            tile.putdata(new_data)

                            # Bounding Box Centering Logic
                            bbox = tile.getbbox()
                            if bbox:
                                # Ignore small noise
                                if (bbox[2] - bbox[0] > 10) and (bbox[3] - bbox[1] > 10):
                                    char_sprite = tile.crop(bbox)
                                    cw, ch = char_sprite.size

                                    # CCenter the image in the target cell
                                    dest_x = (col * target_cell_size) + (target_cell_size // 2) - (cw // 2)
                                    dest_y = (row * target_cell_size) + (target_cell_size // 2) - (ch // 2)

                                    final_sheet.paste(char_sprite, (dest_x, dest_y), char_sprite)

                    backup_directory = os.path.join(os.path.dirname(save_path), "Old Characters")

                    if not os.path.exists(backup_directory):
                        os.makedirs(backup_directory)

                    if os.path.exists(save_path):
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                        backup_filename = f"custome_skin_backup_{timestamp}.png"
                        backup_path = os.path.join(backup_directory, backup_filename)

                        shutil.move(save_path, backup_path)
                        print("Moved old skin to backups folder")

                    # Save sprite sheet
                    final_sheet.save(save_path, format="PNG")

                    # --- 5. Save companion JSON with NLP attributes and game stats ---
                    # Only on first generation (retry would have empty attributes)
                    if attributes or game_stats:
                        json_path = save_path.replace(".png", ".json")
                        with open(json_path, "w") as f:
                            json.dump({
                                "attributes": attributes,
                                "game_stats": game_stats,
                                "input_text": description
                            }, f, indent=2)
                        print(f"Stats saved to: {json_path}")

                    print(f"Success! {target_cell_size}px sprite sheet saved to: {save_path}")

                elif part.text is not None:
                    print(f"API returned text: {part.text}")

        except Exception as e:
            print(f"Error processing and saving: {e}")

    except Exception as e:
        print(f"Error during API call: {e}")


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        user_input = sys.argv[1]
        save_path = sys.argv[2]
        # Optional third arg: --reuse-prompt to skip NLP and read the saved prompt
        reuse_prompt = len(sys.argv) >= 4 and sys.argv[3] == "--reuse-prompt"

        if reuse_prompt:
            prompt_path = save_path.replace(".png", "_prompt.txt")
            if os.path.exists(prompt_path):
                with open(prompt_path) as f:
                    saved_prompt = f.read()
                generate_sprite_sheet(user_input, save_path, prompt_override=saved_prompt)
            else:
                print(f"Error: Saved prompt not found at {prompt_path}")
        else:
            generate_sprite_sheet(user_input, save_path)
    else:
        print("Error: Missing arguments.")
