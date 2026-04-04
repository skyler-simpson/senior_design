"""
Character NER Training Pipeline
Trains a spaCy model to extract character attributes from text.
"""

import random

import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding

from character_ner_training_data import TRAINING_DATA, validate_training_data

# All entity labels (must match training data)
NER_LABELS = [
    "HEIGHT",
    "SPECIES",
    "ELEMENT",
    "PRIMARY_COLOR",
    "SECONDARY_COLOR",
    "CLOTHING",
    "EQUIPMENT",
]


def train_ner_model(output_path="./character_ner_model", num_epochs=250):
    """
    Train a spaCy NER model.

    Args:
        output_path: Where to save model
        num_epochs: Training epochs (100–200 recommended for convergence on small data)
    """

    validate_training_data(TRAINING_DATA)

    print("=" * 70)
    print("TRAINING CHARACTER NER MODEL")
    print("=" * 70)

    print("\n1. Creating blank spaCy model...")
    nlp = spacy.blank("en")
    print("   ✓ Created")

    print("2. Adding NER component...")
    ner = nlp.add_pipe("ner", last=True)
    print("   ✓ Added")

    print("3. Adding entity labels...")
    for label in NER_LABELS:
        ner.add_label(label)
    print(f"   ✓ Added {len(NER_LABELS)} labels")

    print("\n4. Preparing training data...")
    training_examples = []
    for text, annotations in TRAINING_DATA:
        example = Example.from_dict(nlp.make_doc(text), annotations)
        training_examples.append(example)

    print(f"   ✓ Created {len(training_examples)} training examples")

    print("5. Initializing NER component...")
    ner.initialize(lambda: training_examples)
    print("   ✓ Initialized")

    print(f"\n6. Training model ({num_epochs} epochs)...")
    print("   (Loss should decrease over time)")
    print()

    optimizer = nlp.create_optimizer()

    for epoch in range(num_epochs):
        losses = {}
        random.shuffle(training_examples)
        nlp.update(
            training_examples,
            drop=0.35,
            sgd=optimizer,
            losses=losses,
        )

        if (epoch + 1) % 10 == 0 or epoch == 0:
            loss_val = losses.get("ner", 0)
            print(f"   Epoch {epoch + 1:3d}/{num_epochs} - Loss: {loss_val:8.4f}")

    print(f"\n7. Saving model to {output_path}...")
    nlp.to_disk(output_path)
    print("   ✓ Model saved!")

    print("\n" + "=" * 70)
    print("TRAINING COMPLETE!")
    print("=" * 70)
    print("\nNext step:")
    print("  python character_ner_inference.py")

    return nlp


if __name__ == "__main__":
    model = train_ner_model(num_epochs=250)
    print("\n✓ Ready to use with character_ner_inference.py")
