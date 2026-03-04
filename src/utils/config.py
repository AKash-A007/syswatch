# src/utils/config.py
"""Application configuration manager with persistent JSON storage."""

import json
import os
from pathlib import Path
from typing import Any


# Default configuration values
DEFAULTS = {
    "api_host": "localhost",
    "api_port": 8000,
    "api_timeout": 5,
    "use_https": False,
    "service_refresh_interval": 5,
    "metrics_refresh_interval": 1,
    "incidents_refresh_interval": 10,
    "cpu_threshold": 85,
    "memory_threshold": 90,
    "latency_threshold_ms": 500,
    "start_minimized": False,
    "minimize_to_tray": True,
    "show_splash": True,
    "confirm_exit": True,
    "enable_notifications": True,
    "notify_critical": True,
    "notify_high": True,
    "notify_anomaly": False,
    "sound_alerts": False,
    "max_history_points": 3600,
    "data_retention_hours": 24,
}


class AppConfig:
    """Singleton application configuration backed by JSON file."""

    _instance = None
    _data: dict = {}
    _config_path: Path = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._config_path = self._get_config_path()
        self._data = dict(DEFAULTS)
        self.load()

    @staticmethod
    def _get_config_path() -> Path:
        """Return platform-appropriate config file path."""
        if os.name == "nt":
            base = Path(os.environ.get("APPDATA", Path.home()))
        else:
            base = Path.home() / ".config"
        config_dir = base / "SysWatch"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"

    @staticmethod
    def get_data_dir() -> Path:
        """Return directory used for all SysWatch data files."""
        if os.name == "nt":
            base = Path(os.environ.get("APPDATA", Path.home()))
        else:
            base = Path.home() / ".config"
        data_dir = base / "SysWatch"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    def load(self) -> None:
        """Load configuration from disk; fills in any missing keys with defaults."""
        try:
            if self._config_path.exists():
                with open(self._config_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                self._data.update(saved)
        except (json.JSONDecodeError, OSError):
            pass  # Use defaults on any error

    def save(self) -> None:
        """Persist configuration to disk."""
        try:
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except OSError:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def update(self, data: dict) -> None:
        self._data.update(data)

    def reset(self) -> None:
        """Reset all values to defaults and save."""
        self._data = dict(DEFAULTS)
        self.save()

    # Convenience properties
    @property
    def api_base_url(self) -> str:
        protocol = "https" if self._data.get("use_https") else "http"
        host = self._data.get("api_host", "localhost")
        port = self._data.get("api_port", 8000)
        return f"{protocol}://{host}:{port}"

    @property
    def api_timeout(self) -> int:
        return int(self._data.get("api_timeout", 5))

    @property
    def cpu_threshold(self) -> float:
        return float(self._data.get("cpu_threshold", 85))

    @property
    def memory_threshold(self) -> float:
        return float(self._data.get("memory_threshold", 90))

    @property
    def latency_threshold_ms(self) -> float:
        return float(self._data.get("latency_threshold_ms", 500))
