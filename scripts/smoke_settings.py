"""Exercise actual settings dialog and opt-in behavior without an external network."""
import tempfile
from unittest.mock import patch
from PySide6.QtCore import QStandardPaths, QTimer, QUrl
from PySide6.QtWidgets import QApplication,QDialog,QComboBox,QCheckBox,QPushButton
from dotx.__main__ import Browser
from dotx.core import load_data
import shiboken6
root=tempfile.mkdtemp(prefix='dotx-settings-')
app=QApplication([]);app.setApplicationName('DOTX-settings-test');app.setOrganizationName('dotsoftwarelk-test')
with patch.object(QStandardPaths,'writableLocation',return_value=root):
    w=Browser();w.view().setUrl(QUrl('http://example.invalid/'))
    assert w.connection_label.text() == 'HTTP'
    def modify(restore):
        dialog=next(x for x in app.topLevelWidgets() if isinstance(x,QDialog) and x.windowTitle()=='Browser settings' and x.isVisible())
        combos = dialog.findChildren(QComboBox)
        combos[0].setCurrentText('Google')
        combos[1].setCurrentText('Light')
        dialog.findChild(QCheckBox).setChecked(restore)
        next(x for x in dialog.findChildren(QPushButton) if x.text()=='Save settings').click()
    QTimer.singleShot(0,lambda:modify(True));w.settings()
    stored=load_data(w.path)
    assert stored['search']=='Google' and stored['restore_tabs'] is True and stored['appearance']=='light'
    assert '#eef3f8' in w.styleSheet()
    assert stored['session_urls']==['http://example.invalid/']
    QTimer.singleShot(0,lambda:modify(False));w.settings()
    stored=load_data(w.path)
    assert stored['restore_tabs'] is False and stored['session_urls']==[]
    profile=w.profile;shiboken6.delete(w);shiboken6.delete(profile)
print('PASS: settings dialog, appearance, search selection, opt-in and deletion of saved session list')
