import json
import os
import sys

API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "semanticshelf-api"))
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

import torch
import torch.nn as nn
import torch.optim as optim

from app.ml.model import BookGenreLMHead

def main():
    script_dir = os.path.dirname(__file__)
    ml_dir = os.path.join(API_DIR, "app", "ml")

    dataset_path = os.path.join(script_dir, "dataset.json")
    genres_path = os.path.join(ml_dir, "genres.json")
    model_output_path = os.path.join(ml_dir, "model.pt")

    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    with open(genres_path, 'r', encoding='utf-8') as f:
        genres = json.load(f)

    train_samples = [x for x in dataset if x['split'] == 'train']
    test_samples = [x for x in dataset if x['split'] == 'test']

    X_train = torch.tensor([x['embedding'] for x in train_samples], dtype=torch.float32)
    y_train = torch.tensor([x['genre_id'] for x in train_samples], dtype=torch.long)

    X_test = torch.tensor([x['embedding'] for x in test_samples], dtype=torch.float32)
    y_test = torch.tensor([x['genre_id'] for x in test_samples], dtype=torch.long)

    model = BookGenreLMHead(input_dim=384, num_classes=len(genres), hidden_dim=128)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=0.002, weight_decay=1e-4)

    model.train()
    for _ in range(150):
        optimizer.zero_grad()
        loss = criterion(model(X_train), y_train)
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        preds = torch.argmax(model(X_test), dim=1)
        acc = (preds == y_test).float().mean().item()

    torch.save(model.state_dict(), model_output_path)

    print(f"Dataset: {len(dataset)} books ({len(train_samples)} train, {len(test_samples)} test)")
    print(f"Test Accuracy: {acc * 100:.1f}%")
    print(f"Saved weights to {model_output_path}")

if __name__ == '__main__':
    main()
