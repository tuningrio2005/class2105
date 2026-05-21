from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

class CaptureFrame(QWidget):
    geometry_changed = pyqtSignal(QRect)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(200, 200, 400, 300)
        self.border_width = 3
        self.drag = False
        self.resize_dir = None
        self.fps = 0
        self.fps_label = QLabel(self)
        self.fps_label.setStyleSheet('color: #6CFF63; background: rgba(0,0,0,0.5); border-radius: 6px; padding: 2px 6px;')
        self.fps_label.setFont(QFont('Segoe UI', 10))
        self.fps_label.move(8, 8)
        self.update_fps(0)

    def update_fps(self, fps):
        self.fps = fps
        self.fps_label.setText(f'FPS: {fps:.1f}')

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Transparent fill
        painter.fillRect(self.rect(), QColor(0, 0, 0, 40))
        # Neon green border
        pen = QPen(QColor('#6CFF63'), self.border_width)
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(self.border_width//2, self.border_width//2, -self.border_width, -self.border_width))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag = True
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.resize_dir = self._get_resize_dir(event.pos())

    def mouseMoveEvent(self, event):
        if self.drag:
            if self.resize_dir:
                self._resize(event.globalPosition().toPoint())
            else:
                self.move(event.globalPosition().toPoint() - self.drag_pos)
            self.geometry_changed.emit(self.geometry())

    def mouseReleaseEvent(self, event):
        self.drag = False
        self.resize_dir = None

    def _get_resize_dir(self, pos):
        margin = 12
        rect = self.rect()
        if pos.x() > rect.width() - margin and pos.y() > rect.height() - margin:
            return 'se'
        if pos.x() < margin and pos.y() > rect.height() - margin:
            return 'sw'
        if pos.x() > rect.width() - margin and pos.y() < margin:
            return 'ne'
        if pos.x() < margin and pos.y() < margin:
            return 'nw'
        return None

    def _resize(self, global_pos):
        g = self.geometry()
        min_w, min_h = 120, 90
        if self.resize_dir == 'se':
            w = max(min_w, global_pos.x() - g.x())
            h = max(min_h, global_pos.y() - g.y())
            self.setGeometry(g.x(), g.y(), w, h)
        elif self.resize_dir == 'sw':
            w = max(min_w, g.right() - global_pos.x())
            h = max(min_h, global_pos.y() - g.y())
            self.setGeometry(global_pos.x(), g.y(), w, h)
        elif self.resize_dir == 'ne':
            w = max(min_w, global_pos.x() - g.x())
            h = max(min_h, g.bottom() - global_pos.y())
            self.setGeometry(g.x(), global_pos.y(), w, h)
        elif self.resize_dir == 'nw':
            w = max(min_w, g.right() - global_pos.x())
            h = max(min_h, g.bottom() - global_pos.y())
            self.setGeometry(global_pos.x(), global_pos.y(), w, h)
