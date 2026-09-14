import sys
import trimesh

try:
    mesh = trimesh.load(sys.argv[1])
    vol_mm3 = mesh.volume
    print(f"VOLUME_MM3: {vol_mm3}")
except Exception as e:
    print(f"ERROR: {e}")
