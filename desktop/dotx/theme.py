"""Desktop appearance tokens. Websites themselves are not restyled."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

PALETTES = {
    'dark': {'window':'#101928','surface':'#17263a','field':'#202f45','text':'#edf5ff',
             'muted':'#b5c6d9','border':'#344963','button':'#22344c','hover':'#304b69',
             'tab':'#19283a','selected':'#304963','accent':'#89d7f7'},
    'light': {'window':'#eef3f8','surface':'#ffffff','field':'#ffffff','text':'#1a293b',
              'muted':'#40566d','border':'#bdcbd9','button':'#f3f7fb','hover':'#dfeaf4',
              'tab':'#dfe8f1','selected':'#ffffff','accent':'#156385'},
}

def resolve_theme(choice: str, system_scheme=None) -> str:
    if choice in PALETTES: return choice
    if system_scheme is None:
        system_scheme = QApplication.styleHints().colorScheme()
    return 'light' if system_scheme == Qt.ColorScheme.Light else 'dark'

def stylesheet(choice: str) -> str:
    p = PALETTES[resolve_theme(choice)]
    return f'''
    QMainWindow, QDialog {{ background: {p['window']}; color: {p['text']}; }}
    QMenuBar, QStatusBar {{ background: {p['surface']}; color: {p['text']}; }}
    QMenuBar::item {{ padding: 4px 10px; background: transparent; }}
    QMenuBar::item:selected, QMenu::item:selected {{ background: {p['hover']}; color: {p['text']}; }}
    QMenu {{ background: {p['surface']}; color: {p['text']}; border: 1px solid {p['border']}; }}
    QMenu::item {{ padding: 6px 24px; }}
    QToolBar {{ background: {p['surface']}; border: 0; padding: 8px; spacing: 5px; }}
    QLineEdit, QListWidget, QComboBox {{ background: {p['field']}; color: {p['text']}; border: 1px solid {p['border']}; border-radius: 6px; padding: 7px; }}
    QToolButton, QPushButton {{ color: {p['text']}; background: {p['button']}; border: 1px solid {p['border']}; border-radius: 6px; padding: 7px; }}
    QToolButton:hover, QPushButton:hover {{ background: {p['hover']}; }}
    QToolButton:disabled, QPushButton:disabled {{ color: {p['muted']}; }}
    QTabWidget::pane {{ border: 0; }}
    QTabBar::tab {{ background: {p['tab']}; color: {p['muted']}; padding: 10px 18px; min-width: 100px; }}
    QTabBar::tab:selected {{ background: {p['selected']}; color: {p['text']}; }}
    QLabel, QCheckBox {{ color: {p['text']}; }}
    QProgressBar {{ background: {p['field']}; color: {p['text']}; border: 1px solid {p['border']}; border-radius: 4px; text-align: center; }}
    QProgressBar::chunk {{ background: {p['accent']}; }}
    '''
