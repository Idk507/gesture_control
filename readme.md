# 🖐️ Gesture Control - Finger-Based Computer Control

A Python library for controlling your computer using **natural hand gestures** detected by **MediaPipe** and **OpenCV**. Control your cursor, scroll, and click using intuitive finger movements captured by your webcam.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MediaPipe](https://img.shields.io/badge/mediapipe-0.10.35-green.svg)](https://pypi.org/project/mediapipe/)
[![Tests](https://img.shields.io/badge/tests-17%20passed-success.svg)](https://github.com/Idk507/gesture_control)

---

## ✨ Features

- 🎯 **Precise Finger-Based Cursor Control** - Point with your index finger to move the cursor
- 📜 **Natural Scrolling** - Swipe up/down with intuitive direction mapping
- 🖱️ **Pinch Gestures for Clicking**
  - Index finger + thumb → Left click
  - Middle finger + thumb → Right click
- 📹 **Real-time Camera Overlay** - See your hand movements in a corner preview
- ⚡ **High Performance** - Optimized for real-time processing at 30 FPS
- 🔒 **Safety Features** - Configurable click enable/disable, emergency stop (move to top-left corner)
- 🧪 **Fully Tested** - 17 passing tests with comprehensive coverage

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Idk507/gesture_control.git
cd gesture_control

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Basic Usage

```python
from gesture_control import GestureControl

# Start gesture control with default settings
gc = GestureControl(
    enable_cursor_tracking=True,  # Cursor follows index finger
    enable_click=True,             # Enable pinch-to-click
    show_camera_overlay=True       # Show camera preview
)

gc.start()
```

### Run the Demo

```bash
python -m gesture_control.examples.demo
```

---

## 🎮 Gesture Controls

| Gesture | Action | Description |
|---------|--------|-------------|
| 👆 **Point with index finger** | **Cursor tracking** | Move your index finger to control cursor position |
| 👆⬆️ **Swipe finger up** | **Scroll up** | Move finger upward to scroll content down |
| 👆⬇️ **Swipe finger down** | **Scroll down** | Move finger downward to scroll content up |
| 👌 **Pinch index + thumb** | **Left click** | Bring index finger and thumb together |
| 🤌 **Pinch middle + thumb** | **Right click** | Bring middle finger and thumb together |
| ✋ **Hand open** | **Hover mode** | Open hand to hover without actions |
| 🛑 **Move to top-left corner** | **Emergency stop** | PyAutoGUI failsafe trigger |

### Keyboard Controls

- **'q'** in preview window → Quit the application
- **'p'** in preview window → Pause/Resume gesture detection

---

## 📋 Requirements

### System Requirements

- **Python**: 3.11 or 3.12 (⚠️ **Python 3.13+ not supported** - MediaPipe compatibility)
- **Webcam**: Built-in or external camera
- **OS**: Windows, macOS, or Linux

### Dependencies

```
mediapipe>=0.10.35    # Hand landmark detection (tasks API)
opencv-python>=4.8.0  # Camera capture and video processing
pyautogui>=0.9.54     # OS-level cursor/click control
numpy>=1.24.0         # Numerical operations
protobuf>=5.28.0      # MediaPipe dependency
```

---

## 🏗️ Architecture

```
gesture_control/
├── __init__.py              # Package initialization
├── control.py               # Main GestureControl class
├── core/
│   ├── capture.py          # Camera capture with OpenCV
│   ├── detection.py        # MediaPipe hand detection (tasks API)
│   ├── gestures.py         # Gesture recognition logic
│   └── actions.py          # OS action execution
├── utils/
│   ├── config.py           # Configuration management
│   └── logger.py           # Logging utilities
└── examples/
    └── demo.py             # Interactive demo application
```

### Data Flow

```
Camera Frame (OpenCV)
    ↓
MediaPipe Hand Landmarker (21 landmarks per hand)
    ↓
Hand Landmarks (dict format: x, y, z, visibility)
    ↓
Gesture Recognizer (analyze finger positions & movements)
    ↓
Gesture Type (PINCH, SWIPE_UP, SWIPE_DOWN, etc.)
    ↓
Action Executor (PyAutoGUI - cursor, scroll, click)
    ↓
OS-level Control
```

---

## 🔧 Configuration

### GestureControl Parameters

```python
gc = GestureControl(
    camera_index=0,              # Camera device index (0 = default)
    width=640,                   # Frame width in pixels
    height=480,                  # Frame height in pixels
    fps=30,                      # Target frames per second
    show_preview=True,           # Show main preview window
    show_camera_overlay=True,    # Show small camera preview overlay
    enable_cursor_tracking=True, # Enable index finger cursor control
    enable_click=True,           # Enable pinch-to-click gestures
    use_mock_detection=None      # None = auto-detect MediaPipe, True/False = force mock/real
)
```

### Gesture Recognition Tuning

```python
from gesture_control.core.gestures import GestureRecognizer

recognizer = GestureRecognizer(
    swipe_threshold=0.7,         # Minimum movement for swipe (0.0-1.0)
    pinch_threshold=0.05,        # Maximum distance for pinch (0.0-1.0)
    history_length=10,           # Frames to track for movement
    min_confidence=0.5           # Minimum gesture confidence
)
```

### Action Execution Settings

```python
from gesture_control.core.actions import ActionExecutor

executor = ActionExecutor(
    scroll_amount=3,             # Scroll units per gesture
    action_cooldown=0.2,         # Seconds between actions
    enable_safety=True,          # Enable PyAutoGUI failsafe
    enable_click=True            # Allow click actions
)
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_gestures.py

# Run with coverage
pytest --cov=gesture_control --cov-report=html
```

**Test Results:** ✅ 17 passed, ⏭️ 2 skipped (interactive TTY tests)

---

## 🎓 Advanced Usage

### Custom Gesture Handling

```python
from gesture_control import GestureControl
from gesture_control.core.gestures import GestureType

gc = GestureControl()

# Override gesture callback
def custom_gesture_handler(gesture_result):
    if gesture_result.gesture_type == GestureType.PINCH:
        print(f"Pinch detected! Confidence: {gesture_result.confidence:.2f}")
    
gc.on_gesture = custom_gesture_handler
gc.start()
```

### Programmatic Control

```python
from gesture_control import GestureControl

gc = GestureControl(show_preview=False)

# Start in background
gc.start_async()

# ... do other work ...

# Stop when done
gc.stop()
gc.release()
```

### Integration with Other Applications

```python
from gesture_control.core.capture import CameraCapture
from gesture_control.core.detection import HandDetector
from gesture_control.core.gestures import GestureRecognizer

# Use components individually
camera = CameraCapture(camera_index=0)
detector = HandDetector(use_mock=False)
recognizer = GestureRecognizer()

camera.start()
frame = camera.read()

if frame is not None:
    hands = detector.detect_hands(frame)
    for hand in hands:
        gesture = recognizer.recognize_gesture(hand)
        print(f"Gesture: {gesture.gesture_type}")

camera.release()
detector.close()
```

---

## 🐛 Troubleshooting

### MediaPipe Import Error

**Error:** `ModuleNotFoundError: No module named 'mediapipe'`

**Solution:**
```bash
pip install mediapipe==0.10.35
```

### Python 3.13 Compatibility

**Error:** `❌ Unsupported Python version detected: 3.13`

**Solution:** Use Python 3.11 or 3.12:
```bash
# Create conda environment with Python 3.11
conda create -n gesture_control python=3.11
conda activate gesture_control
```

### Camera Not Found

**Error:** `ERROR: Failed to open camera`

**Solution:**
- Check camera permissions in OS settings
- Try different camera index: `GestureControl(camera_index=1)`
- Verify camera works with other applications

### Protobuf Version Conflicts

**Error:** `TypeError: Descriptors cannot be created directly`

**Solution:**
```bash
pip install protobuf==5.29.3
```

### Cursor Movement Too Sensitive

**Solution:** Adjust cursor movement duration in `control.py`:
```python
pyautogui.moveTo(screen_x, screen_y, duration=0.1)  # Increase duration for smoothness
```

---

## 📚 API Reference

### GestureControl Class

```python
class GestureControl:
    def __init__(self, camera_index=0, width=640, height=480, ...):
        """Initialize gesture control system."""
    
    def start(self) -> bool:
        """Start the gesture control loop (blocking)."""
    
    def stop(self):
        """Stop the gesture control system."""
    
    def release(self):
        """Release all resources."""
```

### HandDetector Class

```python
class HandDetector:
    def __init__(self, max_hands=1, detection_confidence=0.5, ...):
        """Initialize MediaPipe hand detector."""
    
    def detect_hands(self, frame) -> List[HandLandmarks]:
        """Detect hands in frame and return landmarks."""
    
    def close(self):
        """Release MediaPipe resources."""
```

### GestureRecognizer Class

```python
class GestureRecognizer:
    def recognize_gesture(self, hand: HandLandmarks) -> GestureResult:
        """Recognize gesture from hand landmarks."""
```

---

## 🌟 Future Enhancements

- [ ] **Drag and Drop** - Pinch and hold to drag objects
- [ ] **Multi-hand Gestures** - Zoom in/out with two hands
- [ ] **Custom Gesture Training** - ML-based gesture learning
- [ ] **Voice Commands Integration** - Combine with speech recognition
- [ ] **Virtual Keyboard** - Type using finger movements
- [ ] **Cross-platform Optimization** - Platform-specific improvements
- [ ] **Gesture Recording** - Save and replay gesture sequences
- [ ] **Accessibility Features** - Adaptive controls for different abilities

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📧 Contact

**Project Maintainer:** Idk507  
**Repository:** [https://github.com/Idk507/gesture_control](https://github.com/Idk507/gesture_control)

---

## 🙏 Acknowledgments

- **MediaPipe** - Google's powerful hand tracking framework
- **OpenCV** - Computer vision library for camera access
- **PyAutoGUI** - Cross-platform GUI automation

---

**Built with ❤️ using Python, MediaPipe, and OpenCV**
