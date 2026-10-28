import sys
from pathlib import Path
from PySide6.QtCore import QStandardPaths, Qt, QUrl, QTimer
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QApplication, QComboBox, QFileDialog, QInputDialog, QLineEdit,
    QListWidget, QMainWindow, QMessageBox, QProgressBar, QTabWidget, QToolBar, QDialog,
    QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QMenu)
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineDownloadRequest
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from .services.github import search_url, parse_results, error_message
from .core import normalize_input, load_data, save_data, validated_state, SEARCH

APP_NAME = 'DOTX Browser — development prototype'
OPEN_WINDOWS = []
PROVIDERS = {
    'Dropbox': 'https://www.dropbox.com/', 'Google Docs': 'https://docs.google.com/',
    'Google Drive': 'https://drive.google.com/', 'Linear': 'https://linear.app/',
    'Notion': 'https://www.notion.so/', 'GitHub': 'https://github.com/',
    'Supabase': 'https://supabase.com/dashboard/',
}

class Page(QWebEnginePage):
    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        # Do not silently invoke external applications or expose local files to arbitrary web pages.
        return url.scheme().lower() in ('http', 'https', 'about', 'data', 'blob')

class Browser(QMainWindow):
    def __init__(self, private=False):
        super().__init__()
        self.private = private
        self.setWindowTitle(APP_NAME + (' — Private window' if private else ''))
        self.resize(1200, 780)
        location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        self.root = Path(location)
        self.path = self.root / 'state.json'
        self.data = validated_state({} if private else load_data(self.path))
        self.closed_tabs = []  # Session-only; never sent to a server.
        self.downloads = []
        self.download_refresh = None
        # Profile belongs to the application so pages are destroyed before the profile.
        if private:
            # An unnamed WebEngine profile is off-the-record; it does not persist cookies/cache.
            self.profile = QWebEngineProfile(QApplication.instance())
            # Delete the transient profile after its window and pages are destroyed.
            self.destroyed.connect(self.profile.deleteLater)
        else:
            self.profile = QWebEngineProfile('dotx', QApplication.instance())
            self.profile.setPersistentStoragePath(str(self.root / 'web'))
            self.profile.setCachePath(str(self.root / 'cache'))
        self.profile.downloadRequested.connect(self.download)
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.sync)
        self.tabs.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs.tabBar().customContextMenuRequested.connect(self.tab_menu)
        self.setCentralWidget(self.tabs)
        bar = QToolBar('Navigation')
        bar.setMovable(False)
        self.addToolBar(bar)
        self.action(bar, '←', self.back, 'Alt+Left', 'Back')
        self.action(bar, '→', self.forward, 'Alt+Right', 'Forward')
        self.action(bar, '↻', self.reload, 'Ctrl+R', 'Reload')
        self.action(bar, '＋', self.new_tab, 'Ctrl+T', 'New tab')
        self.address = QLineEdit()
        self.address.setPlaceholderText('Search or enter an address')
        self.address.returnPressed.connect(self.navigate)
        bar.addWidget(self.address)
        self.action(bar, '☆', self.bookmark, 'Ctrl+D', 'Bookmark this page')
        self.action(bar, 'Bookmarks', self.bookmarks, None, 'Open bookmarks')
        self.action(bar, 'History', self.history, 'Ctrl+H', 'Open history')
        self.action(bar, 'Downloads', self.download_manager, 'Ctrl+J', 'Open downloads')
        self.action(bar, 'Workspace', self.workspace, None, 'Open workspace')
        self.action(bar, 'Settings', self.settings, None, 'Browser settings')
        tools = self.menuBar().addMenu('Tools')
        self.menu_action(tools, 'New private window', self.open_private_window, 'Ctrl+Shift+N')
        self.menu_action(tools, 'Focus address bar', self.focus_address, 'Ctrl+L')
        self.menu_action(tools, 'Close tab', lambda: self.close_tab(self.tabs.currentIndex()), 'Ctrl+W')
        self.menu_action(tools, 'Reopen closed tab', self.reopen_closed, 'Ctrl+Shift+T')
        self.menu_action(tools, 'Duplicate tab', self.duplicate_tab)
        tools.addSeparator()
        self.menu_action(tools, 'Find in page', self.find_in_page, 'Ctrl+F')
        self.menu_action(tools, 'Zoom in', lambda: self.zoom(0.1), 'Ctrl++')
        self.menu_action(tools, 'Zoom out', lambda: self.zoom(-0.1), 'Ctrl+-')
        self.menu_action(tools, 'Reset zoom', self.reset_zoom, 'Ctrl+0')
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(100)
        self.progress.hide()
        self.statusBar().addPermanentWidget(self.progress)
        self.statusBar().showMessage('Private window: browsing history is not saved; downloads remain on disk.' if private else 'Ready')
        self.setStyleSheet('''QMainWindow,QDialog {background:#101928;color:#e8efff} QToolBar {background:#141f31;border:0;padding:9px;spacing:6px} QLineEdit {background:#202f45;color:white;border:1px solid #344963;border-radius:8px;padding:8px} QToolButton,QPushButton {color:#dce9ff;background:#22344c;border:1px solid #314761;border-radius:6px;padding:7px} QToolButton:hover,QPushButton:hover {background:#304b69} QTabWidget::pane {border:0} QTabBar::tab {background:#19283a;color:#bacbe2;padding:10px 18px;min-width:100px} QTabBar::tab:selected {background:#2b405a;color:white} QListWidget,QComboBox {background:#202f45;color:white;border:1px solid #344963;padding:6px} QLabel {color:#e8efff}''')
        self.new_tab()

    def action(self, toolbar, text, handler, shortcut, tooltip):
        a = QAction(text, self)
        a.setToolTip(tooltip)
        if shortcut: a.setShortcut(QKeySequence(shortcut))
        a.triggered.connect(lambda checked=False: handler())
        toolbar.addAction(a)
        return a

    def menu_action(self, menu, label, handler, shortcut=None):
        action = QAction(label, self)
        if shortcut: action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(lambda checked=False: handler())
        menu.addAction(action)
        return action

    def open_private_window(self):
        window = Browser(private=True)
        window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        OPEN_WINDOWS.append(window)
        window.destroyed.connect(lambda: OPEN_WINDOWS.remove(window) if window in OPEN_WINDOWS else None)
        window.show()

    def focus_address(self):
        self.address.setFocus()
        self.address.selectAll()

    def find_in_page(self):
        text, ok = QInputDialog.getText(self, 'Find in page', 'Find text:')
        if ok: self.view().findText(text)

    def zoom(self, amount):
        view = self.view()
        view.setZoomFactor(max(0.25, min(5.0, round(view.zoomFactor() + amount, 2))))
        self.statusBar().showMessage(f'Zoom: {round(view.zoomFactor() * 100)}%', 2500)

    def reset_zoom(self):
        self.view().setZoomFactor(1.0)
        self.statusBar().showMessage('Zoom: 100%', 2500)

    def duplicate_tab(self, index=None):
        view = self.tabs.widget(self.tabs.currentIndex() if index is None else index)
        if view: self.new_tab(view.url().toString() or 'about:blank')

    def reopen_closed(self):
        if self.closed_tabs: self.new_tab(self.closed_tabs.pop())
        else: self.statusBar().showMessage('No recently closed tabs', 2500)

    def tab_menu(self, position):
        index = self.tabs.tabBar().tabAt(position)
        if index < 0: return
        menu = QMenu(self)
        menu.addAction('Duplicate tab', lambda: self.duplicate_tab(index))
        menu.addAction('Close tab', lambda: self.close_tab(index))
        menu.addAction('Reopen closed tab', self.reopen_closed)
        menu.exec(self.tabs.tabBar().mapToGlobal(position))

    def save(self):
        if self.private: return
        try: save_data(self.path, self.data)
        except OSError as e: self.statusBar().showMessage('Could not save browser data: ' + str(e), 8000)

    def view(self): return self.tabs.currentWidget()
    def new_tab(self, url='about:blank'):
        view = QWebEngineView()
        view.setPage(Page(self.profile, view))
        # Default deny until a reviewed, per-origin permission UI exists.
        view.page().permissionRequested.connect(lambda permission: permission.deny())
        i = self.tabs.addTab(view, 'New tab')
        self.tabs.setCurrentIndex(i)
        view.titleChanged.connect(lambda title, v=view: self.title_changed(v, title))
        view.iconChanged.connect(lambda icon, v=view: self.tabs.setTabIcon(self.tabs.indexOf(v), icon) if self.tabs.indexOf(v) >= 0 else None)
        view.urlChanged.connect(lambda u, v=view: self.url_changed(v, u))
        view.loadProgress.connect(lambda p, v=view: self.loading(v, p))
        view.loadFinished.connect(lambda ok, v=view: self.finished(v, ok))
        view.setUrl(QUrl(url))
        return view
    def close_tab(self, index):
        widget = self.tabs.widget(index)
        if widget and widget.url().scheme() in ('http', 'https'):
            self.closed_tabs.append(widget.url().toString())
            self.closed_tabs = self.closed_tabs[-20:]
        self.tabs.removeTab(index)
        if widget: widget.deleteLater()
        if self.tabs.count() == 0: self.new_tab()
    def title_changed(self, view, title):
        i = self.tabs.indexOf(view)
        if i >= 0: self.tabs.setTabText(i, (title or 'New tab')[:35])
    def url_changed(self, view, url):
        if view == self.view(): self.address.setText('' if url.toString() == 'about:blank' else url.toString())
    def loading(self, view, progress):
        if view == self.view():
            self.progress.setValue(progress)
            self.progress.setVisible(progress < 100)
    def finished(self, view, ok):
        url = view.url().toString()
        if not self.private and ok and view.url().scheme() in ('http', 'https'):
            self.data['history'].append({'title': view.title() or url, 'url': url})
            self.data['history'] = self.data['history'][-1000:]
            self.save()
        if view == self.view(): self.statusBar().showMessage('Loaded' if ok else 'Page could not be loaded', 5000)
    def sync(self, index):
        if self.view(): self.url_changed(self.view(), self.view().url())
    def navigate(self):
        try: self.view().setUrl(QUrl(normalize_input(self.address.text(), self.data['search'])))
        except ValueError as e: QMessageBox.warning(self, 'Invalid address', str(e))
    def back(self): self.view().back()
    def forward(self): self.view().forward()
    def reload(self): self.view().reload()
    def bookmark(self):
        if self.private:
            self.statusBar().showMessage('Bookmarks are unavailable in private windows', 5000)
            return
        url = self.view().url().toString()
        if self.view().url().scheme() not in ('http', 'https'): return
        if not any(x.get('url') == url for x in self.data['bookmarks']):
            self.data['bookmarks'].append({'title': self.view().title() or url, 'url': url})
            self.save()
        self.statusBar().showMessage('Bookmark saved', 3000)
    def collection(self, key, title):
        dialog = QDialog(self); dialog.setWindowTitle(title); dialog.resize(620, 430)
        layout = QVBoxLayout(dialog)
        search = QLineEdit(); search.setPlaceholderText('Filter by title or address'); layout.addWidget(search)
        listing = QListWidget(); layout.addWidget(listing)
        def populate():
            listing.clear()
            for x in reversed(self.data[key]):
                if search.text().lower() in (x.get('title', '') + x.get('url', '')).lower():
                    from PySide6.QtWidgets import QListWidgetItem
                    item = QListWidgetItem(x.get('title', '') + '\n' + x.get('url', ''))
                    item.setData(Qt.ItemDataRole.UserRole, x)
                    listing.addItem(item)
        def open_item(item):
            self.new_tab(item.data(Qt.ItemDataRole.UserRole)['url']); dialog.accept()
        def remove():
            item = listing.currentItem()
            if item:
                self.data[key].remove(item.data(Qt.ItemDataRole.UserRole)); self.save(); populate()
        search.textChanged.connect(populate); listing.itemDoubleClicked.connect(open_item)
        buttons = QHBoxLayout(); delete = QPushButton('Delete selected'); delete.clicked.connect(remove); buttons.addWidget(delete)
        if key == 'history':
            clear = QPushButton('Clear history')
            def clear_history():
                if QMessageBox.question(dialog, 'Clear history', 'Delete all saved history?') == QMessageBox.StandardButton.Yes:
                    self.data['history'] = []; self.save(); populate()
            clear.clicked.connect(clear_history); buttons.addWidget(clear)
        layout.addLayout(buttons); populate(); dialog.exec()
    def bookmarks(self): self.collection('bookmarks', 'Bookmarks')
    def history(self): self.collection('history', 'History')
    def workspace(self):
        dialog = QDialog(self); dialog.setWindowTitle('Workspace'); dialog.resize(460, 460)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel('WORKSPACE  /  QUICK LAUNCH'))
        text = QLabel('Open a service in a new tab. These are web links, not connected API accounts. Sign in on each provider’s own website.')
        text.setWordWrap(True); layout.addWidget(text)
        for name, url in PROVIDERS.items():
            button = QPushButton(name + '  ↗')
            button.clicked.connect(lambda checked=False, u=url: (self.new_tab(u), dialog.accept()))
            layout.addWidget(button)
        github = QPushButton('Search public GitHub repositories…')
        github.clicked.connect(lambda: (dialog.accept(), self.github_search()))
        layout.addWidget(github)
        dialog.exec()
    def github_search(self):
        dialog = QDialog(self); dialog.setWindowTitle('GitHub public search'); dialog.resize(680, 500)
        layout = QVBoxLayout(dialog)
        note = QLabel('Search public GitHub repositories without signing in. Your query and IP address are sent to GitHub; results are subject to GitHub rate limits.')
        note.setWordWrap(True); layout.addWidget(note)
        form = QHBoxLayout(); query = QLineEdit(); query.setPlaceholderText('Search public repositories')
        search = QPushButton('Search'); form.addWidget(query); form.addWidget(search); layout.addLayout(form)
        status = QLabel('Enter a search term. No account is connected.'); status.setWordWrap(True); layout.addWidget(status)
        results = QListWidget(); layout.addWidget(results)
        manager = QNetworkAccessManager(dialog)
        active = {'reply': None}
        def start():
            try: url = search_url(query.text())
            except ValueError as e: status.setText(str(e)); return
            if active['reply'] is not None: return
            results.clear(); status.setText('Searching GitHub…'); search.setEnabled(False)
            req = QNetworkRequest(QUrl(url))
            req.setRawHeader(b'Accept', b'application/vnd.github+json')
            req.setRawHeader(b'X-GitHub-Api-Version', b'2022-11-28')
            req.setRawHeader(b'User-Agent', b'DOTX-Browser-development')
            req.setTransferTimeout(15000)
            reply = manager.get(req); active['reply'] = reply
            def done():
                active['reply'] = None; search.setEnabled(True)
                code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute) or 0
                if reply.error() != QNetworkReply.NetworkError.NoError or code != 200:
                    remaining = bytes(reply.rawHeader(b'X-RateLimit-Remaining'))
                    status.setText(error_message(int(code), remaining == b'0' or reply.hasRawHeader(b'Retry-After')))
                else:
                    try:
                        data = parse_results(bytes(reply.readAll()))
                        from PySide6.QtWidgets import QListWidgetItem
                        for repo in data:
                            item = QListWidgetItem(f'{repo.full_name}  ·  {repo.stars:,} stars\n{repo.description}')
                            item.setData(Qt.ItemDataRole.UserRole, repo.html_url); results.addItem(item)
                        status.setText(f'{len(data)} public repositories found. Double-click a result to open it.' if data else 'No public repositories found.')
                    except ValueError as e: status.setText(str(e))
                reply.deleteLater()
            reply.finished.connect(done)
        def open_result(item):
            self.new_tab(item.data(Qt.ItemDataRole.UserRole)); dialog.accept()
        search.clicked.connect(start); query.returnPressed.connect(start); results.itemDoubleClicked.connect(open_result)
        dialog.exec()
        if active['reply'] is not None: active['reply'].abort()
    def settings(self):
        choice, ok = QInputDialog.getItem(self, 'Search settings', 'Default search engine', list(SEARCH), list(SEARCH).index(self.data['search']) if self.data['search'] in SEARCH else 0, False)
        if ok: self.data['search'] = choice; self.save()
    def download_manager(self):
        dialog = QDialog(self); dialog.setWindowTitle('Downloads'); dialog.resize(640, 400)
        layout = QVBoxLayout(dialog)
        note = QLabel('Downloads remain on disk, including downloads from private windows. Open files from your chosen folder.')
        note.setWordWrap(True); layout.addWidget(note)
        listing = QListWidget(); layout.addWidget(listing)
        def refresh():
            selected = listing.currentRow()
            listing.clear()
            for entry in self.downloads:
                req = entry['request']
                state = req.state()
                states = QWebEngineDownloadRequest.DownloadState
                if state == states.DownloadInProgress:
                    text = 'Paused' if req.isPaused() else 'Downloading'
                elif state == states.DownloadCompleted: text = 'Completed'
                elif state == states.DownloadCancelled: text = 'Cancelled'
                elif state == states.DownloadInterrupted: text = 'Failed: ' + req.interruptReasonString()
                else: text = 'Preparing'
                received, total = req.receivedBytes(), req.totalBytes()
                progress = f'{received:,} / {total:,} bytes' if total > 0 else f'{received:,} bytes'
                listing.addItem(f"{entry['path'].name} — {text} — {progress}\n{entry['path'].parent}")
            if 0 <= selected < listing.count(): listing.setCurrentRow(selected)
        def perform(action):
            row = listing.currentRow()
            if 0 <= row < len(self.downloads):
                req = self.downloads[row]['request']
                if req.state() == QWebEngineDownloadRequest.DownloadState.DownloadInProgress:
                    getattr(req, action)()
                    refresh()
        controls = QHBoxLayout()
        for label, action in [('Pause', 'pause'), ('Resume', 'resume'), ('Cancel', 'cancel')]:
            button = QPushButton(label)
            button.clicked.connect(lambda checked=False, name=action: perform(name))
            controls.addWidget(button)
        layout.addLayout(controls)
        self.download_refresh = refresh
        refresh()
        dialog.exec()
        self.download_refresh = None

    def update_downloads(self):
        if self.download_refresh: self.download_refresh()

    def download(self, item):
        name, _ = QFileDialog.getSaveFileName(self, 'Save download', item.downloadFileName())
        if not name: item.cancel(); return
        path = Path(name)
        item.setDownloadDirectory(str(path.parent)); item.setDownloadFileName(path.name)
        self.downloads.append({'request': item, 'path': path})
        item.receivedBytesChanged.connect(self.update_downloads)
        item.totalBytesChanged.connect(self.update_downloads)
        item.stateChanged.connect(self.update_downloads)
        item.isPausedChanged.connect(self.update_downloads)
        item.isFinishedChanged.connect(lambda: self.statusBar().showMessage('Download finished or stopped — open Downloads for details.', 10000))
        item.accept()
        self.update_downloads()
        self.statusBar().showMessage('Download started', 5000)

def main():
    smoke = '--smoke-test' in sys.argv
    app = QApplication([sys.argv[0]] if smoke else sys.argv)
    app.setApplicationName('DOTX Browser')
    app.setOrganizationName('dotsoftwarelk')
    window = Browser(); window.show()
    if smoke:
        window.view().loadFinished.connect(lambda ok: app.exit(0 if ok else 1))
        QTimer.singleShot(15000, lambda: app.exit(2))
        window.view().setHtml('<html><title>DOTX smoke test</title><body>Ready</body></html>')
    return app.exec()

if __name__ == '__main__': sys.exit(main())
