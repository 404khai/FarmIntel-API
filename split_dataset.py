# split_dataset.py

import os
import shutil
import random
from pathlib import Path

DATASET_DIR = "detector/PlantVillage"   # your original downloaded dataset
OUTPUT_DIR = "detector/PlantVillage2"        # where train/ and val/ will be created

TRAIN_RATIO = 0.8  # 80% train, 20% val

classes = os.listdir(DATASET_DIR)

for cls in classes:
    cls_path = Path(DATASET_DIR) / cls
    images = os.listdir(cls_path)
    random.shuffle(images)

    split_idx = int(len(images) * TRAIN_RATIO)
    train_imgs = images[:split_idx]
    val_imgs   = images[split_idx:]

    # Create class folders
    train_cls_dir = Path(OUTPUT_DIR) / "train" / cls
    val_cls_dir   = Path(OUTPUT_DIR) / "val" / cls
    train_cls_dir.mkdir(parents=True, exist_ok=True)
    val_cls_dir.mkdir(parents=True, exist_ok=True)

    # Move images
    for img in train_imgs:
        shutil.copy(cls_path / img, train_cls_dir / img)

    for img in val_imgs:
        shutil.copy(cls_path / img, val_cls_dir / img)

print("Dataset split completed.")
