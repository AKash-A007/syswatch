import pytest
from datetime import datetime
from backend.analyzer import AnomalyDetector, RootCauseEngine

def test_anomaly_detector_no_alerts_initially():
    detector = AnomalyDetector(cpu_threshold=80.0, mem_threshold=85.0, severity_zscore=2.0)
    metrics = {"cpu": 20.0, "memory": 40.0, "latency": 100.0, "requests": 500.0}
    
    # First few data points shouldn't trigger Z-score anomalies
    alerts = []
    for _ in range(5):
        alerts = detector.feed("test-svc", metrics)
        assert len(alerts) == 0

def test_anomaly_detector_static_threshold():
    detector = AnomalyDetector(cpu_threshold=80.0, mem_threshold=85.0)
    
    # Warm up with low values
    for _ in range(5):
        detector.feed("test-svc", {"cpu": 20.0, "memory": 40.0, "latency": 100.0, "requests": 500.0})
        
    # Spike CPU above threshold
    alerts = detector.feed("test-svc", {"cpu": 95.0, "memory": 40.0, "latency": 100.0, "requests": 500.0})
    
    assert len(alerts) > 0
    assert alerts[0]["metric"] == "cpu"
    assert alerts[0]["type"] == "Static Threshold Exceeded"
    assert alerts[0]["severity"] == "critical"

def test_anomaly_detector_zscore_spike():
    detector = AnomalyDetector(cpu_threshold=90.0) # High threshold to avoid static trigger
    
    # Stable baseling
    for _ in range(20):
        detector.feed("z-svc", {"cpu": 10.0, "memory": 40.0, "latency": 50.0, "requests": 100.0})
        
    # Sudden unusual spike that doesn't breach the static 90 threshold
    alerts = detector.feed("z-svc", {"cpu": 70.0, "memory": 40.0, "latency": 50.0, "requests": 100.0})
    
    assert len(alerts) > 0
    assert alerts[0]["type"] == "Statistical Anomaly (Z-Score)"
    assert alerts[0]["metric"] == "cpu"

def test_root_cause_engine():
    engine = RootCauseEngine()
    
    incident = {
        "service": "api-gateway",
        "type": "High Error Rate",
        "description": "Rate at 50%",
        "details": {"error_rate": 50.0},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    analysis = engine.analyze(incident)
    
    assert "root_cause" in analysis
    assert "confidence" in analysis
    assert "explanation" in analysis
    assert "recommendations" in analysis
    assert len(analysis["recommendations"]) > 0
    assert analysis["confidence"] > 0
