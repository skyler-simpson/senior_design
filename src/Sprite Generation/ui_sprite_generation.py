import os
import tkinter as tk
import system_prompts
from google import genai
from google.genai import types
from tkinter import messagebox
from PIL import Image, ImageTk
from dotenv import load_dotenv

load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')

def generate_sprite_sheet():
    description = text_input.get("1.0", tk.END).strip()
    if not description:
        messagebox.showerror("Error", "Please enter a character description!!")
        return

    status_label.config(text="Generating sprite…")
    root.update_idletasks()

    client = genai.Client(api_key=gemini_api_key)

    # appending and prepending system prompt to user's character description
    prompt = system_prompts.prepend_prompt() + description + system_prompts.append_prompt()
    print(prompt)

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[prompt],
    )

    try: 
        for part in response.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                try:
                    image = part.as_image()
                    image.save("generated-sprites\gemini_sprite_sheets\gemini_sprite_sheet.png")
                except Exception as e:
                    print(f"Error processing image: {e}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Reason for API Failure: {response.candidates[0].finish_reason}")



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
