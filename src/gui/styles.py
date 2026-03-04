# src/gui/styles.py
"""SysWatch Pro — Catppuccin Mocha dark theme and color helper functions."""


def get_status_color(status: str) -> str:
    """Return hex color for a service status string."""
    return {
        "healthy":  "#a6e3a1",
        "warning":  "#f9e2af",
        "critical": "#f38ba8",
        "unknown":  "#6c7086",
    }.get(status.lower(), "#6c7086")


def get_severity_color(severity: str) -> str:
    """Return hex color for an incident severity string."""
    return {
        "critical": "#f38ba8",
        "high":     "#fab387",
        "medium":   "#f9e2af",
        "low":      "#89b4fa",
        "info":     "#a6e3a1",
    }.get(severity.lower(), "#cdd6f4")


DARK_THEME = """
/* ============================================================
   SysWatch Pro — Catppuccin Mocha Dark Theme
   ============================================================ */

/* ── Global ─────────────────────────────────────────────────── */
* {
    font-family: "Segoe UI", "Inter", "Arial", sans-serif;
    font-size: 10pt;
    outline: none;
}

QMainWindow, QDialog, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

/* ── Menu Bar ────────────────────────────────────────────────── */
QMenuBar {
    background-color: #181825;
    color: #cdd6f4;
    border-bottom: 1px solid #313244;
    padding: 2px 0;
}
QMenuBar::item { padding: 4px 12px; border-radius: 4px; }
QMenuBar::item:selected { background-color: #313244; }
QMenuBar::item:pressed  { background-color: #45475a; }

QMenu {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item { padding: 6px 24px; border-radius: 4px; }
QMenu::item:selected  { background-color: #313244; color: #89b4fa; }
QMenu::separator { height: 1px; background: #313244; margin: 4px 8px; }

/* ── Status Bar ──────────────────────────────────────────────── */
QStatusBar {
    background-color: #181825;
    color: #a6adc8;
    border-top: 1px solid #313244;
    font-size: 9pt;
}

/* ── Tool Bar ────────────────────────────────────────────────── */
QToolBar {
    background-color: #181825;
    border: none;
    spacing: 4px;
    padding: 4px;
}

/* ── Group Box ───────────────────────────────────────────────── */
QGroupBox {
    color: #89b4fa;
    border: 1px solid #313244;
    border-radius: 8px;
    margin-top: 12px;
    padding: 12px 8px 8px 8px;
    font-weight: bold;
    font-size: 10pt;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: -6px;
    padding: 0 6px;
    background-color: #1e1e2e;
}

/* ── Labels ──────────────────────────────────────────────────── */
QLabel { color: #cdd6f4; }
QLabel[heading="true"] {
    font-size: 13pt;
    font-weight: bold;
    color: #cba6f7;
    padding: 4px 0;
}
QLabel[subheading="true"] {
    font-size: 11pt;
    font-weight: bold;
    color: #89b4fa;
}

/* ── Push Buttons ────────────────────────────────────────────── */
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 10pt;
}
QPushButton:hover   { background-color: #45475a; border-color: #89b4fa; }
QPushButton:pressed { background-color: #585b70; }
QPushButton:disabled { color: #6c7086; background-color: #262637; border-color: #313244; }
QPushButton:checked { background-color: #89b4fa; color: #1e1e2e; border-color: #89b4fa; }

QPushButton[success="true"] {
    background-color: #a6e3a1; color: #1e1e2e; border-color: #a6e3a1; font-weight: bold;
}
QPushButton[success="true"]:hover { background-color: #c0efba; }

QPushButton[danger="true"] {
    background-color: #f38ba8; color: #1e1e2e; border-color: #f38ba8; font-weight: bold;
}
QPushButton[danger="true"]:hover { background-color: #f7a8bc; }

/* ── Line Edit / Spin Box ────────────────────────────────────── */
QLineEdit, QSpinBox, QDoubleSpinBox {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 5px 8px;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #89b4fa;
}
QSpinBox::up-button, QSpinBox::down-button {
    background-color: #313244;
    border: none;
    border-radius: 3px;
    width: 16px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover { background-color: #45475a; }

/* ── Combo Box ───────────────────────────────────────────────── */
QComboBox {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 5px 8px;
    min-width: 80px;
}
QComboBox:hover   { border-color: #89b4fa; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #cdd6f4;
    margin-right: 6px;
}
QComboBox QAbstractItemView {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    selection-background-color: #313244;
    selection-color: #89b4fa;
}

/* ── Check Box ───────────────────────────────────────────────── */
QCheckBox { color: #cdd6f4; spacing: 8px; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 2px solid #45475a;
    border-radius: 4px;
    background-color: #181825;
}
QCheckBox::indicator:checked { background-color: #89b4fa; border-color: #89b4fa; }
QCheckBox::indicator:hover   { border-color: #cba6f7; }

/* ── Tab Widget ──────────────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #313244;
    border-radius: 6px;
    background-color: #1e1e2e;
}
QTabBar::tab {
    background-color: #181825;
    color: #a6adc8;
    border: 1px solid #313244;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 6px 16px;
    margin-right: 2px;
}
QTabBar::tab:selected { background-color: #313244; color: #cba6f7; font-weight: bold; }
QTabBar::tab:hover    { background-color: #2a2a3e; color: #cdd6f4; }

/* ── List Widget ─────────────────────────────────────────────── */
QListWidget {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 6px;
    alternate-background-color: #1a1a2a;
    outline: none;
}
QListWidget::item { padding: 4px 8px; border-radius: 4px; }
QListWidget::item:selected { background-color: #313244; color: #89b4fa; }
QListWidget::item:hover    { background-color: #262637; }

/* ── Table Widget ────────────────────────────────────────────── */
QTableWidget {
    background-color: #181825;
    alternate-background-color: #1a1a2a;
    gridline-color: #313244;
    border: 1px solid #313244;
    border-radius: 6px;
    outline: none;
}
QTableWidget::item { padding: 4px 8px; }
QTableWidget::item:selected { background-color: #313244; color: #89b4fa; }

QHeaderView::section {
    background-color: #24243a;
    color: #89b4fa;
    border: none;
    border-right: 1px solid #313244;
    border-bottom: 1px solid #313244;
    padding: 6px 10px;
    font-weight: bold;
}
QHeaderView::section:first { border-top-left-radius: 6px; }
QHeaderView::section:last  { border-top-right-radius: 6px; border-right: none; }

/* ── Scroll Bar ──────────────────────────────────────────────── */
QScrollBar:vertical {
    background: #1e1e2e;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #585b70; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background: #1e1e2e;
    height: 10px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background: #45475a;
    border-radius: 5px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover { background: #585b70; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Progress Bar ────────────────────────────────────────────── */
QProgressBar {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 6px;
    height: 18px;
    text-align: center;
    color: #cdd6f4;
    font-size: 9pt;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #89b4fa, stop:1 #cba6f7);
    border-radius: 5px;
}

/* ── Text Edit ───────────────────────────────────────────────── */
QTextEdit {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 6px;
    selection-background-color: #313244;
}
QTextEdit:focus { border-color: #89b4fa; }

/* ── Splitter ────────────────────────────────────────────────── */
QSplitter::handle {
    background-color: #313244;
}
QSplitter::handle:horizontal { width: 4px;  }
QSplitter::handle:vertical   { height: 4px; }
QSplitter::handle:hover { background-color: #89b4fa; }

/* ── Dialog ──────────────────────────────────────────────────── */
QDialog {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 8px;
}

/* ── Tooltip ─────────────────────────────────────────────────── */
QToolTip {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 9pt;
}

/* ── Status badge helpers ────────────────────────────────────── */
QLabel[status="healthy"]  { background-color: #a6e3a1; color: #1e1e2e; border-radius: 4px; padding: 2px 6px; font-weight: bold; }
QLabel[status="warning"]  { background-color: #f9e2af; color: #1e1e2e; border-radius: 4px; padding: 2px 6px; font-weight: bold; }
QLabel[status="critical"] { background-color: #f38ba8; color: #1e1e2e; border-radius: 4px; padding: 2px 6px; font-weight: bold; }
QLabel[status="unknown"]  { background-color: #6c7086; color: #1e1e2e; border-radius: 4px; padding: 2px 6px; font-weight: bold; }
"""
