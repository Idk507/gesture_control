"""
Configuration utilities for gesture control library.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """
    Configuration management for gesture control system.

    Handles loading, saving, and default configuration values.
    """

    # Default configuration values
    DEFAULTS = {
        'camera': {
            'index': 0,
            'width': 640,
            'height': 480,
            'fps': 30
        },
        'detection': {
            'max_hands': 1,
            'detection_confidence': 0.7,
            'tracking_confidence': 0.5,
            'use_mock': None  # Auto-detect based on MediaPipe availability
        },
        'gestures': {
            'swipe_threshold': 0.08,
            'pinch_threshold': 0.04,
            'smoothing_frames': 5,
            'min_confidence': 0.6
        },
        'actions': {
            'scroll_amount': 2,
            'action_cooldown': 0.3,
            'enable_safety': True
        },
        'system': {
            'show_preview': True,
            'log_level': 'INFO'
        }
    }

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_file: Path to configuration file (optional)
        """
        self.config_file = config_file or self._get_default_config_path()
        self.config = self.DEFAULTS.copy()
        self.load()

    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        config_dir = Path.home() / '.gesture_control'
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / 'config.json')

    def load(self) -> bool:
        """
        Load configuration from file.

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    self._merge_configs(self.config, loaded_config)
                return True
            else:
                # Save defaults if file doesn't exist
                self.save()
                return True
        except Exception as e:
            print(f"Error loading config: {e}")
            return False

    def save(self) -> bool:
        """
        Save configuration to file.

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def _merge_configs(self, base: Dict, update: Dict):
        """Recursively merge configuration dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key.

        Args:
            key: Dot-separated configuration key (e.g., 'camera.width')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value by dot-separated key.

        Args:
            key: Dot-separated configuration key (e.g., 'camera.width')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config

        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self.config = self.DEFAULTS.copy()

    def __getitem__(self, key: str) -> Any:
        """Get configuration value using dictionary-style access."""
        return self.get(key)

    def __setitem__(self, key: str, value: Any):
        """Set configuration value using dictionary-style access."""
        self.set(key, value)

    def __str__(self):
        """String representation of configuration."""
        return json.dumps(self.config, indent=2)
