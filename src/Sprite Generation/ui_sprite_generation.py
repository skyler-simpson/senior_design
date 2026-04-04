import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests, os, time, datetime, io, base64, shutil, sys, json
from dotenv import load_dotenv
import system_prompts
import google.generativeai as genai

# ---------------------------------------------------------------------------
# Import NLP pipeline (add parent dir so we can find the NLP Model package)
# ---------------------------------------------------------------------------
NLP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "NLP Model")
sys.path.insert(0, NLP_DIR)
from character_ner_inference import load_model, generate_json_response

load_dotenv()
# PixelLab API — commented out for reference
# pixel_lab_api_key = os.getenv('PIXEL_LAB_API_KEY')
# BASE_URL = "https://api.pixellab.ai/v2"
# headers = {
#     "Authorization": f"Bearer {pixel_lab_api_key}",
#     "Content-Type": "application/json"
# }
gemini_api_key = os.getenv('GEMINI_API_KEY')

# ---------------------------------------------------------------------------
# Load the NLP model once at startup
# ---------------------------------------------------------------------------
_nlp = load_model()

# ---------------------------------------------------------------------------
# Image-prompt builder — turns NLP attributes into a structured image prompt
# ---------------------------------------------------------------------------

# Defaults used when the NLP model cannot extract a field
_DEFAULTS = {
    "height":    "average height",
    "element":   "fire",
    "species":   "character",
    "colors":    ["red"],
    "clothing":  ["robes"],
    "equipment": ["sword"],
}


def build_image_prompt(attributes: dict, raw_input: str) -> str:
    """Build a structured sprite-sheet image prompt from NLP-extracted fields,
    falling back to sensible defaults when an attribute is missing."""

    height    = attributes.get("height")        or _DEFAULTS["height"]
    species   = attributes.get("species")       or _DEFAULTS["species"]
    element   = attributes.get("element")       or _DEFAULTS["element"]
    primary   = attributes.get("primary_colors") or _DEFAULTS["colors"]
    clothing  = attributes.get("clothing")       or _DEFAULTS["clothing"]
    equipment = attributes.get("equipment")      or _DEFAULTS["equipment"]

    # Assemble a concise visual description from structured fields
    core = (
        f"A {height} {element} {species} wearing {primary[0]} {clothing[0]} "
        f"wielding a {equipment[0]}"
    )

    # Combine: prepend prompt + structured core + raw user phrasing for flavour
    prompt = (
        f"{system_prompts.prepend_prompt()} "
        f"{core}. {raw_input}. "
        f"The character must remain visually consistent across all frames. "
        f"Art style must be crisp pixel art suitable for immediate use in a game engine."
    )
    return prompt


# ---------------------------------------------------------------------------
# Sprite generation (Gemini path — NLP-enhanced)
# ---------------------------------------------------------------------------

def generate_sprite_sheet():
    description = text_input.get("1.0", tk.END).strip()
    if not description:
        messagebox.showerror("Error", "Please enter a character description!!")
        return

    if _nlp is None:
        messagebox.showerror("Error", "NLP model failed to load. "
                             "Run character_ner_trainer.py first.")
        return

    status_label.config(text="Extracting attributes via NLP…")
    root.update_idletasks()

    # 1. Run NLP pipeline → stats + structured attributes
    result = generate_json_response(description, _nlp)
    attributes = result["attributes"]
    game_stats = result["game_stats"]

    # Print for debugging / poster
    print("\n=== NLP Attributes ===")
    print(json.dumps(attributes, indent=2))
    print("\n=== Game Stats ===")
    print(json.dumps(game_stats, indent=2))

    # 2. Build a structured image prompt for Gemini
    image_prompt = build_image_prompt(attributes, description)
    print(f"\n=== Image Prompt ===\n{image_prompt}\n")

    # 3. Call Gemini to generate the sprite sheet
    status_label.config(text="Generating sprite sheet via Gemini…")
    root.update_idletasks()

    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel(model_name='gemini-3-pro-image-preview')
    response = model.generate_content(image_prompt)

    print(f"Response parts: {len(response.parts)}")
    print(f"Has inline_data: {any(p.inline_data is not None for p in response.parts)}")
    for part in response.parts:
        if part.text == '' and part.inline_data is not None:
            try:
                print(f"Mime type: {part.inline_data.mime_type}")

                # Get the data - it might be base64 encoded
                image_data = part.inline_data.data

                # if it's bytes, try to use directly
                if isinstance(image_data, bytes):
                    image = Image.open(io.BytesIO(image_data))
                else:
                    # if it's a string, decode from base64
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(image_bytes))

                # save generated image
                save_path = os.path.abspath("gemini_sprite_sheet.png")
                image.save(save_path)
                print(f"Image saved to: {save_path}")

            except Exception as e:
                print(f"Error processing image: {e}")
                print(f"Data type: {type(image_data)}")
                print(f"Data length: {len(image_data) if hasattr(image_data, '__len__') else 'N/A'}")
        elif part.text is not None:
            print(part.text)


'''PIXEL LAB API
    prompt = system_prompts.prepend_prompt() + description

    print(prompt)

    client = pixellab.Client(secret=pixel_lab_api_key)
    response = client.generate_image_pixflux(
        description = prompt,
        image_size=dict(width=200, height=200),
        no_background=True,
    )
    print(response.model_config)
    sprite = response.image.pil_image()
    sprite.show()
    sprite.save('sprite-sheet.png')

    status_label.config(text="Sprite Sheet Generated (saved as sprite-sheet.png)!")
'''

# --- UI Setup ---
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
