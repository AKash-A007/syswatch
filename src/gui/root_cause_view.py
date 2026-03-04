# src/gui/root_cause_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QProgressBar, QGroupBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
import requests
import time
from datetime import datetime

from utils.logger import get_logger
from utils.config import AppConfig

logger = get_logger("root_cause_view")


class AIAnalysisThread(QThread):
    """Background thread for AI analysis"""
    
    analysis_complete = Signal(dict)
    progress_update = Signal(int)
    
    def __init__(self, incident_data, config: AppConfig):
        super().__init__()
        self.incident_data = incident_data
        self.config = config
    
    def run(self):
        try:
            steps = [
                ("Gathering metrics", 20),
                ("Analyzing patterns", 40),
                ("Identifying correlations", 60),
                ("Generating insights", 80),
                ("Preparing recommendations", 100)
            ]
            
            for step_name, progress in steps:
                time.sleep(0.3)
                self.progress_update.emit(progress)
            
            url = f"{self.config.api_base_url}/api/analyze"
            response = requests.post(url, json=self.incident_data, timeout=self.config.api_timeout)
            
            if response.status_code == 200:
                result = response.json()
            else:
                raise Exception(f"API Error {response.status_code}")
            
            self.analysis_complete.emit(result)
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            self.analysis_complete.emit({
                "root_cause": "Analysis Failed",
                "confidence": 0,
                "explanation": f"Failed to contact AI engine: {e}",
                "recommendations": []
            })


class RootCauseView(QWidget):
    """AI-powered root cause analysis panel"""
    
    def __init__(self, config: AppConfig = None):
        super().__init__()
        self.config = config or AppConfig()
        self.current_analysis = None
        self.analysis_thread = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        header = QLabel("AI Root Cause Analysis")
        header.setProperty("heading", True)
        layout.addWidget(header)
        
        status_group = self.create_status_section()
        layout.addWidget(status_group)
        
        analysis_group = self.create_analysis_section()
        layout.addWidget(analysis_group)
        
        rec_group = self.create_recommendations_section()
        layout.addWidget(rec_group)
        
        btn_layout = self.create_action_buttons()
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        self.show_idle_state()
    
    def create_status_section(self):
        group = QGroupBox("Analysis Status")
        layout = QVBoxLayout()
        
        self.status_label = QLabel("No incident selected")
        self.status_label.setWordWrap(True)
        
        self.confidence_bar = QProgressBar()
        self.confidence_bar.setVisible(False)
        self.confidence_bar.setFormat("Confidence: %p%")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFormat("Analyzing: %p%")
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.confidence_bar)
        layout.addWidget(self.progress_bar)
        
        group.setLayout(layout)
        return group
    
    def create_analysis_section(self):
        group = QGroupBox("Root Cause")
        layout = QVBoxLayout()
        
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setMinimumHeight(250)
        
        layout.addWidget(self.analysis_text)
        group.setLayout(layout)
        return group
    
    def create_recommendations_section(self):
        group = QGroupBox("Recommended Actions")
        layout = QVBoxLayout()
        
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        self.recommendations_text.setMinimumHeight(200)
        
        layout.addWidget(self.recommendations_text)
        group.setLayout(layout)
        return group
    
    def create_action_buttons(self):
        layout = QHBoxLayout()
        
        self.reanalyze_btn = QPushButton("Re-analyze")
        self.reanalyze_btn.clicked.connect(self.reanalyze)
        self.reanalyze_btn.setEnabled(False)
        
        self.export_btn = QPushButton("Export Report")
        self.export_btn.clicked.connect(self.export_report)
        self.export_btn.setEnabled(False)
        
        layout.addWidget(self.reanalyze_btn)
        layout.addWidget(self.export_btn)
        
        return layout
    
    def show_idle_state(self):
        self.analysis_text.setHtml("""
            <div style='text-align: center; padding: 40px;'>
                <h3 style='color: #cdd6f4;'>No Incident Selected</h3>
                <p style='color: #a6adc8;'>
                    Select an incident from the timeline to view AI-powered root cause analysis.
                </p>
            </div>
        """)
        self.recommendations_text.clear()
        self.export_btn.setEnabled(False)
        self.reanalyze_btn.setEnabled(False)
    
    def analyze_incident(self, incident_data):
        self.current_incident = incident_data
        
        self.status_label.setText(f"Analyzing: {incident_data.get('type', 'Unknown')}")
        self.progress_bar.setVisible(True)
        self.confidence_bar.setVisible(False)
        self.progress_bar.setValue(0)
        
        self.analysis_text.setHtml("""
            <div style='text-align: center; padding: 40px;'>
                <h3 style='color: #89b4fa;'>🤖 AI Analysis in Progress...</h3>
                <p style='color: #a6adc8;'>
                    Gathering metrics, identifying patterns, and generating insights...
                </p>
            </div>
        """)
        
        # Start analysis thread
        self.analysis_thread = AIAnalysisThread(incident_data, self.config)
        self.analysis_thread.progress_update.connect(self.on_progress_update)
        self.analysis_thread.analysis_complete.connect(self.on_analysis_complete)
        self.analysis_thread.start()
    
    def on_progress_update(self, progress):
        self.progress_bar.setValue(progress)
    
    def on_analysis_complete(self, result):
        self.current_analysis = result
        self.progress_bar.setVisible(False)
        self.confidence_bar.setVisible(True)
        self.confidence_bar.setValue(result.get("confidence", 0))
        
        self.status_label.setText("✓ Analysis Complete")
        
        exp = result.get("explanation", "No explanation available")
        self.analysis_text.setHtml(f"""
            <div style='padding: 10px;'>
                <h3 style='color: #f5e0dc; margin-bottom: 10px;'>
                    🎯 {result.get('root_cause', 'Unknown')}
                </h3>
                <div style='color: #cdd6f4; line-height: 1.6;'>
                    {exp.replace('\n', '<br>')}
                </div>
            </div>
        """)
        
        recs = result.get("recommendations", [])
        rec_html = "<div style='padding: 10px;'>"
        for i, rec in enumerate(recs, 1):
            priorities = {'high': '#f38ba8', 'medium': '#f9e2af', 'low': '#89b4fa'}
            color = priorities.get(rec.get('priority', 'low'), '#89b4fa')
            
            rec_html += f"""
                <div style='margin-bottom: 15px; padding: 10px; background-color: #313244; border-radius: 6px; border-left: 4px solid {color};'>
                    <div style='font-weight: bold; color: #f5e0dc; margin-bottom: 5px;'>
                        {i}. {rec.get('action', 'Unknown Action')}
                        <span style='float: right; background-color: {color}; color: #1e1e2e; padding: 2px 8px; border-radius: 4px; font-size: 9pt;'>
                            {rec.get('priority', 'low').upper()}
                        </span>
                    </div>
                    <div style='color: #a6adc8; font-size: 9pt; margin-bottom: 5px;'>
                        {rec.get('description', '')}
                    </div>
                    <div style='color: #89b4fa; font-size: 9pt; font-style: italic;'>
                        💡 {rec.get('impact', '')}
                    </div>
                </div>
            """
        rec_html += "</div>"
        self.recommendations_text.setHtml(rec_html)
        
        self.reanalyze_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
    
    def reanalyze(self):
        if hasattr(self, 'current_incident'):
            self.analyze_incident(self.current_incident)
    
    def export_report(self):
        if not self.current_analysis:
            return
            
        path, _ = QFileDialog.getSaveFileName(self, "Export Report", "incident_report.html", "HTML Files (*.html)")
        if not path:
            return
            
        try:
            html = f"""
            <html>
            <head>
                <title>SysWatch Pro - Incident Report</title>
                <style>
                    body {{ font-family: sans-serif; background: #1e1e2e; color: #cdd6f4; padding: 2em; }}
                    h1, h2, h3 {{ color: #89b4fa; }}
                    .card {{ background: #313244; padding: 1em; border-radius: 8px; margin-bottom: 1em; }}
                    .high {{ border-left: 5px solid #f38ba8; }}
                    .medium {{ border-left: 5px solid #f9e2af; }}
                    .low {{ border-left: 5px solid #89b4fa; }}
                </style>
            </head>
            <body>
                <h1>Root Cause Analysis Report</h1>
                <p>Generated: {datetime.utcnow().isoformat()}</p>
                <div class="card">
                    <h2>Root Cause ({self.current_analysis.get('confidence', 0)}% Confidence)</h2>
                    <h3>{self.current_analysis.get('root_cause')}</h3>
                    <p>{self.current_analysis.get('explanation', '').replace(chr(10), '<br>')}</p>
                </div>
                <h2>Recommendations</h2>
            """
            for rec in self.current_analysis.get('recommendations', []):
                pri = rec.get('priority', 'low')
                html += f"""
                <div class="card {pri}">
                    <h3>{rec.get('action')} ({pri.upper()})</h3>
                    <p>{rec.get('description')}</p>
                    <p><i>Impact: {rec.get('impact')}</i></p>
                </div>
                """
            html += "</body></html>"
            
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
                
            QMessageBox.information(self, "Export Complete", f"Saved to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))