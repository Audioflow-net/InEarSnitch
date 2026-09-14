import re

with open("iem_rig_final.scad", "r") as f:
    content = f.read()

# Replace old TPU names with V44 names
content = content.replace("TPU_Bellows_Base", "TPU_CIEM_Membrane")
content = content.replace("TPU_Ball_Joint_Pad", "TPU_Bristle_Pad")
content = content.replace('"tpu_pad"', '"tpu_bristle_pad"')
content = content.replace('"tpu_giant_bellows"', '"tpu_ciem_membrane"')

with open("iem_rig_final.scad", "w") as f:
    f.write(content)
