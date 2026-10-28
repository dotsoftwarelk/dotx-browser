"""Exercise bookmark edit, folders and JSON export/import through the real dialogs."""
import json,tempfile
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QStandardPaths,QTimer,QUrl
from PySide6.QtWidgets import QApplication,QDialog,QListWidget,QPushButton,QInputDialog,QFileDialog,QMessageBox
from dotx.__main__ import Browser
import shiboken6
root=tempfile.mkdtemp(prefix='dotx-bookmarks-'); exported=Path(root)/'export.json'
app=QApplication([]);app.setOrganizationName('dotsoftwarelk-test');app.setApplicationName('DOTX-bookmarks-test')
with patch.object(QStandardPaths,'writableLocation',return_value=root):
    w=Browser();w.view().setUrl(QUrl('https://example.org/'));w.bookmark()
    def interact():
        d=next(x for x in app.topLevelWidgets() if isinstance(x,QDialog) and x.windowTitle()=='Bookmarks' and x.isVisible())
        d.findChild(QListWidget).setCurrentRow(0)
        next(b for b in d.findChildren(QPushButton) if b.text()=='Edit selected').click()
        next(b for b in d.findChildren(QPushButton) if b.text()=='Export JSON…').click()
        w.data['bookmarks']=[]
        next(b for b in d.findChildren(QPushButton) if b.text()=='Import JSON…').click()
        d.accept()
    with patch.object(QInputDialog,'getText',side_effect=[('Example',True),('https://example.org/',True),('Work',True)]), \
         patch.object(QFileDialog,'getSaveFileName',return_value=(str(exported),'')), \
         patch.object(QFileDialog,'getOpenFileName',return_value=(str(exported),'')), \
         patch.object(QMessageBox,'information',return_value=QMessageBox.StandardButton.Ok):
        QTimer.singleShot(0,interact);w.bookmarks()
    data=json.loads(exported.read_text(encoding='utf-8'))
    assert data['bookmarks'][0]['folder']=='Work'
    assert w.data['bookmarks']==data['bookmarks']
    profile=w.profile;shiboken6.delete(w);shiboken6.delete(profile)
print('PASS: bookmark edit, folder, JSON export and import')
