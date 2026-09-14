import json

with open("dimensions.json", "r") as f:
    data = json.load(f)

data["Adapter_V29_Thin_Layer_Cone"] = {
    "max_outer_diameter_mm": 13.0,
    "base_diameter_mm": 20.0,
    "wall_thickness_mm": 0.75,
    "cone_length_mm": 14.6,
    "tip_outer_mm": 4.0,
    "tip_inner_mm": 2.5
}

with open("dimensions.json", "w") as f:
    json.dump(data, f, indent=2)

print("done")
