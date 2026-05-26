"""
Gesture Control Library

A Python library for controlling laptop monitor scrolling using hand gestures
detected by MediaPipe Hands and processed via OpenCV.

Usage:
    from gesture_control import GestureControl
    gc = GestureControl()
    gc.start()
"""

from .core.capture import CameraCapture
from .core.detection import HandDetector, HandLandmarks
from .core.gestures import GestureRecognizer, GestureType, GestureAction, GestureResult
from .core.actions import ActionExecutor, ActionType, ActionResult

# Import the main control system from the integration module
from .control import GestureControl

__version__ = "0.1.0"
__author__ = "Gesture Control Library"
__description__ = "Hand gesture-based laptop monitor control"

__all__ = [
    # Main API
    "GestureControl",

    # Core components
    "CameraCapture",
    "HandDetector",
    "HandLandmarks",
    "GestureRecognizer",
    "ActionExecutor",

    # Types and enums
    "GestureType",
    "GestureAction",
    "GestureResult",
    "ActionType",
    "ActionResult",

    # Metadata
    "__version__",
    "__author__",
    "__description__",
]
