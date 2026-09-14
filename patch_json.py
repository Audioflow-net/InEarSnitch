import json

with open("dimensions.json", "r") as f:
    data = json.load(f)

coupler = data["Hardware_IEC711_Coupler"]
coupler["acoustic_bore_diameter_mm"] = 6.5
coupler["acoustic_bore_depth_mm"] = 3.0
coupler["nut_hole_depth_mm"] = 6.0

with open("dimensions.json", "w") as f:
    json.dump(data, f, indent=2)

print("dimensions.json patched!")
