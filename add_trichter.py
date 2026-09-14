import json

with open('dimensions.json', 'r') as f:
    data = json.load(f)

new_adapters = {
    "Adapter_V26_Collet_Chuck_Trichter": {
        "max_outer_diameter_mm": 13.0,
        "base_diameter_mm": 20.0,
        "funnel_depth_mm": 5.5,
        "funnel_width_mm": 34.0
    },
    "Adapter_V28_True_Cone": {
        "max_outer_diameter_mm": 13.0,
        "base_diameter_mm": 20.0,
        "cone_angle_deg": 45.0
    }
}

data.update(new_adapters)

with open('dimensions.json', 'w') as f:
    json.dump(data, f, indent=2)
