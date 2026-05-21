from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
import os

class ControlPanel(QWidget):
    start_detection = pyqtSignal(list)
    stop_detection = pyqtSignal()
    open_captured = pyqtSignal()
    mute_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Screen Object Detector')
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedWidth(320)
        self.setStyleSheet(self._dark_style())
        self._build_ui()
        self.is_running = False
        self.counters = {}

    def _build_ui(self):
        layout = QVBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText('person, cup, phone')
        layout.addWidget(QLabel('Target objects (comma separated):'))
        layout.addWidget(self.input)

        btn_layout = QHBoxLayout()
        self.toggle_btn = QPushButton('Start Detection')
        self.toggle_btn.clicked.connect(self._toggle)
        btn_layout.addWidget(self.toggle_btn)
        self.status = QLabel()
        self._set_status(False)
        btn_layout.addWidget(self.status)
        layout.addLayout(btn_layout)

        self.counter_panel = QTextEdit()
        self.counter_panel.setReadOnly(True)
        self.counter_panel.setFixedHeight(80)
        layout.addWidget(QLabel('Captured objects:'))
        layout.addWidget(self.counter_panel)

        self.mute_cb = QCheckBox('Mute voice')
        self.mute_cb.stateChanged.connect(lambda s: self.mute_changed.emit(s == Qt.CheckState.Checked))
        layout.addWidget(self.mute_cb)

        open_btn = QPushButton('Open captured folder')
        open_btn.clicked.connect(lambda: self.open_captured.emit())
        layout.addWidget(open_btn)

        self.setLayout(layout)

    def _toggle(self):
        if self.is_running:
            self.stop_detection.emit()
            self.toggle_btn.setText('Start Detection')
            self._set_status(False)
        else:
            targets = [t.strip().lower() for t in self.input.text().split(',') if t.strip()]
            self.start_detection.emit(targets)
            self.toggle_btn.setText('Stop Detection')
            self._set_status(True)
        self.is_running = not self.is_running

    def _set_status(self, running):
        color = '#27ae60' if running else '#e74c3c'
        self.status.setText(f'<span style="color:{color};font-size:18px;">●</span>')

    def update_counters(self, counters):
        self.counters = counters
        text = '\n'.join(f'{k}: {v}' for k, v in counters.items())
        self.counter_panel.setText(text)

    def _dark_style(self):
        return '''
            QWidget {
                background: #23272e;
                color: #f5f6fa;
                border-radius: 12px;
                font-family: "Segoe UI", "SF Pro", "Inter", sans-serif;
                font-size: 15px;
            }
            QLineEdit, QTextEdit {
                background: #181a20;
                border: 1px solid #6C63FF;
                border-radius: 8px;
                color: #f5f6fa;
            }
            QPushButton {
                background: #6C63FF;
                color: white;
                border-radius: 8px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background: #554ee3;
            }
            QCheckBox {
                padding: 4px;
            }
        '''
