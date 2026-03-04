# src/gui/settings_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLineEdit, QSpinBox, QCheckBox, QPushButton,
    QGroupBox, QTabWidget, QWidget, QFormLayout, QMessageBox
)
from utils.config import AppConfig
import requests


class SettingsDialog(QDialog):
    """Application settings dialog"""
    
    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 500)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        tabs.addTab(self.create_connection_tab(), "Connection")
        tabs.addTab(self.create_monitoring_tab(), "Monitoring")
        tabs.addTab(self.create_ui_tab(), "Interface")
        tabs.addTab(self.create_notifications_tab(), "Notifications")
        
        layout.addWidget(tabs)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setProperty("success", True)
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def create_connection_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        group = QGroupBox("Backend Connection")
        form = QFormLayout()
        
        self.api_host = QLineEdit()
        form.addRow("API Host:", self.api_host)
        
        self.api_port = QSpinBox()
        self.api_port.setRange(1, 65535)
        form.addRow("API Port:", self.api_port)
        
        self.api_timeout = QSpinBox()
        self.api_timeout.setRange(1, 60)
        self.api_timeout.setSuffix(" seconds")
        form.addRow("Request Timeout:", self.api_timeout)
        
        self.use_https = QCheckBox("Use HTTPS")
        form.addRow("", self.use_https)
        
        group.setLayout(form)
        layout.addWidget(group)
        
        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self.test_connection)
        layout.addWidget(test_btn)
        
        layout.addStretch()
        return widget
    
    def create_monitoring_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        refresh_group = QGroupBox("Refresh Rates")
        refresh_form = QFormLayout()
        
        self.service_refresh = QSpinBox()
        self.service_refresh.setRange(1, 300)
        self.service_refresh.setSuffix(" seconds")
        refresh_form.addRow("Services:", self.service_refresh)
        
        self.metrics_refresh = QSpinBox()
        self.metrics_refresh.setRange(1, 60)
        self.metrics_refresh.setSuffix(" seconds")
        refresh_form.addRow("Metrics:", self.metrics_refresh)
        
        self.incidents_refresh = QSpinBox()
        self.incidents_refresh.setRange(1, 300)
        self.incidents_refresh.setSuffix(" seconds")
        refresh_form.addRow("Incidents:", self.incidents_refresh)
        
        refresh_group.setLayout(refresh_form)
        layout.addWidget(refresh_group)
        
        threshold_group = QGroupBox("Alert Thresholds")
        threshold_form = QFormLayout()
        
        self.cpu_threshold = QSpinBox()
        self.cpu_threshold.setRange(1, 100)
        self.cpu_threshold.setSuffix(" %")
        threshold_form.addRow("CPU Warning:", self.cpu_threshold)
        
        self.memory_threshold = QSpinBox()
        self.memory_threshold.setRange(1, 100)
        self.memory_threshold.setSuffix(" %")
        threshold_form.addRow("Memory Warning:", self.memory_threshold)
        
        self.latency_threshold = QSpinBox()
        self.latency_threshold.setRange(1, 10000)
        self.latency_threshold.setSuffix(" ms")
        threshold_form.addRow("Latency Warning:", self.latency_threshold)
        
        threshold_group.setLayout(threshold_form)
        layout.addWidget(threshold_group)
        
        layout.addStretch()
        return widget
    
    def create_ui_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        group = QGroupBox("Interface Preferences")
        form = QFormLayout()
        
        self.start_minimized = QCheckBox("Start minimized to tray")
        form.addRow("", self.start_minimized)
        
        self.minimize_to_tray = QCheckBox("Minimize to tray on close")
        form.addRow("", self.minimize_to_tray)
        
        self.show_splash = QCheckBox("Show splash screen on startup")
        form.addRow("", self.show_splash)
        
        self.confirm_exit = QCheckBox("Confirm before exit")
        form.addRow("", self.confirm_exit)
        
        group.setLayout(form)
        layout.addWidget(group)
        layout.addStretch()
        return widget
    
    def create_notifications_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        group = QGroupBox("Notification Preferences")
        form = QFormLayout()
        
        self.enable_notifications = QCheckBox("Enable system notifications")
        form.addRow("", self.enable_notifications)
        
        self.notify_critical = QCheckBox("Notify on critical incidents")
        form.addRow("", self.notify_critical)
        
        self.notify_high = QCheckBox("Notify on high severity incidents")
        form.addRow("", self.notify_high)
        
        self.notify_anomaly = QCheckBox("Notify on metric anomalies")
        form.addRow("", self.notify_anomaly)
        
        self.sound_alerts = QCheckBox("Play sound alerts")
        form.addRow("", self.sound_alerts)
        
        group.setLayout(form)
        layout.addWidget(group)
        layout.addStretch()
        return widget
    
    def load_settings(self):
        c = self.config
        self.api_host.setText(c.get("api_host"))
        self.api_port.setValue(c.get("api_port"))
        self.api_timeout.setValue(c.get("api_timeout"))
        self.use_https.setChecked(c.get("use_https"))
        
        self.service_refresh.setValue(c.get("service_refresh_interval"))
        self.metrics_refresh.setValue(c.get("metrics_refresh_interval"))
        self.incidents_refresh.setValue(c.get("incidents_refresh_interval"))
        
        self.cpu_threshold.setValue(c.get("cpu_threshold"))
        self.memory_threshold.setValue(c.get("memory_threshold"))
        self.latency_threshold.setValue(c.get("latency_threshold_ms"))
        
        self.start_minimized.setChecked(c.get("start_minimized"))
        self.minimize_to_tray.setChecked(c.get("minimize_to_tray"))
        self.show_splash.setChecked(c.get("show_splash"))
        self.confirm_exit.setChecked(c.get("confirm_exit"))
        
        self.enable_notifications.setChecked(c.get("enable_notifications"))
        self.notify_critical.setChecked(c.get("notify_critical"))
        self.notify_high.setChecked(c.get("notify_high"))
        self.notify_anomaly.setChecked(c.get("notify_anomaly"))
        self.sound_alerts.setChecked(c.get("sound_alerts"))
    
    def save_settings(self):
        c = self.config
        c.set("api_host", self.api_host.text())
        c.set("api_port", self.api_port.value())
        c.set("api_timeout", self.api_timeout.value())
        c.set("use_https", self.use_https.isChecked())
        
        c.set("service_refresh_interval", self.service_refresh.value())
        c.set("metrics_refresh_interval", self.metrics_refresh.value())
        c.set("incidents_refresh_interval", self.incidents_refresh.value())
        
        c.set("cpu_threshold", self.cpu_threshold.value())
        c.set("memory_threshold", self.memory_threshold.value())
        c.set("latency_threshold_ms", self.latency_threshold.value())
        
        c.set("start_minimized", self.start_minimized.isChecked())
        c.set("minimize_to_tray", self.minimize_to_tray.isChecked())
        c.set("show_splash", self.show_splash.isChecked())
        c.set("confirm_exit", self.confirm_exit.isChecked())
        
        c.set("enable_notifications", self.enable_notifications.isChecked())
        c.set("notify_critical", self.notify_critical.isChecked())
        c.set("notify_high", self.notify_high.isChecked())
        c.set("notify_anomaly", self.notify_anomaly.isChecked())
        c.set("sound_alerts", self.sound_alerts.isChecked())
        
        c.save()
        self.accept()
    
    def reset_to_defaults(self):
        self.config.reset()
        self.load_settings()
    
    def test_connection(self):
        protocol = "https" if self.use_https.isChecked() else "http"
        url = f"{protocol}://{self.api_host.text()}:{self.api_port.value()}/api/health"
        try:
            response = requests.get(url, timeout=self.api_timeout.value())
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Connection successful!")
            else:
                QMessageBox.warning(self, "Failed", f"Connection failed: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")