# detector/predictor.py
import torch
from torchvision import transforms
from PIL import Image

class LeafDiseaseModel:
    def __init__(self, model_path, label_path):
        self.model = torch.load(model_path, map_location=torch.device("cpu"))
        self.model.eval()

        with open(label_path, "r") as f:
            self.labels = [line.strip() for line in f.readlines()]

        self.preprocess = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def predict(self, image_file, top_k=3):
        image = Image.open(image_file).convert("RGB")
        img_tensor = self.preprocess(image).unsqueeze(0)

        with torch.no_grad():
            outputs = self.model(img_tensor)
            probs = torch.softmax(outputs, dim=1)

        top_probs, top_idxs = probs.topk(top_k)

        results = []
        for prob, idx in zip(top_probs[0], top_idxs[0]):
            results.append({
                "label": self.labels[idx],
                "confidence": float(prob)
            })

        return results


# Load model once
model = LeafDiseaseModel(
    model_path="saved_models/leaf_model.pt",
    label_path="saved_models/labels.txt"
)
