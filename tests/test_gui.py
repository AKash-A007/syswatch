import pytest
from unittest.mock import MagicMock, patch

# Optional GUI tests using PySide6 mechanics can go here.
# Since GUI testing without a screen in CI is flaky, we mock out the QApplication
# and only test basic initialization of dialogs if qt is available.
try:
    from PySide6.QtWidgets import QApplication
    from gui.settings_dialog import SettingsDialog
    from utils.config import AppConfig
    has_qt = True
except ImportError:
    has_qt = False

@pytest.fixture
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # don't quit app in between tests to prevent segfaults

@pytest.mark.skipif(not has_qt, reason="PySide6 not installed")
@patch('utils.config.AppConfig.save')
@patch('utils.config.AppConfig.load')
def test_settings_dialog_save(mock_load, mock_save, qapp):
    config = AppConfig() # creates a fresh mock AppConfig
    dialog = SettingsDialog(config)
    
    # Modify something in the UI
    dialog.api_host.setText("test.localhost")
    dialog.api_port.setValue(9090)
    dialog.use_https.setChecked(True)
    
    # Save settings
    dialog.save_settings()
    
    # Check config was updated
    assert config.get("api_host") == "test.localhost"
    assert config.get("api_port") == 9090
    assert config.get("use_https") is True
    
    # Assert save was called
    mock_save.assert_called()

@pytest.mark.skipif(not has_qt, reason="PySide6 not installed")
@patch('requests.get')
def test_settings_dialog_test_connection(mock_get, qapp):
    config = AppConfig()
    dialog = SettingsDialog(config)
    
    # Setup mock response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp
    
    # This shouldn't crash
    with patch('gui.settings_dialog.QMessageBox.information'):
        dialog.test_connection()
    
    mock_get.assert_called_once()
