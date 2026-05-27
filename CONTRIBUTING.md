# Contributing to Gesture Control

Thank you for your interest in contributing to Gesture Control! This document provides guidelines and instructions for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or 3.12 (⚠️ Python 3.13+ not supported)
- Git for version control
- A webcam for testing gesture features

### Setting Up Development Environment

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/gesture_control.git
   cd gesture_control
   ```

2. **Create a Python virtual environment:**
   ```bash
   # Using conda (recommended)
   conda create -n gesture_control python=3.11
   conda activate gesture_control

   # Or using venv
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

4. **Verify installation:**
   ```bash
   pytest  # Should show 17 passed, 2 skipped
   python -m gesture_control.examples.demo  # Run the demo
   ```

## 📝 Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# Or for bug fixes:
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Follow the existing code structure and conventions
- Add tests for new features
- Update documentation as needed
- Keep commits focused and atomic

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_gestures.py

# Run with coverage
pytest --cov=gesture_control --cov-report=html

# Manual testing
python -m gesture_control.examples.demo
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "Add feature: your feature description"
```

**Commit Message Guidelines:**
- Use present tense ("Add feature" not "Added feature")
- Be descriptive but concise
- Reference issues/PRs when applicable: `Fix #123: Description`

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub with:
- Clear description of changes
- Reference to related issues
- Screenshots/videos for UI changes
- Test results

## 🏗️ Project Structure

```
gesture_control/
├── gesture_control/          # Main package
│   ├── __init__.py          # Package exports
│   ├── control.py           # Main GestureControl class
│   ├── core/                # Core functionality
│   │   ├── actions.py       # Action execution (PyAutoGUI)
│   │   ├── capture.py       # Camera capture (OpenCV)
│   │   ├── detection.py     # Hand detection (MediaPipe)
│   │   └── gestures.py      # Gesture recognition
│   ├── utils/               # Utilities
│   │   ├── config.py        # Configuration
│   │   └── logger.py        # Logging
│   └── examples/            # Example scripts
│       └── demo.py          # Interactive demo
├── tests/                   # Test suite
│   ├── test_actions.py
│   ├── test_camera.py
│   ├── test_detection.py
│   ├── test_gestures.py
│   ├── test_integration.py
│   └── test_module.py
├── README.md               # Main documentation
├── CHANGELOG.md           # Version history
├── requirements.txt       # Dependencies
└── setup.py              # Package configuration
```

## 🧪 Testing Guidelines

### Writing Tests

1. **Use pytest fixtures:**
   ```python
   @pytest.fixture
   def gesture_recognizer():
       return GestureRecognizer()
   ```

2. **Test both success and failure cases:**
   ```python
   def test_gesture_recognition_success(gesture_recognizer):
       # Test valid gesture
       assert result.gesture_type == GestureType.PINCH
   
   def test_gesture_recognition_invalid(gesture_recognizer):
       # Test invalid input
       with pytest.raises(ValueError):
           recognizer.recognize_gesture(None)
   ```

3. **Mock external dependencies:**
   ```python
   @pytest.mark.skipif(not sys.stdin.isatty(), reason="Requires TTY")
   def test_interactive_feature():
       # Test that requires user interaction
       pass
   ```

### Test Coverage

- Aim for >80% code coverage
- Focus on core functionality
- Test edge cases and error handling
- Skip interactive tests in CI environments

## 🎨 Code Style

### Python Style Guide

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these specifics:

```python
# Use 4 spaces for indentation
def function_name(param1: str, param2: int) -> bool:
    """Docstring explaining the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    """
    return True

# Type hints for function signatures
def detect_hands(self, frame: np.ndarray) -> List[HandLandmarks]:
    pass

# Descriptive variable names
cursor_position = (screen_x, screen_y)  # Good
cp = (x, y)  # Bad

# Constants in UPPER_CASE
MAX_HANDS = 2
PINCH_THRESHOLD = 0.05
```

### Documentation

- **Docstrings** for all public classes and functions
- **Comments** for complex logic
- **Type hints** for function parameters and returns
- **README updates** for new features

## 🐛 Bug Reports

### Before Submitting

1. Check existing issues
2. Test with latest version
3. Verify it's not a configuration issue

### Bug Report Template

```markdown
**Description:**
Clear description of the bug

**Environment:**
- OS: [Windows 11 / macOS 14 / Ubuntu 22.04]
- Python version: [3.11.5]
- MediaPipe version: [0.10.35]

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Screenshots/Videos:**
If applicable

**Error Messages:**
```
Paste error messages here
```

**Additional Context:**
Any other relevant information
```

## 💡 Feature Requests

### Before Submitting

1. Check if feature already exists
2. Review existing feature requests
3. Consider if it fits project scope

### Feature Request Template

```markdown
**Feature Description:**
Clear description of the feature

**Use Case:**
Why is this feature needed?

**Proposed Solution:**
How could this be implemented?

**Alternatives Considered:**
Other ways to solve the problem

**Additional Context:**
Screenshots, mockups, examples
```

## 🔄 Pull Request Guidelines

### Before Submitting PR

- [ ] Code follows project style guidelines
- [ ] Tests added/updated for changes
- [ ] All tests passing locally
- [ ] Documentation updated
- [ ] Changelog updated (for significant changes)
- [ ] Commit messages are clear and descriptive

### PR Checklist

- [ ] PR title is clear and descriptive
- [ ] Description explains what/why/how
- [ ] References related issues
- [ ] Screenshots/videos for UI changes
- [ ] Ready for review (not draft)

### Review Process

1. Automated tests run on PR
2. Code review by maintainers
3. Requested changes addressed
4. Approval and merge

## 🏆 Recognition

Contributors will be recognized in:
- GitHub contributors page
- Release notes for significant contributions
- README acknowledgments section

## 📧 Getting Help

- **Issues:** [GitHub Issues](https://github.com/Idk507/gesture_control/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Idk507/gesture_control/discussions)
- **Email:** Contact project maintainer

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Gesture Control! 🙏**
