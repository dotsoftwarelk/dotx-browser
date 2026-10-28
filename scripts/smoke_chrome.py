"""Check real chrome actions, history state, per-tab progress and narrow layout."""
import os
import tempfile
import threading
from unittest.mock import patch
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
os.environ['XDG_DATA_HOME'] = tempfile.mkdtemp(prefix='dotx-chrome-')
from PySide6.QtCore import QEventLoop, QTimer, QUrl, Qt, QStandardPaths
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QToolBar
from dotx.__main__ import Browser
import shiboken6

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data = ('<title>Local ' + self.path + '</title><p>DOTX chrome test</p>').encode()
        self.send_response(200); self.send_header('Content-Length', str(len(data))); self.end_headers()
        try: self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError): pass
    def log_message(self, *args): pass

server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
app = QApplication([]); app.setApplicationName('DOTX-chrome-test'); app.setOrganizationName('dotsoftwarelk-test')
location = patch.object(QStandardPaths, 'writableLocation', return_value=os.environ['XDG_DATA_HOME'])
location.start()
w = Browser(); w.show(); app.processEvents()

def wait_load(trigger):
    loop = QEventLoop(); done = []
    def completed(ok): done.append(ok); loop.quit()
    w.view().loadFinished.connect(completed)
    QTimer.singleShot(10000, loop.quit)
    trigger(); loop.exec(); w.view().loadFinished.disconnect(completed)
    assert done == [True], done
    app.processEvents()

base = f'http://127.0.0.1:{server.server_port}'
QTest.qWait(50)  # Allow the startup about:blank load to start.
if w.view().page().isLoading():
    loop = QEventLoop()
    w.view().loadFinished.connect(loop.quit)
    QTimer.singleShot(15000, loop.quit)
    loop.exec()
    w.view().loadFinished.disconnect(loop.quit)
    assert not w.view().page().isLoading(), 'startup page timed out'
assert not w.back_action.isEnabled() and not w.forward_action.isEnabled()
assert len(w.chrome_actions) == 10
bar = w.findChild(QToolBar)
for action in w.chrome_actions.values():
    assert not action.icon().isNull() and action.toolTip()
    assert bar.widgetForAction(action).accessibleName() == action.toolTip()
assert w.address.accessibleName() and w.progress.accessibleName()
wait_load(lambda: w.view().setUrl(QUrl(base + '/one')))
wait_load(lambda: w.view().setUrl(QUrl(base + '/two')))
assert w.back_action.isEnabled() and not w.forward_action.isEnabled()
wait_load(w.back)
assert w.forward_action.isEnabled() and w.view().url().path() == '/one'
assert w.connection_label.text() == 'HTTP' and w.connection_label.property('scheme') == 'http'
first = w.view(); w.title_changed(first, 'A very long title ' * 30)
assert len(w.tabs.tabToolTip(0)) == 512
second = w.new_tab(); app.processEvents()
assert not w.back_action.isEnabled() and not w.forward_action.isEnabled()
w.loading(first, 42); w.tabs.setCurrentWidget(first)
assert w.progress.isVisible() and w.progress.value() == 42
w.tabs.setCurrentWidget(second); assert not w.progress.isVisible()
w.tabs.setCurrentWidget(first)
for theme in ('light', 'dark', 'system'):
    w.data['appearance'] = theme; w.apply_theme(); app.processEvents()
    assert all(not a.icon().isNull() for a in w.chrome_actions.values())
for width in (1180, 760, 540):
    w.resize(width, 600); app.processEvents()
    assert w.address.isVisible() and w.address.width() >= 120
w.data['appearance'] = 'light'; w.apply_theme(); app.processEvents()
QTest.keyClick(w, Qt.Key.Key_L, Qt.KeyboardModifier.ControlModifier); app.processEvents()
assert w.address.hasFocus()
menus = w.menuBar().actions()
menu = menus[0].menu()
assert all(w.chrome_actions[name] in menu.actions() for name in ('bookmark', 'bookmarks', 'history', 'downloads', 'workspace', 'settings'))
server.shutdown(); shiboken6.delete(w); location.stop()
print('PASS: actual navigation actions, per-tab progress, icon accessibility, themes, Ctrl+L and narrow layout')
