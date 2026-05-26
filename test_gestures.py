#!/usr/bin/env python
# coding: utf-8

# # Gesture Recognition Module
# 
# This notebook implements gesture recognition logic for the hand gesture control system.
# It analyzes hand landmark movements to detect specific gestures like swipes, pinches, and hand states.
# 
# ## Supported Gestures
# 
# Based on the README requirements:
# - **Swipe Down** → Scroll down
# - **Swipe Up** → Scroll up  
# - **Pinch Gesture** → Select/Click
# - **Hand Open** → Hover/Idle Mode
# 
# ## Requirements
# - NumPy (for coordinate calculations)
# - Hand detection data from previous module

# In[1]:


import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import hand detection classes (from previous notebook)
import sys
sys.path.append('.')
from test_detection import HandLandmarks, HandDetector


# ## Gesture Types
# 
# Define the supported gesture types and their corresponding actions.

# In[2]:


class GestureType(Enum):
    """Enumeration of supported gesture types."""

    NONE = "none"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    PINCH = "pinch"
    HAND_OPEN = "hand_open"
    HAND_CLOSED = "hand_closed"

    def __str__(self):
        return self.value

class GestureAction(Enum):
    """Corresponding actions for each gesture."""

    NONE = "none"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    SCROLL_LEFT = "scroll_left"
    SCROLL_RIGHT = "scroll_right"
    CLICK = "click"
    HOVER = "hover"
    IDLE = "idle"

# Gesture to action mapping
GESTURE_ACTIONS = {
    GestureType.SWIPE_UP: GestureAction.SCROLL_UP,
    GestureType.SWIPE_DOWN: GestureAction.SCROLL_DOWN,
    GestureType.SWIPE_LEFT: GestureAction.SCROLL_LEFT,
    GestureType.SWIPE_RIGHT: GestureAction.SCROLL_RIGHT,
    GestureType.PINCH: GestureAction.CLICK,
    GestureType.HAND_OPEN: GestureAction.HOVER,
    GestureType.HAND_CLOSED: GestureAction.IDLE,
    GestureType.NONE: GestureAction.NONE,
}

class GestureResult:
    """Result of gesture recognition."""

    def __init__(self, gesture_type: GestureType, confidence: float, hand_data: Any = None):
        """
        Initialize gesture result.

        Args:
            gesture_type: Detected gesture type
            confidence: Confidence score (0.0-1.0)
            hand_data: Associated hand landmark data
        """
        self.gesture_type = gesture_type
        self.confidence = confidence
        self.action = GESTURE_ACTIONS.get(gesture_type, GestureAction.NONE)
        self.hand_data = hand_data
        self.timestamp = time.time()

    def __str__(self):
        return f"GestureResult(type={self.gesture_type.value}, confidence={self.confidence:.2f}, action={self.action.value})"


# ## Gesture Recognition Class
# 
# The GestureRecognizer analyzes hand movements and detects gestures using:
# - **Movement tracking**: Velocity and displacement analysis
# - **Threshold-based detection**: Configurable sensitivity settings
# - **Smoothing filters**: Moving averages to reduce noise
# - **State management**: Gesture state transitions

# In[3]:


class GestureRecognizer:
    """
    Recognizes hand gestures from landmark data.

    Uses movement analysis, thresholds, and smoothing to detect gestures reliably.
    """

    def __init__(self,
                 swipe_threshold: float = 0.1,
                 pinch_threshold: float = 0.05,
                 smoothing_frames: int = 5,
                 min_confidence: float = 0.7):
        """
        Initialize gesture recognizer.

        Args:
            swipe_threshold: Minimum displacement for swipe detection
            pinch_threshold: Maximum distance for pinch detection
            smoothing_frames: Number of frames for smoothing
            min_confidence: Minimum confidence for gesture recognition
        """
        self.swipe_threshold = swipe_threshold
        self.pinch_threshold = pinch_threshold
        self.smoothing_frames = smoothing_frames
        self.min_confidence = min_confidence

        # Movement history for smoothing
        self.position_history = []
        self.velocity_history = []

        # Gesture state
        self.last_gesture = GestureType.NONE
        self.gesture_start_time = None

        logger.info(f"GestureRecognizer initialized with thresholds: swipe={swipe_threshold}, pinch={pinch_threshold}")

    def recognize_gesture(self, hand: HandLandmarks) -> GestureResult:
        """
        Analyze hand landmarks and recognize gesture.

        Args:
            hand: Hand landmark data

        Returns:
            GestureResult with detected gesture and confidence
        """
        if hand is None or not hand.landmarks:
            return GestureResult(GestureType.NONE, 0.0)

        # Extract key positions
        index_tip = hand.get_landmark(8)  # Index finger tip
        thumb_tip = hand.get_landmark(4)  # Thumb tip
        wrist = hand.get_wrist_position()

        if not all([index_tip, thumb_tip, wrist]):
            return GestureResult(GestureType.NONE, 0.0)

        # Update movement history
        current_pos = np.array([index_tip['x'], index_tip['y']])
        self._update_history(current_pos)

        # Analyze different gesture types
        gestures = [
            self._detect_pinch(index_tip, thumb_tip),
            self._detect_hand_state(hand),
            self._detect_swipe(),
        ]

        # Find the best gesture (highest confidence)
        best_gesture = GestureResult(GestureType.NONE, 0.0, hand)

        for gesture_result in gestures:
            if gesture_result.confidence > best_gesture.confidence:
                best_gesture = gesture_result

        # Update gesture state
        if best_gesture.gesture_type != self.last_gesture:
            self.last_gesture = best_gesture.gesture_type
            self.gesture_start_time = time.time() if best_gesture.gesture_type != GestureType.NONE else None

        return best_gesture

    def _update_history(self, current_pos: np.ndarray):
        """Update position and velocity history for smoothing."""
        self.position_history.append(current_pos)

        # Keep only recent positions
        if len(self.position_history) > self.smoothing_frames:
            self.position_history.pop(0)

        # Calculate velocity if we have enough history
        if len(self.position_history) >= 2:
            velocity = self.position_history[-1] - self.position_history[-2]
            self.velocity_history.append(velocity)

            if len(self.velocity_history) > self.smoothing_frames:
                self.velocity_history.pop(0)

    def _detect_swipe(self) -> GestureResult:
        """Detect swipe gestures based on movement direction and distance."""
        if len(self.position_history) < self.smoothing_frames:
            return GestureResult(GestureType.NONE, 0.0)

        # Calculate smoothed displacement
        start_pos = np.mean(self.position_history[:3], axis=0)  # First 3 frames
        end_pos = np.mean(self.position_history[-3:], axis=0)  # Last 3 frames
        displacement = end_pos - start_pos

        # Calculate displacement magnitude
        distance = np.linalg.norm(displacement)

        if distance < self.swipe_threshold:
            return GestureResult(GestureType.NONE, 0.0)

        # Determine swipe direction
        dx, dy = displacement

        # Normalize direction
        if distance > 0:
            dx_norm, dy_norm = dx / distance, dy / distance
        else:
            return GestureResult(GestureType.NONE, 0.0)

        # Classify swipe direction
        confidence = min(distance / (self.swipe_threshold * 2), 1.0)  # Scale confidence

        if abs(dx_norm) > abs(dy_norm):
            # Horizontal swipe
            if dx_norm > 0.7:
                return GestureResult(GestureType.SWIPE_RIGHT, confidence)
            elif dx_norm < -0.7:
                return GestureResult(GestureType.SWIPE_LEFT, confidence)
        else:
            # Vertical swipe
            if dy_norm > 0.7:
                return GestureResult(GestureType.SWIPE_DOWN, confidence)
            elif dy_norm < -0.7:
                return GestureResult(GestureType.SWIPE_UP, confidence)

        return GestureResult(GestureType.NONE, 0.0)

    def _detect_pinch(self, index_tip: Dict, thumb_tip: Dict) -> GestureResult:
        """Detect pinch gesture based on distance between index finger and thumb."""
        # Calculate distance between finger tips
        index_pos = np.array([index_tip['x'], index_tip['y']])
        thumb_pos = np.array([thumb_tip['x'], thumb_tip['y']])

        distance = np.linalg.norm(index_pos - thumb_pos)

        # Pinch is detected when fingers are close together
        if distance < self.pinch_threshold:
            confidence = 1.0 - (distance / self.pinch_threshold)
            confidence = min(confidence, 1.0)
            return GestureResult(GestureType.PINCH, confidence)

        return GestureResult(GestureType.NONE, 0.0)

    def _detect_hand_state(self, hand: HandLandmarks) -> GestureResult:
        """Detect overall hand state (open/closed) for hover/idle modes."""
        finger_tips = hand.get_finger_tips()
        wrist = hand.get_wrist_position()

        if not finger_tips or not wrist:
            return GestureResult(GestureType.NONE, 0.0)

        # Calculate distances from wrist to finger tips
        wrist_pos = np.array([wrist['x'], wrist['y']])

        distances = []
        for tip_name, tip_pos in finger_tips.items():
            tip_coords = np.array([tip_pos['x'], tip_pos['y']])
            distance = np.linalg.norm(tip_coords - wrist_pos)
            distances.append(distance)

        avg_distance = np.mean(distances)

        # Simple heuristic: hand is "open" if fingers are extended
        # This is a basic implementation - could be improved with more sophisticated analysis
        if avg_distance > 0.15:  # Threshold for "open" hand
            return GestureResult(GestureType.HAND_OPEN, 0.8)
        else:
            return GestureResult(GestureType.HAND_CLOSED, 0.8)

    def reset(self):
        """Reset gesture recognition state."""
        self.position_history.clear()
        self.velocity_history.clear()
        self.last_gesture = GestureType.NONE
        self.gesture_start_time = None
        logger.info("Gesture recognizer reset")

    def get_gesture_stats(self) -> Dict:
        """Get statistics about gesture recognition."""
        return {
            'current_gesture': self.last_gesture.value,
            'history_length': len(self.position_history),
            'gesture_duration': time.time() - self.gesture_start_time if self.gesture_start_time else 0,
            'thresholds': {
                'swipe': self.swipe_threshold,
                'pinch': self.pinch_threshold,
                'smoothing_frames': self.smoothing_frames,
            }
        }


# ## Testing Gesture Recognition
# 
# Let's test the gesture recognition with mock hand data.

# In[4]:


# Test gesture recognition
def test_gesture_recognition():
    """Test gesture recognition functionality."""

    print("Testing Gesture Recognition...")

    # Initialize recognizer
    recognizer = GestureRecognizer(
        swipe_threshold=0.05,  # Lower threshold for testing
        pinch_threshold=0.03,
        smoothing_frames=3
    )

    # Initialize hand detector for mock data
    detector = HandDetector(use_mock=True)

    print("\n1. Testing with static hand (should detect hand state)...")
    test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    # Test multiple frames of static hand
    for i in range(5):
        hands = detector.detect_hands(test_frame)
        if hands:
            gesture = recognizer.recognize_gesture(hands[0])
            print(f"   Frame {i+1}: {gesture}")
        else:
            print(f"   Frame {i+1}: No hands detected")

    print("\n2. Testing pinch gesture simulation...")
    # Create mock hand with close finger tips (pinch)
    mock_landmarks = detector._create_mock_landmark_data()

    # Modify landmarks to simulate pinch (close index and thumb)
    mock_landmarks.landmark[4].x = 0.5  # Thumb
    mock_landmarks.landmark[4].y = 0.5
    mock_landmarks.landmark[8].x = 0.52  # Index (close to thumb)
    mock_landmarks.landmark[8].y = 0.52

    mock_hand = HandLandmarks(mock_landmarks, "Right")
    gesture = recognizer.recognize_gesture(mock_hand)
    print(f"   Pinch test: {gesture}")

    print("\n3. Testing gesture statistics...")
    stats = recognizer.get_gesture_stats()
    print(f"   Current gesture: {stats['current_gesture']}")
    print(f"   History length: {stats['history_length']}")
    print(f"   Thresholds: {stats['thresholds']}")

    # Test reset
    print("\n4. Testing reset functionality...")
    recognizer.reset()
    stats_after_reset = recognizer.get_gesture_stats()
    print(f"   After reset - History length: {stats_after_reset['history_length']}")
    print(f"   After reset - Current gesture: {stats_after_reset['current_gesture']}")

    detector.close()
    print("\n✅ Gesture recognition tests completed")

# Run the test
test_gesture_recognition()


# ## Advanced Gesture Testing
# 
# Test gesture recognition with simulated movement patterns.

# In[5]:


# Advanced gesture testing
def test_simulated_gestures():
    """Test gesture recognition with simulated movement patterns."""

    print("Testing Simulated Gestures...")

    recognizer = GestureRecognizer(swipe_threshold=0.02, smoothing_frames=5)

    # Simulate vertical swipe down
    print("\n1. Simulating SWIPE DOWN gesture...")
    gestures_detected = []

    for i in range(10):
        # Create mock hand with moving index finger
        mock_data = type('MockData', (), {})()
        mock_data.landmark = []

        # Base position that moves down over time
        base_y = 0.3 + (i * 0.01)  # Moving down

        for j in range(21):
            lm = type('Landmark', (), {})()
            lm.x = 0.5 + np.random.uniform(-0.05, 0.05)
            lm.y = base_y + np.random.uniform(-0.02, 0.02)
            lm.z = np.random.uniform(-0.1, 0.1)
            lm.visibility = 0.9
            mock_data.landmark.append(lm)

        mock_hand = HandLandmarks(mock_data, "Right")
        gesture = recognizer.recognize_gesture(mock_hand)
        gestures_detected.append(gesture)

        if gesture.gesture_type != GestureType.NONE:
            print(f"   Frame {i+1}: {gesture}")

    # Check if swipe was detected
    swipe_detected = any(g.gesture_type == GestureType.SWIPE_DOWN for g in gestures_detected)
    print(f"   Swipe down detected: {swipe_detected}")

    # Reset and test swipe up
    recognizer.reset()
    print("\n2. Simulating SWIPE UP gesture...")
    gestures_detected = []

    for i in range(10):
        base_y = 0.4 - (i * 0.01)  # Moving up

        mock_data = type('MockData', (), {})()
        mock_data.landmark = []

        for j in range(21):
            lm = type('Landmark', (), {})()
            lm.x = 0.5 + np.random.uniform(-0.05, 0.05)
            lm.y = base_y + np.random.uniform(-0.02, 0.02)
            lm.z = np.random.uniform(-0.1, 0.1)
            lm.visibility = 0.9
            mock_data.landmark.append(lm)

        mock_hand = HandLandmarks(mock_data, "Right")
        gesture = recognizer.recognize_gesture(mock_hand)
        gestures_detected.append(gesture)

        if gesture.gesture_type != GestureType.NONE:
            print(f"   Frame {i+1}: {gesture}")

    swipe_up_detected = any(g.gesture_type == GestureType.SWIPE_UP for g in gestures_detected)
    print(f"   Swipe up detected: {swipe_up_detected}")

    print("\n✅ Simulated gesture tests completed")

# Run simulated gesture tests
test_simulated_gestures()


# ## Performance Testing
# 
# Test gesture recognition performance and timing.

# In[6]:


# Performance test
def performance_test():
    """Test gesture recognition performance."""

    print("Performance Testing...")

    recognizer = GestureRecognizer()
    detector = HandDetector(use_mock=True)

    # Create test frame
    test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    # Test processing time for 100 frames
    start_time = time.time()
    num_frames = 100
    gestures_found = 0

    for i in range(num_frames):
        hands = detector.detect_hands(test_frame)
        if hands:
            gesture = recognizer.recognize_gesture(hands[0])
            if gesture.gesture_type != GestureType.NONE:
                gestures_found += 1

    end_time = time.time()

    # Calculate metrics
    total_time = end_time - start_time
    avg_time_per_frame = total_time / num_frames
    fps = 1.0 / avg_time_per_frame if avg_time_per_frame > 0 else 0

    print(f"📊 Performance Results:")
    print(f"   Frames processed: {num_frames}")
    print(f"   Total time: {total_time:.3f} seconds")
    print(f"   Average time per frame: {avg_time_per_frame:.4f} seconds")
    print(f"   Processing FPS: {fps:.2f}")
    print(f"   Gestures detected: {gestures_found}")

    detector.close()

# Run performance test
performance_test()


# ## Error Handling and Edge Cases
# 
# Test gesture recognition with various error conditions.

# In[7]:


# Error handling test
def test_error_handling():
    """Test error handling in gesture recognition."""

    print("Testing Error Handling...")

    recognizer = GestureRecognizer()

    # Test with None hand
    print("1. Testing with None hand...")
    gesture = recognizer.recognize_gesture(None)
    print(f"   Result: {gesture} (expected NONE)")

    # Test with empty hand landmarks
    print("2. Testing with empty landmarks...")
    empty_hand = HandLandmarks(None, "Right")
    gesture = recognizer.recognize_gesture(empty_hand)
    print(f"   Result: {gesture} (expected NONE)")

    # Test with missing key landmarks
    print("3. Testing with incomplete landmarks...")
    # Create hand with missing index finger
    mock_data = type('MockData', (), {})()
    mock_data.landmark = []

    # Add all landmarks except index tip (8)
    for i in range(21):
        if i != 8:  # Skip index tip
            lm = type('Landmark', (), {})()
            lm.x, lm.y, lm.z = 0.5, 0.5, 0.0
            lm.visibility = 0.9
            mock_data.landmark.append(lm)

    incomplete_hand = HandLandmarks(mock_data, "Right")
    gesture = recognizer.recognize_gesture(incomplete_hand)
    print(f"   Result: {gesture} (expected NONE due to missing landmarks)")

    # Test reset functionality
    print("4. Testing reset after errors...")
    recognizer.reset()
    stats = recognizer.get_gesture_stats()
    print(f"   After reset: history={stats['history_length']}, gesture={stats['current_gesture']}")

    print("\n✅ Error handling tests completed")

# Run error handling test
test_error_handling()


# ## Gesture Recognition Summary
# 
# This notebook has implemented a comprehensive gesture recognition system with:
# 
# - **Multiple gesture types**: Swipe up/down/left/right, pinch, hand open/closed
# - **Movement analysis**: Velocity and displacement tracking with smoothing
# - **Configurable thresholds**: Adjustable sensitivity for different use cases
# - **State management**: Gesture transition tracking and timing
# - **Confidence scoring**: Reliability assessment for each detection
# 
# ### Key Features
# - **Real-time processing**: Optimized for live camera feed analysis
# - **Robust error handling**: Graceful handling of missing or invalid data
# - **Extensible design**: Easy to add new gesture types
# - **Performance monitoring**: Built-in timing and statistics
# 
# ### Gesture Mapping
# - **Swipe Down** → Scroll down
# - **Swipe Up** → Scroll up
# - **Pinch** → Click/Select
# - **Hand Open** → Hover mode
# - **Hand Closed** → Idle mode
# 
# ### Technical Implementation
# - **Smoothing**: Moving average filters reduce noise and false positives
# - **Thresholds**: Configurable sensitivity prevents accidental triggers
# - **Direction analysis**: Normalized vectors for reliable directional detection
# - **Distance calculations**: Euclidean distance for pinch and hand state detection
# 
# ### Next Steps
# - Integrate with OS action mapping (scroll, keyboard events)
# - Create main control loop combining camera, detection, and gestures
# - Add user calibration and gesture training features
