# src/gui/incident_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QLabel, QHeaderView, QGroupBox,
    QPushButton, QComboBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from .styles import get_severity_color
import requests
import csv
from datetime import datetime

from utils.logger import get_logger
from utils.config import AppConfig

logger = get_logger("incident_view")


class IncidentView(QWidget):
    """Incident timeline and management view"""
    
    incident_selected = Signal(dict)
    
    def __init__(self, config: AppConfig = None):
        super().__init__()
        self.config = config or AppConfig()
        self.incidents = []
        self.setup_ui()
        self.load_initial_incidents()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        header = self.create_header()
        layout.addWidget(header)
        
        group = QGroupBox("Incident Timeline")
        group_layout = QVBoxLayout()
        
        self.incident_table = QTableWidget()
        self.setup_table()
        group_layout.addWidget(self.incident_table)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        self.footer_label = QLabel("0 incidents in last 24 hours")
        self.footer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.footer_label)
    
    def create_header(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        title = QLabel("Incidents")
        title.setProperty("heading", True)
        
        filter_label = QLabel("Filter:")
        self.severity_filter = QComboBox()
        self.severity_filter.addItems(["All", "Critical", "High", "Medium", "Low"])
        self.severity_filter.currentTextChanged.connect(self.apply_filter)
        
        export_btn = QPushButton("Export CSV")
        export_btn.clicked.connect(self.export_csv)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.setProperty("danger", True)
        clear_btn.clicked.connect(self.clear_incidents)
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(filter_label)
        layout.addWidget(self.severity_filter)
        layout.addWidget(export_btn)
        layout.addWidget(clear_btn)
        
        return widget
    
    def setup_table(self):
        self.incident_table.setColumnCount(6)
        self.incident_table.setHorizontalHeaderLabels([
            "Time", "Service", "Severity", "Type", "Description", "Status"
        ])
        
        header = self.incident_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.incident_table.setSortingEnabled(True)
        self.incident_table.itemSelectionChanged.connect(self.on_incident_selected)
        
        self.incident_table.setAlternatingRowColors(True)
        self.incident_table.verticalHeader().setVisible(False)
    
    def load_initial_incidents(self):
        self.refresh_incidents()
    
    def refresh_incidents(self):
        url = f"{self.config.api_base_url}/api/incidents"
        try:
            response = requests.get(url, timeout=self.config.api_timeout)
            if response.status_code == 200:
                self.incidents = response.json().get("incidents", [])
                self.update_table()
            else:
                logger.error(f"Failed to fetch incidents (code {response.status_code})")
        except requests.exceptions.RequestException as e:
            logger.error(f"Requests error on incidents fetch: {e}")
    
    def update_table(self):
        self.incident_table.setRowCount(0)
        
        for incident in self.incidents:
            row = self.incident_table.rowCount()
            self.incident_table.insertRow(row)
            
            try:
                timestamp = datetime.fromisoformat(incident["timestamp"])
                time_str = timestamp.strftime("%H:%M:%S")
            except:
                time_str = incident["timestamp"]
            
            time_item = QTableWidgetItem(time_str)
            service_item = QTableWidgetItem(incident["service"])
            severity_item = QTableWidgetItem(incident["severity"].upper())
            type_item = QTableWidgetItem(incident["type"])
            desc_item = QTableWidgetItem(incident["description"])
            status_item = QTableWidgetItem(incident.get("status", "active").upper())
            
            severity_color = get_severity_color(incident["severity"])
            severity_item.setBackground(QColor(severity_color))
            severity_item.setForeground(QColor("#1e1e2e"))
            
            status = incident.get("status", "active")
            if status == "active":
                status_item.setBackground(QColor("#f38ba8"))
                status_item.setForeground(QColor("#1e1e2e"))
            elif status == "resolved":
                status_item.setBackground(QColor("#a6e3a1"))
                status_item.setForeground(QColor("#1e1e2e"))
            else:
                status_item.setBackground(QColor("#f9e2af"))
                status_item.setForeground(QColor("#1e1e2e"))
            
            self.incident_table.setItem(row, 0, time_item)
            self.incident_table.setItem(row, 1, service_item)
            self.incident_table.setItem(row, 2, severity_item)
            self.incident_table.setItem(row, 3, type_item)
            self.incident_table.setItem(row, 4, desc_item)
            self.incident_table.setItem(row, 5, status_item)
        
        self.footer_label.setText(f"{len(self.incidents)} incidents found")
    
    def apply_filter(self, severity):
        for row in range(self.incident_table.rowCount()):
            severity_item = self.incident_table.item(row, 2)
            if severity == "All" or severity_item.text() == severity.upper():
                self.incident_table.setRowHidden(row, False)
            else:
                self.incident_table.setRowHidden(row, True)
    
    def on_incident_selected(self):
        selected_rows = self.incident_table.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            if row < len(self.incidents):
                self.incident_selected.emit(self.incidents[row])
    
    def clear_incidents(self):
        reply = QMessageBox.question(self, "Clear Incidents", "Delete all incidents?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            url = f"{self.config.api_base_url}/api/incidents"
            try:
                requests.delete(url, timeout=self.config.api_timeout)
                self.incidents = []
                self.update_table()
            except Exception as e:
                logger.error(f"Failed to clear incidents: {e}")
                
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Incidents CSV", "incidents.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Time", "Service", "Severity", "Type", "Description", "Status"])
                for i in self.incidents:
                    writer.writerow([
                        i["timestamp"], i["service"], i["severity"],
                        i["type"], i["description"], i.get("status", "active")
                    ])
            QMessageBox.information(self, "Export Complete", f"Saved to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))