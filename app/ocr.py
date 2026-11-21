"""
Day 12 — OCR module for HealthLabelCheck
Extracts text from a food label image using EasyOCR,
with Pillow preprocessing (contrast + resize) to improve accuracy.

Usage:
    from app.ocr import extract_text_from_image
    text = extract_text_from_image("data/sample_label.png")
"""

import os
from typing import List, Tuple
from PIL import Image, ImageEnhance, ImageFilter


# ── Preprocessing ─────────────────────────────────────────────────────���───────

def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Prepare an image for OCR:
    - Convert to RGB (handles RGBA / palette modes)
    - Upscale small images so OCR has enough pixels
    - Sharpen + boost contrast for faded labels
    """
    image = image.convert("RGB")

    # Upscale if smaller than 800px wide
    w, h = image.size
    if w < 800:
        scale = 800 / w
        image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    # Sharpen
    image = image.filter(ImageFilter.SHARPEN)

    # Boost contrast
    image = ImageEnhance.Contrast(image).enhance(1.5)

    return image


# ── EasyOCR extraction ────────────────────────────────────────────────────────

_reader = None  # lazy singleton — loading the model takes ~5 s


def _get_reader():
    """Return (and cache) the EasyOCR reader for English."""
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(["en"], gpu=False, verbose=False)
    return _reader


def extract_text_from_image(
    image_source,
    confidence_threshold: float = 0.3,
) -> str:
    """
    Run EasyOCR on an image and return all detected text as one string.

    Args:
        image_source: file path (str), PIL Image, or bytes.
        confidence_threshold: minimum confidence to include a text block.

    Returns:
        A single string with all detected text, one line per detection.
    """
    # Load image
    if isinstance(image_source, str):
        if not os.path.exists(image_source):
            raise FileNotFoundError(f"Image not found: {image_source}")
        image = Image.open(image_source)
    elif isinstance(image_source, bytes):
        import io
        image = Image.open(io.BytesIO(image_source))
    elif isinstance(image_source, Image.Image):
        image = image_source
    else:
        raise TypeError(f"Unsupported image_source type: {type(image_source)}")

    image = preprocess_image(image)

    reader = _get_reader()
    # EasyOCR accepts a numpy array
    import numpy as np
    img_array = np.array(image)

    results: List[Tuple] = reader.readtext(img_array, detail=1)

    lines = []
    for (_bbox, text, confidence) in results:
        if confidence >= confidence_threshold and text.strip():
            lines.append(text.strip())

    return "\n".join(lines)


def extract_text_with_boxes(
    image_source,
    confidence_threshold: float = 0.3,
) -> List[dict]:
    """
    Return detailed OCR results including bounding boxes and confidence.

    Returns list of dicts: {text, confidence, bbox}
    """
    if isinstance(image_source, str):
        image = Image.open(image_source)
    elif isinstance(image_source, bytes):
        import io
        image = Image.open(io.BytesIO(image_source))
    else:
        image = image_source

    image = preprocess_image(image)

    reader = _get_reader()
    import numpy as np
    img_array = np.array(image)
    results = reader.readtext(img_array, detail=1)

    detections = []
    for (bbox, text, confidence) in results:
        if confidence >= confidence_threshold and text.strip():
            detections.append({
                "text":       text.strip(),
                "confidence": round(float(confidence), 3),
                "bbox":       [[int(c) for c in pt] for pt in bbox],
            })
    return detections


# ── Standalone test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_label.png"
    print(f"Extracting text from: {path}\n")
    text = extract_text_from_image(path)
    print("--- Extracted text ---")
    print(text)
    print(f"\nTotal characters extracted: {len(text)}")
