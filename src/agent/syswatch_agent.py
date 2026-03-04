# src/agent/syswatch_agent.py
"""Standalone SysWatch agent for tracking process/host metrics and reporting to API."""

import sys
import time
import json
import threading
import argparse
import socket
from datetime import datetime
from typing import Dict, Optional

try:
    import psutil
    import requests
except ImportError:
    print("Error: psutil and requests packages are required.")
    print("Install with: pip install psutil requests")
    sys.exit(1)


class SysWatchAgent:
    """Agent that collects metrics and posts them to SysWatch Server."""

    def __init__(
        self,
        service_id: str,
        service_name: Optional[str] = None,
        api_url: str = "http://localhost:8000",
        interval: int = 5,
    ):
        self.service_id = service_id
        self.service_name = service_name or service_id
        self.api_url = api_url.rstrip("/")
        self.interval = interval
        self.running = False
        self._thread: Optional[threading.Thread] = None

        # Resolve IPs
        self.hostname = socket.gethostname()
        try:
            self.ip = socket.gethostbyname(self.hostname)
        except Exception:
            self.ip = "127.0.0.1"

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        
        # Register service first
        self._register_service()

        self._thread = threading.Thread(
            target=self._run_loop, name=f"SysWatchAgent-{self.service_id}", daemon=True
        )
        self._thread.start()
        print(f"[{datetime.now().isoformat()}] Agent started for {self.service_id}")
        print(f"Reporting to {self.api_url} every {self.interval}s")

    def stop(self) -> None:
        self.running = False
        if self._thread:
            self._thread.join(timeout=3)
        print(f"[{datetime.now().isoformat()}] Agent stopped.")

    def _register_service(self) -> None:
        """Register the service with the main SysWatch backend."""
        payload = {
            "id": self.service_id,
            "name": self.service_name,
            "status": "healthy",
            "metadata": {
                "hostname": self.hostname,
                "ip": self.ip,
                "agent_version": "1.0",
                "os": sys.platform,
            }
        }
        try:
            requests.post(f"{self.api_url}/api/agents/register", json=payload, timeout=5)
        except Exception as e:
            print(f"Warning: Failed to register service: {e}")

    def _collect_metrics(self) -> Dict[str, float]:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        
        # We don't have real app latency here, so we fake something proportional to CPU
        latency = 10.0 + (cpu * 2)
        # Requests proportional to remaining health
        requests_ps = max(5.0, 100.0 - cpu)

        return {
            "cpu": float(cpu),
            "memory": float(mem),
            "latency": float(latency),
            "requests": float(requests_ps)
        }

    def _run_loop(self) -> None:
        psutil.cpu_percent(interval=None)  # discard first measurement
        while self.running:
            metrics = self._collect_metrics()
            try:
                # Post direct to the metrics ingestion endpoint
                endpoint = f"{self.api_url}/api/agents/metrics/{self.service_id}"
                resp = requests.post(endpoint, json=metrics, timeout=5)
                if resp.status_code not in (200, 201, 202):
                    print(f"Agent warning: API returned {resp.status_code}")
            except Exception as e:
                print(f"Agent send error: {e}")
            
            time.sleep(self.interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SysWatch Agent")
    parser.add_argument("--id", "-i", required=True, help="Unique service ID")
    parser.add_argument("--name", "-n", help="Display name of the service")
    parser.add_argument("--url", "-u", default="http://localhost:8000", help="SysWatch API URL")
    parser.add_argument("--interval", "-t", type=int, default=5, help="Collection interval (seconds)")
    
    args = parser.parse_args()
    
    agent = SysWatchAgent(
        service_id=args.id,
        service_name=args.name,
        api_url=args.url,
        interval=args.interval
    )
    
    try:
        agent.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        agent.stop()
