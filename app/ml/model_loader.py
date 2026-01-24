import torch
import torchvision.models as models

MODELS = {
    "tomato": "app/ml/best_tomato_model_efficientnet_b0_fixed.pth",
    "potato": "app/ml/best_papa_model_mobilenet_v2_fixed.pth",
    "pepper": "app/ml/best_pimienta_model_efficientnet_b0_fixed.pth",
}

# ✅ FORZAR CPU COMPLETAMENTE
device = torch.device("cpu")
print(f"🔧 Usando dispositivo: {device}")

_loaded_models = {}

def get_model(plant_type: str):
    """Carga modelos .pth que tienen estructura personalizada"""
    
    if plant_type not in MODELS:
        raise ValueError(f"Modelo no soportado: {plant_type}")
    
    if plant_type in _loaded_models:
        return _loaded_models[plant_type]
    
    print(f"📦 Cargando {plant_type}...")
    
    # 1. Cargar archivo
    loaded = torch.load(MODELS[plant_type], map_location=device)
    
    # 2. Si es state_dict, crear arquitectura compatible
    if isinstance(loaded, dict):
        print("   Es un state_dict...")
        
        # Determinar número de clases
        classifier_key = None
        for key in loaded.keys():
            if 'classifier' in key and 'weight' in key:
                classifier_key = key
                break
        
        if classifier_key:
            num_classes = loaded[classifier_key].shape[0]
            print(f"   Clases detectadas: {num_classes}")
        else:
            num_classes = {"tomato": 8, "potato": 3, "pepper": 2}[plant_type]
            print(f"   Clases por defecto: {num_classes}")
        
        # Crear modelo base
        if plant_type == "tomato" or plant_type == "pepper":
            model = models.efficientnet_b0(weights=None)
            in_features = model.classifier[1].in_features
            model.classifier = torch.nn.Sequential(
                torch.nn.Dropout(p=0.2, inplace=True),
                torch.nn.Linear(in_features, num_classes)
            )
        elif plant_type == "potato":
            model = models.mobilenet_v2(weights=None)
            in_features = model.classifier[1].in_features
            model.classifier = torch.nn.Sequential(
                torch.nn.Dropout(p=0.2, inplace=True),
                torch.nn.Linear(in_features, num_classes)
            )
        
        # CORRECCIÓN: Adaptar claves correctamente
        new_state_dict = {}
        for key, value in loaded.items():
            new_key = key
            
            # Caso 1: Tiene 'backbone.features.' -> 'features.'
            if new_key.startswith('backbone.features.'):
                new_key = new_key.replace('backbone.features.', 'features.')
            
            # Caso 2: Tiene solo 'backbone.' -> 'features.'
            elif new_key.startswith('backbone.'):
                new_key = new_key.replace('backbone.', 'features.')
            
            # Caso 3: Tiene 'features.classifier.' -> 'classifier.'
            if new_key.startswith('features.classifier.'):
                new_key = new_key.replace('features.classifier.', 'classifier.')
            
            new_state_dict[new_key] = value
        
        # Cargar pesos (con strict=False para compatibilidad)
        try:
            model.load_state_dict(new_state_dict, strict=False)
            print("   ✅ Pesos cargados (algunas diferencias ignoradas)")
        except Exception as e:
            print(f"   ❌ Error crítico: {e}")
            raise
    
    # 3. Si ya es modelo completo
    elif hasattr(loaded, 'eval'):
        print("   ✅ Modelo completo cargado")
        model = loaded
    
    else:
        raise ValueError(f"Formato desconocido")
    
    # 4. Configurar para inferencia
    model.to(device)
    model.eval()
    
    for param in model.parameters():
        param.requires_grad = False
    
    _loaded_models[plant_type] = model
    print(f"   ✅ Modelo listo")
    
    return model