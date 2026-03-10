import os
from dataclasses import dataclass
from typing import Optional

import mss
import numpy as np
from PIL import Image
import pytesseract

# OCRConfig dataclass to hold configuration for OCR processing
@dataclass
class OCRConfig:
    # region is a box in SCREEN coordinates
    x: int
    y: int
    w: int
    h: int

    psm: int = 6  # Default to single block of text
    whitelist: Optional[str] = None

# Initialize tesseract command for Windows if needed
def init_tesseract_windows():
    # Only needed on Windows if tesseract isn't in PATH.
    if os.name == "nt":
        # CHANGE THIS IF NEEDED
        guess = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.isfile(guess):
            pytesseract.pytesseract.tesseract_cmd = guess

# Simple preprocessing to improve OCR accuracy
def _preprocess(img: Image.Image) -> Image.Image:
    # Convert to grayscale
    gray = img.convert("L")
    arr = np.array(gray)

    # Simple thresholding
    thr = 180
    arr = (arr > thr).astype(np.uint8) * 255
    return Image.fromarray(arr)

# Main OCR function to capture a region of the screen and extract text
def ocr_region(cfg: OCRConfig) -> str:
    with mss.mss() as sct:
        shot = sct.grab({"left": cfg.x, "top": cfg.y, "width": cfg.w, "height": cfg.h})
        img = Image.frombytes("RGB", shot.size, shot.rgb)

    img = _preprocess(img)

    tess_config = f"--psm {cfg.psm}"
    if cfg.whitelist:
        tess_config += f" -c tessedit_char_whitelist={cfg.whitelist}"
    
    text = pytesseract.image_to_string(img, config=tess_config)
    # clean up
    text = text.strip()
    # collapse multiple lines/spaces
    text = " ".join(text.split())
    return text