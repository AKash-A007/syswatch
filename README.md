# 🖥️ SysWatch Pro - Desktop Edition

**AI-Driven Distributed Systems Debugger**

A professional desktop application for monitoring distributed systems with real-time metrics, intelligent incident detection, and AI-powered root cause analysis.

---

## ✨ Features

### 🎯 Core Capabilities
- **Real-Time Monitoring**: Live CPU, memory, latency, and throughput metrics
- **Service Dashboard**: Visual overview of all monitored services
- **Incident Timeline**: Chronological view of detected issues
- **AI Root Cause Analysis**: Intelligent problem diagnosis with recommended fixes
- **Interactive Debugging**: Manual stress testing and incident simulation

### 🎨 Professional UI
- Modern dark theme with Catppuccin color palette
- Responsive layout with resizable panels
- System tray integration
- Multi-tab metrics visualization
- Color-coded severity indicators

### 🔧 Technical Highlights
- Native Qt desktop application (PySide6)
- FastAPI backend with async operations
- PyQtGraph for high-performance charting
- Modular architecture for easy extension
- Cross-platform compatibility

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Windows 10/11 (Linux/macOS compatible with minor adjustments)
- 4GB RAM minimum
- 500MB disk space

### Quick Start

#### 1. Clone or Extract Project
```bash
# If using git
git clone <your-repo-url>
cd syswatch-pro

# Or extract the ZIP file
```

#### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run Application
```bash
python src/main.py
```

The application will:
1. Start the backend API server on `http://localhost:8000`
2. Launch the desktop GUI
3. Begin monitoring (with mock data if no services connected)

---

## 🏗️ Project Structure

```
syswatch-pro/
│
├── src/
│   ├── gui/                    # Frontend components
│   │   ├── main_window.py     # Main application window
│   │   ├── service_panel.py   # Service monitoring panel
│   │   ├── metrics_view.py    # Real-time graphs
│   │   ├── incident_view.py   # Incident timeline
│   │   ├── root_cause_view.py # AI analysis panel
│   │   ├── settings_dialog.py # Settings configuration
│   │   └── styles.py          # UI theme/styling
│   │
│   ├── backend/                # Backend API
│   │   ├── api_server.py      # FastAPI server
│   │   ├── collector.py       # Metrics collection
│   │   ├── analyzer.py        # AI analysis engine
│   │   └── storage.py         # Data persistence
│   │
│   ├── agent/                  # Service agent
│   │   └── syswatch_agent.py  # Client-side monitoring
│   │
│   └── main.py                 # Application entry point
│
├── resources/                  # Icons, images, styles
├── tests/                      # Unit tests
├── requirements.txt            # Python dependencies
├── build.spec                  # PyInstaller config
├── setup.py                    # Package configuration
└── README.md                   # This file
```

---

## 🚀 Building Executable (Windows)

### Method 1: Single EXE File

```bash
# Install PyInstaller (if not already installed)
pip install pyinstaller

# Build using spec file
pyinstaller build.spec

# Output will be in: dist/SysWatch_Pro.exe
```

### Method 2: Directory with Dependencies

```bash
# Build with all dependencies in folder
pyinstaller --onedir --windowed --name SysWatch_Pro src/main.py

# Output will be in: dist/SysWatch_Pro/
```

### Method 3: Advanced Build

```bash
# Custom build with icon and optimizations
pyinstaller --onefile ^
    --windowed ^
    --name SysWatch_Pro ^
    --icon resources/app_icon.ico ^
    --add-data "resources;resources" ^
    --hidden-import PySide6 ^
    --hidden-import pyqtgraph ^
    --hidden-import fastapi ^
    src/main.py
```

### Build Options Explained

| Option | Description |
|--------|-------------|
| `--onefile` | Single executable (slower startup) |
| `--onedir` | Directory with dependencies (faster startup) |
| `--windowed` | No console window |
| `--console` | Show console (for debugging) |
| `--icon` | Custom application icon |
| `--name` | Output file name |
| `--add-data` | Include resource files |

---

## ⚙️ Configuration

### Settings Dialog
Access via `Tools > Settings` or `Ctrl+,`

**Connection Settings**
- API Host/Port
- Request timeout
- HTTPS toggle

**Monitoring Settings**
- Refresh rates (services, metrics, incidents)
- Alert thresholds (CPU, memory, latency)

**UI Preferences**
- Start minimized
- System tray behavior
- Splash screen

**Notifications**
- System notifications
- Severity filters
- Sound alerts

### Configuration File
Settings are saved to: `%APPDATA%/SysWatch/config.json` (Windows)

---

## 🔌 Connecting Real Services

### Step 1: Install Agent on Service
```bash
pip install syswatch-agent
```

### Step 2: Initialize Agent
```python
from syswatch_agent import SysWatchAgent

agent = SysWatchAgent(
    service_name="my-service",
    api_url="http://localhost:8000"
)

agent.start()
```

### Step 3: Configure in SysWatch
1. Open SysWatch Pro
2. Click "Add Service" in Services panel
3. Enter service details
4. Service will appear automatically once agent connects

---

## 🧪 Testing & Development

### Run Tests
```bash
pytest tests/
```

### Run with Debug Console
```bash
# Shows backend logs and errors
python src/main.py --console
```

### Mock Data Mode
The application automatically uses mock data when services aren't connected. Perfect for:
- UI development
- Testing layouts
- Demonstrations
- Screenshots

---

## 📊 Features Deep Dive

### Service Monitoring
- Status tracking (Healthy, Warning, Critical)
- CPU and memory usage
- Uptime tracking
- Quick service selection

### Metrics Visualization
- **CPU & Memory Tab**: Dedicated graphs for resource usage
- **Latency & Requests Tab**: Response time and throughput
- **All Metrics Tab**: Combined view with normalized scales
- Time window controls (1min - 1hour)
- Pause/resume functionality
- Zoom and pan support

### Incident Management
- Automatic severity classification
- Filter by severity level
- Click to analyze with AI
- Status tracking (Active, Investigating, Resolved)
- Export capabilities

### AI Root Cause Analysis
- Natural language explanations
- Confidence scoring
- Prioritized recommendations
- Related incident correlation
- Timeline reconstruction

---

## 🎯 Usage Tips

### Best Practices
1. **Start Small**: Begin with 2-3 services to understand the interface
2. **Set Thresholds**: Adjust alert thresholds to match your infrastructure
3. **Use Time Windows**: Switch between 1min (debugging) and 1hour (trends)
4. **Export Reports**: Save AI analysis for post-mortems
5. **Tray Mode**: Minimize to tray for always-on monitoring

### Keyboard Shortcuts
- `F5` - Refresh all data
- `Ctrl+,` - Open settings
- `Ctrl+E` - Export data
- `Ctrl+Q` - Quit application

### Troubleshooting
- **Services not appearing**: Check agent installation and API connection
- **Graphs not updating**: Verify backend is running on port 8000
- **High CPU usage**: Increase refresh intervals in settings
- **Missing data**: Check firewall settings for localhost:8000

---

## 🛠️ Advanced Customization

### Custom Themes
Edit `src/gui/styles.py` to create custom color schemes.

### Additional Metrics
Add new metric types in `src/backend/collector.py`.

### Custom Analyzers
Extend AI analysis in `src/backend/analyzer.py`.

### Plugin System
Create custom panels by inheriting from `QWidget`.

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📮 Support

- **Issues**: GitHub Issues
- **Email**: support@syswatch.dev (example)
- **Docs**: https://docs.syswatch.dev (example)

---

## 🎓 Interview Talking Points

When discussing this project in interviews:

### Technical Depth
- "Built a native desktop application using Qt framework"
- "Implemented real-time data visualization with PyQtGraph"
- "Created RESTful API backend with FastAPI"
- "Used multiprocessing for concurrent backend/frontend"

### Engineering Decisions
- "Chose Qt over Electron for better performance and lower memory footprint"
- "Implemented async I/O for non-blocking metrics collection"
- "Used observer pattern for component communication"
- "Designed modular architecture for easy feature additions"

### Problem Solving
- "Handled cross-thread communication between GUI and backend"
- "Optimized graph rendering for smooth 60 FPS updates"
- "Implemented graceful degradation with mock data"
- "Created efficient data structures for time-series storage"

### Production Readiness
- "Packaged as standalone executable with PyInstaller"
- "Implemented error handling and logging"
- "Added configuration persistence"
- "Created comprehensive user documentation"

---

**Built with ❤️ for distributed systems engineers**