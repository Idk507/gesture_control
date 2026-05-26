#!/usr/bin/env python3
"""
Test script for the gesture control module.
"""

import sys
import os

# Add gesture_control to path
sys.path.insert(0, 'gesture_control')

def test_import():
    """Test importing the module."""
    try:
        from gesture_control import GestureControl
        print("✅ Module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_create_instance():
    """Test creating a GestureControl instance."""
    try:
        from gesture_control import GestureControl
        gc = GestureControl(use_mock_detection=True)
        print("✅ GestureControl instance created")
        return gc
    except Exception as e:
        print(f"❌ Instance creation failed: {e}")
        return None

def test_system_stats(gc):
    """Test getting system statistics."""
    try:
        stats = gc.get_system_stats()
        print(f"✅ System stats retrieved: state={stats['state']}")
        return True
    except Exception as e:
        print(f"❌ Stats retrieval failed: {e}")
        return False

def test_components():
    """Test importing individual components."""
    try:
        from gesture_control.core.capture import CameraCapture
        from gesture_control.core.detection import HandDetector
        from gesture_control.core.gestures import GestureRecognizer
        from gesture_control.core.actions import ActionExecutor
        print("✅ All core components imported successfully")
        return True
    except Exception as e:
        print(f"❌ Component import failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Gesture Control Module")
    print("=" * 40)

    # Test import
    if not test_import():
        return

    # Test components
    if not test_components():
        return

    # Test instance creation
    gc = test_create_instance()
    if gc is None:
        return

    # Test system stats
    if not test_system_stats(gc):
        return

    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    main()
