# src/main.py

import sys
import multiprocessing
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont
from gui.main_window import MainWindow
from backend.api_server import start_server


class BackendController:
    """Controller for backend operations"""
    
    def __init__(self):
        self.backend_process = None
    
    def start_backend(self):
        """Start backend server in separate process"""
        self.backend_process = multiprocessing.Process(
            target=start_server,
            args=("localhost", 8000)
        )
        self.backend_process.daemon = True
        self.backend_process.start()
        print("Backend server started on http://localhost:8000")
    
    def shutdown(self):
        """Shutdown backend server"""
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.join(timeout=2)
            print("Backend server shutdown complete")
    
    def run_stress_test(self):
        """Trigger stress test"""
        import requests
        try:
            requests.post("http://localhost:8000/api/stress-test", timeout=2)
        except:
            pass
    
    def simulate_incident(self):
        """Simulate incident"""
        import requests
        try:
            requests.post("http://localhost:8000/api/simulate-incident", timeout=2)
        except:
            pass


def create_splash_screen():
    """Create splash screen"""
    # Create a simple colored splash screen
    pixmap = QPixmap(600, 400)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    splash = QSplashScreen(pixmap)
    splash.setStyleSheet("""
        QSplashScreen {
            background-color: #1e1e2e;
            border: 2px solid #89b4fa;
            border-radius: 10px;
        }
    """)
    
    font = QFont("Segoe UI", 16, QFont.Bold)
    splash.setFont(font)
    
    splash.showMessage(
        "SysWatch Pro\n\nInitializing...",
        Qt.AlignCenter,
        Qt.GlobalColor.white
    )
    
    return splash


def main():
    """Main application entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("SysWatch Pro")
    app.setOrganizationName("SysWatch")
    app.setApplicationVersion("1.0.0")
    
    # Show splash screen
    splash = create_splash_screen()
    splash.show()
    app.processEvents()
    
    # Initialize backend controller
    backend = BackendController()
    
    # Update splash
    splash.showMessage(
        "SysWatch Pro\n\nStarting backend server...",
        Qt.AlignCenter,
        Qt.GlobalColor.white
    )
    app.processEvents()
    
    # Start backend server
    backend.start_backend()
    
    # Wait a bit for backend to start
    import time
    time.sleep(1)
    
    # Update splash
    splash.showMessage(
        "SysWatch Pro\n\nLoading UI...",
        Qt.AlignCenter,
        Qt.GlobalColor.white
    )
    app.processEvents()
    
    # Create main window
    window = MainWindow(backend)
    
    # Close splash and show main window
    splash.finish(window)
    window.show()
    
    # Run application
    try:
        exit_code = app.exec()
    finally:
        backend.shutdown()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    # Freeze support for PyInstaller
    multiprocessing.freeze_support()
    main()