# model_utils.py
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import timm
import numpy as np

IMG_SIZE = 224
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_NAME = "efficientnet_b0"

# preprocessing
preprocess = transforms.Compose([
    transforms.Resize(int(IMG_SIZE*1.14)),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
])

def load_model(checkpoint_path, num_classes=None, enable_dropout_mc=False):
    # create model architecture
    model = timm.create_model(MODEL_NAME, pretrained=False, num_classes=num_classes)
    ck = torch.load(checkpoint_path, map_location=DEVICE)
    model.load_state_dict(ck['model_state'])
    model.to(DEVICE)
    model.eval()
    # optionally keep dropout layers active for MC Dropout
    if enable_dropout_mc:
        # set dropout layers to train() so dropout is active; keep batchnorm in eval
        def enable_dropout(m):
            if isinstance(m, torch.nn.Dropout):
                m.train()
        model.apply(enable_dropout)
    return model, ck.get('class_to_idx', None)

def predict_image(model, pil_image: Image.Image, class_to_idx, topk=3, mc_dropout_runs=0):
    x = preprocess(pil_image).unsqueeze(0).to(DEVICE)  # 1 x C x H x W
    idx_to_class = {v:k for k,v in class_to_idx.items()} if class_to_idx else None

    # single deterministic pass
    with torch.no_grad():
        logits = model(x)
        probs = F.softmax(logits, dim=1).cpu().numpy()[0]

    # Monte Carlo Dropout runs for uncertainty (if requested)
    if mc_dropout_runs and mc_dropout_runs > 0:
        preds = []
        model.train()  # to activate dropout layers (but this switches batchnorm too)
        with torch.no_grad():
            for _ in range(mc_dropout_runs):
                logits_mc = model(x)
                preds.append(F.softmax(logits_mc, dim=1).cpu().numpy()[0])
        preds = np.stack(preds, axis=0)  # runs x classes
        mean_probs = preds.mean(axis=0)
        std_probs = preds.std(axis=0)
        probs = mean_probs
        uncertainty = std_probs  # per-class std
        # restore model eval mode
        model.eval()
    else:
        uncertainty = np.zeros_like(probs)

    topk_idx = probs.argsort()[-topk:][::-1]
    results = []
    for i in topk_idx:
        cls_name = idx_to_class[i] if idx_to_class else str(i)
        results.append({
            'label': cls_name,
            'probability': float(probs[i]),
            'uncertainty': float(uncertainty[i])
        })
    return results
