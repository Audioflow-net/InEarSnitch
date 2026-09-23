import math
import re

def parse_ascii_stl(path):
    facets = []
    min_x, max_x = float("inf"), float("-inf")
    min_y, max_y = float("inf"), float("-inf")
    min_z, max_z = float("inf"), float("-inf")
    
    current_normal = None
    current_vertices = []
    
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("facet normal"):
                parts = line.split()
                current_normal = (float(parts[2]), float(parts[3]), float(parts[4]))
                current_vertices = []
            elif line.startswith("vertex"):
                parts = line.split()
                vx, vy, vz = float(parts[1]), float(parts[2]), float(parts[3])
                current_vertices.append((vx, vy, vz))
                min_x = min(min_x, vx)
                max_x = max(max_x, vx)
                min_y = min(min_y, vy)
                max_y = max(max_y, vy)
                min_z = min(min_z, vz)
                max_z = max(max_z, vz)
            elif line.startswith("endfacet"):
                if current_normal and len(current_vertices) == 3:
                    facets.append({
                        "normal": current_normal,
                        "vertices": current_vertices
                    })
    
    bounds = ((min_x, max_x), (min_y, max_y), (min_z, max_z))
    return bounds, facets

bounds, facets = parse_ascii_stl("/tmp/test_wedge_sleeve.stl")
print("Bounds:", bounds)
print("Total facets:", len(facets))

# Let's inspect facets where X > 17 (outer is 22, pocket is 17.25)
outer_cut_facets = [f for f in facets if any(v[0] > 17.25 and v[1] > 17.25 for v in f["vertices"])]
print("Facets in positive quadrant (X > 17.25, Y > 17.25):", len(outer_cut_facets))

# Check for holes/cutouts on the +X wall (around X=22)
wall_cut = [f for f in facets if any(v[0] > 17.25 and 0 < v[1] < 17.25 and 2.5 < v[2] < 42.0 for v in f["vertices"])]
print("Facets along X wall cut:", len(wall_cut))
