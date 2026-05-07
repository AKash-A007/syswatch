# src/backend/api_server.py

import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

import sentry_sdk
import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

# Allow running as module and resolving imports correctly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.analyzer import AnomalyDetector, RootCauseEngine
from backend.collector import MetricsCollector, _status_from_usage
from backend.storage import Storage
from utils.logger import get_logger

logger = get_logger("api")

# ─── Sentry Initialisation ────────────────────────────────────────────────────
# DSN is read from the SENTRY_DSN environment variable.
# Set it in Render → Environment, or locally via .env.
_sentry_dsn = os.getenv("SENTRY_DSN", "")
if _sentry_dsn:
    sentry_sdk.init(
        dsn=_sentry_dsn,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
        ],
        # Capture 10% of transactions to stay within free-tier limits
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
        environment=os.getenv("PYTHON_ENV", "development"),
        release=os.getenv("APP_VERSION", "1.0.0"),
        send_default_pii=False,  # GDPR-safe default
    )


# ─── Lifespan (replaces deprecated on_event) ──────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic using modern lifespan context manager."""
    global storage, collector, detector, rca_engine
    storage = Storage()
    collector = MetricsCollector(storage=storage)
    detector = AnomalyDetector()
    rca_engine = RootCauseEngine()
    collector.start()
    logger.info("API Server started and components initialized.")
    yield
    # Shutdown
    if collector:
        collector.stop()
    if storage:
        storage.close()
    logger.info("API Server shutdown.")


app = FastAPI(title="SysWatch APIs", version="1.0.0", lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── API Routes ────────────────────────────────────────────────────────────────

# ─── Data models ───────────────────────────────────────────────────────────────


class ServiceModel(BaseModel):
    id: str
    name: str
    status: str
    cpu_usage: float
    memory_usage: float
    uptime_seconds: int


class AgentRegisterModel(BaseModel):
    id: str
    name: str
    status: str = "healthy"
    metadata: dict = {}


class AgentMetricsModel(BaseModel):
    cpu: float
    memory: float
    latency: float
    requests: float


class IncidentModel(BaseModel):
    service: str
    severity: str
    type: str
    description: str
    status: str = "active"
    details: dict = {}


class AnalysisRequest(BaseModel):
    id: int
    service: str
    type: str
    severity: str
    details: dict


# ─── Globals ───────────────────────────────────────────────────────────────────

storage: Storage = None
collector: MetricsCollector = None
detector: AnomalyDetector = None
rca_engine: RootCauseEngine = None

# ─── API Routes ────────────────────────────────────────────────────────────────


@app.get("/")
async def root():
    return {"message": "SysWatch API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Root-level health check — used by Render, Docker HEALTHCHECK, and UptimeRobot."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/health")
async def health_check():
    """Legacy health endpoint — kept for backwards compatibility."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ─── System & Host Metrics ───


@app.get("/api/system")
async def get_system_metrics():
    """Get metrics about the machine running the main SysWatch process."""
    if not collector:
        raise HTTPException(503, "Collector not initialized")
    return collector.get_host_metrics()


# ─── Services ───


@app.get("/api/services")
async def get_services():
    """Get all connected services (including mock/demo services)."""
    # Force sync demo services into DB right before returning
    db_services = storage.get_services()
    db_svc_keys = {s["id"] for s in db_services}

    mem_services = collector.get_services()
    for mem_svc in mem_services:
        if mem_svc["id"] not in db_svc_keys:
            storage.upsert_service(
                {
                    "id": mem_svc["id"],
                    "name": mem_svc["name"],
                    "status": mem_svc["status"],
                    "cpu_usage": mem_svc.get("cpu_usage", 0.0),
                    "memory_usage": mem_svc.get("memory_usage", 0.0),
                    "uptime_seconds": mem_svc.get("uptime_seconds", 0),
                }
            )

    # Return directly from storage so it is consistent
    return {"services": storage.get_services()}


@app.get("/api/services/{service_id}")
async def get_service(service_id: str):
    """Get specific service."""
    for s in storage.get_services():
        if s["id"] == service_id:
            return s
    raise HTTPException(status_code=404, detail="Service not found")


@app.get("/api/metrics/{service_id}")
async def get_metrics(service_id: str, background_tasks: BackgroundTasks):
    """Get real-time metrics for service and perform fast anomaly detection."""
    # This acts as the tick for anomaly detection for the web UI as well
    metrics = collector.get_service_metrics(service_id)
    if not metrics:
        # Fallback to checking storage recent
        hist = storage.get_metrics_history(service_id, limit=1)
        if hist:
            metrics = {
                "cpu": hist[0]["cpu"],
                "memory": hist[0]["memory"],
                "latency": hist[0]["latency"],
                "requests": hist[0]["requests"],
            }
        else:
            raise HTTPException(status_code=404, detail="No metrics found")

    # Run detector in background
    background_tasks.add_task(process_metrics_anomalies, service_id, metrics)
    return metrics


def process_metrics_anomalies(service_id: str, metrics: dict[str, float]):
    """Background task to run detector and save incidents if anomalies found."""
    alerts = detector.feed(service_id, metrics)
    for alert in alerts:
        incident = {
            "timestamp": alert["timestamp"],
            "service": alert["service"],
            "severity": alert["severity"],
            "type": alert["type"],
            "description": alert["description"],
            "status": "active",
            "details": {
                "metric": alert["metric"],
                "value": alert["value"],
                "threshold": alert["threshold"],
                "zscore": alert["zscore"],
            },
        }
        storage.save_incident(incident)


@app.get("/api/metrics/{service_id}/history")
async def get_metrics_history(service_id: str, limit: int = 120):
    """Fetch time series data directly from memory collector, or fallback to DB."""
    hist = collector.get_service_history(service_id, limit=limit)
    if hist and len(hist.get("cpu", [])) > 0:
        return hist
    # DB fallback
    db_hist = storage.get_metrics_history(service_id, limit=limit)
    return {
        "timestamps": [r["timestamp"] for r in db_hist],
        "cpu": [r["cpu"] for r in db_hist],
        "memory": [r["memory"] for r in db_hist],
        "latency": [r["latency"] for r in db_hist],
        "requests": [r["requests"] for r in db_hist],
    }


# ─── Incidents ───


@app.get("/api/incidents")
async def get_incidents():
    """Get all incidents"""
    return {"incidents": storage.get_incidents()}


@app.post("/api/incidents")
async def create_incident(incident: IncidentModel):
    """Create new incident"""
    data = incident.dict()
    new_id = storage.save_incident(data)
    data["id"] = new_id
    data["timestamp"] = datetime.utcnow().isoformat()
    return data


@app.delete("/api/incidents")
async def clear_incidents():
    """Clear all incidents"""
    storage.clear_incidents()
    return {"status": "cleared"}


@app.post("/api/analyze")
async def analyze_incident(request: AnalysisRequest):
    """Run root-cause analysis on an incident."""
    incident_dict = request.dict()
    return rca_engine.analyze(incident_dict)


@app.post("/api/stress-test")
async def run_stress_test():
    """Trigger stress test directly in memory for demo service."""
    svc = collector._services.get("api-gateway")
    if svc:
        svc.base_cpu = min(99, svc.base_cpu + 60)
        svc.base_mem = min(99, svc.base_mem + 40)
        return {"status": "started", "message": "Stress test initiated on api-gateway"}
    return {"status": "failed", "message": "Target service not found"}


@app.post("/api/simulate-incident")
async def simulate_incident():
    """Simulate an incident."""
    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": "api-gateway",
        "severity": "critical",
        "type": "High Error Rate",
        "description": "User simulated incident. Rate at 50%.",
        "status": "active",
        "details": {"error_rate": 50.0},
    }
    nid = storage.save_incident(data)
    data["id"] = nid
    return data


# ─── External Agent Registration ───


@app.post("/api/agents/register")
async def register_agent(agent: AgentRegisterModel):
    """Register an external agent."""
    collector.add_service(agent.id, agent.name, base_cpu=5, base_mem=10)
    data = agent.dict()
    data["cpu_usage"] = 0.0
    data["memory_usage"] = 0.0
    data["uptime_seconds"] = 0
    storage.upsert_service(data)
    return {"status": "registered", "id": agent.id}


@app.post("/api/agents/metrics/{service_id}")
async def post_agent_metrics(service_id: str, metrics: AgentMetricsModel):
    """Receive metrics from an external agent."""
    m_dict = metrics.dict()
    # Let detector look for anomalies
    process_metrics_anomalies(service_id, m_dict)
    # Save to storage
    storage.save_metrics(service_id, m_dict)
    # Update services table status
    status = _status_from_usage(metrics.cpu, metrics.memory)
    storage.upsert_service(
        {
            "id": service_id,
            "name": service_id,
            "status": status,
            "cpu_usage": metrics.cpu,
            "memory_usage": metrics.memory,
            "uptime_seconds": 0,
        }
    )
    return {"status": "received"}


def start_server(host="0.0.0.0", port=8000):
    """Start the API server"""
    uvicorn.run("backend.api_server:app", host=host, port=port, log_level="warning")


if __name__ == "__main__":
    start_server()
