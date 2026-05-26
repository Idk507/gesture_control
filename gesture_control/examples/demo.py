#!/usr/bin/env python3
"""
Demo script for gesture control library.

This script demonstrates the basic usage of the gesture control system.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for importing gesture_control
sys.path.insert(0, str(Path(__file__).parent.parent))

from gesture_control import GestureControl


def main():
    """Main demo function."""
    print("🎯 Gesture Control Library Demo")
    print("=" * 40)
    print()
    print("This demo will start the gesture control system.")
    print("Make sure you have a webcam available.")
    print()
    print("Controls:")
    print("  - Swipe down with your hand: Scroll down")
    print("  - Swipe up with your hand: Scroll up")
    print("  - Pinch fingers together: Mouse click")
    print("  - Hand open: Hover mode")
    print("  - Press 'q' in the preview window: Quit")
    print("  - Press 'p' in the preview window: Pause/Resume")
    print()
    print("Move your mouse to the top-left corner to emergency stop.")
    print()

    # Ask user for confirmation
    try:
        response = input("Ready to start? (y/N): ").lower().strip()
        if response != 'y':
            print("Demo cancelled.")
            return
    except KeyboardInterrupt:
        print("\nDemo cancelled.")
        return

    print("\n🚀 Starting gesture control system...")

    try:
        # Create gesture control system
        # Using mock detection by default since MediaPipe may not be available
        gc = GestureControl(
            camera_index=0,      # Default camera
            width=640,           # Frame width
            height=480,          # Frame height
            fps=30,              # Target FPS
            show_preview=True,   # Show preview window
            use_mock_detection=True  # Use mock for demo (set to None or False for real detection)
        )

        # Start the system (this will block until stopped)
        success = gc.start()

        if success:
            print("\n✅ Demo completed successfully!")
        else:
            print("\n❌ Demo failed to start.")

    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


def show_available_options():
    """Show available configuration options."""
    print("\n🔧 Configuration Options:")
    print("You can customize the system by modifying these parameters:")
    print()
    print("GestureControl(")
    print("    camera_index=0,      # Camera device (0=default)")
    print("    width=640,           # Frame width")
    print("    height=480,          # Frame height")
    print("    fps=30,              # Target frames per second")
    print("    show_preview=True,   # Show live preview window")
    print("    use_mock_detection=None  # None=auto-detect, True=force mock, False=force real")
    print(")")
    print()
    print("For real hand detection, install MediaPipe:")
    print("    pip install mediapipe")
    print("    # Note: Requires Python 3.11 or 3.12")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        show_available_options()
