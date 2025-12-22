# Image scanning utilities using pyautogui
import pyautogui
import os
from typing import List, Optional, Tuple
from config import IMAGE_CONFIDENCE


def find_image(image_path: str, confidence: float = IMAGE_CONFIDENCE) -> Optional[Tuple[int, int]]:
    """
    Find a single image on screen and return its center coordinates.
    
    Args:
        image_path: Path to the image file
        confidence: Match confidence (0.0 to 1.0)
    
    Returns:
        Tuple of (x, y) center coordinates, or None if not found
    """
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return None
    
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            center = pyautogui.center(location)
            return (int(center.x), int(center.y))
        return None
    except Exception as e:
        print(f"Error finding image: {e}")
        return None


def find_all_images(image_path: str, confidence: float = IMAGE_CONFIDENCE) -> List:
    """
    Find all instances of an image on screen.
    
    Args:
        image_path: Path to the image file
        confidence: Match confidence (0.0 to 1.0)
    
    Returns:
        List of Box objects for each match
    """
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return []
    
    try:
        matches = list(pyautogui.locateAllOnScreen(image_path, confidence=confidence))
        return matches
    except Exception as e:
        print(f"Error finding images: {e}")
        return []


def boxes_overlap(box1, box2, threshold: float = 0.5) -> bool:
    """
    Check if two boxes overlap by more than threshold.
    
    Args:
        box1: First box (with left, top, width, height attributes)
        box2: Second box
        threshold: Overlap ratio threshold (0.0 to 1.0)
    
    Returns:
        True if boxes overlap by more than threshold
    """
    # Calculate intersection
    x_left = max(box1.left, box2.left)
    y_top = max(box1.top, box2.top)
    x_right = min(box1.left + box1.width, box2.left + box2.width)
    y_bottom = min(box1.top + box1.height, box2.top + box2.height)
    
    if x_right < x_left or y_bottom < y_top:
        return False  # No intersection
    
    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    box1_area = box1.width * box1.height
    box2_area = box2.width * box2.height
    smaller_area = min(box1_area, box2_area)
    
    overlap_ratio = intersection_area / smaller_area if smaller_area > 0 else 0
    return overlap_ratio > threshold


def filter_duplicate_boxes(boxes: List, threshold: float = 0.5) -> List:
    """
    Filter out duplicate/overlapping boxes.
    
    Args:
        boxes: List of Box objects
        threshold: Overlap threshold for considering duplicates
    
    Returns:
        List of unique boxes
    """
    unique = []
    for box in boxes:
        is_duplicate = False
        for existing in unique:
            if boxes_overlap(box, existing, threshold):
                is_duplicate = True
                break
        if not is_duplicate:
            unique.append(box)
    return unique


def click_at(x: int, y: int, delay: float = 0.3) -> None:
    """Click at specified coordinates with optional delay."""
    import time
    pyautogui.click(x, y)
    time.sleep(delay)


def hotkey(*keys) -> None:
    """Press a keyboard hotkey combination."""
    pyautogui.hotkey(*keys)
