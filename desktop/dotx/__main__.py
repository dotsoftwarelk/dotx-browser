import sys
from pathlib import Path
from PySide6.QtCore import QStandardPaths, Qt, QUrl
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QApplication, QComboBox, QFileDialog, QInputDialog, QLineEdit,
    QListWidget, QMainWindow, QMessageBox, QProgressBar, QTabWidget, QToolBar, QDialog,
    QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QMenu)
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PySide6.QtWebEngineWidgets import QWebEngineView
from .core import normalize_input, load_data, save_data, SEARCH

APP_NAME = 'DOTX Browser — development prototype'
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1200, 780)
        location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        self.root = Path(location)
        self.path = self.root / 'state.json'
        self.data = load_data(self.path)
        self.data.setdefault('bookmarks', [])
        self.data.setdefault('history', [])
        self.data.setdefault('search', 'DuckDuckGo')
        self.closed_tabs = []  # Session-only; never sent to a server.
        # Profile belongs to the application so pages are destroyed before the profile.
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
        self.action(bar, 'Workspace', self.workspace, None, 'Open workspace')
        self.action(bar, 'Settings', self.settings, None, 'Browser settings')
        tools = self.menuBar().addMenu('Tools')
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
        self.statusBar().showMessage('Ready')
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
        try: save_data(self.path, self.data)
        except OSError as e: self.statusBar().showMessage('Could not save browser data: ' + str(e), 8000)

    def view(self): return self.tabs.currentWidget()
    def new_tab(self, url='about:blank'):
        view = QWebEngineView()
        view.setPage(Page(self.profile, view))
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
        if ok and view.url().scheme() in ('http', 'https'):
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
        dialog.exec()
    def settings(self):
        choice, ok = QInputDialog.getItem(self, 'Search settings', 'Default search engine', list(SEARCH), list(SEARCH).index(self.data['search']) if self.data['search'] in SEARCH else 0, False)
        if ok: self.data['search'] = choice; self.save()
    def download(self, item):
        name, _ = QFileDialog.getSaveFileName(self, 'Save download', item.downloadFileName())
        if not name: item.cancel(); return
        path = Path(name)
        item.setDownloadDirectory(str(path.parent)); item.setDownloadFileName(path.name)
        item.isFinishedChanged.connect(lambda: self.statusBar().showMessage('Download finished or stopped — check your chosen destination.', 10000))
        item.accept()
        self.statusBar().showMessage('Download started', 5000)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('DOTX Browser')
    app.setOrganizationName('dotsoftwarelk')
    window = Browser(); window.show()
    return app.exec()

if __name__ == '__main__': sys.exit(main())
