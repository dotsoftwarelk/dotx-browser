"""Original lightweight line icons for DOTX chrome, rendered locally by Qt SVG."""
from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

# Each path uses a 24×24 viewBox and the same rounded stroke convention.
PATHS = {
    'back': '<path d="M15 5 8 12l7 7M8 12h12"/>',
    'forward': '<path d="m9 5 7 7-7 7M16 12H4"/>',
    'reload': '<path d="M20 7v5h-5M20 12a8 8 0 1 1-2-5.3L20 9"/>',
    'new_tab': '<path d="M12 5v14M5 12h14"/>',
    'bookmark': '<path d="M6 4h12v16l-6-4-6 4z"/>',
    'bookmarks': '<path d="M4 5h6a3 3 0 0 1 2 1 3 3 0 0 1 2-1h6v13h-6a3 3 0 0 0-2 1 3 3 0 0 0-2-1H4zM12 6v13"/>',
    'history': '<path d="M4 5v5h5M4 10a8 8 0 1 1 2 7M12 7v5l3 2"/>',
    'downloads': '<path d="M12 3v11m-4-4 4 4 4-4M5 16v3h14v-3"/>',
    'workspace': '<rect x="4" y="4" width="7" height="7" rx="1"/><rect x="13" y="4" width="7" height="7" rx="1"/><rect x="4" y="13" width="7" height="7" rx="1"/><rect x="13" y="13" width="7" height="7" rx="1"/>',
    'settings': '<circle cx="12" cy="12" r="3"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M18.4 5.6 17 7M7 17l-1.4 1.4"/><circle cx="12" cy="12" r="7"/>',
}

def _pixmap(name: str, color: str) -> QPixmap:
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{PATHS[name]}</svg>'
    renderer = QSvgRenderer(QByteArray(svg.encode('ascii')))
    image = QPixmap(24, 24)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    return image

def action_icon(name: str, foreground: str, disabled: str) -> QIcon:
    icon = QIcon()
    icon.addPixmap(_pixmap(name, foreground), QIcon.Mode.Normal)
    icon.addPixmap(_pixmap(name, disabled), QIcon.Mode.Disabled)
    return icon
