import torch
from torchvision import transforms
from PIL import Image

class LeafDiseaseModel:
    def __init__(self, model_path, label_path):
        # Load model architecture (match training)
        import timm
        self.labels = []

        with open(label_path, "r") as f:
            self.labels = [line.strip() for line in f.readlines()]

        num_classes = len(self.labels)

        self.model = timm.create_model(
            "efficientnet_b0",
            pretrained=False,
            num_classes=num_classes
        )
        self.model.load_state_dict(torch.load(model_path, map_location="cpu"))
        self.model.eval()

        self.preprocess = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225],
            ),
        ])

    def predict(self, img_path, top_k=3):
        img = Image.open(img_path).convert("RGB")
        tensor = self.preprocess(img).unsqueeze(0)

        with torch.no_grad():
            out = self.model(tensor)
            probs = torch.softmax(out, dim=1)

        top_probs, top_idxs = probs.topk(top_k)

        results = [
            {
                "label": self.labels[idx],
                "confidence": float(prob)
            }
            for prob, idx in zip(top_probs[0], top_idxs[0])
        ]

        return results


# Load ONCE globally (crucial)
model = LeafDiseaseModel(
    model_path="detector/model/disease_model/best_model.pth",
    label_path="detector/model/disease_model/labels.txt"
)
