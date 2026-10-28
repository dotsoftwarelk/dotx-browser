"""Headless test of opt-in tab persistence and restart, with an isolated data directory."""
import tempfile
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QStandardPaths, QUrl
from PySide6.QtWidgets import QApplication
from dotx.__main__ import Browser
from dotx.core import load_data
import shiboken6

root = tempfile.mkdtemp(prefix='dotx-session-')
app = QApplication([]); app.setOrganizationName('dotsoftwarelk-test'); app.setApplicationName('DOTX-session-test')
with patch.object(QStandardPaths, 'writableLocation', return_value=root):
    w = Browser()
    # The default never records a session, even after navigation.
    w.view().setUrl(QUrl('https://example.org/one'))
    w.persist_session()
    assert not Path(root, 'state.json').exists()
    w.data['restore_tabs'] = True
    w.new_tab('https://example.org/two')
    w.persist_session()
    saved = load_data(Path(root, 'state.json'))
    assert saved['session_urls'] == ['https://example.org/one', 'https://example.org/two']
    profile = w.profile
    shiboken6.delete(w)
    shiboken6.delete(profile)
    w2 = Browser()
    assert w2.tabs.count() == 2
    assert [w2.tabs.widget(i).url().toString() for i in range(2)] == saved['session_urls']
    private = Browser(private=True)
    assert private.tabs.count() == 1
    assert not private.data['restore_tabs'] and private.data['session_urls'] == []
    private.data['restore_tabs'] = True
    private.view().setUrl(QUrl('https://private.example/'))
    private.persist_session()
    assert load_data(Path(root, 'state.json'))['session_urls'] == saved['session_urls']
    profile2 = w2.profile
    shiboken6.delete(private); shiboken6.delete(w2); shiboken6.delete(profile2)
print('PASS: opt-in session persistence and restart; private profile excluded')
