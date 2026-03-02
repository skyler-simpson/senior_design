"""
Character NER Training Pipeline
Trains a spaCy model to extract character attributes from text
"""

import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
import random
import json

# TRAINING DATA - Example sentences with labeled entities

TRAINING_DATA = [
    # Height examples
    ("A tall wizard", {"entities": [(2, 6, "HEIGHT")]}),
    ("A short dwarf", {"entities": [(2, 7, "HEIGHT")]}),
    ("An average human", {"entities": [(3, 10, "HEIGHT")]}),
    ("A towering giant", {"entities": [(2, 10, "HEIGHT")]}),
    ("A tiny fairy", {"entities": [(2, 6, "HEIGHT")]}),
    ("Very tall knight", {"entities": [(5, 9, "HEIGHT")]}),
    
    # Species/Class examples
    ("A wizard", {"entities": [(2, 8, "SPECIES")]}),
    ("An elf warrior", {"entities": [(3, 6, "SPECIES")]}),
    ("A dwarf", {"entities": [(2, 7, "SPECIES")]}),
    ("An orc", {"entities": [(3, 6, "SPECIES")]}),
    ("A mage", {"entities": [(2, 6, "SPECIES")]}),
    ("A knight", {"entities": [(2, 8, "SPECIES")]}),
    ("A rogue", {"entities": [(2, 7, "SPECIES")]}),
    ("A paladin", {"entities": [(2, 9, "SPECIES")]}),
    
    # Element examples
    ("An ice mage", {"entities": [(3, 6, "ELEMENT")]}),
    ("A fire wizard", {"entities": [(2, 6, "ELEMENT")]}),
    ("A lightning sorcerer", {"entities": [(2, 11, "ELEMENT")]}),
    ("A dark knight", {"entities": [(2, 6, "ELEMENT")]}),
    ("An earth elemental", {"entities": [(3, 8, "ELEMENT")]}),
    ("A water mage", {"entities": [(2, 7, "ELEMENT")]}),
    
    # Color examples
    ("Wearing purple robes", {"entities": [(8, 14, "PRIMARY_COLOR")]}),
    ("With blue armor", {"entities": [(5, 9, "PRIMARY_COLOR")]}),
    ("Red cloak", {"entities": [(0, 3, "PRIMARY_COLOR")]}),
    ("Silver sword", {"entities": [(0, 6, "PRIMARY_COLOR")]}),
    ("Black boots", {"entities": [(0, 5, "PRIMARY_COLOR")]}),
    ("Golden crown", {"entities": [(0, 6, "PRIMARY_COLOR")]}),
    ("Green tunic", {"entities": [(0, 5, "PRIMARY_COLOR")]}),
    
    # Clothing examples
    ("Wearing robes", {"entities": [(8, 13, "CLOTHING")]}),
    ("Purple dress", {"entities": [(0, 6, "CLOTHING")]}),
    ("Iron armor", {"entities": [(5, 10, "CLOTHING")]}),
    ("Leather jacket", {"entities": [(0, 6, "CLOTHING")]}),
    ("Silk cloak", {"entities": [(0, 4, "CLOTHING")]}),
    ("Steel plate", {"entities": [(0, 5, "CLOTHING")]}),
    
    # Equipment examples
    ("Carrying a staff", {"entities": [(11, 16, "EQUIPMENT")]}),
    ("With a sword", {"entities": [(7, 12, "EQUIPMENT")]}),
    ("Holding a bow", {"entities": [(9, 12, "EQUIPMENT")]}),
    ("A magical wand", {"entities": [(10, 14, "EQUIPMENT")]}),
    ("A glowing shield", {"entities": [(10, 16, "EQUIPMENT")]}),
    ("Dual swords", {"entities": [(5, 11, "EQUIPMENT")]}),
    
    # Trait examples
    ("Looks ethereal", {"entities": [(6, 13, "SPECIAL_TRAIT")]}),
    ("Appears magical", {"entities": [(8, 15, "SPECIAL_TRAIT")]}),
    ("Seems fierce", {"entities": [(6, 11, "SPECIAL_TRAIT")]}),
    ("Very noble", {"entities": [(5, 10, "SPECIAL_TRAIT")]}),
    ("Glowing aura", {"entities": [(0, 7, "SPECIAL_TRAIT")]}),
    ("Shimmering", {"entities": [(0, 10, "SPECIAL_TRAIT")]}),
    
    # COMBINED EXAMPLES
    ("A tall ice wizard with purple robes and a glowing staff", {
        "entities": [
            (2, 6, "HEIGHT"),
            (7, 10, "ELEMENT"),
            (11, 16, "SPECIES"),
            (22, 28, "PRIMARY_COLOR"),
            (29, 34, "CLOTHING"),
            (41, 48, "SPECIAL_TRAIT"),
            (49, 54, "EQUIPMENT")
        ]
    }),
    ("A short fire dwarf carrying a golden axe", {
        "entities": [
            (2, 7, "HEIGHT"),
            (8, 12, "ELEMENT"),
            (13, 18, "SPECIES"),
            (31, 37, "PRIMARY_COLOR"),
            (38, 41, "EQUIPMENT")
        ]
    }),
    ("An average human with dark armor and a sword", {
        "entities": [
            (3, 10, "HEIGHT"),
            (11, 16, "SPECIES"),
            (22, 26, "PRIMARY_COLOR"),
            (27, 32, "CLOTHING"),
            (39, 44, "EQUIPMENT")
        ]
    }),
    ("A towering orc warrior with green skin", {
        "entities": [
            (2, 10, "HEIGHT"),
            (11, 14, "SPECIES"),
            (28, 33, "PRIMARY_COLOR"),
        ]
    }),
    ("A lightning mage in blue robes with a staff", {
        "entities": [
            (2, 11, "ELEMENT"),
            (12, 16, "SPECIES"),
            (20, 24, "PRIMARY_COLOR"),
            (25, 30, "CLOTHING"),
            (39, 44, "EQUIPMENT")
        ]
    }),
    ("An ethereal elf archer with a bow", {
        "entities": [
            (3, 10, "SPECIAL_TRAIT"),
            (11, 14, "SPECIES"),
            (15, 21, "SPECIES"),
            (31, 34, "EQUIPMENT"),
        ]
    }),
    ("A dark vampire in black leather with crimson eyes", {
        "entities": [
            (2, 6, "ELEMENT"),
            (7, 14, "SPECIES"),
            (18, 23, "PRIMARY_COLOR"),
            (24, 30, "CLOTHING"),
            (36, 43, "PRIMARY_COLOR")
        ]
    }),
    ("Tall noble knight with silver armor", {
        "entities": [
            (0, 4, "HEIGHT"),
            (5, 10, "SPECIAL_TRAIT"),
            (11, 16, "SPECIES"),
            (22, 28, "PRIMARY_COLOR"),
            (29, 34, "CLOTHING")
        ]
    }),
    ("A fast rogue with twin daggers", {
        "entities": [
            (2, 6, "SPECIAL_TRAIT"),
            (7, 11, "SPECIES"),
            (17, 21, "EQUIPMENT")
        ]
    }),
    ("Slow heavy paladin in golden plate armor", {
        "entities": [
            (0, 4, "SPECIAL_TRAIT"),
            (5, 10, "SPECIAL_TRAIT"),
            (11, 18, "SPECIES"),
            (22, 28, "PRIMARY_COLOR"),
            (29, 33, "CLOTHING")
        ]
    }),
]

# TRAINING FUNCTION

def train_ner_model(output_path="./character_ner_model"):
    """
    Train a spaCy NER model on character descriptions
    
    Args:
        output_path: Where to save the trained model
    """
    
    print("=" * 60)
    print("TRAINING CHARACTER NER MODEL")
    print("=" * 60)
    
    # Create blank English model
    print("\n1. Creating blank spaCy model...")
    nlp = spacy.blank("en")
    
    # Add NER pipeline component
    print("2. Adding NER component...")
    ner = nlp.add_pipe("ner", last=True)
    
    # Add labels
    print("3. Adding entity labels...")
    labels = ["HEIGHT", "SPECIES", "ELEMENT", "PRIMARY_COLOR", "SECONDARY_COLOR", 
              "CLOTHING", "EQUIPMENT", "SPECIAL_TRAIT"]
    for label in labels:
        ner.add_label(label)
    
    # Convert training data to spaCy format
    print("4. Preparing training data...")
    training_examples = []
    for text, annotations in TRAINING_DATA:
        example = Example.from_dict(nlp.make_doc(text), annotations)
        training_examples.append(example)
    
    print(f"   Created {len(training_examples)} training examples")
    
    # Initialize the NER component with examples
    # This is critical - it tells spaCy what transitions are possible
    print("4.5. Initializing NER component...")
    ner.initialize(lambda: training_examples)
    
    # Training loop
    print("5. Training model...")
    optimizer = nlp.create_optimizer()
    
    # Train for multiple epochs
    n_epochs = 30
    for epoch in range(n_epochs):
        losses = {}
        
        # Shuffle data each epoch
        random.shuffle(training_examples)
        
        # Update model
        nlp.update(
            training_examples,
            drop=0.5,
            sgd=optimizer,
            losses=losses
        )
        
        if (epoch + 1) % 10 == 0:
            print(f"   Epoch {epoch + 1}/{n_epochs} - Loss: {losses.get('ner', 0):.4f}")
    
    # Save model
    print(f"\n6. Saving model to {output_path}...")
    nlp.to_disk(output_path)
    print("   ✓ Model saved!")
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    
    return nlp


if __name__ == "__main__":
    model = train_ner_model()
    print("\nYou can now use this model in character_ner_inference.py")