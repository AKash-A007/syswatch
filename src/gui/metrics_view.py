# src/gui/metrics_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QGroupBox, QTabWidget
)
from PySide6.QtCore import Qt, QTimer, Signal
import pyqtgraph as pg
import requests
from collections import deque
from datetime import datetime

from utils.logger import get_logger
from utils.config import AppConfig

logger = get_logger("metrics_view")


class MetricsView(QWidget):
    """Real-time metrics visualization with multiple graphs and System Overview."""
    
    anomaly_detected = Signal(dict)
    
    def __init__(self, config: AppConfig = None):
        super().__init__()
        self.config = config or AppConfig()
        self.current_service = None
        
        self.data_history = {
            'cpu': deque(maxlen=100),
            'memory': deque(maxlen=100),
            'latency': deque(maxlen=100),
            'requests': deque(maxlen=100),
            'timestamps': deque(maxlen=100)
        }
        
        # Additional state for host metrics if "System Overview" is selected
        # If current_service == "_system_", we poll /api/system instead
        
        self.setup_ui()
        self.setup_graphs()
        self.start_update_timer()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        header = self.create_header()
        layout.addWidget(header)
        
        self.tab_widget = QTabWidget()
        
        cpu_mem_widget = self.create_cpu_memory_tab()
        self.tab_widget.addTab(cpu_mem_widget, "CPU & Memory")
        
        latency_widget = self.create_latency_tab()
        self.tab_widget.addTab(latency_widget, "Latency & Network")
        
        combined_widget = self.create_combined_tab()
        self.tab_widget.addTab(combined_widget, "Combined Metrics")
        
        layout.addWidget(self.tab_widget)
    
    def create_header(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        title = QLabel("Real-Time Metrics")
        title.setProperty("heading", True)
        
        window_label = QLabel("Time Window:")
        self.window_combo = QComboBox()
        self.window_combo.addItems(["1 min", "5 min", "15 min", "1 hour"])
        self.window_combo.setCurrentText("5 min")
        self.window_combo.currentTextChanged.connect(self.on_time_window_changed)
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setCheckable(True)
        self.pause_btn.toggled.connect(self.on_pause_toggled)
        
        sys_btn = QPushButton("System Overview")
        sys_btn.clicked.connect(self.show_system_overview)
        
        reset_btn = QPushButton("Reset Graphs")
        reset_btn.clicked.connect(self.reset_graphs)
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(sys_btn)
        layout.addWidget(window_label)
        layout.addWidget(self.window_combo)
        layout.addWidget(self.pause_btn)
        layout.addWidget(reset_btn)
        
        return widget
    
    def create_cpu_memory_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        cpu_group = QGroupBox("CPU Usage (%)")
        cpu_layout = QVBoxLayout()
        self.cpu_plot = pg.PlotWidget()
        self.cpu_plot.setBackground('#181825')
        self.cpu_plot.setYRange(0, 100)
        self.cpu_plot.showGrid(x=True, y=True, alpha=0.3)
        self.cpu_plot.setLabel('left', 'CPU %')
        cpu_layout.addWidget(self.cpu_plot)
        cpu_group.setLayout(cpu_layout)
        
        mem_group = QGroupBox("Memory Usage (%)")
        mem_layout = QVBoxLayout()
        self.mem_plot = pg.PlotWidget()
        self.mem_plot.setBackground('#181825')
        self.mem_plot.setYRange(0, 100)
        self.mem_plot.showGrid(x=True, y=True, alpha=0.3)
        self.mem_plot.setLabel('left', 'Memory %')
        mem_layout.addWidget(self.mem_plot)
        mem_group.setLayout(mem_layout)
        
        layout.addWidget(cpu_group)
        layout.addWidget(mem_group)
        
        return widget
    
    def create_latency_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        latency_group = QGroupBox("Latency (ms) / Disk I/O")
        latency_layout = QVBoxLayout()
        self.latency_plot = pg.PlotWidget()
        self.latency_plot.setBackground('#181825')
        self.latency_plot.showGrid(x=True, y=True, alpha=0.3)
        self.latency_plot.setLabel('left', 'ms')
        latency_layout.addWidget(self.latency_plot)
        latency_group.setLayout(latency_layout)
        
        req_group = QGroupBox("Requests/s / Network I/O")
        req_layout = QVBoxLayout()
        self.req_plot = pg.PlotWidget()
        self.req_plot.setBackground('#181825')
        self.req_plot.showGrid(x=True, y=True, alpha=0.3)
        self.req_plot.setLabel('left', 'Count')
        req_layout.addWidget(self.req_plot)
        req_group.setLayout(req_layout)
        
        layout.addWidget(latency_group)
        layout.addWidget(req_group)
        
        return widget
    
    def create_combined_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = QGroupBox("Combined Overview")
        group_layout = QVBoxLayout()
        
        self.combined_plot = pg.PlotWidget()
        self.combined_plot.setBackground('#181825')
        self.combined_plot.showGrid(x=True, y=True, alpha=0.3)
        self.combined_plot.setLabel('left', 'Normalized Scale')
        self.combined_plot.addLegend()
        
        group_layout.addWidget(self.combined_plot)
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        return widget
    
    def setup_graphs(self):
        self.cpu_curve = self.cpu_plot.plot(pen=pg.mkPen(color='#89b4fa', width=2), name='CPU')
        self.mem_curve = self.mem_plot.plot(pen=pg.mkPen(color='#a6e3a1', width=2), name='Memory')
        self.latency_curve = self.latency_plot.plot(pen=pg.mkPen(color='#f9e2af', width=2), name='Latency/Disk')
        self.req_curve = self.req_plot.plot(pen=pg.mkPen(color='#cba6f7', width=2), name='Requests/Net')
        
        self.combined_cpu = self.combined_plot.plot(pen=pg.mkPen(color='#89b4fa', width=2), name='CPU')
        self.combined_mem = self.combined_plot.plot(pen=pg.mkPen(color='#a6e3a1', width=2), name='Memory')
        self.combined_latency = self.combined_plot.plot(pen=pg.mkPen(color='#f9e2af', width=2), name='Latency (n)')
        self.combined_req = self.combined_plot.plot(pen=pg.mkPen(color='#cba6f7', width=2), name='Requests (n)')
    
    def start_update_timer(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_graphs)
        self.update_timer.start(int(self.config.get("metrics_refresh_interval", 1) * 1000))
        self.paused = False
    
    def update_graphs(self):
        if self.paused:
            return
        
        if not self.current_service:
            return
            
        data = self.fetch_metrics_data()
        if not data:
            return
        
        self.data_history['cpu'].append(data.get('cpu', 0.0))
        self.data_history['memory'].append(data.get('memory', 0.0))
        self.data_history['latency'].append(data.get('latency', data.get('disk_percent', 0.0)))
        self.data_history['requests'].append(data.get('requests', data.get('process_count', 0.0) / 10))
        self.data_history['timestamps'].append(datetime.utcnow())
        
        self.check_anomalies(data)
        
        c = list(self.data_history['cpu'])
        m = list(self.data_history['memory'])
        l = list(self.data_history['latency'])
        r = list(self.data_history['requests'])
        
        if c:
            self.cpu_curve.setData(c)
            self.mem_curve.setData(m)
            self.latency_curve.setData(l)
            self.req_curve.setData(r)
            
            # normalize for combined
            lnorm = [min(x/5.0, 100) for x in l]
            rnorm = [min(x, 100) for x in r]
            self.combined_cpu.setData(c)
            self.combined_mem.setData(m)
            self.combined_latency.setData(lnorm)
            self.combined_req.setData(rnorm)
    
    def fetch_metrics_data(self):
        url = f"{self.config.api_base_url}/api/system" if self.current_service == "_system_" else f"{self.config.api_base_url}/api/metrics/{self.current_service}"
        try:
            r = requests.get(url, timeout=self.config.api_timeout)
            if r.status_code == 200:
                return r.json()
        except requests.exceptions.RequestException:
            pass
        return None
    
    def check_anomalies(self, data):
        c, m = data.get('cpu', 0), data.get('memory', 0)
        if c > self.config.cpu_threshold or m > self.config.memory_threshold:
            self.anomaly_detected.emit({
                'service': self.current_service or 'Unknown',
                'type': 'high_resource_usage',
                'cpu': c,
                'memory': m
            })
    
    def load_service_metrics(self, service_id):
        self.current_service = service_id
        self.reset_graphs()
        
    def show_system_overview(self):
        self.current_service = "_system_"
        self.reset_graphs()
    
    def reset_graphs(self):
        for key in self.data_history:
            self.data_history[key].clear()
        
        self.cpu_curve.setData([])
        self.mem_curve.setData([])
        self.latency_curve.setData([])
        self.req_curve.setData([])
        self.combined_cpu.setData([])
        self.combined_mem.setData([])
        self.combined_latency.setData([])
        self.combined_req.setData([])

    def on_time_window_changed(self, window):
        window_sizes = {"1 min": 60, "5 min": 300, "15 min": 900, "1 hour": 3600}
        new_size = window_sizes.get(window, 300)
        for key in self.data_history:
            self.data_history[key] = deque(self.data_history[key], maxlen=new_size)
    
    def on_pause_toggled(self, checked):
        self.paused = checked
        self.pause_btn.setText("Resume" if checked else "Pause")