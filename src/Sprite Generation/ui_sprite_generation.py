import os
import tkinter as tk
import system_prompts
from google import genai
from google.genai import types
from tkinter import messagebox
from PIL import Image, ImageTk
import os, io, base64, sys, json
from dotenv import load_dotenv
import system_prompts

from google import genai

# ---------------------------------------------------------------------------
# Import NLP pipeline
# ---------------------------------------------------------------------------
NLP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "NLP Model"
)
sys.path.insert(0, NLP_DIR)

from character_ner_inference import load_model, generate_json_response

# ---------------------------------------------------------------------------
# Load environment + NLP
# ---------------------------------------------------------------------------
load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')

_nlp = load_model()

# ---------------------------------------------------------------------------
# Defaults for missing NLP fields
# ---------------------------------------------------------------------------
_DEFAULTS = {
    "height": "average height",
    "element": "fire",
    "species": "character",
    "colors": ["red"],
    "clothing": ["robes"],
    "equipment": ["sword"],
}

# ---------------------------------------------------------------------------
# Prompt Builder
# ---------------------------------------------------------------------------
def build_image_prompt(attributes: dict, raw_input: str) -> str:
    height = attributes.get("height") or _DEFAULTS["height"]
    species = attributes.get("species") or _DEFAULTS["species"]
    element = attributes.get("element") or _DEFAULTS["element"]
    primary = attributes.get("primary_colors") or _DEFAULTS["colors"]
    clothing = attributes.get("clothing") or _DEFAULTS["clothing"]
    equipment = attributes.get("equipment") or _DEFAULTS["equipment"]

    core = (
        f"A {height} {element} {species} wearing {primary[0]} {clothing[0]} "
        f"wielding a {equipment[0]}"
    )

    prompt = (
        f"{system_prompts.prepend_prompt()} "
        f"{core}. "
        f"The character must remain visually consistent across all frames. "
        f"Art style must be crisp pixel art suitable for immediate use in a game engine."
    )
    return prompt

def generate_image(prompt: str):
    client = genai.Client(api_key=gemini_api_key)

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=prompt
    )

    for candidate in response.candidates:
        for part in candidate.content.parts:

            if hasattr(part, "inline_data") and part.inline_data:
                try:
                    image_data = part.inline_data.data

                    if isinstance(image_data, bytes):
                        return Image.open(io.BytesIO(image_data))
                    else:
                        image_bytes = base64.b64decode(image_data)
                        return Image.open(io.BytesIO(image_bytes))

                except Exception as e:
                    print(f"Error decoding image: {e}")

            elif hasattr(part, "text") and part.text:
                print("Model text response:", part.text)

    return None

# ---------------------------------------------------------------------------
# Main Sprite Generation Function
# ---------------------------------------------------------------------------
def generate_sprite_sheet():
    description = text_input.get("1.0", tk.END).strip()

    if not description:
        messagebox.showerror("Error", "Please enter a character description!")
        return

    if _nlp is None:
        messagebox.showerror("Error", "NLP model failed to load.")
        return

    status_label.config(text="Extracting attributes via NLP…")
    root.update_idletasks()

    # 1. NLP Processing
    result = generate_json_response(description, _nlp)
    attributes = result["attributes"]
    game_stats = result["game_stats"]

    print("\n=== NLP Attributes ===")
    print(json.dumps(attributes, indent=2))

    print("\n=== Game Stats ===")
    print(json.dumps(game_stats, indent=2))

    # 2. Build Prompt
    image_prompt = build_image_prompt(attributes, description)

    print("\n=== Image Prompt ===")
    print(image_prompt)

    # 3. Generate Image
    status_label.config(text="Generating sprite sheet via Gemini…")
    root.update_idletasks()

    image = generate_image(image_prompt)

    if image:
        save_path = os.path.abspath("gemini_sprite_sheet.png")
        image.save(save_path)

        status_label.config(text=f"Saved: {save_path}")
        print(f"Image saved to: {save_path}")
    else:
        status_label.config(text="Failed to generate image.")
        messagebox.showerror("Error", "Image generation failed.")

# ---------------------------------------------------------------------------
# UI Setup
# ---------------------------------------------------------------------------
root = tk.Tk()
root.title("AI Character Sprite Generator")

label = tk.Label(root, text="Describe your game character:")
label.pack()

text_input = tk.Text(root, height=5, width=50)
text_input.pack()

button = tk.Button(root, text="Generate Sprite", command=generate_sprite_sheet)
button.pack()

status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()