# src/utils/logger.py
"""Centralized logging configuration for SysWatch Pro."""

import logging
import logging.handlers
import sys
from pathlib import Path


# ANSI color codes for console output
_COLORS = {
    "DEBUG": "\033[36m",     # Cyan
    "INFO": "\033[32m",      # Green
    "WARNING": "\033[33m",   # Yellow
    "ERROR": "\033[31m",     # Red
    "CRITICAL": "\033[35m",  # Magenta
    "RESET": "\033[0m",
}

_LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_MAX_BYTES = 5 * 1024 * 1024   # 5 MB per log file
_BACKUP_COUNT = 3
_initialized = False


class _ColoredFormatter(logging.Formatter):
    """Formatter that adds ANSI color codes for console output."""

    def format(self, record: logging.LogRecord) -> str:
        color = _COLORS.get(record.levelname, "")
        reset = _COLORS["RESET"]
        record.levelname = f"{color}{record.levelname}{reset}"
        return super().format(record)


def _get_log_path() -> Path:
    import os
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path.home() / ".config"
    log_dir = base / "SysWatch"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "syswatch.log"


def setup_logging(level: int = logging.INFO) -> None:
    """Initialize root logger with file (rotating) and console handlers.

    Call once at application startup. Subsequent calls are no-ops.
    """
    global _initialized
    if _initialized:
        return
    _initialized = True

    root = logging.getLogger("syswatch")
    root.setLevel(level)
    root.propagate = False

    # --- File handler (rotating) ---
    file_handler = logging.handlers.RotatingFileHandler(
        _get_log_path(),
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
    file_handler.setLevel(level)

    # --- Console handler (colored) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(_ColoredFormatter(_LOG_FORMAT, _DATE_FORMAT))
    console_handler.setLevel(level)

    root.addHandler(file_handler)
    root.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a child logger of the 'syswatch' root logger.

    Automatically calls setup_logging() if not yet initialized.
    """
    setup_logging()
    return logging.getLogger(f"syswatch.{name}")
