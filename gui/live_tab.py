import os
import json
import copy
import math
import cv2
import numpy as np
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QGroupBox,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QSplitter,
    QScrollArea,
    QSizePolicy,
    QHeaderView,
    QAbstractItemView,
    QInputDialog,
    QMessageBox,
    QDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap, QKeySequence, QShortcut, QColor, QBrush, QFont
from gui.config_preview_dialog import ConfigPreviewDialog

UNIT_CATALOG = [
    {"id": "dragon", "name": "Dragon", "type": "troop"},
    {"id": "antrom", "name": "Sở ních ky", "type": "troop"},
    {"id": "vaky", "name": "Thánh nữ vanky", "type": "troop"},
    {"id": "apprentice", "name": "Apprentice Warden", "type": "troop"},
    {"id": "king", "name": "Barbarian King", "type": "hero"},
    {"id": "queen", "name": "Archer Queen", "type": "hero"},
    {"id": "warden", "name": "Grand Warden", "type": "hero"},
    {"id": "royal_champion", "name": "Royal Champion", "type": "hero"},
    {"id": "minion_prince", "name": "Minion Prince", "type": "hero"},
    {"id": "duke", "name": "Grand Duke", "type": "hero"},
    {"id": "leu", "name": "Siege Machine (Lều)", "type": "siege"},
    {"id": "rage", "name": "Rage Spell", "type": "spell"},
    {"id": "bang", "name": "Freeze Spell", "type": "spell"},
    {"id": "healing", "name": "Healing Spell", "type": "spell"},
    {"id": "lightning", "name": "Lightning Spell", "type": "spell"},
    {"id": "vatto", "name": "Overgrowth Spell", "type": "spell"},
    {"id": "poison", "name": "Poison Spell", "type": "spell"},
    {"id": "skeleton", "name": "Skeleton Spell", "type": "spell"},
    {"id": "totem", "name": "Hero Totem", "type": "totem"},
    {"id": "equipment", "name": "Hero Equipment Ability", "type": "totem"},
    {"id": "nhay", "name": "Jump Spell", "type": "spell"},
]

PRESET_TAGS = [
    "Main Army",
    "Funnel Left",
    "Funnel Right",
    "Heroes",
    "Spells",
    "Siege",
    "Cleanup",
    "Phase 1",
    "Phase 2",
    "Phase 3"
]

TAG_COLOR_MAP = {
    "Funnel Left": {"hex": "#3B82F6", "bgr": (246, 130, 59), "qt": QColor("#3B82F6")},
    "Funnel Right": {"hex": "#06B6D4", "bgr": (212, 182, 6), "qt": QColor("#06B6D4")},
    "Main Army": {"hex": "#10B981", "bgr": (129, 185, 16), "qt": QColor("#10B981")},
    "Heroes": {"hex": "#F59E0B", "bgr": (11, 158, 245), "qt": QColor("#F59E0B")},
    "Spells": {"hex": "#8B5CF6", "bgr": (246, 92, 139), "qt": QColor("#8B5CF6")},
    "Siege": {"hex": "#EF4444", "bgr": (68, 68, 239), "qt": QColor("#EF4444")},
    "Cleanup": {"hex": "#6B7280", "bgr": (128, 114, 107), "qt": QColor("#6B7280")},
    "Phase 1": {"hex": "#EC4899", "bgr": (153, 72, 236), "qt": QColor("#EC4899")},
    "Phase 2": {"hex": "#38BDF8", "bgr": (248, 189, 56), "qt": QColor("#38BDF8")},
    "Phase 3": {"hex": "#A855F7", "bgr": (247, 85, 168), "qt": QColor("#A855F7")}
}

DEFAULT_TAG_COLOR = {"hex": "#10B981", "bgr": (129, 185, 16), "qt": QColor("#10B981")}

def get_tag_color(tag: str):
    if not tag or tag not in TAG_COLOR_MAP:
        return DEFAULT_TAG_COLOR
    return TAG_COLOR_MAP[tag]


class ClickableImageLabel(QLabel):
    drag_started = Signal(int, int, bool)   # real_x, real_y, is_shift
    drag_moved = Signal(int, int, bool)     # real_x, real_y, is_shift
    drag_ended = Signal(int, int)           # real_x, real_y
    canvas_clicked = Signal(int, int)       # real_x, real_y
    resized = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap_original_size = (1600, 900)
        self.adding_enabled = True
        self.is_mouse_down = False
        self.press_pos = None
        self.setMouseTracking(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit()

    def get_real_coords(self, event_pos):
        pix = self.pixmap()
        if not pix or pix.isNull():
            return None
        lbl_w = self.width()
        lbl_h = self.height()
        pix_w = pix.width()
        pix_h = pix.height()

        dx = (lbl_w - pix_w) / 2
        dy = (lbl_h - pix_h) / 2

        click_x = event_pos.x() - dx
        click_y = event_pos.y() - dy

        if 0 <= click_x <= pix_w and 0 <= click_y <= pix_h:
            orig_w, orig_h = self.pixmap_original_size
            if orig_w > 0 and orig_h > 0:
                real_x = int((click_x / pix_w) * orig_w)
                real_y = int((click_y / pix_h) * orig_h)
                real_x = max(0, min(orig_w, real_x))
                real_y = max(0, min(orig_h, real_y))
                return real_x, real_y
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.adding_enabled:
            coords = self.get_real_coords(event.position())
            if coords:
                self.is_mouse_down = True
                self.press_pos = coords
                is_shift = bool(event.modifiers() & Qt.ShiftModifier)
                self.drag_started.emit(coords[0], coords[1], is_shift)

    def mouseMoveEvent(self, event):
        coords = self.get_real_coords(event.position())
        if coords:
            is_shift = bool(event.modifiers() & Qt.ShiftModifier)
            if self.is_mouse_down:
                self.drag_moved.emit(coords[0], coords[1], is_shift)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_mouse_down:
            self.is_mouse_down = False
            coords = self.get_real_coords(event.position())
            if coords:
                # Check if it was a quick click vs drag
                if self.press_pos and math.hypot(coords[0] - self.press_pos[0], coords[1] - self.press_pos[1]) < 8:
                    self.canvas_clicked.emit(coords[0], coords[1])
                else:
                    self.drag_ended.emit(coords[0], coords[1])


class LiveTab(QWidget):
    config_changed = Signal()

    def __init__(self, device=None):
        super().__init__()
        self.device = device
        self.deploy_actions = []
        self.current_frame = None
        self._is_loading = True
        self.selected_action_index = -1

        # Random Config & Multi-Config State
        self.random_mode = "Sequential"
        self.random_configs = []
        self.active_config_index = 0

        # Interactive mode states
        self.is_move_mode = False
        self.is_dragging_marker = False
        self.drag_target_index = -1
        self.is_shift_held = False
        self.active_tag_filter = "All Tags"
        self.is_grouped_view = False

        # History state
        self.history = []
        self.history_index = -1
        self.has_unsaved_changes = False

        self.init_shortcuts()
        self.init_ui()

    def init_shortcuts(self):
        self.undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.undo_shortcut.activated.connect(self.undo)

        self.redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        self.redo_shortcut.activated.connect(self.redo)

    def apply_data(self, data: dict):
        self._is_loading = True
        try:
            self.random_mode = data.get("random_mode", "Sequential")
            raw_random_configs = data.get("random_configs", [])

            if not raw_random_configs:
                # Upgrade legacy single deploy_actions into random_configs format
                legacy_actions = data.get("deploy_actions", [])
                self.random_configs = [{
                    "id": "cfg_1",
                    "name": "Config 1",
                    "enabled": True,
                    "deploy_actions": copy.deepcopy(legacy_actions)
                }]
            else:
                self.random_configs = copy.deepcopy(raw_random_configs)

            self.active_config_index = 0
            if self.random_configs:
                self.deploy_actions = self.random_configs[0].get("deploy_actions", [])
            else:
                self.deploy_actions = []

            self.selected_action_index = 0 if self.deploy_actions else -1
            self.history = []
            self.history_index = -1
            self.push_to_history(initial=True)

            self.update_config_selector_ui()
            self.populate_all_views()
            self.has_unsaved_changes = False
            self.update_unsaved_badge()
        finally:
            self._is_loading = False

    def sync_active_config_actions(self):
        """Keep current active config deploy_actions in sync with self.deploy_actions."""
        if 0 <= self.active_config_index < len(self.random_configs):
            self.random_configs[self.active_config_index]["deploy_actions"] = copy.deepcopy(self.deploy_actions)

    def save_config_data(self):
        try:
            self.sync_active_config_actions()
            data = {}
            if os.path.exists("config.json"):
                try:
                    with open("config.json", "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    pass

            data["random_mode"] = self.random_mode
            data["random_configs"] = self.random_configs
            data["deploy_actions"] = self.deploy_actions  # Backward compatibility

            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            self.has_unsaved_changes = False
            self.update_unsaved_badge()
            self.status_label.setText(f"✅ Saved to config.json! Mode: [{self.random_mode}] | Configs: {len(self.random_configs)}")
            self.config_changed.emit()
        except Exception as e:
            print("Error saving config:", e)

    def update_config_selector_ui(self):
        """Update Random Mode combo and Active Config combo without triggering loops."""
        if not hasattr(self, "combo_random_mode") or not hasattr(self, "combo_active_config"):
            return

        self._is_loading = True

        # Mode
        mode_idx = 0 if self.random_mode == "Sequential" else 1
        self.combo_random_mode.setCurrentIndex(mode_idx)

        # Configs dropdown
        self.combo_active_config.clear()
        for idx, cfg in enumerate(self.random_configs):
            pts = len(cfg.get("deploy_actions", []))
            status = "✓" if cfg.get("enabled", True) else "✗"
            self.combo_active_config.addItem(f"[{status}] {cfg.get('name', f'Config {idx+1}')} ({pts} pts)")

        if 0 <= self.active_config_index < self.combo_active_config.count():
            self.combo_active_config.setCurrentIndex(self.active_config_index)

        self._is_loading = False

    def on_random_mode_changed(self, index: int):
        if self._is_loading:
            return
        self.random_mode = "Sequential" if index == 0 else "Random"
        self.has_unsaved_changes = True
        self.update_unsaved_badge()
        self.status_label.setText(f"🎲 Chế độ thi hành chuyển sang: [{self.random_mode}]")

    def on_active_config_changed(self, index: int):
        if self._is_loading or index < 0 or index >= len(self.random_configs):
            return

        # Save current active config's deploy actions before switching
        self.sync_active_config_actions()

        self.active_config_index = index
        self.deploy_actions = copy.deepcopy(self.random_configs[index].get("deploy_actions", []))
        self.selected_action_index = 0 if self.deploy_actions else -1

        self.populate_all_views()
        self.status_label.setText(f"📂 Đang chỉnh sửa: '{self.random_configs[index].get('name')}' ({len(self.deploy_actions)} points)")

    def add_new_config(self):
        name, ok = QInputDialog.getText(self, "Tạo Config mới", "Tên Config:")
        if ok and name.strip():
            self.sync_active_config_actions()
            new_idx = len(self.random_configs)
            new_cfg = {
                "id": f"cfg_{new_idx + 1}",
                "name": name.strip(),
                "enabled": True,
                "deploy_actions": copy.deepcopy(self.deploy_actions)
            }
            self.random_configs.append(new_cfg)
            self.active_config_index = new_idx
            self.deploy_actions = copy.deepcopy(new_cfg["deploy_actions"])

            self.update_config_selector_ui()
            self.populate_all_views()
            self.has_unsaved_changes = True
            self.update_unsaved_badge()

    def duplicate_current_config(self):
        if not (0 <= self.active_config_index < len(self.random_configs)):
            return

        self.sync_active_config_actions()
        curr = self.random_configs[self.active_config_index]
        new_name = f"{curr.get('name', 'Config')} (Copy)"
        new_idx = len(self.random_configs)

        dup_cfg = {
            "id": f"cfg_{new_idx + 1}",
            "name": new_name,
            "enabled": True,
            "deploy_actions": copy.deepcopy(curr.get("deploy_actions", []))
        }
        self.random_configs.append(dup_cfg)
        self.active_config_index = new_idx
        self.deploy_actions = copy.deepcopy(dup_cfg["deploy_actions"])

        self.update_config_selector_ui()
        self.populate_all_views()
        self.has_unsaved_changes = True
        self.update_unsaved_badge()

    def rename_current_config(self):
        if not (0 <= self.active_config_index < len(self.random_configs)):
            return

        curr_name = self.random_configs[self.active_config_index].get("name", "")
        name, ok = QInputDialog.getText(self, "Đổi tên Config", "Tên mới:", text=curr_name)
        if ok and name.strip():
            self.random_configs[self.active_config_index]["name"] = name.strip()
            self.update_config_selector_ui()
            self.has_unsaved_changes = True
            self.update_unsaved_badge()

    def delete_current_config(self):
        if len(self.random_configs) <= 1:
            QMessageBox.warning(self, "Cảnh báo", "Phải giữ lại ít nhất 1 Config!")
            return

        if 0 <= self.active_config_index < len(self.random_configs):
            self.random_configs.pop(self.active_config_index)
            self.active_config_index = max(0, self.active_config_index - 1)
            self.deploy_actions = copy.deepcopy(self.random_configs[self.active_config_index].get("deploy_actions", []))

            self.update_config_selector_ui()
            self.populate_all_views()
            self.has_unsaved_changes = True
            self.update_unsaved_badge()

    def move_config_up(self):
        idx = self.active_config_index
        if idx > 0:
            self.sync_active_config_actions()
            self.random_configs[idx], self.random_configs[idx - 1] = self.random_configs[idx - 1], self.random_configs[idx]
            self.active_config_index = idx - 1
            self.update_config_selector_ui()
            self.has_unsaved_changes = True
            self.update_unsaved_badge()

    def move_config_down(self):
        idx = self.active_config_index
        if idx < len(self.random_configs) - 1:
            self.sync_active_config_actions()
            self.random_configs[idx], self.random_configs[idx + 1] = self.random_configs[idx + 1], self.random_configs[idx]
            self.active_config_index = idx + 1
            self.update_config_selector_ui()
            self.has_unsaved_changes = True
            self.update_unsaved_badge()

    def open_visual_canvas_editor(self):
        self.sync_active_config_actions()
        curr_data = {
            "random_mode": self.random_mode,
            "random_configs": self.random_configs,
            "deploy_actions": self.deploy_actions
        }
        dlg = ConfigPreviewDialog("Live Deploy", curr_data, parent=self)
        if dlg.exec() == QDialog.Accepted:
            updated = dlg.get_updated_config()
            self.apply_data(updated)
            self.has_unsaved_changes = True
            self.update_unsaved_badge()


    def push_to_history(self, initial=False):
        snapshot = copy.deepcopy(self.deploy_actions)
        if self.history_index >= 0:
            self.history = self.history[:self.history_index + 1]
        
        self.history.append(snapshot)
        if len(self.history) > 50:
            self.history.pop(0)
        self.history_index = len(self.history) - 1

        if not initial and not self._is_loading:
            self.has_unsaved_changes = True
            self.update_unsaved_badge()
            self.config_changed.emit()

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.deploy_actions = copy.deepcopy(self.history[self.history_index])
            self.populate_all_views()
            self.has_unsaved_changes = True
            self.update_unsaved_badge()
            self.status_label.setText(f"↩️ Undo step {self.history_index + 1}/{len(self.history)}")

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.deploy_actions = copy.deepcopy(self.history[self.history_index])
            self.populate_all_views()
            self.has_unsaved_changes = True
            self.update_unsaved_badge()
            self.status_label.setText(f"↪️ Redo step {self.history_index + 1}/{len(self.history)}")

    def update_unsaved_badge(self):
        if self.has_unsaved_changes:
            self.unsaved_badge.setText("⚠️ Chưa lưu thay đổi")
            self.unsaved_badge.setStyleSheet("color: #F59E0B; font-weight: bold; background-color: #312E81; padding: 4px 10px; border-radius: 6px; font-size: 11px;")
        else:
            self.unsaved_badge.setText("✓ Đã đồng bộ")
            self.unsaved_badge.setStyleSheet("color: #10B981; font-weight: bold; background-color: #064E3B; padding: 4px 10px; border-radius: 6px; font-size: 11px;")

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Master Toolbar
        toolbar_box = QGroupBox("⚡ Live Deploy Tools & Filters")
        toolbar_layout = QHBoxLayout(toolbar_box)
        toolbar_layout.setContentsMargins(12, 10, 12, 10)
        toolbar_layout.setSpacing(8)

        self.sys_label = QLabel("🎯 LIVE DEPLOY SYSTEM")
        self.sys_label.setStyleSheet("color: #60A5FA; font-weight: bold; font-size: 12px;")

        # Move position mode toggle
        self.move_mode_btn = QPushButton("🎯 Chuyển Vị Trí (Move Coords)")
        self.move_mode_btn.setCheckable(True)
        self.move_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #27272A;
                color: #F4F4F5;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 6px;
                border: 1px solid #3F3F46;
            }
            QPushButton:checked {
                background-color: #F59E0B;
                color: #000000;
                border: 1px solid #FBBF24;
            }
        """)
        self.move_mode_btn.toggled.connect(self.toggle_move_mode)

        # Filter Tag Dropdown
        toolbar_layout.addWidget(self.sys_label)
        toolbar_layout.addWidget(self.move_mode_btn)
        toolbar_layout.addSpacing(15)

        toolbar_layout.addWidget(QLabel("Filter Tag:"))
        self.tag_filter_combo = QComboBox()
        self.tag_filter_combo.addItem("All Tags")
        for t in PRESET_TAGS:
            self.tag_filter_combo.addItem(t)
        self.tag_filter_combo.currentTextChanged.connect(self.on_tag_filter_changed)
        toolbar_layout.addWidget(self.tag_filter_combo)

        # Grouping view toggle
        self.view_mode_btn = QPushButton("📂 Xem theo Nhóm Tag")
        self.view_mode_btn.setCheckable(True)
        self.view_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #27272A;
                color: #A1A1AA;
                font-weight: bold;
                padding: 6px 10px;
                border-radius: 6px;
            }
            QPushButton:checked {
                background-color: #3B82F6;
                color: #FFFFFF;
            }
        """)
        self.view_mode_btn.toggled.connect(self.toggle_group_view)
        toolbar_layout.addWidget(self.view_mode_btn)

        toolbar_layout.addStretch()

        self.unsaved_badge = QLabel("✓ Đã đồng bộ")
        self.update_unsaved_badge()

        self.undo_btn = QPushButton("↩️ Undo")
        self.undo_btn.setToolTip("Khôi phục bước trước (Ctrl + Z)")
        self.undo_btn.setStyleSheet("padding: 5px 10px; font-size: 11px; background-color: #27272A; color: white;")
        self.undo_btn.clicked.connect(self.undo)

        self.redo_btn = QPushButton("↪️ Redo")
        self.redo_btn.setToolTip("Đi tới bước sau (Ctrl + Y)")
        self.redo_btn.setStyleSheet("padding: 5px 10px; font-size: 11px; background-color: #27272A; color: white;")
        self.redo_btn.clicked.connect(self.redo)

        self.save_all_btn = QPushButton("💾 Lưu Config")
        self.save_all_btn.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; padding: 6px 14px; font-size: 12px;")
        self.save_all_btn.clicked.connect(self.save_config_data)

        toolbar_layout.addWidget(self.unsaved_badge)
        toolbar_layout.addWidget(self.undo_btn)
        toolbar_layout.addWidget(self.redo_btn)
        toolbar_layout.addWidget(self.save_all_btn)

        main_layout.addWidget(toolbar_box)

        # Content horizontal splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        # Left Column: Canvas Preview
        left_box = QGroupBox("🗺️ Interactive Live Battlefield Canvas (1600x900)")
        left_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout = QVBoxLayout(left_box)
        left_layout.setContentsMargins(8, 12, 8, 8)

        self.img_label = ClickableImageLabel()
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setStyleSheet("background-color: #0A0A0C; border-radius: 8px; border: 2px solid #3F3F46;")
        self.img_label.setMinimumSize(480, 320)
        self.img_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.img_label.drag_started.connect(self.on_canvas_drag_started)
        self.img_label.drag_moved.connect(self.on_canvas_drag_moved)
        self.img_label.drag_ended.connect(self.on_canvas_drag_ended)
        self.img_label.canvas_clicked.connect(self.on_canvas_clicked)
        self.img_label.resized.connect(self.redraw_frame)

        left_layout.addWidget(self.img_label)

        self.hint_label = QLabel("💡 Drag Marker để di chuyển tọa độ. Bật 'Chuyển Vị Trí' để nhấp chọn điểm mới. Giữ Shift để Snap 10px.")
        self.hint_label.setStyleSheet("color: #F59E0B; font-size: 11px; font-weight: 500; background-color: #18181B; padding: 6px 10px; border-radius: 4px;")
        left_layout.addWidget(self.hint_label)

        splitter.addWidget(left_box)

        # Right Column: Action Inspector & Live Coordinate List
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # Status log box
        self.status_label = QLabel("Chào mừng bạn đến với hệ thống Live Deploy mới!")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #60A5FA; font-size: 11px; font-weight: 700; background-color: #09090B; padding: 8px; border-radius: 6px; border: 1px solid #27272A;")
        right_layout.addWidget(self.status_label)

        # Selected Action Editor Box
        editor_box = QGroupBox("⚙️ Selected Action Properties Editor")
        editor_layout = QVBoxLayout(editor_box)
        editor_layout.setContentsMargins(10, 10, 10, 10)
        editor_layout.setSpacing(8)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Unit:"))
        self.unit_combo = QComboBox()
        self.unit_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        for u in UNIT_CATALOG:
            self.unit_combo.addItem(f"{u['name']} ({u['type']})", u['id'])
        row1.addWidget(self.unit_combo)

        row1.addWidget(QLabel("Tag:"))
        self.tag_combo = QComboBox()
        self.tag_combo.setEditable(True)
        for t in PRESET_TAGS:
            self.tag_combo.addItem(t)
        self.tag_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        row1.addWidget(self.tag_combo)
        editor_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("X:"))
        self.spin_x = QSpinBox()
        self.spin_x.setRange(0, 1600)
        self.spin_x.setValue(800)
        row2.addWidget(self.spin_x)

        row2.addWidget(QLabel("Y:"))
        self.spin_y = QSpinBox()
        self.spin_y.setRange(0, 900)
        self.spin_y.setValue(450)
        row2.addWidget(self.spin_y)

        self.move_pos_action_btn = QPushButton("🎯 Move Position")
        self.move_pos_action_btn.setStyleSheet("background-color: #D97706; color: white; font-weight: bold; padding: 4px 8px;")
        self.move_pos_action_btn.clicked.connect(lambda: self.move_mode_btn.setChecked(True))
        row2.addWidget(self.move_pos_action_btn)

        editor_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Repeat:"))
        self.spin_repeat = QSpinBox()
        self.spin_repeat.setRange(1, 100)
        self.spin_repeat.setValue(1)
        row3.addWidget(self.spin_repeat)

        row3.addWidget(QLabel("Delay (s):"))
        self.spin_delay = QDoubleSpinBox()
        self.spin_delay.setRange(0.05, 10.0)
        self.spin_delay.setSingleStep(0.1)
        self.spin_delay.setValue(0.5)
        row3.addWidget(self.spin_delay)

        self.chk_enabled = QCheckBox("Enabled")
        self.chk_enabled.setChecked(True)
        row3.addWidget(self.chk_enabled)
        editor_layout.addLayout(row3)

        btn_editor_layout = QHBoxLayout()
        self.add_action_btn = QPushButton("➕ Thêm Hành Động Mới")
        self.add_action_btn.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; padding: 6px;")
        self.add_action_btn.clicked.connect(self.add_deploy_action)

        self.save_action_btn = QPushButton("💾 Cập Nhật Action")
        self.save_action_btn.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; padding: 6px;")
        self.save_action_btn.clicked.connect(self.save_edited_action)

        btn_editor_layout.addWidget(self.add_action_btn)
        btn_editor_layout.addWidget(self.save_action_btn)
        editor_layout.addLayout(btn_editor_layout)

        right_layout.addWidget(editor_box)

        # Deployment Action List & Live Coordinate List Box
        list_box = QGroupBox("📋 Live Deployment Action List & Coordinates")
        list_box_layout = QVBoxLayout(list_box)
        list_box_layout.setContentsMargins(10, 10, 10, 10)

        # Table View
        self.table_view = QTableWidget()
        self.table_view.setColumnCount(7)
        self.table_view.setHorizontalHeaderLabels(["#", "Status", "Unit", "Tag", "Coords (X,Y)", "Repeat", "Delay"])
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_view.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view.setStyleSheet("""
            QTableWidget {
                background-color: #09090B;
                border: 1px solid #27272A;
                border-radius: 6px;
                color: #F4F4F5;
                gridline-color: #18181B;
            }
            QHeaderView::section {
                background-color: #18181B;
                color: #A1A1AA;
                font-weight: bold;
                border: 1px solid #27272A;
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #2563EB;
                color: #FFFFFF;
            }
        """)
        self.table_view.itemSelectionChanged.connect(self.on_table_selection_changed)
        list_box_layout.addWidget(self.table_view)

        # Tree View for Grouped View
        self.tree_view = QTreeWidget()
        self.tree_view.setHeaderLabels(["Execution Order & Unit", "Tag", "Coords", "Repeat", "Delay"])
        self.tree_view.setStyleSheet("""
            QTreeWidget {
                background-color: #09090B;
                border: 1px solid #27272A;
                border-radius: 6px;
                color: #F4F4F5;
            }
            QHeaderView::section {
                background-color: #18181B;
                color: #A1A1AA;
                font-weight: bold;
                padding: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #2563EB;
                color: #FFFFFF;
            }
        """)
        self.tree_view.itemSelectionChanged.connect(self.on_tree_selection_changed)
        self.tree_view.hide()
        list_box_layout.addWidget(self.tree_view)

        # Reorder & Manipulate Controls
        row_manip = QHBoxLayout()
        row_manip.setSpacing(6)
        self.move_up_btn = QPushButton("⬆️ Lên")
        self.move_up_btn.clicked.connect(self.move_action_up)
        self.move_down_btn = QPushButton("⬇️ Xuống")
        self.move_down_btn.clicked.connect(self.move_action_down)
        self.duplicate_btn = QPushButton("📋 Nhân bản")
        self.duplicate_btn.clicked.connect(self.duplicate_action)
        self.delete_btn = QPushButton("🗑️ Xóa Action")
        self.delete_btn.setStyleSheet("background-color: #DC2626; color: white; font-weight: bold;")
        self.delete_btn.clicked.connect(self.delete_action)

        row_manip.addWidget(self.move_up_btn)
        row_manip.addWidget(self.move_down_btn)
        row_manip.addWidget(self.duplicate_btn)
        row_manip.addWidget(self.delete_btn)
        list_box_layout.addLayout(row_manip)

        right_layout.addWidget(list_box)

        right_scroll.setWidget(right_container)
        splitter.addWidget(right_scroll)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter)
        self.populate_all_views()

    def toggle_move_mode(self, checked: bool):
        self.is_move_mode = checked
        if checked:
            self.img_label.setCursor(Qt.CrossCursor)
            self.status_label.setText("🎯 Chế độ 'Chuyển Vị Trí' đang bật: Hãy nhấp lên bản đồ để cập nhật tọa độ mới cho Action đang chọn!")
        else:
            self.img_label.setCursor(Qt.ArrowCursor)
            self.status_label.setText("Đã tắt chế độ 'Chuyển Vị Trí'. Drag marker hoặc click bản đồ để chọn/thêm.")

    def on_tag_filter_changed(self, text: str):
        self.active_tag_filter = text
        self.populate_all_views()

    def toggle_group_view(self, checked: bool):
        self.is_grouped_view = checked
        if checked:
            self.table_view.hide()
            self.tree_view.show()
            self.view_mode_btn.setText("📋 Flat Table View")
        else:
            self.tree_view.hide()
            self.table_view.show()
            self.view_mode_btn.setText("📂 Xem theo Nhóm Tag")
        self.populate_all_views()

    # --- CANVAS EVENT HANDLERS ---
    def on_canvas_clicked(self, real_x, real_y):
        if self.is_move_mode:
            # Update coordinate of selected action
            if 0 <= self.selected_action_index < len(self.deploy_actions):
                act = self.deploy_actions[self.selected_action_index]
                act["x"] = real_x
                act["y"] = real_y
                self.spin_x.setValue(real_x)
                self.spin_y.setValue(real_y)
                self.push_to_history()
                self.populate_all_views()
                self.status_label.setText(f"🎯 Đã cập nhật tọa độ Action #{self.selected_action_index + 1} ({act['unit_name']}) thành ({real_x}, {real_y})")
            else:
                self.status_label.setText("⚠️ Hãy chọn một Action trong danh sách trước khi nhấp chuyển vị trí!")
            self.move_mode_btn.setChecked(False)
        else:
            # Hit test existing marker
            hit_radius = 35
            best_idx = -1
            best_dist = float('inf')
            for idx, act in enumerate(self.deploy_actions):
                dist = math.hypot(act['x'] - real_x, act['y'] - real_y)
                if dist < best_dist and dist <= hit_radius:
                    best_dist = dist
                    best_idx = idx

            if best_idx >= 0:
                self.selected_action_index = best_idx
                self.select_row_in_views(best_idx)
                act = self.deploy_actions[best_idx]
                self.status_label.setText(f"📍 Đã chọn Action #{best_idx + 1}: {act['unit_name']} [{act.get('tag', '')}] tại ({act['x']}, {act['y']})")
            else:
                # Add new action at clicked spot
                self.spin_x.setValue(real_x)
                self.spin_y.setValue(real_y)
                self.add_deploy_action()

    def on_canvas_drag_started(self, real_x, real_y, is_shift):
        if self.is_move_mode:
            return
        self.is_shift_held = is_shift
        hit_radius = 35

        best_idx = -1
        best_dist = float('inf')
        for idx, act in enumerate(self.deploy_actions):
            dist = math.hypot(act['x'] - real_x, act['y'] - real_y)
            if dist < best_dist and dist <= hit_radius:
                best_dist = dist
                best_idx = idx

        if best_idx >= 0:
            self.is_dragging_marker = True
            self.drag_target_index = best_idx
            self.selected_action_index = best_idx
            self.select_row_in_views(best_idx)
            self.status_label.setText(f"🖐️ Đang kéo Marker #{best_idx + 1} ({self.deploy_actions[best_idx]['unit_name']})...")
        self.redraw_frame()

    def on_canvas_drag_moved(self, real_x, real_y, is_shift):
        self.is_shift_held = is_shift
        if not self.is_dragging_marker or self.drag_target_index < 0:
            return

        final_x = round(real_x / 10) * 10 if is_shift else real_x
        final_y = round(real_y / 10) * 10 if is_shift else real_y

        idx = self.drag_target_index
        snap_str = " [SNAP 10px]" if is_shift else ""

        if 0 <= idx < len(self.deploy_actions):
            self.deploy_actions[idx]["x"] = final_x
            self.deploy_actions[idx]["y"] = final_y
            self.spin_x.setValue(final_x)
            self.spin_y.setValue(final_y)
            unit_name = self.deploy_actions[idx]["unit_name"]
            self.status_label.setText(f"📍 Kéo Marker #{idx+1} ({unit_name}): ({final_x}, {final_y}){snap_str}")

        self.redraw_frame()

    def on_canvas_drag_ended(self, real_x, real_y):
        if self.is_dragging_marker and self.drag_target_index >= 0:
            idx = self.drag_target_index
            if 0 <= idx < len(self.deploy_actions):
                act = self.deploy_actions[idx]
                self.status_label.setText(f"📍 Đã thả Marker #{idx+1} ({act['unit_name']}) tại ({act['x']}, {act['y']})")
            self.push_to_history()
            self.populate_all_views()

        self.is_dragging_marker = False
        self.drag_target_index = -1
        self.redraw_frame()

    # --- ACTION MANAGEMENT HANDLERS ---
    def add_deploy_action(self):
        unit_id = self.unit_combo.currentData()
        unit_name = self.unit_combo.currentText().split(' (')[0]
        tag_val = self.tag_combo.currentText().strip() or "Main Army"

        unit_type = "troop"
        for u in UNIT_CATALOG:
            if u["id"] == unit_id:
                unit_type = u["type"]
                break

        act = {
            "id": f"act_{len(self.deploy_actions) + 1}",
            "unit_id": unit_id,
            "unit_name": unit_name,
            "unit_type": unit_type,
            "x": self.spin_x.value(),
            "y": self.spin_y.value(),
            "repeat_count": self.spin_repeat.value(),
            "delay": self.spin_delay.value(),
            "enabled": self.chk_enabled.isChecked(),
            "tag": tag_val
        }
        self.deploy_actions.append(act)
        self.selected_action_index = len(self.deploy_actions) - 1
        self.push_to_history()
        self.populate_all_views()
        self.status_label.setText(f"➕ Đã thêm Action #{len(self.deploy_actions)}: {unit_name} [{tag_val}] tại ({act['x']}, {act['y']})")

    def save_edited_action(self):
        if 0 <= self.selected_action_index < len(self.deploy_actions):
            unit_id = self.unit_combo.currentData()
            unit_name = self.unit_combo.currentText().split(' (')[0]
            tag_val = self.tag_combo.currentText().strip() or "Main Army"

            unit_type = "troop"
            for u in UNIT_CATALOG:
                if u["id"] == unit_id:
                    unit_type = u["type"]
                    break

            self.deploy_actions[self.selected_action_index].update({
                "unit_id": unit_id,
                "unit_name": unit_name,
                "unit_type": unit_type,
                "x": self.spin_x.value(),
                "y": self.spin_y.value(),
                "repeat_count": self.spin_repeat.value(),
                "delay": self.spin_delay.value(),
                "enabled": self.chk_enabled.isChecked(),
                "tag": tag_val
            })
            self.push_to_history()
            self.populate_all_views()
            self.status_label.setText(f"💾 Cập nhật thành công Action #{self.selected_action_index + 1}")

    def duplicate_action(self):
        if 0 <= self.selected_action_index < len(self.deploy_actions):
            act = dict(self.deploy_actions[self.selected_action_index])
            act["id"] = f"act_{len(self.deploy_actions) + 1}"
            act["x"] = min(1550, act["x"] + 25)
            act["y"] = min(850, act["y"] + 25)
            self.deploy_actions.append(act)
            self.selected_action_index = len(self.deploy_actions) - 1
            self.push_to_history()
            self.populate_all_views()
            self.status_label.setText(f"📋 Nhân bản Action -> #{len(self.deploy_actions)}")

    def delete_action(self):
        if 0 <= self.selected_action_index < len(self.deploy_actions):
            deleted = self.deploy_actions.pop(self.selected_action_index)
            if self.selected_action_index >= len(self.deploy_actions):
                self.selected_action_index = len(self.deploy_actions) - 1
            self.push_to_history()
            self.populate_all_views()
            self.status_label.setText(f"🗑️ Đã xóa Action {deleted.get('unit_name')} [{deleted.get('tag', '')}]")

    def move_action_up(self):
        row = self.selected_action_index
        if row > 0:
            self.deploy_actions[row], self.deploy_actions[row - 1] = self.deploy_actions[row - 1], self.deploy_actions[row]
            self.selected_action_index = row - 1
            self.push_to_history()
            self.populate_all_views()
            self.status_label.setText(f"⬆️ Chuyển Action lên vị trí #{row}")

    def move_action_down(self):
        row = self.selected_action_index
        if 0 <= row < len(self.deploy_actions) - 1:
            self.deploy_actions[row], self.deploy_actions[row + 1] = self.deploy_actions[row + 1], self.deploy_actions[row]
            self.selected_action_index = row + 1
            self.push_to_history()
            self.populate_all_views()
            self.status_label.setText(f"⬇️ Chuyển Action xuống vị trí #{row + 2}")

    # --- VIEW SELECTION SYNCHRONIZATION ---
    def select_row_in_views(self, index):
        if not (0 <= index < len(self.deploy_actions)):
            return
        act = self.deploy_actions[index]

        # Update Inspector inputs
        self.spin_x.setValue(act["x"])
        self.spin_y.setValue(act["y"])
        self.spin_repeat.setValue(act.get("repeat_count", 1))
        self.spin_delay.setValue(act.get("delay", 0.5))
        self.chk_enabled.setChecked(act.get("enabled", True))
        self.tag_combo.setCurrentText(act.get("tag", "Main Army"))

        combo_idx = self.unit_combo.findData(act["unit_id"])
        if combo_idx >= 0:
            self.unit_combo.setCurrentIndex(combo_idx)

        # Select table row
        if not self.is_grouped_view:
            for row in range(self.table_view.rowCount()):
                item = self.table_view.item(row, 0)
                if item and item.data(Qt.UserRole) == index:
                    self.table_view.blockSignals(True)
                    self.table_view.selectRow(row)
                    self.table_view.blockSignals(False)
                    break

        self.redraw_frame()

    def on_table_selection_changed(self):
        selected_rows = self.table_view.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            idx_item = self.table_view.item(row, 0)
            if idx_item:
                orig_index = idx_item.data(Qt.UserRole)
                if orig_index is not None and 0 <= orig_index < len(self.deploy_actions):
                    self.selected_action_index = orig_index
                    self.select_row_in_views(orig_index)

    def on_tree_selection_changed(self):
        selected_items = self.tree_view.selectedItems()
        if selected_items:
            item = selected_items[0]
            orig_index = item.data(0, Qt.UserRole)
            if orig_index is not None and 0 <= orig_index < len(self.deploy_actions):
                self.selected_action_index = orig_index
                self.select_row_in_views(orig_index)

    def populate_all_views(self):
        self.populate_table_view()
        self.populate_tree_view()
        self.redraw_frame()

    def populate_table_view(self):
        self.table_view.blockSignals(True)
        self.table_view.setRowCount(0)

        visible_count = 0
        for idx, act in enumerate(self.deploy_actions):
            tag = act.get("tag", "Main Army")
            if self.active_tag_filter != "All Tags" and tag != self.active_tag_filter:
                continue

            row = self.table_view.rowCount()
            self.table_view.insertRow(row)

            # Execution order #
            item_order = QTableWidgetItem(f"#{idx + 1}")
            item_order.setData(Qt.UserRole, idx)
            item_order.setFont(QFont("Consolas", 9, QFont.Bold))

            # Enabled Status
            status_str = "✓ On" if act.get("enabled", True) else "X Off"
            item_status = QTableWidgetItem(status_str)
            item_status.setForeground(QBrush(QColor("#10B981") if act.get("enabled", True) else QColor("#EF4444")))

            # Unit
            item_unit = QTableWidgetItem(act.get("unit_name", ""))

            # Tag with Pill Color
            item_tag = QTableWidgetItem(f"[{tag}]")
            t_color = get_tag_color(tag)
            item_tag.setForeground(QBrush(t_color["qt"]))
            item_tag.setFont(QFont("Consolas", 9, QFont.Bold))

            # Coords
            item_coords = QTableWidgetItem(f"({act['x']}, {act['y']})")

            # Repeat
            item_repeat = QTableWidgetItem(f"x{act.get('repeat_count', 1)}")

            # Delay
            item_delay = QTableWidgetItem(f"{act.get('delay', 0.5)}s")

            for col, item in enumerate([item_order, item_status, item_unit, item_tag, item_coords, item_repeat, item_delay]):
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table_view.setItem(row, col, item)

            if idx == self.selected_action_index:
                self.table_view.selectRow(row)
            visible_count += 1

        self.table_view.blockSignals(False)

    def populate_tree_view(self):
        self.tree_view.blockSignals(True)
        self.tree_view.clear()

        # Group actions by tag
        groups = {}
        for idx, act in enumerate(self.deploy_actions):
            tag = act.get("tag", "Main Army")
            if self.active_tag_filter != "All Tags" and tag != self.active_tag_filter:
                continue
            if tag not in groups:
                groups[tag] = []
            groups[tag].append((idx, act))

        for tag, items in groups.items():
            t_color = get_tag_color(tag)
            group_header = QTreeWidgetItem(self.tree_view)
            group_header.setText(0, f"▼ {tag} ({len(items)} actions)")
            group_header.setForeground(0, QBrush(t_color["qt"]))
            group_header.setFont(0, QFont("Segoe UI", 10, QFont.Bold))

            for idx, act in items:
                child = QTreeWidgetItem(group_header)
                child.setText(0, f"  #{idx + 1} {act.get('unit_name')}")
                child.setText(1, f"[{tag}]")
                child.setText(2, f"({act['x']}, {act['y']})")
                child.setText(3, f"x{act.get('repeat_count', 1)}")
                child.setText(4, f"{act.get('delay', 0.5)}s")
                child.setData(0, Qt.UserRole, idx)

            group_header.setExpanded(True)

        self.tree_view.blockSignals(False)

    def update_frame(self, frame):
        self.current_frame = frame
        self.redraw_frame()

    def redraw_frame(self):
        if self.current_frame is None:
            bg = np.zeros((900, 1600, 3), dtype=np.uint8)
            bg[:, :] = (20, 24, 30)
            for x in range(0, 1600, 100):
                cv2.line(bg, (x, 0), (x, 900), (35, 42, 52), 1)
            for y in range(0, 900, 100):
                cv2.line(bg, (0, y), (1600, y), (35, 42, 52), 1)
            cv2.putText(bg, "TACTICAL LIVE BATTLEFIELD PREVIEW (1600 x 900)", (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 116, 139), 2)
            frame = bg
        else:
            frame = self.current_frame.copy()

        h, w, c = frame.shape
        self.img_label.pixmap_original_size = (w, h)

        # Render Crosshairs if active dragging or in move mode
        if self.is_dragging_marker and 0 <= self.drag_target_index < len(self.deploy_actions):
            drag_act = self.deploy_actions[self.drag_target_index]
            drag_x, drag_y = drag_act["x"], drag_act["y"]
            cv2.line(frame, (drag_x, 0), (drag_x, h), (0, 215, 255), 1, cv2.LINE_AA)
            cv2.line(frame, (0, drag_y), (w, drag_y), (0, 215, 255), 1, cv2.LINE_AA)

        # Draw Live Deploy Action Markers
        for idx, act in enumerate(self.deploy_actions):
            if not act.get("enabled", True):
                continue
            x, y = act["x"], act["y"]
            tag = act.get("tag", "Main Army")

            # Check tag filter
            if self.active_tag_filter != "All Tags" and tag != self.active_tag_filter:
                continue

            t_color = get_tag_color(tag)
            bgr_color = t_color["bgr"]

            is_being_dragged = self.is_dragging_marker and self.drag_target_index == idx
            is_selected = idx == self.selected_action_index

            if is_being_dragged:
                cv2.circle(frame, (x, y), 28, (0, 215, 255), 3, cv2.LINE_AA)
                cv2.circle(frame, (x, y), 18, bgr_color, -1)
                cv2.circle(frame, (x, y), 20, (255, 255, 255), 2)
            elif is_selected:
                cv2.circle(frame, (x, y), 24, (0, 215, 255), 3, cv2.LINE_AA)
                cv2.circle(frame, (x, y), 17, bgr_color, -1)
                cv2.circle(frame, (x, y), 19, (255, 255, 255), 2)
            else:
                cv2.circle(frame, (x, y), 16, bgr_color, -1)
                cv2.circle(frame, (x, y), 18, (255, 255, 255), 2)

            # Order number inside marker
            num_str = str(idx + 1)
            font_scale = 0.5 if len(num_str) <= 2 else 0.4
            offset_x = 5 if len(num_str) == 1 else (9 if len(num_str) == 2 else 12)
            cv2.putText(
                frame,
                num_str,
                (x - offset_x, y + 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            # Marker tag & info label below
            tag_txt = f"{act['unit_name']} ({x},{y}) [{tag}]"
            if is_being_dragged and self.is_shift_held:
                tag_txt += " [SNAP]"
            cv2.putText(frame, tag_txt, (x - 45, y + 36), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        bytes_per_line = 3 * w
        q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(q_img)

        lbl_w = max(self.img_label.width(), 360)
        lbl_h = max(self.img_label.height(), 260)
        scaled_pix = pix.scaled(lbl_w, lbl_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.img_label.setPixmap(scaled_pix)
