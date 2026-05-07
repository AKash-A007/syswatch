# src/gui/styles.py
"""SysWatch Pro — Checkmk-inspired professional monitoring theme."""


def get_status_color(status: str) -> str:
    """Return hex color for a service status string."""
    return {
        "healthy": "#2db571",
        "warning": "#e8b400",
        "critical": "#e8294c",
        "unknown": "#7f8a9d",
    }.get(status.lower(), "#7f8a9d")


def get_severity_color(severity: str) -> str:
    """Return hex color for an incident severity string."""
    return {
        "critical": "#e8294c",
        "high": "#f06830",
        "medium": "#e8b400",
        "low": "#0082c9",
        "info": "#2db571",
    }.get(severity.lower(), "#d4dae3")


DARK_THEME = """
/* ============================================================
   SysWatch Pro — Checkmk-style Professional Monitoring Theme
   ============================================================ */

/* ── Global ─────────────────────────────────────────────────── */
* {
    font-family: "Segoe UI", "Inter", "Roboto", "Arial", sans-serif;
    font-size: 10pt;
    outline: none;
}

QMainWindow, QDialog {
    background-color: #13151a;
    color: #d4dae3;
}

QWidget {
    background-color: #1a1d23;
    color: #d4dae3;
}

/* ── Header Bar (object name: headerBar) ─────────────────────── */
QWidget#headerBar {
    background-color: #0d0f13;
    border-bottom: 2px solid #0082c9;
}

QLabel#appTitle {
    color: #ffffff;
    font-size: 15pt;
    font-weight: bold;
    letter-spacing: 0.5px;
}

QLabel#appSubtitle {
    color: #8a93a2;
    font-size: 9pt;
}

/* ── Status Summary Cards ────────────────────────────────────── */
QFrame#summaryCard {
    background-color: #13151a;
    border: 1px solid #2a2d35;
    border-radius: 6px;
    padding: 4px;
}

QLabel#countOk {
    color: #2db571;
    font-size: 22pt;
    font-weight: bold;
}
QLabel#countWarn {
    color: #e8b400;
    font-size: 22pt;
    font-weight: bold;
}
QLabel#countCrit {
    color: #e8294c;
    font-size: 22pt;
    font-weight: bold;
}
QLabel#countUnknown {
    color: #7f8a9d;
    font-size: 22pt;
    font-weight: bold;
}
QLabel#cardLabel {
    color: #8a93a2;
    font-size: 8pt;
    font-weight: bold;
    letter-spacing: 0.5px;
}

/* ── Menu Bar ────────────────────────────────────────────────── */
QMenuBar {
    background-color: #0d0f13;
    color: #b0b8c4;
    border-bottom: 1px solid #2a2d35;
    padding: 2px 0;
    font-size: 9.5pt;
}
QMenuBar::item { padding: 5px 14px; }
QMenuBar::item:selected { background-color: #1e2128; color: #ffffff; }
QMenuBar::item:pressed  { background-color: #0082c9; color: #ffffff; }

QMenu {
    background-color: #13151a;
    color: #d4dae3;
    border: 1px solid #2a2d35;
    border-radius: 4px;
    padding: 4px 0;
}
QMenu::item { padding: 7px 28px 7px 16px; }
QMenu::item:selected  { background-color: #0082c9; color: #ffffff; }
QMenu::separator { height: 1px; background: #2a2d35; margin: 4px 0; }

/* ── Status Bar ──────────────────────────────────────────────── */
QStatusBar {
    background-color: #0d0f13;
    color: #6b7280;
    border-top: 1px solid #2a2d35;
    font-size: 9pt;
    padding: 2px 6px;
}
QStatusBar::item { border: none; }

/* ── Side Panel (service list) ───────────────────────────────── */
QWidget#sidePanel {
    background-color: #13151a;
    border-right: 1px solid #2a2d35;
}

QLabel#panelTitle {
    color: #8a93a2;
    font-size: 8pt;
    font-weight: bold;
    letter-spacing: 1px;
    padding: 10px 12px 6px 12px;
    text-transform: uppercase;
}

/* ── Group Box ───────────────────────────────────────────────── */
QGroupBox {
    color: #8a93a2;
    border: 1px solid #2a2d35;
    border-radius: 6px;
    margin-top: 14px;
    padding: 12px 8px 8px 8px;
    font-weight: bold;
    font-size: 9pt;
    letter-spacing: 0.5px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    top: -7px;
    padding: 0 6px;
    background-color: #1a1d23;
    color: #8a93a2;
}

/* ── Labels ──────────────────────────────────────────────────── */
QLabel { color: #d4dae3; background: transparent; }

QLabel[heading="true"] {
    font-size: 12pt;
    font-weight: bold;
    color: #ffffff;
    padding: 4px 0;
}
QLabel[subheading="true"] {
    font-size: 10pt;
    font-weight: bold;
    color: #0082c9;
}
QLabel[muted="true"] {
    color: #6b7280;
    font-size: 9pt;
}

/* ── Push Buttons ────────────────────────────────────────────── */
QPushButton {
    background-color: #22262e;
    color: #c0c8d4;
    border: 1px solid #2a2d35;
    border-radius: 5px;
    padding: 6px 18px;
    font-size: 9.5pt;
    font-weight: 500;
}
QPushButton:hover   {
    background-color: #2a2f3a;
    border-color: #0082c9;
    color: #ffffff;
}
QPushButton:pressed { background-color: #0070ad; border-color: #0082c9; color: #fff; }
QPushButton:disabled { color: #3d4452; background-color: #1a1d23; border-color: #22262e; }
QPushButton:checked { background-color: #0082c9; color: #ffffff; border-color: #0082c9; }

QPushButton[primary="true"] {
    background-color: #0082c9;
    color: #ffffff;
    border-color: #0082c9;
    font-weight: bold;
}
QPushButton[primary="true"]:hover { background-color: #0095e0; }

QPushButton[success="true"] {
    background-color: #1e6b3a;
    color: #2db571;
    border-color: #2db571;
    font-weight: bold;
}
QPushButton[success="true"]:hover { background-color: #2db571; color: #fff; }

QPushButton[danger="true"] {
    background-color: #5a1522;
    color: #e8294c;
    border-color: #e8294c;
    font-weight: bold;
}
QPushButton[danger="true"]:hover { background-color: #e8294c; color: #fff; }

QPushButton[warning="true"] {
    background-color: #4a3800;
    color: #e8b400;
    border-color: #e8b400;
    font-weight: bold;
}
QPushButton[warning="true"]:hover { background-color: #e8b400; color: #000; }

/* ── Line Edit / Spin Box ────────────────────────────────────── */
QLineEdit, QSpinBox, QDoubleSpinBox {
    background-color: #13151a;
    color: #d4dae3;
    border: 1px solid #2a2d35;
    border-radius: 5px;
    padding: 5px 8px;
    selection-background-color: #0082c9;
    selection-color: #ffffff;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #0082c9;
    background-color: #161921;
}
QSpinBox::up-button, QSpinBox::down-button {
    background-color: #22262e;
    border: none;
    border-radius: 3px;
    width: 16px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover { background-color: #2a2d35; }

/* ── Combo Box ───────────────────────────────────────────────── */
QComboBox {
    background-color: #13151a;
    color: #d4dae3;
    border: 1px solid #2a2d35;
    border-radius: 5px;
    padding: 5px 8px;
    min-width: 80px;
}
QComboBox:hover   { border-color: #0082c9; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #6b7280;
    margin-right: 6px;
}
QComboBox QAbstractItemView {
    background-color: #13151a;
    color: #d4dae3;
    border: 1px solid #2a2d35;
    selection-background-color: #0082c9;
    selection-color: #ffffff;
}

/* ── Check Box ───────────────────────────────────────────────── */
QCheckBox { color: #d4dae3; spacing: 8px; background: transparent; }
QCheckBox::indicator {
    width: 15px; height: 15px;
    border: 1px solid #3d4452;
    border-radius: 3px;
    background-color: #13151a;
}
QCheckBox::indicator:checked {
    background-color: #0082c9;
    border-color: #0082c9;
    image: none;
}
QCheckBox::indicator:hover { border-color: #0082c9; }

/* ── Tab Widget ──────────────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #2a2d35;
    border-top: none;
    background-color: #1a1d23;
    border-radius: 0 0 6px 6px;
}
QTabBar {
    background: transparent;
}
QTabBar::tab {
    background-color: #13151a;
    color: #6b7280;
    border: 1px solid #2a2d35;
    border-bottom: none;
    padding: 7px 20px;
    margin-right: 1px;
    font-size: 9.5pt;
    font-weight: 500;
}
QTabBar::tab:first { border-top-left-radius: 6px; }
QTabBar::tab:last  { border-top-right-radius: 6px; }
QTabBar::tab:selected {
    background-color: #1a1d23;
    color: #0082c9;
    border-top: 2px solid #0082c9;
    font-weight: bold;
}
QTabBar::tab:hover:!selected { background-color: #1e2128; color: #b0b8c4; }

/* ── List Widget ─────────────────────────────────────────────── */
QListWidget {
    background-color: #13151a;
    border: none;
    alternate-background-color: #161921;
    outline: none;
}
QListWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #1e2128;
    color: #c0c8d4;
}
QListWidget::item:selected {
    background-color: #162033;
    color: #ffffff;
    border-left: 3px solid #0082c9;
}
QListWidget::item:hover { background-color: #1e2128; }

/* ── Table Widget ────────────────────────────────────────────── */
QTableWidget {
    background-color: #13151a;
    alternate-background-color: #161921;
    gridline-color: #1e2128;
    border: none;
    outline: none;
    selection-background-color: #162033;
    selection-color: #ffffff;
}
QTableWidget::item {
    padding: 5px 10px;
    border-bottom: 1px solid #1e2128;
    color: #c0c8d4;
}
QTableWidget::item:selected {
    background-color: #162033;
    color: #ffffff;
}

QHeaderView {
    background-color: #0d0f13;
}
QHeaderView::section {
    background-color: #0d0f13;
    color: #6b7280;
    border: none;
    border-right: 1px solid #2a2d35;
    border-bottom: 2px solid #2a2d35;
    padding: 7px 12px;
    font-weight: bold;
    font-size: 8.5pt;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
QHeaderView::section:first { padding-left: 14px; }
QHeaderView::section:last { border-right: none; }

/* ── Scroll Bar ──────────────────────────────────────────────── */
QScrollBar:vertical {
    background: #13151a;
    width: 8px;
    border-radius: 4px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #2a2d35;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #3d4452; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background: #13151a;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #2a2d35;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: #3d4452; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Progress Bar ────────────────────────────────────────────── */
QProgressBar {
    background-color: #0d0f13;
    border: none;
    border-radius: 3px;
    height: 6px;
    text-align: center;
    color: transparent;
    font-size: 8pt;
}
QProgressBar::chunk {
    background: #0082c9;
    border-radius: 3px;
}
QProgressBar[status="ok"]::chunk       { background: #2db571; }
QProgressBar[status="warning"]::chunk  { background: #e8b400; }
QProgressBar[status="critical"]::chunk { background: #e8294c; }

/* ── Text Edit ───────────────────────────────────────────────── */
QTextEdit {
    background-color: #13151a;
    color: #c0c8d4;
    border: 1px solid #2a2d35;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #0082c9;
    line-height: 1.5;
}
QTextEdit:focus { border-color: #0082c9; }

/* ── Splitter ────────────────────────────────────────────────── */
QSplitter::handle {
    background-color: #2a2d35;
}
QSplitter::handle:horizontal { width: 3px; }
QSplitter::handle:vertical   { height: 3px; }
QSplitter::handle:hover { background-color: #0082c9; }

/* ── Dialog ──────────────────────────────────────────────────── */
QDialog {
    background-color: #1a1d23;
    border: 1px solid #2a2d35;
}

/* ── Tooltip ─────────────────────────────────────────────────── */
QToolTip {
    background-color: #0d0f13;
    color: #d4dae3;
    border: 1px solid #2a2d35;
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 9pt;
}

/* ── Status badge labels ─────────────────────────────────────── */
QLabel[status="healthy"]  {
    background-color: #1e4d32;
    color: #2db571;
    border: 1px solid #2db571;
    border-radius: 3px;
    padding: 2px 8px;
    font-weight: bold;
    font-size: 8.5pt;
}
QLabel[status="warning"]  {
    background-color: #3d3000;
    color: #e8b400;
    border: 1px solid #e8b400;
    border-radius: 3px;
    padding: 2px 8px;
    font-weight: bold;
    font-size: 8.5pt;
}
QLabel[status="critical"] {
    background-color: #3d0a12;
    color: #e8294c;
    border: 1px solid #e8294c;
    border-radius: 3px;
    padding: 2px 8px;
    font-weight: bold;
    font-size: 8.5pt;
}
QLabel[status="unknown"]  {
    background-color: #22262e;
    color: #7f8a9d;
    border: 1px solid #3d4452;
    border-radius: 3px;
    padding: 2px 8px;
    font-weight: bold;
    font-size: 8.5pt;
}

/* ── Severity pill labels ────────────────────────────────────── */
QLabel[severity="critical"] {
    background-color: #3d0a12; color: #e8294c;
    border: 1px solid #e8294c;
    border-radius: 3px; padding: 1px 7px; font-weight: bold; font-size: 8pt;
}
QLabel[severity="high"] {
    background-color: #3a1a00; color: #f06830;
    border: 1px solid #f06830;
    border-radius: 3px; padding: 1px 7px; font-weight: bold; font-size: 8pt;
}
QLabel[severity="medium"] {
    background-color: #3d3000; color: #e8b400;
    border: 1px solid #e8b400;
    border-radius: 3px; padding: 1px 7px; font-weight: bold; font-size: 8pt;
}
QLabel[severity="low"] {
    background-color: #00203d; color: #0082c9;
    border: 1px solid #0082c9;
    border-radius: 3px; padding: 1px 7px; font-weight: bold; font-size: 8pt;
}

/* ── Separator line ──────────────────────────────────────────── */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {
    color: #2a2d35;
    border: none;
    background: #2a2d35;
    max-height: 1px;
}
"""
