"""Exercise actual bookmark, history and download empty/search states."""
import os, tempfile
from unittest.mock import patch
os.environ['XDG_DATA_HOME'] = tempfile.mkdtemp(prefix='dotx-empty-test-')
from PySide6.QtCore import QTimer, QStandardPaths
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QListWidget
from dotx.__main__ import Browser
import shiboken6
app = QApplication([]); app.setApplicationName('DOTX-empty-test'); app.setOrganizationName('dotsoftwarelk-test')
location = patch.object(QStandardPaths, 'writableLocation', return_value=os.environ['XDG_DATA_HOME'])
location.start()
w = Browser()
def check(title, expected, search=False):
    failures = []
    def run():
        d = next(x for x in app.topLevelWidgets() if isinstance(x, QDialog) and x.windowTitle() == title and x.isVisible())
        try:
            if search:
                d.findChild(QLineEdit).setText('no matching text')
            assert d.findChild(QListWidget).count() == 0
            assert any(x.text() == expected and x.isVisible() for x in d.findChildren(QLabel))
        except Exception as exc:
            failures.append(exc)
        finally:
            d.accept()
    QTimer.singleShot(0, run)
    {'Bookmarks': w.bookmarks, 'History': w.history, 'Downloads': w.download_manager}[title]()
    if failures: raise failures[0]
check('Bookmarks', 'No bookmarks yet.')
check('History', 'No history entries yet.')
check('Downloads', 'No downloads in this window yet.')
w.data['bookmarks'] = [{'title':'Example', 'url':'https://example.org/', 'folder':'Bookmarks'}]
w.data['history'] = [{'title':'Example', 'url':'https://example.org/'}]
check('Bookmarks', 'No matching bookmarks.', True)
check('History', 'No matching history entries.', True)
shiboken6.delete(w); location.stop()
print('PASS: empty bookmark, history, download and no-match filter states')
