import os, pixellab, requests, time
from dotenv import load_dotenv

load_dotenv()
pixel_lab_api_key = os.getenv('PIXEL_LAB_API_KEY')
BASE_URL = "https://api.pixellab.ai/v2"
headers = {
            "Authorization": f"Bearer {pixel_lab_api_key}",
            "Content-Type": "application/json"
          }

def generate_static_sprite():

    desc1 = 'Game sprite sheet with animation frames and character poses, ' \
            'pixel art or 2D game asset collection showing movement cycles, ' \
            'organized sprite layout for game development, retro gaming graphics ' \
            'perfect for indie games and platformers. the sprite should be that of ' \
            'a ninja with fire powers. include frames of the ninja shooting a fireball from all angles'

    # description = '2D game sprite sheet with animation frames and character poses. Sheet should' \
                #   'be organized for game development. Sprite should be that of a ninja with' \
                #   'fire powers. Include frames of the ninja from all angles.'

    client = pixellab.Client(secret=pixel_lab_api_key)
    response = client.generate_image_pixflux(
        description = desc1,
        image_size=dict(width=200, height=200),
        no_background=True,
        
    )
    print(response.model_config)
    sprite = response.image.pil_image()
    sprite.show()
    sprite.save('sprite-sheet.png')
    # sprite.save('.\sprite-gen-test.py\sprite.png')

def character_in_4_directions():
    print('generating sprite in 4 directions...')
    
    response = requests.post(f"{BASE_URL}/create-character-with-4-directions",
    headers=headers,
    json={
            "description": "small nimble archer wearing green hood, quiver on back, lean build, pixel art, 8-bit style", # got description from chatgpt
            "image_size": {"width": 64, "height": 64},
            "text_guidance_scale": 10,
            "outline": "thin",
            "shading": "flat",
            "detail": "low",
            "seed": 12345
        }
    )
    print("status: ", response.status_code)
    print("response: ", response.text)

    response.raise_for_status()
    data = response.json()
    print(f"data: {data}")

    background_job_id = data.get("background_job_id")
    print(f"Job submitted: {background_job_id}")

    # Poll for job completion. Just checks status of job every 15 sec until it is complete (images created)
    # NOTE: (from gpt)
    while True:
        job = requests.get(f"{BASE_URL}/background-jobs/{background_job_id}", headers=headers).json()
        status = job.get("status")
        print("Job status:", status)
        if status == "completed":
            print("job.json(): ", job)
            print(job.keys())
            character_id = data["character_id"]
            break
        elif status == "failed":
            print("Job failed:", job)
            return
        time.sleep(15)

    # images are stored in zip
    result = requests.get(f"{BASE_URL}/characters/{character_id}/zip", headers=headers)
    with open("sprite_sheet.zip", "wb") as f:
        f.write(result.content)
    print("Sprite sheet saved as sprite_sheet.zip")

character_in_4_directions()