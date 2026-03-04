import pytest
import os
import psutil
from unittest.mock import patch, MagicMock
from backend.collector import MetricsCollector, _status_from_usage
from backend.storage import Storage

@pytest.fixture
def storage():
    # Use in-memory SQLite for testing
    idx = Storage(":memory:")
    yield idx
    idx.close()

@pytest.fixture
def collector(storage):
    col = MetricsCollector(storage=storage)
    yield col
    col.stop()

def test_status_from_usage():
    assert _status_from_usage(10, 20) == "healthy"
    assert _status_from_usage(80, 50) == "warning"
    assert _status_from_usage(50, 85) == "warning"
    assert _status_from_usage(95, 90) == "critical"

def test_collector_initialization(collector):
    assert not collector._running
    assert "api-gateway" in collector._services

def test_add_service(collector):
    collector.add_service("test-svc", "Test Service", base_cpu=15, base_mem=30)
    assert "test-svc" in collector._services
    svc = collector._services["test-svc"]
    assert svc.name == "Test Service"
    assert svc.base_cpu == 15

@patch('psutil.cpu_percent')
@patch('psutil.virtual_memory')
@patch('psutil.disk_io_counters')
@patch('psutil.net_io_counters')
def test_collect_host_metrics(mock_net, mock_disk, mock_mem, mock_cpu, collector):
    mock_cpu.return_value = 42.0
    
    mem_mock = MagicMock()
    mem_mock.percent = 60.0
    mock_mem.return_value = mem_mock
    
    disk_mock = MagicMock()
    disk_mock.read_bytes = 1000
    disk_mock.write_bytes = 2000
    mock_disk.return_value = disk_mock
    
    net_mock = MagicMock()
    net_mock.bytes_sent = 500
    net_mock.bytes_recv = 1500
    mock_net.return_value = net_mock
    
    metrics = collector.get_host_metrics()
    
    assert 'cpu' in metrics
    assert metrics['cpu'] == 42.0
    assert metrics['memory'] == 60.0
    assert 'disk_read_bytes_sec' in metrics
    assert 'net_recv_bytes_sec' in metrics

def test_service_metrics_tick(collector):
    # Tick updates the in-memory history
    collector._tick()
    
    hist = collector.get_service_history("api-gateway", limit=5)
    assert len(hist['cpu']) == 1
    assert len(hist['memory']) == 1
    assert len(hist['timestamps']) == 1
    
    metrics = collector.get_service_metrics("api-gateway")
    assert metrics is not None
    assert 'cpu' in metrics
    assert 'status' in metrics

def test_start_stop(collector):
    collector.start()
    assert collector._running
    collector.stop()
    assert not collector._running
