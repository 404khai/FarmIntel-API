import os
from ultralytics import YOLO
from django.conf import settings

# Load your trained model
MODEL_PATH = os.path.join(settings.BASE_DIR, "ai_models/best.pt")

yolo_model = YOLO(MODEL_PATH)

def run_pest_detection(image_path):
    """
    Runs YOLOv8 inference on an image and returns:
    - detected pest classes
    - confidence scores
    """
    results = yolo_model(image_path)[0]  # first batch

    detected_pests = []
    confidence_scores = []

    for box in results.boxes:
        cls_id = int(box.cls)
        pest_name = results.names[cls_id]
        conf = float(box.conf)

        detected_pests.append(pest_name)
        confidence_scores.append(round(conf, 3))

    return detected_pests, confidence_scores
