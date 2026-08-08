import json
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QPlainTextEdit,
    QCheckBox,
    QGroupBox,
    QApplication
)
from PySide6.QtCore import Qt, Signal


class ConsoleTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auto_scroll = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Header / Control Toolbar Group
        toolbar_group = QGroupBox("📜 System Execution Console & Runtime Logs")
        toolbar_group.setStyleSheet("""
            QGroupBox {
                font-weight: 700;
                color: #A1A1AA;
                border: 1px solid #27272A;
                border-radius: 8px;
                margin-top: 4px;
                padding-top: 10px;
                background-color: #18181B;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                background-color: #27272A;
                border-radius: 4px;
                color: #3B82F6;
            }
        """)

        toolbar_layout = QHBoxLayout(toolbar_group)
        toolbar_layout.setContentsMargins(12, 10, 12, 10)
        toolbar_layout.setSpacing(10)

        self.status_badge = QLabel("🟢 Ready")
        self.status_badge.setStyleSheet("color: #10B981; font-weight: bold; background-color: #064E3B; padding: 4px 10px; border-radius: 4px; font-size: 11px;")

        self.line_count_label = QLabel("Lines: 0")
        self.line_count_label.setStyleSheet("color: #A1A1AA; font-size: 11px; font-weight: 600;")

        toolbar_layout.addWidget(self.status_badge)
        toolbar_layout.addWidget(self.line_count_label)
        toolbar_layout.addStretch()

        self.auto_scroll_cb = QCheckBox("Tự động cuộn xuống (Auto-Scroll)")
        self.auto_scroll_cb.setChecked(True)
        self.auto_scroll_cb.setStyleSheet("color: #E4E4E7; font-weight: 500; font-size: 12px;")
        self.auto_scroll_cb.toggled.connect(self._on_autoscroll_toggled)

        self.copy_btn = QPushButton("📋 Sao chép Log")
        self.copy_btn.setToolTip("Sao chép toàn bộ nội dung console log vào Clipboard")
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #27272A;
                color: #F4F4F5;
                font-weight: 600;
                border-radius: 6px;
                border: 1px solid #3F3F46;
                padding: 5px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #3F3F46;
            }
        """)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)

        self.clear_btn = QPushButton("🧹 Xóa Console")
        self.clear_btn.setToolTip("Xóa sạch toàn bộ nhật ký hiển thị trên màn hình")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #7F1D1D;
                color: #FECACA;
                font-weight: 600;
                border-radius: 6px;
                border: 1px solid #991B1B;
                padding: 5px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #991B1B;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_log)

        toolbar_layout.addWidget(self.auto_scroll_cb)
        toolbar_layout.addWidget(self.copy_btn)
        toolbar_layout.addWidget(self.clear_btn)

        layout.addWidget(toolbar_group)

        # Main Log Output Area
        self.log_edit = QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setStyleSheet("""
            QPlainTextEdit {
                background-color: #09090B;
                color: #34D399;
                font-family: 'Consolas', 'Courier New', 'Fira Code', monospace;
                font-size: 13px;
                line-height: 1.5;
                border: 1px solid #27272A;
                border-radius: 8px;
                padding: 12px;
                selection-background-color: #1E3A8A;
                selection-color: #FFFFFF;
            }
        """)

        layout.addWidget(self.log_edit, stretch=1)

    def append_log(self, text: str):
        self.log_edit.appendPlainText(text)
        count = self.log_edit.blockCount()
        self.line_count_label.setText(f"Lines: {count}")
        if self.auto_scroll:
            scrollbar = self.log_edit.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def clear_log(self):
        self.log_edit.clear()
        self.line_count_label.setText("Lines: 0")

    def copy_to_clipboard(self):
        text = self.log_edit.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

    def _on_autoscroll_toggled(self, checked: bool):
        self.auto_scroll = checked

    def set_status(self, text: str, is_active: bool = True):
        self.status_badge.setText(text)
        if is_active:
            self.status_badge.setStyleSheet("color: #10B981; font-weight: bold; background-color: #064E3B; padding: 4px 10px; border-radius: 4px; font-size: 11px;")
        else:
            self.status_badge.setStyleSheet("color: #9CA3AF; font-weight: bold; background-color: #374151; padding: 4px 10px; border-radius: 4px; font-size: 11px;")
