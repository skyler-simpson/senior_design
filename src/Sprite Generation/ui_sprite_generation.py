import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests, os, time
from dotenv import load_dotenv

load_dotenv()
pixel_lab_api_key = os.getenv('PIXEL_LAB_API_KEY')
BASE_URL = "https://api.pixellab.ai/v2"
headers = {
    "Authorization": f"Bearer {pixel_lab_api_key}",
    "Content-Type": "application/json"
}

def generate_sprite():
    description = text_input.get("1.0", tk.END).strip()
    if not description:
        messagebox.showerror("Error", "Please enter a character description.")
        return

    status_label.config(text="Generating sprite…")
    root.update_idletasks()

    payload = {
        "description": description,
        "image_size": {"width": 64, "height": 64},
        "text_guidance_scale": 10,
        "outline": "thin",
        "shading": "flat",
        "detail": "low",
        "seed": 12345
    }

    response = requests.post(f"{BASE_URL}/create-character-with-4-directions",
                             headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    background_job_id = data["background_job_id"]

    # Poll for completion
    while True:
        job = requests.get(f"{BASE_URL}/background-jobs/{background_job_id}",
                           headers=headers).json()
        if job["status"] == "completed":
            character_id = data["character_id"]
            break
        time.sleep(5)

    # Download zip → just show a placeholder image for now
    result = requests.get(f"{BASE_URL}/characters/{character_id}/zip", headers=headers)
    with open("sprite_sheet.zip", "wb") as f:
        f.write(result.content)

    # Show success
    status_label.config(text="Sprite Sheet Generated (saved as sprite_sheet.zip)!")

# --- UI Setup ---
root = tk.Tk()
root.title("AI Character Sprite Generator")

label = tk.Label(root, text="Describe your game character:")
label.pack()

text_input = tk.Text(root, height=5, width=50)
text_input.pack()

button = tk.Button(root, text="Generate Sprite", command=generate_sprite)
button.pack()

status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()
