import numpy as np
import cv2
import torch
import os
from torchvision import transforms
from torch.nn import functional as F
from torch import topk
from model import build_model

def verify_image_with_model(image_path):
    seed = 42
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = True

    # Define computation device.
    device = 'cpu'
    # Class names.
    class_names = ['fake', 'real']
    # Initialize model, switch to eval model, load trained weights.
    model = build_model(
        pretrained=False,
        fine_tune=False, 
        num_classes=2
    ).to(device)
    model = model.eval()
    model.load_state_dict(torch.load(r"C:\Users\sraad\Downloads\zeus\elements\input\model.pth")['model_state_dict'])  # Provide the path to your model here

    # Define the transforms, resize => tensor => normalize.
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    # Read the image.
    image = cv2.imread(image_path)
    orig_image = image.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width, _ = orig_image.shape
    # Apply the image transforms.
    image_tensor = transform(image)
    # Add batch dimension.
    image_tensor = image_tensor.unsqueeze(0)
    # Forward pass through model.
    outputs = model(image_tensor.to(device))
    # Get the softmax probabilities.
    probs = F.softmax(outputs).data.squeeze()
    # Get the class indices of top k probabilities.
    class_idx = topk(probs, 1)[1].int()

    # Return the verification result
    verdict = class_names[int(class_idx)]
    probability = float(probs[class_idx])
    return {'verdict': verdict, 'probability': round(probability*100,2)}
