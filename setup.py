"""
Setup script for gesture-control package.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Package metadata
setup(
    name="gesture-control",
    version="0.1.0",
    author="Gesture Control Library",
    author_email="",
    description="Hand gesture-based laptop monitor control using MediaPipe and OpenCV",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Idk507/gesture-control",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opencv-python>=4.5.0",
        "pyautogui>=0.9.50",
        "numpy>=1.19.0",
        # MediaPipe is optional - will use mock implementation if not available
        # "mediapipe>=0.8.0",  # Uncomment if you want to require MediaPipe
    ],
    extras_require={
        "mediapipe": ["mediapipe>=0.8.0"],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.812",
        ],
    },
    entry_points={
        "console_scripts": [
            "gesture-control-demo=gesture_control.examples.demo:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
