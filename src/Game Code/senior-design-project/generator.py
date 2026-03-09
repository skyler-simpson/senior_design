import sys
import os
import system_prompts
from google import genai
from google.genai import types
from dotenv import load_dotenv

from PIL import Image
from io import BytesIO

load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')
 
def generate_sprite_sheet(description, save_path):
    print(f"Generating character based on: {description}")

    client = genai.Client(api_key=gemini_api_key)

    prompt = system_prompts.prepend_prompt() + description + system_prompts.append_prompt()
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
                    
                    # --- THE NEW AUTO-CROP & RESIZE LOGIC ---
                    orig_width, orig_height = clean_image.size
                    
                    # 1. Calculate the true width of the 5x6 grid
                    frame_size = orig_height / 6
                    grid_width = int(frame_size * 5)
                    
                    # 2. Crop out the extra right-side background: (left, top, right, bottom)
                    cropped_image = clean_image.crop((0, 0, grid_width, orig_height))
                    
                    # 3. Resize the cleanly cropped grid to Godot's exact dimensions
                    final_image = cropped_image.resize((640, 768), Image.NEAREST)
                    
                    # 4. Save it!
                    final_image.save(save_path, format="PNG")
                    print(f"Success! Game-ready image saved to: {save_path}")
                    
                elif part.text is not None:
                    print(f"API returned text instead of an image: {part.text}")
                    
        except Exception as e:
            print(f"Error processing and saving the image: {e}")
                
    except Exception as e:
        print(f"Error during API call: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        user_input = sys.argv[1]
        save_path = sys.argv[2] 
        generate_sprite_sheet(user_input, save_path)
    else:
        print("Error: Missing arguments from Godot.")
