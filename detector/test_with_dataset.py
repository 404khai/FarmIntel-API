import os, random
from detector.predictor import model

DATASET = "detector/PlantVillage"

# Pick a random class
random_class = random.choice(os.listdir(DATASET))
folder = os.path.join(DATASET, random_class)

# Pick a random image inside class folder
img = random.choice(os.listdir(folder))
img_path = os.path.join(folder, img)

print("Testing:", img_path)

result = model.predict(img_path, top_k=3)
print(result)
