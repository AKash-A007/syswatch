# src/backend/collector.py
"""Real-time metrics collection using psutil + simulated service metrics."""

import threading
import time
import random
import math
from collections import deque
from datetime import datetime
from typing import Dict, Optional, Deque, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import psutil
from utils.logger import get_logger
from utils.config import AppConfig

logger = get_logger("collector")

# ─── Service definitions (simulated distributed services) ─────────────────────

DEMO_SERVICES: List[Dict] = [
    {"id": "api-gateway",          "name": "API Gateway",           "base_cpu": 22, "base_mem": 40},
    {"id": "auth-service",         "name": "Auth Service",          "base_cpu": 12, "base_mem": 35},
    {"id": "user-service",         "name": "User Service",          "base_cpu": 65, "base_mem": 75},
    {"id": "payment-service",      "name": "Payment Service",       "base_cpu": 18, "base_mem": 42},
    {"id": "notification-service", "name": "Notification Service",  "base_cpu": 88, "base_mem": 91},
    {"id": "analytics-service",    "name": "Analytics Service",     "base_cpu": 35, "base_mem": 55},
    {"id": "cache-service",        "name": "Cache Service (Redis)", "base_cpu": 8,  "base_mem": 28},
    {"id": "db-service",           "name": "Database Service",      "base_cpu": 45, "base_mem": 68},
]

_STATUS_MAP = {
    (0, 60):   "healthy",
    (60, 80):  "warning",
    (80, 101): "critical",
}


def _status_from_usage(cpu: float, mem: float) -> str:
    composite = max(cpu, mem)
    for (lo, hi), status in _STATUS_MAP.items():
        if lo <= composite < hi:
            return status
    return "critical"


class _ServiceState:
    """Tracks evolving simulation state for one service."""

    def __init__(self, svc: Dict):
        self.id = svc["id"]
        self.name = svc["name"]
        self.base_cpu: float = svc["base_cpu"]
        self.base_mem: float = svc["base_mem"]
        self.cpu: float = self.base_cpu
        self.memory: float = self.base_mem
        self.latency: float = 80.0 + self.base_cpu * 2
        self.requests: float = 30.0
        self.start_time = datetime.utcnow()
        # Slow drift variables
        self._cpu_drift: float = 0.0
        self._mem_drift: float = 0.0
        self._t: float = 0.0

    def tick(self) -> None:
        """Advance simulation by one second."""
        self._t += 1
        # Sinusoidal drift + random noise
        self._cpu_drift = 8 * math.sin(self._t / 30) + random.gauss(0, 2)
        self._mem_drift = 5 * math.sin(self._t / 60 + 1) + random.gauss(0, 1.5)

        self.cpu = max(1.0, min(99.0, self.base_cpu + self._cpu_drift))
        self.memory = max(1.0, min(99.0, self.base_mem + self._mem_drift))

        # Latency correlates with CPU
        self.latency = max(10.0, self.cpu * 4 + random.gauss(0, 20))
        # Requests inversely related to latency
        self.requests = max(1.0, 120 - self.latency / 5 + random.gauss(0, 5))

    @property
    def uptime_seconds(self) -> int:
        return int((datetime.utcnow() - self.start_time).total_seconds())

    def as_service_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": _status_from_usage(self.cpu, self.memory),
            "cpu_usage": round(self.cpu, 1),
            "memory_usage": round(self.memory, 1),
            "uptime_seconds": self.uptime_seconds,
        }

    def as_metrics_dict(self) -> Dict:
        return {
            "cpu": round(self.cpu, 2),
            "memory": round(self.memory, 2),
            "latency": round(self.latency, 1),
            "requests": round(self.requests, 1),
        }


class MetricsCollector:
    """
    Background metrics collector.

    - Collects real host-level metrics via psutil every second.
    - Simulates per-service metrics with realistic drift.
    - Keeps an in-memory rolling window of the last MAX_HISTORY points.
    """

    MAX_HISTORY = 3600  # 1 hour at 1-second resolution

    def __init__(self, storage=None):
        self._storage = storage
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Service simulation states
        self._services: Dict[str, _ServiceState] = {
            svc["id"]: _ServiceState(svc) for svc in DEMO_SERVICES
        }

        # Rolling history per service
        self._history: Dict[str, Dict[str, Deque]] = {
            svc_id: {
                "cpu": deque(maxlen=self.MAX_HISTORY),
                "memory": deque(maxlen=self.MAX_HISTORY),
                "latency": deque(maxlen=self.MAX_HISTORY),
                "requests": deque(maxlen=self.MAX_HISTORY),
                "timestamps": deque(maxlen=self.MAX_HISTORY),
            }
            for svc_id in self._services
        }

        # Host system history
        self._host_history: Dict[str, Deque] = {
            "cpu": deque(maxlen=self.MAX_HISTORY),
            "memory": deque(maxlen=self.MAX_HISTORY),
            "disk_read": deque(maxlen=self.MAX_HISTORY),
            "disk_write": deque(maxlen=self.MAX_HISTORY),
            "net_in": deque(maxlen=self.MAX_HISTORY),
            "net_out": deque(maxlen=self.MAX_HISTORY),
            "timestamps": deque(maxlen=self.MAX_HISTORY),
        }

        self._prev_disk = None
        self._prev_net = None

        logger.info("MetricsCollector initialized")

    # ── Public API ─────────────────────────────────────────────────────────────

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._collect_loop, name="metrics-collector", daemon=True
        )
        self._thread.start()
        logger.info("MetricsCollector started")

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        logger.info("MetricsCollector stopped")

    def get_services(self) -> List[Dict]:
        with self._lock:
            return [s.as_service_dict() for s in self._services.values()]

    def get_service(self, service_id: str) -> Optional[Dict]:
        with self._lock:
            svc = self._services.get(service_id)
            return svc.as_service_dict() if svc else None

    def get_service_metrics(self, service_id: str) -> Optional[Dict]:
        with self._lock:
            svc = self._services.get(service_id)
            return svc.as_metrics_dict() if svc else None

    def get_service_history(self, service_id: str, limit: int = 120) -> Dict[str, List]:
        with self._lock:
            hist = self._history.get(service_id, {})
            return {
                k: list(v)[-limit:]
                for k, v in hist.items()
            }

    def get_host_metrics(self) -> Dict:
        """Return current real host system metrics."""
        try:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            return {
                "cpu": round(cpu, 1),
                "memory": round(mem.percent, 1),
                "memory_used_gb": round(mem.used / 1e9, 2),
                "memory_total_gb": round(mem.total / 1e9, 2),
                "disk_percent": round(disk.percent, 1),
                "disk_used_gb": round(disk.used / 1e9, 1),
                "disk_total_gb": round(disk.total / 1e9, 1),
                "cpu_count": psutil.cpu_count(),
                "process_count": len(psutil.pids()),
            }
        except Exception as e:
            logger.error(f"Error reading host metrics: {e}")
            return {}

    def get_host_history(self, limit: int = 120) -> Dict[str, List]:
        with self._lock:
            return {k: list(v)[-limit:] for k, v in self._host_history.items()}

    def add_service(self, service_id: str, name: str,
                    base_cpu: float = 20, base_mem: float = 45) -> None:
        with self._lock:
            state = _ServiceState({
                "id": service_id, "name": name,
                "base_cpu": base_cpu, "base_mem": base_mem,
            })
            self._services[service_id] = state
            self._history[service_id] = {
                "cpu": deque(maxlen=self.MAX_HISTORY),
                "memory": deque(maxlen=self.MAX_HISTORY),
                "latency": deque(maxlen=self.MAX_HISTORY),
                "requests": deque(maxlen=self.MAX_HISTORY),
                "timestamps": deque(maxlen=self.MAX_HISTORY),
            }

    # ── Internal ───────────────────────────────────────────────────────────────

    def _collect_loop(self) -> None:
        # Warm up psutil counters
        psutil.cpu_percent(interval=None)
        psutil.disk_io_counters()
        psutil.net_io_counters()
        time.sleep(1)

        while self._running:
            try:
                self._tick()
            except Exception as e:
                logger.error(f"Collector tick error: {e}")
            time.sleep(1)

    def _tick(self) -> None:
        now_str = datetime.utcnow().isoformat()

        # --- Host metrics ---
        try:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent

            disk_io = psutil.disk_io_counters()
            net_io = psutil.net_io_counters()

            disk_read = disk_write = net_in = net_out = 0.0
            if self._prev_disk and disk_io:
                disk_read = max(0, disk_io.read_bytes - self._prev_disk.read_bytes) / 1e6
                disk_write = max(0, disk_io.write_bytes - self._prev_disk.write_bytes) / 1e6
            if self._prev_net and net_io:
                net_in = max(0, net_io.bytes_recv - self._prev_net.bytes_recv) / 1e6
                net_out = max(0, net_io.bytes_sent - self._prev_net.bytes_sent) / 1e6

            self._prev_disk = disk_io
            self._prev_net = net_io

            with self._lock:
                self._host_history["cpu"].append(round(cpu, 1))
                self._host_history["memory"].append(round(mem, 1))
                self._host_history["disk_read"].append(round(disk_read, 3))
                self._host_history["disk_write"].append(round(disk_write, 3))
                self._host_history["net_in"].append(round(net_in, 3))
                self._host_history["net_out"].append(round(net_out, 3))
                self._host_history["timestamps"].append(now_str)

        except Exception as e:
            logger.debug(f"Host metric error: {e}")

        # --- Service simulation ---
        with self._lock:
            for svc_id, state in self._services.items():
                state.tick()
                m = state.as_metrics_dict()
                hist = self._history[svc_id]
                hist["cpu"].append(m["cpu"])
                hist["memory"].append(m["memory"])
                hist["latency"].append(m["latency"])
                hist["requests"].append(m["requests"])
                hist["timestamps"].append(now_str)

                # Persist to storage every 10 ticks
                if self._storage and int(time.time()) % 10 == 0:
                    try:
                        self._storage.save_metrics(svc_id, m)
                    except Exception:
                        pass
