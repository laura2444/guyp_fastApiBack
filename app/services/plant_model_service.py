from PIL import Image
import torch
from torch import Tensor
import torchvision.transforms as transforms
from app.ml.model_loader import get_model
from app.ml.class_mapping import get_class_name

# ✅ FORZAR CPU aquí también
device = torch.device("cpu")

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def predict(image: Image.Image, plant_type: str) -> dict:
    model = get_model(plant_type)
    
    # ✅ Asegurar que el tensor también esté en CPU
    tensor: Tensor = transform(image)  # type: ignore
    input_tensor = tensor.unsqueeze(0).to(device)  # .to(device) asegura CPU
    
    with torch.no_grad():
        outputs = model(input_tensor)
        probs = torch.softmax(outputs, dim=1)
        
        class_id = int(torch.argmax(probs, dim=1).item())
        confidence = float(probs[0][class_id].item())
    
    return {
        "plant_type": plant_type,
        "class_id": class_id,
        "prediction": get_class_name(plant_type, class_id),
        "confidence": round(confidence, 4)
    }