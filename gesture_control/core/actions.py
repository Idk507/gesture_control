"""
Action execution module for gesture control library.

Maps detected gestures to OS-level actions using PyAutoGUI for cross-platform control.
"""

import pyautogui
import time
import platform
from typing import Dict, Optional, Any
import logging
from enum import Enum

# Set up logging
logger = logging.getLogger(__name__)

# Configure PyAutoGUI
pyautogui.FAILSAFE = True  # Enable failsafe
pyautogui.PAUSE = 0.01     # Small pause between actions

# Import gesture classes
from .gestures import GestureType, GestureAction, GestureResult

# Detect OS for platform-specific behavior
CURRENT_OS = platform.system().lower()
logger.info(f"Detected OS: {CURRENT_OS}")


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
    GestureAction.RIGHT_CLICK: ActionType.RIGHT_CLICK,
    GestureAction.HOVER: ActionType.HOVER,
    GestureAction.IDLE: ActionType.IDLE,
    GestureAction.NONE: ActionType.NONE,
}


class ActionExecutor:
    """
    Executes OS-level actions based on gesture recognition results.

    Uses PyAutoGUI for cross-platform mouse and keyboard control.
    Includes safety measures and rate limiting to prevent accidental actions.
    """

    def __init__(self,
                 scroll_amount: int = 3,
                 action_cooldown: float = 0.2,
                 enable_safety: bool = True,
                 enable_click: bool = False):
        """
        Initialize action executor.

        Args:
            scroll_amount: Number of scroll units per scroll action
            action_cooldown: Minimum time between actions (seconds)
            enable_safety: Enable safety measures (failsafe, etc.)
            enable_click: Allow mouse click action from gestures
        """
        self.scroll_amount = scroll_amount
        self.action_cooldown = action_cooldown
        self.enable_safety = enable_safety
        self.enable_click = enable_click

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
            elif action_type == ActionType.RIGHT_CLICK:
                return self._right_click()
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
        # Scroll up - positive values scroll UP in PyAutoGUI (content moves down)
        scroll_units = self.scroll_amount
        pyautogui.scroll(scroll_units)
        return ActionResult(ActionType.SCROLL_UP, True, f"Scrolled up {abs(scroll_units)} units")

    def _scroll_down(self) -> ActionResult:
        """Perform scroll down action."""
        # Scroll down - negative values scroll DOWN in PyAutoGUI (content moves up)
        scroll_units = -self.scroll_amount
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
        if not self.enable_click:
            return ActionResult(ActionType.CLICK, True, "Click action disabled")
        pyautogui.click()
        return ActionResult(ActionType.CLICK, True, "Mouse clicked")

    def _right_click(self) -> ActionResult:
        """Perform right-click action."""
        if not self.enable_click:
            return ActionResult(ActionType.RIGHT_CLICK, True, "Right-click action disabled")
        pyautogui.rightClick()
        return ActionResult(ActionType.RIGHT_CLICK, True, "Right-clicked")

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
                'enable_click': self.enable_click,
            }
        }

    def reset_stats(self):
        """Reset action statistics."""
        self.action_counts = {action: 0 for action in ActionType}
        self.last_action_time = 0
        self.last_action_type = None
        logger.info("Action statistics reset")
