# PixelForge User Manual

## Project Team & Project Description
Read more about the development team behind PixelForge and what the project is [here](https://github.com/skyler-simpson/senior_design)!

## At a high level, how does PixelForge work?
![alt text](design_diagrams/image-2.png)

The image above is the design diagram for our project. It is read from left to right, starting with the red input square. As stated, you, the user, is prompted to describe your character and its abilities. This description is then sent to our Natural Language Processing (NLP) model.

The NLP model reads what you've inputted and then writes a description of its own. This description is everything the model thinks is important/relevant to generating your described character. It's important to have the NLP model as its generated description is phrased in a way that makes it easy for the sprite generation model to build your characer.

Once we get the NLP model's description, the sprite generation model uses Google's Nano Banana to generate the sprite sheet. This sprite sheet (examples below) is a PNG file which contains images of the character performing different actions (walking, running, jumping, etc). This sprite sheet is then sent over to the game platform.

The game platform is built on an engine called GoDot. It is a free, open-source game engine that is used to develop 2D or 3D games. It is used to build out the minigame that the user will be able to interact with. As input, it takes in the sprite sheet from the NLP model and uses it to render the character in the minigame.

Once the character is rendered, users will be able to play in the 2D minigame with the character that they described in the beginning.

## Examples of sprite sheets
![alt text](<src/Sprite Generation/generated-sprites/gemini_sprite_sheets/gemini_sprite_sheet_fire_ninja.png>)
![alt text](<src/Sprite Generation/generated-sprites/gemini_sprite_sheets/gemini_sprite_sheet_water_wizard.png>)
![alt text](<src/Sprite Generation/generated-sprites/gemini_sprite_sheets/gemini_sprite_sheet_dbz.png>)

## FAQ