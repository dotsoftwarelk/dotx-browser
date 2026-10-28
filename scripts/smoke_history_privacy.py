"""Exercise the history preference with actual WebEngine loads and a restart."""
import tempfile
from unittest.mock import patch
from PySide6.QtCore import QEventLoop, QStandardPaths, QTimer, QUrl
from PySide6.QtWidgets import QApplication, QCheckBox, QDialog, QPushButton
from dotx.__main__ import Browser
from dotx.core import load_data
import shiboken6

root = tempfile.mkdtemp(prefix='dotx-history-test-')
app = QApplication([])
app.setApplicationName('DOTX-history-test')
app.setOrganizationName('dotsoftwarelk-test')

def load(view, name):
    loop = QEventLoop()
    result = []
    def done(ok):
        result.append(ok)
        loop.quit()
    view.loadFinished.connect(done)
    QTimer.singleShot(10000, loop.quit)
    view.setHtml('<html><title>Privacy test</title><body>local test</body></html>', QUrl('https://example.invalid/' + name))
    loop.exec()
    view.loadFinished.disconnect(done)
    assert result == [True], result

def set_history(window, enabled):
    def change():
        dialog = next(x for x in app.topLevelWidgets() if isinstance(x, QDialog) and x.windowTitle() == 'Browser settings' and x.isVisible())
        next(c for c in dialog.findChildren(QCheckBox) if c.text() == 'Save browsing history on this device').setChecked(enabled)
        next(b for b in dialog.findChildren(QPushButton) if b.text() == 'Save settings').click()
    QTimer.singleShot(0, change)
    window.settings()

def destroy(window):
    profile = window.profile
    shiboken6.delete(window)
    shiboken6.delete(profile)

with patch.object(QStandardPaths, 'writableLocation', return_value=root):
    window = Browser()
    load(window.view(), 'before')
    assert [x['url'] for x in window.data['history']] == ['https://example.invalid/before']
    set_history(window, False)
    assert load_data(window.path)['history_enabled'] is False
    load(window.view(), 'disabled')
    assert [x['url'] for x in window.data['history']] == ['https://example.invalid/before']
    destroy(window)
    window = Browser()
    assert window.data['history_enabled'] is False
    load(window.view(), 'after-restart')
    assert [x['url'] for x in window.data['history']] == ['https://example.invalid/before']
    set_history(window, True)
    load(window.view(), 'enabled')
    assert [x['url'] for x in window.data['history']] == ['https://example.invalid/before', 'https://example.invalid/enabled']
    destroy(window)
    private = Browser(private=True)
    load(private.view(), 'private')
    assert private.data['history'] == []
    destroy(private)
print('PASS: history preference, actual page loads, persisted setting, restart and private window')
