import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests, os, time, pixellab, datetime, io, base64, shutil
from dotenv import load_dotenv
import system_prompts
import google.generativeai as genai

load_dotenv()
pixel_lab_api_key = os.getenv('PIXEL_LAB_API_KEY')
gemini_api_key = os.getenv('GEMINI_API_KEY')
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
        time.sleep(15)

    # Download zip → just show a placeholder image for now
    result = requests.get(f"{BASE_URL}/characters/{character_id}/zip", headers=headers)
    with open("sprite_sheet.zip", "wb") as f:
        f.write(result.content)

    # Show success
    status_label.config(text="Sprite Sheet Generated (saved as sprite_sheet.zip)!")

def generate_sprite_sheet():
    description = text_input.get("1.0", tk.END).strip()
    if not description:
        messagebox.showerror("Error", "Please enter a character description!!")
        return

    status_label.config(text="Generating sprite…")
    root.update_idletasks()

    # appending and prepending system prompt to user's character description
    prompt = system_prompts.prepend_prompt() + description
    
    print(prompt)

    genai.configure(api_key=gemini_api_key)
    # model = genai.GenerativeModel(model_name='gemini-3-pro-image-preview')
    model = genai.GenerativeModel(model_name='gemini-2.5-flash')
    response = model.generate_content(prompt)

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
                # os.rename(save_path, 'src/Sprite Generation/generated-sprites/gemini_sprite_sheets/')
                # image.save("src/Sprite Generation/generated-sprites/gemini_sprite_sheets/gemini_sprite_sheet.png")
                image.save(save_path)
                # shutil.move(save_path, "src/Sprite Generation/generated-sprites/gemini_sprite_sheets/")
                print(f"Image saved to: {save_path}")
                
            except Exception as e:
                print(f"Error processing image: {e}")
                print(f"Data type: {type(image_data)}")
                print(f"Data length: {len(image_data) if hasattr(image_data, '__len__') else 'N/A'}")
        elif part.text is not None:
            print(part.text)

'''PIXEL LAB API
    # appending and prepending system prompt to user's character description
    prompt = system_prompts.prepend_prompt() \
            + description
            # + "Generate the following sprite: " \
    #         + system_prompts.append_prompt()
    
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
