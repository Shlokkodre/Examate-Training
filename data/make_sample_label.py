"""
Day 12 — Generate a realistic sample food label image for OCR testing.

The label mimics a home-made chakli packet with most (but not all)
mandatory FSSAI declarations so the checker finds both compliant and
missing items.

Run from repo root:
    python data/make_sample_label.py
Output: data/sample_label.png
"""

from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_PATH = "data/sample_label.png"

# Label content — deliberately missing Nutritional Information (5.3)
# and Food Additive Declaration (5.12) to make the test interesting
LABEL_LINES = [
    ("CHAKLI SNACKS", 28, True),
    ("Premium Rice Flour Chakli", 18, False),
    ("", 14, False),
    ("Ingredients: Rice flour, Bengal gram flour,", 14, False),
    ("vegetable oil, sesame seeds, salt, spices.", 14, False),
    ("", 14, False),
    ("Net Qty: 200g", 15, True),
    ("", 14, False),
    ("Mfg: Sunita Home Foods", 13, False),
    ("12, Ganesh Nagar, Kopargaon,", 13, False),
    ("Maharashtra - 423601", 13, False),
    ("", 13, False),
    ("MFD: 17/11/2026   Best Before: 17/02/2027", 13, False),
    ("", 13, False),
    ("FSSAI Lic. No.: 11417030000133", 13, False),
    ("", 13, False),
    ("Veg  [GREEN DOT]", 13, False),
    ("", 13, False),
    ("Allergen Info: Contains sesame seeds.", 13, False),
    ("Manufactured in a facility that handles peanuts.", 13, False),
    ("", 13, False),
    ("Store in a cool, dry place.", 12, False),
    ("Keep away from moisture.", 12, False),
]


def build_label(output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    # Canvas
    W, H = 600, 700
    img = Image.new("RGB", (W, H), color=(255, 253, 240))  # cream background
    draw = ImageDraw.Draw(img)

    # Border
    draw.rectangle([8, 8, W - 8, H - 8], outline=(34, 139, 34), width=4)
    draw.rectangle([14, 14, W - 14, H - 14], outline=(34, 139, 34), width=1)

    # Veg symbol (green filled circle)
    draw.ellipse([520, 580, 548, 608], fill=(34, 139, 34), outline=(0, 100, 0), width=2)
    draw.rectangle([516, 576, 552, 612], outline=(34, 139, 34), width=2)

    # Try to load a font; fall back to default
    try:
        font_bold = ImageFont.truetype("arial.ttf", 28)
        font_normal = ImageFont.truetype("arial.ttf", 14)
    except OSError:
        font_bold = ImageFont.load_default()
        font_normal = ImageFont.load_default()

    y = 30
    for text, size, bold in LABEL_LINES:
        if not text:
            y += 8
            continue
        try:
            fnt = ImageFont.truetype("arial.ttf", size)
        except OSError:
            fnt = ImageFont.load_default()

        color = (20, 20, 20) if not bold else (10, 60, 10)
        draw.text((30, y), text, font=fnt, fill=color)
        y += size + 6

    img.save(output_path, "PNG")
    size_kb = os.path.getsize(output_path) / 1024
    print(f"Label image created: {output_path}  ({size_kb:.1f} KB,  {W}x{H} px)")


if __name__ == "__main__":
    build_label(OUTPUT_PATH)
