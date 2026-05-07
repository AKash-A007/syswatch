# src/gui/main_window.py

import csv

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from utils.config import AppConfig

from .incident_view import IncidentView
from .metrics_view import MetricsView
from .root_cause_view import RootCauseView
from .service_panel import ServicePanel
from .settings_dialog import SettingsDialog
from .styles import DARK_THEME


class MainWindow(QMainWindow):
    """Professional main window with full feature set"""

    def __init__(self, backend_controller):
        super().__init__()
        self.backend = backend_controller
        self.config = AppConfig()

        self.setup_ui()
        self.create_menus()
        self.create_status_bar()
        self.create_tray_icon()
        self.connect_signals()
        self.start_auto_refresh()

    def setup_ui(self):
        self.setWindowTitle("SysWatch Pro — Distributed Systems Monitor")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        self.setStyleSheet(DARK_THEME)

        # ── Root container ───────────────────────────────────────────
        root = QWidget()
        root.setObjectName("rootWidget")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Header Bar ───────────────────────────────────────────────
        header = QWidget()
        header.setObjectName("headerBar")
        header.setFixedHeight(64)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 0, 18, 0)
        header_layout.setSpacing(16)

        # Logo + title
        title_block = QWidget()
        title_block.setObjectName("headerBar")
        title_layout = QVBoxLayout(title_block)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)

        app_title = QLabel("⬡  SysWatch Pro")
        app_title.setObjectName("appTitle")
        app_subtitle = QLabel("AI-Driven Distributed Systems Monitor")
        app_subtitle.setObjectName("appSubtitle")
        title_layout.addWidget(app_title)
        title_layout.addWidget(app_subtitle)

        header_layout.addWidget(title_block)
        header_layout.addStretch(1)

        # Status summary cards
        self._summary_cards = {}
        cards_data = [
            ("ok", "OK", "#2db571", "countOk"),
            ("warn", "WARNING", "#e8b400", "countWarn"),
            ("crit", "CRITICAL", "#e8294c", "countCrit"),
            ("unknown", "UNKNOWN", "#7f8a9d", "countUnknown"),
        ]
        for key, label_text, color, obj_name in cards_data:
            card = QFrame()
            card.setObjectName("summaryCard")
            card.setFixedWidth(110)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 6, 10, 6)
            card_layout.setSpacing(1)
            card_layout.setAlignment(Qt.AlignCenter)

            count_lbl = QLabel("0")
            count_lbl.setObjectName(obj_name)
            count_lbl.setAlignment(Qt.AlignCenter)

            name_lbl = QLabel(label_text)
            name_lbl.setObjectName("cardLabel")
            name_lbl.setAlignment(Qt.AlignCenter)
            name_lbl.setStyleSheet(
                f"color: {color}; font-size: 7.5pt; font-weight: bold; background: transparent;"
            )

            card_layout.addWidget(count_lbl)
            card_layout.addWidget(name_lbl)
            header_layout.addWidget(card)
            self._summary_cards[key] = count_lbl

        # Divider line
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("background: #2a2d35; max-height: 1px; border: none;")

        root_layout.addWidget(header)
        root_layout.addWidget(div)

        # ── Main content area ────────────────────────────────────────
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(3)

        self.service_panel = ServicePanel(self.config)
        self.service_panel.setMinimumWidth(280)

        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        center_splitter = QSplitter(Qt.Vertical)
        center_splitter.setHandleWidth(3)

        self.metrics_view = MetricsView(self.config)
        self.incident_view = IncidentView(self.config)

        center_splitter.addWidget(self.metrics_view)
        center_splitter.addWidget(self.incident_view)
        center_splitter.setSizes([600, 300])

        center_layout.addWidget(center_splitter)

        self.root_cause_view = RootCauseView(self.config)
        self.root_cause_view.setMinimumWidth(350)

        main_splitter.addWidget(self.service_panel)
        main_splitter.addWidget(center_widget)
        main_splitter.addWidget(self.root_cause_view)
        main_splitter.setSizes([300, 820, 430])

        content_layout.addWidget(main_splitter)
        root_layout.addWidget(content, 1)
        self.setCentralWidget(root)

    def create_menus(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")

        export_action = QAction("&Export Data...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu("&View")
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.manual_refresh)
        view_menu.addAction(refresh_action)

        tools_menu = menubar.addMenu("&Tools")

        stress_test_action = QAction("Run &Stress Test", self)
        stress_test_action.triggered.connect(self.run_stress_test)
        tools_menu.addAction(stress_test_action)

        simulate_incident_action = QAction("&Simulate Incident", self)
        simulate_incident_action.triggered.connect(self.simulate_incident)
        tools_menu.addAction(simulate_incident_action)

        tools_menu.addSeparator()

        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)

        help_menu = menubar.addMenu("&Help")
        about_action = QAction("&About SysWatch Pro", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar_connection()

    def update_status_bar_connection(self):
        self.status_bar.showMessage(f"Ready | Connected to {self.config.api_base_url}")

    def create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)

        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)

        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_application)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def connect_signals(self):
        self.service_panel.service_selected.connect(self.on_service_selected)
        self.incident_view.incident_selected.connect(self.on_incident_selected)
        self.metrics_view.anomaly_detected.connect(self.on_anomaly_detected)

    def start_auto_refresh(self):
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh)
        # Use config's service refresh interval internally for UI tick
        interval = self.config.get("service_refresh_interval", 5) * 1000
        self.refresh_timer.start(interval)

    def on_service_selected(self, service_id):
        self.metrics_view.load_service_metrics(service_id)
        self.status_bar.showMessage(f"Viewing metrics for: {service_id}")

    def on_incident_selected(self, incident_data):
        self.root_cause_view.analyze_incident(incident_data)

    def on_anomaly_detected(self, anomaly_data):
        if self.config.get("enable_notifications"):
            self.tray_icon.showMessage(
                "Anomaly Detected",
                f"Service: {anomaly_data.get('service', 'Unknown')}",
                QSystemTrayIcon.Warning,
                3000,
            )

    def auto_refresh(self):
        self.service_panel.refresh_services()
        self.incident_view.refresh_incidents()
        self._update_summary_cards()

    def _update_summary_cards(self):
        """Recount services by status and update the header summary cards."""
        try:
            import requests

            resp = requests.get(f"{self.config.api_base_url}/api/services", timeout=1)
            services = resp.json().get("services", [])
            counts = {"ok": 0, "warn": 0, "crit": 0, "unknown": 0}
            for svc in services:
                st = svc.get("status", "unknown").lower()
                if st == "healthy":
                    counts["ok"] += 1
                elif st == "warning":
                    counts["warn"] += 1
                elif st == "critical":
                    counts["crit"] += 1
                else:
                    counts["unknown"] += 1
            for key, lbl in self._summary_cards.items():
                lbl.setText(str(counts.get(key, 0)))
        except Exception:
            pass

    def manual_refresh(self):
        self.auto_refresh()
        self.status_bar.showMessage("Data refreshed", 2000)

    def export_data(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Services Data", "services.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "Status", "CPU", "Memory", "Uptime"])
                for s in self.service_panel.current_services.values():
                    writer.writerow(
                        [
                            s.get("id"),
                            s.get("name"),
                            s.get("status"),
                            s.get("cpu_usage"),
                            s.get("memory_usage"),
                            s.get("uptime_seconds"),
                        ]
                    )
            QMessageBox.information(self, "Export Complete", f"Services exported to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def run_stress_test(self):
        reply = QMessageBox.question(
            self,
            "Stress Test",
            "This will generate high load on API Gateway. Continue?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            import requests

            try:
                requests.post(f"{self.config.api_base_url}/api/stress-test", timeout=2)
                self.status_bar.showMessage("Stress test started", 3000)
            except Exception:
                self.status_bar.showMessage("Stress test failed to start", 3000)

    def simulate_incident(self):
        import requests

        try:
            requests.post(f"{self.config.api_base_url}/api/simulate-incident", timeout=2)
            self.status_bar.showMessage("Incident simulated", 3000)
            self.manual_refresh()
        except Exception:
            self.status_bar.showMessage("Failed to simulate incident", 3000)

    def open_settings(self):
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            # Apply new refresh settings
            self.refresh_timer.start(int(self.config.get("service_refresh_interval", 5) * 1000))
            self.metrics_view.update_timer.start(
                int(self.config.get("metrics_refresh_interval", 1) * 1000)
            )
            self.update_status_bar_connection()

    def show_about(self):
        QMessageBox.about(
            self,
            "About SysWatch Pro",
            "<h2>SysWatch Pro v1.0</h2>"
            "<p>AI-Driven Distributed Systems Debugger</p>"
            "<p>Technology Stack:<br>Python • Qt (PySide6) • PyQtGraph • FastAPI</p>",
        )

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()

    def quit_application(self):
        if self.backend:
            self.backend.shutdown()
        QApplication.quit()

    def closeEvent(self, event):
        if self.config.get("confirm_exit"):
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "Are you sure you want to exit SysWatch Pro?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.No:
                event.ignore()
                return

        if self.config.get("minimize_to_tray"):
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "SysWatch Pro", "Application minimized to tray", QSystemTrayIcon.Information, 2000
            )
        else:
            self.quit_application()
