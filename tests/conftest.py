"""
tests/conftest.py — Shared pytest fixtures for SysWatch Pro.

Adds src/ to sys.path so all imports like `from backend.analyzer import ...`
work correctly without any PYTHONPATH hacks.
"""

import sys
import os
import pytest

# ── Path Setup ────────────────────────────────────────────────────────────────
# Add `src/` to sys.path so tests can import project modules directly.
SRC_PATH = os.path.join(os.path.dirname(__file__), "..", "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, os.path.abspath(SRC_PATH))


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_metrics():
    """Return a standard healthy metrics dict for reuse across tests."""
    return {
        "cpu": 20.0,
        "memory": 40.0,
        "latency": 100.0,
        "requests": 500.0,
    }


@pytest.fixture
def high_cpu_metrics():
    """Return metrics with CPU spiked above typical thresholds."""
    return {
        "cpu": 95.0,
        "memory": 40.0,
        "latency": 100.0,
        "requests": 500.0,
    }


@pytest.fixture
def sample_incident():
    """Return a minimal incident dict matching what AnomalyDetector produces."""
    from datetime import datetime
    return {
        "service": "api-gateway",
        "type": "High Error Rate",
        "description": "Error rate at 50%",
        "details": {"error_rate": 50.0},
        "timestamp": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def anomaly_detector():
    """Return a fresh AnomalyDetector with default thresholds."""
    from backend.analyzer import AnomalyDetector
    return AnomalyDetector()


@pytest.fixture
def root_cause_engine():
    """Return a fresh RootCauseEngine instance."""
    from backend.analyzer import RootCauseEngine
    return RootCauseEngine()
