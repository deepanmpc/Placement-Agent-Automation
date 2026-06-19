import sys
from PIL import Image

def get_colors(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        width, height = img.size
        print(f"Image Size: {width}x{height}")
        y = height // 2
        colors = []
        for x in [int(width * 0.1), int(width * 0.5), int(width * 0.9)]:
            r, g, b = img.getpixel((x, y))
            colors.append(f"rgb({r}, {g}, {b})")
            print(f"Pixel at ({x}, {y}): rgb({r}, {g}, {b})")
            
        print("Gradient rough estimate:")
        print("linear-gradient(90deg, " + ", ".join(colors) + ")")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        get_colors(sys.argv[1])
    else:
        print("Provide an image path.")
