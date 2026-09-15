from PIL import Image

img0 = Image.open("screenshot_step0.png").convert("RGB")
img1 = Image.open("screenshot_step1.png").convert("RGB")
width, height = img0.size
y = height // 2

def find_graph_bounds(img):
    # Graph background is very dark, almost black
    bounds = []
    in_graph = False
    for x in range(width):
        r, g, b = img.getpixel((x, y))
        # Check if color is dark (graph background)
        is_dark = (r < 30 and g < 30 and b < 30)
        
        if is_dark and not in_graph:
            bounds.append(x)
            in_graph = True
        elif not is_dark and in_graph:
            bounds.append(x)
            in_graph = False
    return bounds

print("Graph bounds in Freq Response tab:", find_graph_bounds(img0))
print("Graph bounds in Waterfall tab:", find_graph_bounds(img1))
