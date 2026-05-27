# Changelog

All notable changes to the Gesture Control project will be documented in this file.


### Added
- 🎯 **Finger-based cursor control** - Cursor now follows index finger tip (landmark 8) instead of wrist for precise control
- 🖱️ **Pinch gesture support**:
  - Index finger + thumb pinch for left-click
  - Middle finger + thumb pinch for right-click
- 📹 **Camera overlay feature** - Small 160x120 camera preview in bottom-right corner to visualize hand movements
- 🔒 **Safety features**:
  - `enable_click` parameter (default: False for safety)
  - `enable_cursor_tracking` parameter for optional cursor control
  - PyAutoGUI failsafe (move to top-left corner for emergency stop)
- ✅ **Comprehensive test suite** - 17 passing tests covering all core functionality
- 🐍 **Python version validation** - Runtime check blocking Python 3.13+ (MediaPipe incompatibility)
- 📝 **Enhanced documentation** - Complete README with usage examples, API reference, and troubleshooting

### Changed
- 🔄 **Updated to MediaPipe 0.10.35** - Migrated from deprecated `solutions` API to modern `tasks` API:
  - Uses `mp.tasks.vision.HandLandmarker` instead of `mp.solutions.hands.Hands`
  - Landmarks now stored as dicts `{'x': float, 'y': float, 'z': float, 'visibility': float}`
  - Detection method changed from `process()` to `detect()`
- 📜 **Fixed scroll direction** - Natural scrolling behavior (finger down = scroll down, finger up = scroll up)
- 🔧 **Improved gesture recognition**:
  - Better pinch detection with configurable threshold (default: 0.05)
  - Gesture priority system to prevent conflicts
  - Swipe detection with movement history tracking (10 frames)
- ⚡ **Optimized performance** - Cursor movement with 0.05s duration for smooth tracking

### Fixed
- 🐛 Fixed landmark data structure handling - Proper support for dict-based landmarks from new MediaPipe API
- 🐛 Fixed protobuf dependency conflicts - Locked to version 5.29.3 (compatible with both MediaPipe and TensorFlow)
- 🐛 Fixed Python 3.13 compatibility issues - Added validation to prevent unsupported Python versions
- 🐛 Fixed pytest fixtures - Converted return-based fixtures to proper `@pytest.fixture` decorators
- 🐛 Fixed TTY interactive tests - Added skip conditions for non-interactive environments

### Technical Details
- **MediaPipe Model**: Auto-downloads to `~/.mediapipe/models/hand_landmarker.task`
- **Hand Landmarks**: 21 points per hand (MediaPipe standard)
  - Index 0: Wrist
  - Index 4: Thumb tip
  - Index 8: Index finger tip (used for cursor)
  - Index 12: Middle finger tip (used for right-click)
- **Dependencies**:
  - MediaPipe 0.10.35
  - Protobuf 5.29.3
  - TensorFlow 2.20.0
  - OpenCV 4.8.0+
  - PyAutoGUI 0.9.54+
  - NumPy 1.24.0+

### Known Issues
- Python 3.13+ not supported (MediaPipe compatibility limitation)
- MediaPipe clearcut uploader warnings in console (non-critical, analytics-related)
- Landmark projection warnings (non-critical, ROI-related)

### Deprecated
- ❌ Old MediaPipe `solutions` API (removed in MediaPipe 0.10.35)
- ❌ Wrist-based cursor tracking (replaced with index finger tracking)

---

## [0.1.0] - Initial Architecture

### Added
- Basic project structure
- Camera capture with OpenCV
- MediaPipe hand detection (legacy API)
- Gesture recognition system
- Action execution with PyAutoGUI
- Demo application

---

**Format:** This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.
**Versioning:** This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
