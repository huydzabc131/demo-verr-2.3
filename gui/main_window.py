from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QFrame,
    QScrollArea,
    QSizePolicy
)
from gui.bot_page import BotPage


STYLE_SHEET = """
QWidget {
    background-color: #121214;
    color: #F4F4F5;
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    font-size: 13px;
}

/* Header Frame */
QFrame#headerFrame {
    background-color: #18181B;
    border-bottom: 1px solid #27272A;
    padding: 8px 16px;
}

/* Main Tab Widget for Bots */
QTabWidget#mainTabs::pane {
    border: 1px solid #27272A;
    border-radius: 10px;
    background-color: #18181B;
    top: -1px;
}

QTabWidget#mainTabs QTabBar::tab {
    background-color: #27272A;
    color: #A1A1AA;
    padding: 10px 22px;
    font-weight: 600;
    font-size: 13px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
    border: 1px solid #3F3F46;
    border-bottom: none;
}

QTabWidget#mainTabs QTabBar::tab:selected {
    background-color: #2563EB;
    color: #FFFFFF;
    border-color: #2563EB;
}

QTabWidget#mainTabs QTabBar::tab:hover:!selected {
    background-color: #3F3F46;
    color: #F4F4F5;
}

/* QGroupBox */
QGroupBox {
    background-color: #18181B;
    border: 1px solid #27272A;
    border-radius: 10px;
    font-weight: 700;
    font-size: 13px;
    color: #60A5FA;
    margin-top: 12px;
    padding-top: 14px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 2px 8px;
    background-color: #27272A;
    border-radius: 4px;
    color: #93C5FD;
}

/* QComboBox */
QComboBox {
    background-color: #09090B;
    border: 1px solid #3F3F46;
    border-radius: 6px;
    padding: 6px 12px;
    color: #F4F4F5;
    min-width: 100px;
    min-height: 24px;
}

QComboBox:hover {
    border-color: #3B82F6;
}

QComboBox:focus {
    border-color: #60A5FA;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #18181B;
    border: 1px solid #3F3F46;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
    color: #F4F4F5;
    padding: 4px;
}

/* QSpinBox & QDoubleSpinBox */
QSpinBox, QDoubleSpinBox {
    background-color: #09090B;
    border: 1px solid #3F3F46;
    border-radius: 6px;
    padding: 6px 10px;
    color: #F4F4F5;
    min-height: 24px;
}

QSpinBox:hover, QDoubleSpinBox:hover {
    border-color: #3B82F6;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #60A5FA;
}

/* QCheckBox */
QCheckBox {
    color: #F4F4F5;
    spacing: 8px;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #3F3F46;
    background-color: #09090B;
}

QCheckBox::indicator:hover {
    border-color: #3B82F6;
}

QCheckBox::indicator:checked {
    background-color: #2563EB;
    border-color: #2563EB;
}

/* QRadioButton */
QRadioButton {
    color: #F4F4F5;
    spacing: 8px;
    font-size: 13px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 1px solid #3F3F46;
    background-color: #09090B;
}

QRadioButton::indicator:hover {
    border-color: #3B82F6;
}

QRadioButton::indicator:checked {
    background-color: #2563EB;
    border-color: #2563EB;
}

/* Buttons */
QPushButton {
    background-color: #27272A;
    color: #F4F4F5;
    font-weight: 600;
    border-radius: 6px;
    border: 1px solid #3F3F46;
    padding: 7px 14px;
    min-height: 22px;
}

QPushButton:hover {
    background-color: #3F3F46;
    border-color: #52525B;
}

QPushButton:pressed {
    background-color: #18181B;
}

/* Splitter Handles */
QSplitter::handle {
    background-color: #27272A;
    border-radius: 2px;
}

QSplitter::handle:hover {
    background-color: #3B82F6;
}

QSplitter::handle:horizontal {
    width: 6px;
}

QSplitter::handle:vertical {
    height: 6px;
}

/* ScrollBar */
QScrollBar:vertical {
    border: none;
    background: #09090B;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #3F3F46;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #52525B;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #09090B;
    height: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background: #3F3F46;
    min-width: 24px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal:hover {
    background: #52525B;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ScrollArea */
QScrollArea {
    border: none;
    background-color: transparent;
}
"""


class MainWindow(QWidget):

    def __init__(self, bots):
        super().__init__()

        self.setWindowTitle("Clash Auto Farm Pro - Control Studio")
        self.setMinimumSize(1020, 680)
        self.resize(1280, 820)
        self.setStyleSheet(STYLE_SHEET)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top Header Bar
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 10, 16, 10)

        title_label = QLabel("⚔️ Clash Auto Farm Pro")
        title_label.setStyleSheet("font-size: 18px; font-weight: 800; color: #F4F4F5; letter-spacing: 0.5px;")

        version_badge = QLabel("v1.0 Pro")
        version_badge.setStyleSheet("""
            background-color: #2563EB;
            color: #FFFFFF;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 10px;
        """)

        self.status = QLabel("Status : Ready")
        self.status.setStyleSheet("""
            background-color: #10B981;
            color: #FFFFFF;
            font-size: 11px;
            font-weight: 700;
            padding: 4px 14px;
            border-radius: 12px;
        """)

        header_title_box = QHBoxLayout()
        header_title_box.setSpacing(10)
        header_title_box.addWidget(title_label)
        header_title_box.addWidget(version_badge)

        header_layout.addLayout(header_title_box)
        header_layout.addStretch()
        header_layout.addWidget(self.status)

        main_layout.addWidget(header_frame)

        # Center Content Layout
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(14, 14, 14, 14)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        for bot in bots:
            page = BotPage(bot)
            self.tabs.addTab(page, f"🤖 {bot.name}")

        content_layout.addWidget(self.tabs)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

