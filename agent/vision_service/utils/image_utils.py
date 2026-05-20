import cv2
import numpy as np
from PIL import Image

def convert_to_grayscale(img_array: np.ndarray) -> np.ndarray:
    """Converts a BGR image array to grayscale."""
    return cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)

def resize_if_needed(img: Image.Image, max_width: int, max_height: int) -> Image.Image:
    """Resizes the image if it exceeds the maximum dimensions."""
    if img.width > max_width or img.height > max_height:
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    return img

def pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
    """Converts PIL Image to OpenCV numpy array."""
    # Convert RGB to BGR
    open_cv_image = np.array(pil_img) 
    return open_cv_image[:, :, ::-1].copy()

def cv2_to_pil(cv2_img: np.ndarray) -> Image.Image:
    """Converts OpenCV numpy array to PIL Image."""
    # Convert BGR to RGB
    rgb_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_img)
