#!/usr/bin/env python3
"""
Test script for the gesture control module.
"""

import sys
import os
import pytest

# Add gesture_control to path
sys.path.insert(0, 'gesture_control')

def test_import():
    """Test importing the module."""
    from gesture_control import GestureControl
    print("✅ Module imported successfully")
    assert GestureControl is not None

@pytest.fixture
def gc():
    """Provide a gesture control instance for tests."""
    from gesture_control import GestureControl
    return GestureControl(use_mock_detection=True)


def test_create_instance(gc):
    """Test creating a GestureControl instance."""
    print("✅ GestureControl instance created")
    assert gc is not None

def test_system_stats(gc):
    """Test getting system statistics."""
    stats = gc.get_system_stats()
    print(f"✅ System stats retrieved: state={stats['state']}")
    assert 'state' in stats

def test_components():
    """Test importing individual components."""
    from gesture_control.core.capture import CameraCapture
    from gesture_control.core.detection import HandDetector
    from gesture_control.core.gestures import GestureRecognizer
    from gesture_control.core.actions import ActionExecutor
    print("✅ All core components imported successfully")
    assert all([CameraCapture, HandDetector, GestureRecognizer, ActionExecutor])

def main():
    """Run all tests."""
    print("🧪 Testing Gesture Control Module")
    print("=" * 40)

    # Test import
    test_import()
    test_components()

    # Fixture is managed by pytest, so build explicitly for script mode
    from gesture_control import GestureControl
    instance = GestureControl(use_mock_detection=True)
    test_create_instance(instance)
    test_system_stats(instance)

    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    main()
