CLASS_NAMES = {
    "tomato": [
        "Bacterial_spot",           # 0
        "Early_blight",             # 1  
        "Late_blight",              # 2
        "Leaf_Mold",                # 3
        "Septoria_leaf_spot",       # 4
        "Tomato_Yellow_Leaf_Curl_Virus",  # 5
        "Tomato_mosaic_virus",      # 6
        "Healthy"                   # 7
    ],
    "potato": [
        "Early_blight",
        "Late_blight",
        "Healthy"
    ],
    "pepper": [
        "Bacterial_spot",
        "Healthy"
    ]
}

def get_class_name(plant_type: str, class_id: int) -> str:
    try:
        return CLASS_NAMES[plant_type][class_id]
    except (KeyError, IndexError):
        raise ValueError(f"Tipo de planta '{plant_type}' o clase {class_id} inválida")