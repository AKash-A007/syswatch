# src/gui/service_panel.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QListWidgetItem, QPushButton, QGroupBox, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from .styles import get_status_color
import requests

from utils.logger import get_logger
from utils.config import AppConfig

logger = get_logger("service_panel")


class ServicePanel(QWidget):
    """Service monitoring and selection panel"""
    
    service_selected = Signal(str)  # Emits service_id when selected
    
    def __init__(self, config: AppConfig = None):
        super().__init__()
        self.config = config or AppConfig()
        self.current_services = {}
        # Keep refs to labels to avoid findChild
        self.lbl_healthy = None
        self.lbl_warning = None
        self.lbl_critical = None
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("Services")
        header.setProperty("heading", True)
        layout.addWidget(header)
        
        # Summary stats
        stats_widget = self.create_stats_widget()
        layout.addWidget(stats_widget)
        
        # Service list
        group = QGroupBox("Active Services")
        group_layout = QVBoxLayout()
        
        self.service_list = QListWidget()
        self.service_list.itemClicked.connect(self.on_service_clicked)
        group_layout.addWidget(self.service_list)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_services)
        
        self.add_btn = QPushButton("Add Service")
        self.add_btn.clicked.connect(self.add_service)
        
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.add_btn)
        
        group_layout.addLayout(btn_layout)
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        # Status summary
        self.status_summary = QLabel("Total: 0 services")
        self.status_summary.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_summary)
        
        # Initial load
        self.refresh_services()
    
    def create_stats_widget(self):
        """Create statistics widget"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        h_widget, self.lbl_healthy = self.create_stat_label("0", "Healthy", "healthy")
        w_widget, self.lbl_warning = self.create_stat_label("0", "Warning", "warning")
        c_widget, self.lbl_critical = self.create_stat_label("0", "Critical", "critical")
        
        layout.addWidget(h_widget)
        layout.addWidget(w_widget)
        layout.addWidget(c_widget)
        
        return widget
    
    def create_stat_label(self, value, name, status):
        """Create a status statistic label, returning (widget, label_ref)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setProperty("status", status)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18pt;
                font-weight: bold;
                background-color: {get_status_color(status)};
                color: #1e1e2e;
                border-radius: 8px;
                padding: 8px 12px;
            }}
        """)
        
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(name_label)
        
        return widget, value_label
    
    def refresh_services(self):
        """Refresh service list from backend"""
        try:
            url = f"{self.config.api_base_url}/api/services"
            response = requests.get(url, timeout=self.config.api_timeout)
            if response.status_code == 200:
                services = response.json().get("services", [])
                self.update_service_list(services)
            else:
                self.show_error(f"Failed to fetch services: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.show_error("Backend unavailable. Loading cached data if any.")
    
    def update_service_list(self, services):
        """Update the service list widget"""
        self.service_list.clear()
        self.current_services = {}
        
        healthy = warning = critical = 0
        
        for service in services:
            service_id = service.get("id", "unknown")
            name = service.get("name", service_id)
            status = service.get("status", "unknown").lower()
            cpu = service.get("cpu_usage", 0.0)
            memory = service.get("memory_usage", 0.0)
            
            if status == "healthy":
                healthy += 1
            elif status == "warning":
                warning += 1
            elif status == "critical":
                critical += 1
            
            item = QListWidgetItem(self.service_list)
            item_widget = self.create_service_item(name, status, cpu, memory)
            item.setSizeHint(item_widget.sizeHint())
            
            self.service_list.setItemWidget(item, item_widget)
            self.current_services[service_id] = service
        
        self.update_stats(healthy, warning, critical)
        self.status_summary.setText(f"Total: {len(services)} services")
    
    def create_service_item(self, name, status, cpu, memory):
        """Create a custom widget for service list item"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        top_layout = QHBoxLayout()
        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        
        status_badge = QLabel(status.upper())
        status_badge.setProperty("status", status)
        status_badge.setFixedSize(70, 20)
        status_badge.setAlignment(Qt.AlignCenter)
        
        top_layout.addWidget(name_label)
        top_layout.addStretch()
        top_layout.addWidget(status_badge)
        
        metrics_label = QLabel(f"CPU: {cpu:.1f}% | Memory: {memory:.1f}%")
        metrics_label.setStyleSheet("font-size: 9pt; color: #a6adc8;")
        
        layout.addLayout(top_layout)
        layout.addWidget(metrics_label)
        
        return widget
    
    def update_stats(self, healthy, warning, critical):
        """Update statistics display"""
        if self.lbl_healthy:
            self.lbl_healthy.setText(str(healthy))
        if self.lbl_warning:
            self.lbl_warning.setText(str(warning))
        if self.lbl_critical:
            self.lbl_critical.setText(str(critical))
    
    def on_service_clicked(self, item):
        """Handle service selection"""
        index = self.service_list.row(item)
        if index < len(self.current_services):
            service_id = list(self.current_services.keys())[index]
            self.service_selected.emit(service_id)
    
    def add_service(self):
        """Add new service to monitor"""
        text, ok = QInputDialog.getText(self, "Add Service", "Enter service name:")
        if ok and text:
            svc_id = text.lower().replace(" ", "-")
            url = f"{self.config.api_base_url}/api/agents/register"
            try:
                payload = {"id": svc_id, "name": text, "status": "unknown"}
                res = requests.post(url, json=payload, timeout=self.config.api_timeout)
                if res.status_code == 200:
                    self.refresh_services()
                else:
                    self.show_error("Failed to register service.")
            except Exception as e:
                self.show_error(str(e))
    
    def show_error(self, message):
        """Show error message"""
        logger.error(f"ServicePanel: {message}")