import os
import timm
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import transforms
from torchvision.datasets import ImageFolder
from torch.optim import AdamW
from tqdm import tqdm

DATA_DIR = "detector/PlantVillage2"  # your dataset root
SAVE_DIR = "detector/model"
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 15
MODEL_NAME = "efficientnet_b0"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Create save folder if missing
os.makedirs(SAVE_DIR, exist_ok=True)

# Transforms
train_tfms = transforms.Compose([
    transforms.RandomResizedCrop(IMG_SIZE),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(0.2, 0.2, 0.2, 0.1),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

val_tfms = transforms.Compose([
    transforms.Resize(int(IMG_SIZE * 1.2)),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# Load datasets (must follow ImageFolder structure)
train_ds = ImageFolder(os.path.join(DATA_DIR, "train"), train_tfms)
val_ds   = ImageFolder(os.path.join(DATA_DIR, "val"), val_tfms)

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
val_loader   = DataLoader(val_ds, batch_size=BATCH_SIZE)

# Number of classes
NUM_CLASSES = len(train_ds.classes)

# Save label file
with open(os.path.join(SAVE_DIR, "labels.txt"), "w") as f:
    for cls in train_ds.classes:
        f.write(cls + "\n")

print("Generated labels:", train_ds.classes)

# Load model
model = timm.create_model(MODEL_NAME, pretrained=True, num_classes=NUM_CLASSES)
model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = AdamW(model.parameters(), lr=1e-4)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

best_val = 0.0

# Training Loop
for epoch in range(EPOCHS):
    model.train()
    pbar = tqdm(train_loader, desc=f"Epoch {epoch + 1}/{EPOCHS}")

    for imgs, labels in pbar:
        imgs, labels = imgs.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        pbar.set_postfix(loss=float(loss))

    # Validation
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs)
            preds = outputs.argmax(1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    val_acc = correct / total
    print(f"Validation Accuracy: {val_acc:.4f}")

    if val_acc > best_val:
        best_val = val_acc
        torch.save(model.state_dict(), os.path.join(SAVE_DIR, "best_model.pth"))
        print("🔥 Saved New Best Model")

print("Training Complete.")
