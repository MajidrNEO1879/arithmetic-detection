import torch
import requests
import BytesIO
from PIL import Image
def predict_from_url(model, url, transform, class_names, device=None):
    # Select device automatically if not provided
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Download the image
    response = requests.get(url)
    image = Image.open(BytesIO(response.content)).convert("RGB")

    # Apply your transform (resize, normalize, etc.)
    input_tensor = transform(image).unsqueeze(0).to(device)  # Add batch dimension

    # Run inference
    model.eval()
    with torch.no_grad():
        output = model(input_tensor)
        _, pred = torch.max(output, 1)
        pred_class = class_names[pred.item()]

    print(f"Predicted class: {pred_class}")
    return pred_class