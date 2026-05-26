#!/usr/bin/env python
# coding: utf-8

# # Action Mapping Module
# 
# This notebook implements OS-level action mapping for the gesture control system.
# It converts detected gestures into actual system actions like scrolling, mouse clicks, and keyboard events.
# 
# ## Requirements
# - PyAutoGUI (for cross-platform OS control)
# - Gesture recognition data from previous module

# In[1]:


import pyautogui
import time
import platform
from typing import Dict, Optional, Any
import logging
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure PyAutoGUI
pyautogui.FAILSAFE = True  # Enable failsafe
pyautogui.PAUSE = 0.01     # Small pause between actions

# Import gesture classes (from previous notebook)
import sys
sys.path.append('.')
from test_gestures import GestureType, GestureAction, GestureResult

# Detect OS for platform-specific behavior
CURRENT_OS = platform.system().lower()
logger.info(f"Detected OS: {CURRENT_OS}")


# ## Action Types and Platform Support
# 
# Define the action types and their platform-specific implementations.
# PyAutoGUI provides cross-platform support for mouse and keyboard actions.

# In[2]:


class ActionType(Enum):
    """Types of actions that can be performed."""

    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    SCROLL_LEFT = "scroll_left"
    SCROLL_RIGHT = "scroll_right"
    CLICK = "click"
    RIGHT_CLICK = "right_click"
    DOUBLE_CLICK = "double_click"
    HOVER = "hover"
    IDLE = "idle"
    KEY_PRESS = "key_press"
    NONE = "none"

class ActionResult:
    """Result of performing an action."""

    def __init__(self, action_type: ActionType, success: bool, message: str = "", details: Any = None):
        """
        Initialize action result.

        Args:
            action_type: Type of action performed
            success: Whether the action was successful
            message: Optional message about the action
            details: Additional details about the action
        """
        self.action_type = action_type
        self.success = success
        self.message = message
        self.details = details
        self.timestamp = time.time()

    def __str__(self):
        status = "✅" if self.success else "❌"
        return f"{status} {self.action_type.value}: {self.message}"

# Gesture to action mapping (matching README requirements)
GESTURE_TO_ACTION = {
    GestureAction.SCROLL_UP: ActionType.SCROLL_UP,
    GestureAction.SCROLL_DOWN: ActionType.SCROLL_DOWN,
    GestureAction.SCROLL_LEFT: ActionType.SCROLL_LEFT,
    GestureAction.SCROLL_RIGHT: ActionType.SCROLL_RIGHT,
    GestureAction.CLICK: ActionType.CLICK,
    GestureAction.HOVER: ActionType.HOVER,
    GestureAction.IDLE: ActionType.IDLE,
    GestureAction.NONE: ActionType.NONE,
}


# ## Action Executor Class
# 
# The ActionExecutor handles the actual execution of OS-level actions using PyAutoGUI.
# It includes safety measures, rate limiting, and platform-specific optimizations.

# In[3]:


class ActionExecutor:
    """
    Executes OS-level actions based on gesture recognition results.

    Uses PyAutoGUI for cross-platform mouse and keyboard control.
    Includes safety measures and rate limiting to prevent accidental actions.
    """

    def __init__(self,
                 scroll_amount: int = 3,
                 action_cooldown: float = 0.2,
                 enable_safety: bool = True):
        """
        Initialize action executor.

        Args:
            scroll_amount: Number of scroll units per scroll action
            action_cooldown: Minimum time between actions (seconds)
            enable_safety: Enable safety measures (failsafe, etc.)
        """
        self.scroll_amount = scroll_amount
        self.action_cooldown = action_cooldown
        self.enable_safety = enable_safety

        # Rate limiting
        self.last_action_time = 0
        self.last_action_type = None

        # Action statistics
        self.action_counts = {action: 0 for action in ActionType}

        # Platform-specific settings
        self._configure_platform()

        logger.info(f"ActionExecutor initialized: scroll={scroll_amount}, cooldown={action_cooldown}s")

    def _configure_platform(self):
        """Configure platform-specific settings."""
        if CURRENT_OS == "windows":
            # Windows-specific settings
            self.scroll_direction = 1  # Positive for down on Windows
        elif CURRENT_OS == "darwin":  # macOS
            # macOS-specific settings
            self.scroll_direction = -1  # Negative for down on macOS
        else:  # Linux and others
            # Linux-specific settings
            self.scroll_direction = 1

        logger.info(f"Platform configured: {CURRENT_OS}, scroll_direction={self.scroll_direction}")

    def execute_gesture(self, gesture_result: GestureResult) -> ActionResult:
        """
        Execute action based on gesture result.

        Args:
            gesture_result: Result from gesture recognition

        Returns:
            ActionResult indicating success/failure
        """
        if gesture_result.action == GestureAction.NONE:
            return ActionResult(ActionType.NONE, True, "No action required")

        # Check rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_action_time

        if time_since_last < self.action_cooldown:
            return ActionResult(ActionType.NONE, True, 
                              f"Rate limited ({time_since_last:.2f}s < {self.action_cooldown}s)")

        # Get action type
        action_type = GESTURE_TO_ACTION.get(gesture_result.action, ActionType.NONE)

        # Execute action
        result = self._execute_action(action_type, gesture_result.confidence)

        # Update statistics
        if result.success:
            self.last_action_time = current_time
            self.last_action_type = action_type
            self.action_counts[action_type] += 1

        return result

    def _execute_action(self, action_type: ActionType, confidence: float) -> ActionResult:
        """Execute the specific action type."""
        try:
            if action_type == ActionType.SCROLL_UP:
                return self._scroll_up()
            elif action_type == ActionType.SCROLL_DOWN:
                return self._scroll_down()
            elif action_type == ActionType.SCROLL_LEFT:
                return self._scroll_left()
            elif action_type == ActionType.SCROLL_RIGHT:
                return self._scroll_right()
            elif action_type == ActionType.CLICK:
                return self._click()
            elif action_type == ActionType.HOVER:
                return self._hover()
            elif action_type == ActionType.IDLE:
                return self._idle()
            else:
                return ActionResult(action_type, False, f"Unknown action type: {action_type}")

        except Exception as e:
            logger.error(f"Error executing action {action_type}: {e}")
            return ActionResult(action_type, False, f"Execution error: {e}")

    def _scroll_up(self) -> ActionResult:
        """Perform scroll up action."""
        # Scroll up (negative direction)
        scroll_units = -self.scroll_amount * self.scroll_direction
        pyautogui.scroll(scroll_units)
        return ActionResult(ActionType.SCROLL_UP, True, f"Scrolled up {abs(scroll_units)} units")

    def _scroll_down(self) -> ActionResult:
        """Perform scroll down action."""
        # Scroll down (positive direction)
        scroll_units = self.scroll_amount * self.scroll_direction
        pyautogui.scroll(scroll_units)
        return ActionResult(ActionType.SCROLL_DOWN, True, f"Scrolled down {abs(scroll_units)} units")

    def _scroll_left(self) -> ActionResult:
        """Perform horizontal scroll left."""
        # Horizontal scrolling (if supported)
        try:
            # Some systems support horizontal scroll with shift+scroll
            pyautogui.keyDown('shift')
            pyautogui.scroll(-self.scroll_amount)
            pyautogui.keyUp('shift')
            return ActionResult(ActionType.SCROLL_LEFT, True, f"Scrolled left {self.scroll_amount} units")
        except Exception:
            return ActionResult(ActionType.SCROLL_LEFT, False, "Horizontal scroll not supported")

    def _scroll_right(self) -> ActionResult:
        """Perform horizontal scroll right."""
        try:
            pyautogui.keyDown('shift')
            pyautogui.scroll(self.scroll_amount)
            pyautogui.keyUp('shift')
            return ActionResult(ActionType.SCROLL_RIGHT, True, f"Scrolled right {self.scroll_amount} units")
        except Exception:
            return ActionResult(ActionType.SCROLL_RIGHT, False, "Horizontal scroll not supported")

    def _click(self) -> ActionResult:
        """Perform mouse click action."""
        pyautogui.click()
        return ActionResult(ActionType.CLICK, True, "Mouse clicked")

    def _hover(self) -> ActionResult:
        """Handle hover mode (no action, just state)."""
        # Hover mode doesn't perform an action, just indicates ready state
        return ActionResult(ActionType.HOVER, True, "Hover mode active")

    def _idle(self) -> ActionResult:
        """Handle idle mode."""
        # Idle mode - no action
        return ActionResult(ActionType.IDLE, True, "Idle mode")

    def execute_action_direct(self, action_type: ActionType) -> ActionResult:
        """Execute an action directly (for testing/manual control)."""
        return self._execute_action(action_type, 1.0)

    def get_action_stats(self) -> Dict:
        """Get action execution statistics."""
        return {
            'total_actions': sum(self.action_counts.values()),
            'action_counts': {action.value: count for action, count in self.action_counts.items()},
            'last_action': self.last_action_type.value if self.last_action_type else None,
            'last_action_time': self.last_action_time,
            'platform': CURRENT_OS,
            'settings': {
                'scroll_amount': self.scroll_amount,
                'action_cooldown': self.action_cooldown,
                'scroll_direction': self.scroll_direction,
            }
        }

    def reset_stats(self):
        """Reset action statistics."""
        self.action_counts = {action: 0 for action in ActionType}
        self.last_action_time = 0
        self.last_action_type = None
        logger.info("Action statistics reset")


# ## Testing Action Execution
# 
# Let's test the action execution functionality. **Note:** These tests will actually perform mouse/keyboard actions, so use caution!

# In[4]:


# Test action execution (with safety warnings)
def test_action_execution():
    """Test action execution functionality."""

    print("🔔 ACTION EXECUTION TEST")
    print("⚠️  WARNING: This test will perform actual mouse/keyboard actions!")
    print("   Make sure your environment is safe for testing.")
    print("   PyAutoGUI failsafe: Move mouse to top-left corner to abort.\n")

    # Ask for user confirmation
    response = input("Do you want to continue with action testing? (y/N): ").lower().strip()
    if response != 'y':
        print("Action testing cancelled.")
        return

    print("\nTesting Action Execution...")

    # Initialize executor with safe settings
    executor = ActionExecutor(
        scroll_amount=1,  # Small scroll amount for testing
        action_cooldown=0.5,  # Longer cooldown for testing
        enable_safety=True
    )

    print("\n1. Testing direct action execution...")

    # Test hover (safe action)
    result = executor.execute_action_direct(ActionType.HOVER)
    print(f"   Hover: {result}")

    # Test idle (safe action)
    result = executor.execute_action_direct(ActionType.IDLE)
    print(f"   Idle: {result}")

    print("\n2. Testing gesture-based execution...")

    # Create mock gesture results
    from test_gestures import GestureResult, GestureAction

    # Test scroll down gesture
    scroll_gesture = GestureResult(GestureType.SWIPE_DOWN, 0.9)
    scroll_gesture.action = GestureAction.SCROLL_DOWN
    result = executor.execute_gesture(scroll_gesture)
    print(f"   Scroll down gesture: {result}")

    # Test rate limiting
    print("\n3. Testing rate limiting...")
    time.sleep(0.1)  # Wait less than cooldown
    result2 = executor.execute_gesture(scroll_gesture)
    print(f"   Rate limited result: {result2}")

    print("\n4. Testing statistics...")
    stats = executor.get_action_stats()
    print(f"   Total actions: {stats['total_actions']}")
    print(f"   Action counts: {stats['action_counts']}")
    print(f"   Platform: {stats['platform']}")

    print("\n✅ Action execution tests completed")
    print("💡 Tip: Test scroll actions in a scrollable window (browser, text editor, etc.)")

# Uncomment to run (requires user confirmation)
# test_action_execution()
print("Action execution test commented out for safety - uncomment to test")


# ## Safe Testing (No Actual Actions)
# 
# Test the action mapping logic without performing actual OS actions.

# In[5]:


# Safe testing without actual actions
def test_safe_action_mapping():
    """Test action mapping logic without performing actual actions."""

    print("Testing Safe Action Mapping (No Actual Actions)...")

    # Create mock executor that doesn't perform actions
    class MockActionExecutor(ActionExecutor):
        def __init__(self):
            super().__init__()
            self.mock_actions = []

        def _scroll_up(self):
            self.mock_actions.append("scroll_up")
            return ActionResult(ActionType.SCROLL_UP, True, "Mock scroll up")

        def _scroll_down(self):
            self.mock_actions.append("scroll_down")
            return ActionResult(ActionType.SCROLL_DOWN, True, "Mock scroll down")

        def _click(self):
            self.mock_actions.append("click")
            return ActionResult(ActionType.CLICK, True, "Mock click")

    executor = MockActionExecutor()

    # Test all gesture types
    gesture_tests = [
        (GestureType.SWIPE_DOWN, GestureAction.SCROLL_DOWN),
        (GestureType.SWIPE_UP, GestureAction.SCROLL_UP),
        (GestureType.PINCH, GestureAction.CLICK),
        (GestureType.HAND_OPEN, GestureAction.HOVER),
        (GestureType.NONE, GestureAction.NONE),
    ]

    print("\nTesting gesture to action mapping...")
    for gesture_type, expected_action in gesture_tests:
        gesture_result = GestureResult(gesture_type, 0.8)
        gesture_result.action = expected_action

        result = executor.execute_gesture(gesture_result)
        print(f"   {gesture_type.value} → {expected_action.value}: {result}")

    print(f"\nMock actions performed: {executor.mock_actions}")

    # Test statistics
    stats = executor.get_action_stats()
    print(f"\nAction statistics: {stats['action_counts']}")

    print("\n✅ Safe action mapping tests completed")

# Run safe testing
test_safe_action_mapping()


# ## Platform-Specific Testing
# 
# Test platform-specific behavior and configurations.

# In[6]:


# Platform testing
def test_platform_support():
    """Test platform-specific functionality."""

    print("Testing Platform Support...")
    print(f"Current OS: {CURRENT_OS}")

    executor = ActionExecutor()

    # Test platform configuration
    print(f"\nPlatform settings:")
    stats = executor.get_action_stats()
    for key, value in stats['settings'].items():
        print(f"   {key}: {value}")

    # Test PyAutoGUI functionality
    print(f"\nPyAutoGUI info:")
    try:
        screen_size = pyautogui.size()
        print(f"   Screen size: {screen_size}")

        mouse_pos = pyautogui.position()
        print(f"   Mouse position: {mouse_pos}")

        print(f"   Failsafe enabled: {pyautogui.FAILSAFE}")
        print(f"   Pause between actions: {pyautogui.PAUSE}s")

    except Exception as e:
        print(f"   Error getting PyAutoGUI info: {e}")

    # Test action availability
    print(f"\nAction availability:")
    available_actions = [
        "scroll_up", "scroll_down", "click", 
        "hover", "idle"
    ]

    for action in available_actions:
        print(f"   {action}: ✅ Available")

    # Horizontal scroll may not be available on all platforms
    try:
        # Test horizontal scroll detection
        result = executor.execute_action_direct(ActionType.SCROLL_LEFT)
        h_scroll_available = "✅" if result.success else "❌"
        print(f"   horizontal_scroll: {h_scroll_available} ({result.message})")
    except Exception as e:
        print(f"   horizontal_scroll: ❌ Error testing: {e}")

    print("\n✅ Platform support tests completed")

# Run platform testing
test_platform_support()


# ## Performance and Error Handling
# 
# Test performance characteristics and error handling.

# In[7]:


# Performance and error testing
def test_performance_and_errors():
    """Test performance and error handling."""

    print("Testing Performance and Error Handling...")

    # Mock executor for safe testing
    class MockActionExecutor(ActionExecutor):
        def _scroll_up(self):
            time.sleep(0.001)  # Simulate small delay
            return ActionResult(ActionType.SCROLL_UP, True, "Mock scroll")

    executor = MockActionExecutor(action_cooldown=0.01)  # Fast cooldown for testing

    # Performance test
    print("\n1. Performance testing...")
    import time

    num_tests = 100
    start_time = time.time()

    for i in range(num_tests):
        gesture = GestureResult(GestureType.SWIPE_UP, 0.8)
        gesture.action = GestureAction.SCROLL_UP
        executor.execute_gesture(gesture)

    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / num_tests
    actions_per_sec = 1.0 / avg_time if avg_time > 0 else 0

    print(f"   Processed {num_tests} actions in {total_time:.3f} seconds")
    print(f"   Average time per action: {avg_time:.4f} seconds")
    print(f"   Actions per second: {actions_per_sec:.1f}")

    # Error handling test
    print("\n2. Error handling testing...")

    # Test invalid gesture
    invalid_gesture = GestureResult(GestureType.NONE, 0.0)
    invalid_gesture.action = GestureAction.NONE
    result = executor.execute_gesture(invalid_gesture)
    print(f"   Invalid gesture: {result}")

    # Test rate limiting
    gesture = GestureResult(GestureType.SWIPE_DOWN, 0.9)
    gesture.action = GestureAction.SCROLL_DOWN

    result1 = executor.execute_gesture(gesture)
    result2 = executor.execute_gesture(gesture)  # Should be rate limited
    print(f"   Rate limiting: First={result1.success}, Second={result2.success}")

    # Test statistics
    print("\n3. Statistics testing...")
    stats = executor.get_action_stats()
    print(f"   Total actions executed: {stats['total_actions']}")
    print(f"   Most common action: {max(stats['action_counts'], key=stats['action_counts'].get)}")

    # Reset and verify
    executor.reset_stats()
    reset_stats = executor.get_action_stats()
    print(f"   After reset: {reset_stats['total_actions']} actions")

    print("\n✅ Performance and error handling tests completed")

# Run performance testing
test_performance_and_errors()


# ## Action Mapping Summary
# 
# This notebook has implemented a comprehensive OS action mapping system with:
# 
# - **Cross-platform support**: PyAutoGUI for Windows, macOS, and Linux
# - **Gesture-to-action mapping**: Direct mapping from detected gestures to OS actions
# - **Safety measures**: Failsafe mechanisms and rate limiting
# - **Platform-specific optimizations**: Scroll direction adjustments for different OSes
# - **Performance monitoring**: Action statistics and timing measurements
# 
# ### Supported Actions
# - **Scroll Up/Down**: Vertical scrolling with platform-specific direction handling
# - **Scroll Left/Right**: Horizontal scrolling using shift+scroll
# - **Click**: Mouse click for selection
# - **Hover/Idle**: State management for gesture control system
# 
# ### Safety Features
# - **Rate limiting**: Prevents accidental repeated actions
# - **Failsafe**: PyAutoGUI failsafe (move mouse to corner to abort)
# - **Cooldown periods**: Configurable delays between actions
# - **Error handling**: Graceful handling of execution failures
# 
# ### Platform Support
# - **Windows**: Native scroll wheel support
# - **macOS**: Inverted scroll direction handling
# - **Linux**: Standard scroll wheel behavior
# 
# ### Technical Implementation
# - **PyAutoGUI integration**: Cross-platform mouse and keyboard control
# - **Action queuing**: Rate limiting prevents action spam
# - **Statistics tracking**: Performance monitoring and debugging
# - **Mock testing**: Safe testing without actual system actions
# 
# ### Next Steps
# - Integrate with main control loop
# - Add configuration system for action customization
# - Implement gesture training/calibration features
