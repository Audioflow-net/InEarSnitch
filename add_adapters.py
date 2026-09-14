import json

with open('dimensions.json', 'r') as f:
    data = json.load(f)

new_adapters = {
    "Adapter_TPU_Marshmallow_Pad": {
        "max_outer_diameter_mm": 13.0,
        "base_diameter_mm": 20.0,
        "pad_thickness_mm": 5.0
    },
    "Adapter_TPU_Tiny_Caps": {
        "max_outer_diameter_mm": 13.0,
        "base_diameter_mm": 20.0,
        "cap_height_mm": 6.0
    },
    "Adapter_TPU_Bristle_Pad": {
        "max_outer_diameter_mm": 13.0,
        "base_diameter_mm": 20.0,
        "bristle_length_mm": 4.0
    },
    "Adapter_TPU_Membrane": {
        "max_outer_diameter_mm": 13.0,
        "base_diameter_mm": 20.0,
        "membrane_thickness_mm": 0.4
    },
    "Adapter_Iris_Valve_Concept": {
        "max_outer_diameter_mm": 13.0,
        "base_diameter_mm": 20.0,
        "wall_thickness_mm": 1.2
    }
}

data.update(new_adapters)

with open('dimensions.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Added new adapters to dimensions.json")
