import os
import json
import copy
import cv2
import numpy as np
from typing import List, Dict, Any

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QSplitter,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsEllipseItem,
    QGraphicsTextItem,
    QGraphicsPixmapItem,
    QHeaderView,
    QAbstractItemView,
    QSizePolicy,
    QMenu,
    QInputDialog,
    QMessageBox
)
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QColor, QPen, QBrush, QFont, QPixmap, QImage, QTransform, QCursor, QPainter

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
    "Funnel Left": {"hex": "#3B82F6", "qt": QColor("#3B82F6")},
    "Funnel Right": {"hex": "#06B6D4", "qt": QColor("#06B6D4")},
    "Main Army": {"hex": "#10B981", "qt": QColor("#10B981")},
    "Heroes": {"hex": "#F59E0B", "qt": QColor("#F59E0B")},
    "Spells": {"hex": "#8B5CF6", "qt": QColor("#8B5CF6")},
    "Siege": {"hex": "#EF4444", "qt": QColor("#EF4444")},
    "Cleanup": {"hex": "#6B7280", "qt": QColor("#6B7280")},
    "Phase 1": {"hex": "#EC4899", "qt": QColor("#EC4899")},
    "Phase 2": {"hex": "#38BDF8", "qt": QColor("#38BDF8")},
    "Phase 3": {"hex": "#A855F7", "qt": QColor("#A855F7")}
}
DEFAULT_TAG_COLOR = {"hex": "#10B981", "qt": QColor("#10B981")}


class StrategyGraphicsView(QGraphicsView):
    """Custom QGraphicsView supporting mouse wheel zoom and middle button panning."""

    canvas_double_clicked = Signal(int, int)

    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        antialiasing = getattr(QPainter.RenderHint, 'Antialiasing', None) or getattr(QPainter, 'Antialiasing', None)
        smooth = getattr(QPainter.RenderHint, 'SmoothPixmapTransform', None) or getattr(QPainter, 'SmoothPixmapTransform', None)
        if antialiasing is not None:
            self.setRenderHint(antialiasing, True)
        if smooth is not None:
            self.setRenderHint(smooth, True)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setStyleSheet("QGraphicsView { border: 1px solid #27272A; background-color: #0A0A0C; border-radius: 8px; }")

        self._is_panning = False
        self._pan_start = QPointF()

    def wheelEvent(self, event):
        zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15
        self.scale(zoom_factor, zoom_factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._is_panning = True
            self._pan_start = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_panning:
            delta = event.position() - self._pan_start
            self._pan_start = event.position()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - int(delta.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(delta.y()))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._is_panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.position().toPoint())
            x = max(0, min(1600, int(scene_pos.x())))
            y = max(0, min(900, int(scene_pos.y())))
            self.canvas_double_clicked.emit(x, y)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


class StrategyMarkerItem(QGraphicsEllipseItem):
    """Interactive Draggable Marker Item on Canvas."""

    def __init__(self, index: int, action_data: Dict[str, Any], parent_tab):
        super().__init__(-14, -14, 28, 28)
        self.index = index
        self.action_data = action_data
        self.parent_tab = parent_tab
        self._updating_from_code = False

        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self.setPos(float(action_data.get("x", 800)), float(action_data.get("y", 450)))
        self.setZValue(10)

        self.setToolTip(f"#{index + 1}: {action_data.get('unit_name', 'Deploy')}")

        self.number_item = QGraphicsTextItem(str(index + 1), self)
        self.number_item.setDefaultTextColor(QColor("#FFFFFF"))
        font = QFont("Consolas", 10, QFont.Bold)
        self.number_item.setFont(font)
        self.number_item.setPos(14, -12)

        self.update_appearance(False)

    def update_appearance(self, selected: bool):
        enabled = self.action_data.get("enabled", True)
        tag = self.action_data.get("tag", "Main Army")
        tag_color = TAG_COLOR_MAP.get(tag, DEFAULT_TAG_COLOR)["qt"]

        if selected:
            self.setPen(QPen(QColor("#00D7FF"), 3))
            self.setBrush(QBrush(tag_color if enabled else QColor("#6B7280")))
            self.setZValue(20)
        else:
            self.setPen(QPen(QColor("#FFFFFF"), 2))
            self.setBrush(QBrush(tag_color if enabled else QColor("#3F3F46")))
            self.setZValue(10)

    def contextMenuEvent(self, event):
        menu = QMenu()
        act_del = menu.addAction("🗑️ Delete Point")
        act_dup = menu.addAction("📋 Duplicate Point")
        act_toggle = menu.addAction("👁️ Toggle Enabled/Disabled")

        exec_fn = getattr(menu, 'exec', None) or getattr(menu, 'exec_', None)
        chosen = exec_fn(event.screenPos())
        if chosen == act_del:
            self.parent_tab.delete_point_at_index(self.index)
        elif chosen == act_dup:
            self.parent_tab.duplicate_point_at_index(self.index)
        elif chosen == act_toggle:
            self.parent_tab.toggle_point_enabled(self.index)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and not self._updating_from_code:
            if self.parent_tab:
                new_pos = value
                x = max(0, min(1600, int(new_pos.x())))
                y = max(0, min(900, int(new_pos.y())))
                self.parent_tab.on_marker_dragged(self.index, x, y)
        elif change == QGraphicsItem.ItemSelectedHasChanged:
            if value and not self._updating_from_code:
                if self.parent_tab:
                    self.parent_tab.select_action(self.index)
        return super().itemChange(change, value)


class StrategyTab(QWidget):
    """Standalone Dedicated Strategy Manager & Random Config Tab."""

    config_changed = Signal()

    def __init__(self, device: str = "emulator-5554"):
        super().__init__()
        self.device = device

        self.random_mode = "Sequential"
        self.random_configs: List[Dict[str, Any]] = []
        self.active_config_index = 0
        self.deploy_actions: List[Dict[str, Any]] = []

        self.selected_action_index = -1
        self.markers: List[StrategyMarkerItem] = []
        self._block_signals = False
        self.current_frame = None
        self.bg_item = None

        self.init_ui()
        self.load_battlefield_background()
        self.ensure_default_configs()

    def ensure_default_configs(self):
        if not self.random_configs:
            self.random_configs = [{
                "id": "cfg_1",
                "name": "Config 1",
                "enabled": True,
                "deploy_actions": [
                    {
                        "id": "act_1",
                        "unit_id": "dragon",
                        "unit_name": "Dragon",
                        "unit_type": "troop",
                        "x": 800,
                        "y": 450,
                        "repeat_count": 1,
                        "delay": 0.5,
                        "enabled": True,
                        "tag": "Main Army"
                    }
                ]
            }]
            self.active_config_index = 0
            self.deploy_actions = copy.deepcopy(self.random_configs[0]["deploy_actions"])

        self.populate_config_list()
        self.populate_action_table()
        self.build_markers()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- TOP HEADER BAR ---
        top_bar = QGroupBox("🎲 Strategy Manager & Random Execution Settings")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(12, 8, 12, 8)
        top_layout.setSpacing(12)

        top_layout.addWidget(QLabel("Execution Mode:"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["🔄 Sequential (Lần lượt 1→2→3...)", "🎲 Random (Chọn ngẫu nhiên)"])
        self.combo_mode.currentIndexChanged.connect(self.on_mode_changed)
        top_layout.addWidget(self.combo_mode)

        top_layout.addSpacing(15)
        self.lbl_active_summary = QLabel("Active: Config 1 (1 points)")
        self.lbl_active_summary.setStyleSheet("font-weight: 700; color: #60A5FA; font-size: 13px;")
        top_layout.addWidget(self.lbl_active_summary)

        top_layout.addStretch()

        self.btn_save = QPushButton("💾 Save Strategy Configs")
        self.btn_save.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; padding: 6px 16px;")
        self.btn_save.clicked.connect(self.save_to_file)

        self.status_badge = QLabel("✅ Synced")
        self.status_badge.setStyleSheet("background-color: #065F46; color: #34D399; padding: 4px 10px; border-radius: 10px; font-weight: bold;")

        top_layout.addWidget(self.status_badge)
        top_layout.addWidget(self.btn_save)

        main_layout.addWidget(top_bar)

        # --- MAIN SPLITTER ---
        self.main_splitter = QSplitter(Qt.Horizontal)

        # =========================================================================
        # 1. LEFT PANEL: Configs List & Deploy Points List
        # =========================================================================
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # Configs Box
        cfg_box = QGroupBox("📋 Strategy Configs List")
        cfg_box_layout = QVBoxLayout(cfg_box)

        self.list_configs = QListWidget()
        self.list_configs.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_configs.setDragDropMode(QAbstractItemView.InternalMove)
        self.list_configs.itemSelectionChanged.connect(self.on_config_selected)
        self.list_configs.model().rowsMoved.connect(self.on_configs_reordered)
        cfg_box_layout.addWidget(self.list_configs)

        cfg_btn_layout = QHBoxLayout()
        self.btn_add_cfg = QPushButton("➕ Add")
        self.btn_add_cfg.clicked.connect(self.add_config)
        self.btn_dup_cfg = QPushButton("📋 Duplicate")
        self.btn_dup_cfg.clicked.connect(self.duplicate_config)
        self.btn_rename_cfg = QPushButton("✏️ Rename")
        self.btn_rename_cfg.clicked.connect(self.rename_config)
        self.btn_del_cfg = QPushButton("🗑️ Delete")
        self.btn_del_cfg.setStyleSheet("background-color: #991B1B; color: white;")
        self.btn_del_cfg.clicked.connect(self.delete_config)

        cfg_btn_layout.addWidget(self.btn_add_cfg)
        cfg_btn_layout.addWidget(self.btn_dup_cfg)
        cfg_btn_layout.addWidget(self.btn_rename_cfg)
        cfg_btn_layout.addWidget(self.btn_del_cfg)
        cfg_box_layout.addLayout(cfg_btn_layout)

        left_layout.addWidget(cfg_box, stretch=1)

        # Actions Sequence Box
        pts_box = QGroupBox("🎯 Deploy Actions Sequence")
        pts_box_layout = QVBoxLayout(pts_box)

        self.table_actions = QTableWidget(0, 5)
        self.table_actions.setHorizontalHeaderLabels(["#", "Unit", "Coord", "Rpt", "Delay"])
        self.table_actions.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_actions.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_actions.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_actions.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_actions.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table_actions.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_actions.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_actions.itemSelectionChanged.connect(self.on_action_table_selected)
        pts_box_layout.addWidget(self.table_actions)

        pts_btn_layout = QHBoxLayout()
        self.btn_add_pt = QPushButton("➕ Add Point")
        self.btn_add_pt.clicked.connect(self.add_point)
        self.btn_dup_pt = QPushButton("📋 Duplicate")
        self.btn_dup_pt.clicked.connect(self.duplicate_point)
        self.btn_del_pt = QPushButton("🗑️ Remove")
        self.btn_del_pt.clicked.connect(self.delete_point)
        self.btn_up_pt = QPushButton("⬆️")
        self.btn_up_pt.clicked.connect(self.move_point_up)
        self.btn_dn_pt = QPushButton("⬇️")
        self.btn_dn_pt.clicked.connect(self.move_point_down)

        pts_btn_layout.addWidget(self.btn_add_pt)
        pts_btn_layout.addWidget(self.btn_dup_pt)
        pts_btn_layout.addWidget(self.btn_del_pt)
        pts_btn_layout.addWidget(self.btn_up_pt)
        pts_btn_layout.addWidget(self.btn_dn_pt)
        pts_box_layout.addLayout(pts_btn_layout)

        left_layout.addWidget(pts_box, stretch=2)

        self.main_splitter.addWidget(left_widget)

        # =========================================================================
        # 2. CENTER PANEL: Battlefield Canvas Editor (Maximizing screen space)
        # =========================================================================
        center_widget = QGroupBox("🗺️ Interactive Battlefield Visual Editor")
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(8, 8, 8, 8)

        # Canvas Control Toolbar
        canvas_tools = QHBoxLayout()
        self.btn_fit = QPushButton("🔍 Fit Window")
        self.btn_fit.clicked.connect(self.fit_canvas)
        self.btn_reset_zoom = QPushButton("🔄 Reset Zoom")
        self.btn_reset_zoom.clicked.connect(self.reset_canvas_zoom)
        self.btn_zoom_in = QPushButton("➕")
        self.btn_zoom_in.clicked.connect(lambda: self.graphics_view.scale(1.2, 1.2))
        self.btn_zoom_out = QPushButton("➖")
        self.btn_zoom_out.clicked.connect(lambda: self.graphics_view.scale(1.0 / 1.2, 1.0 / 1.2))

        lbl_hint = QLabel("💡 Tip: Double-click canvas to add point. Middle-click drag to pan. Wheel to zoom.")
        lbl_hint.setStyleSheet("color: #71717A; font-size: 11px;")

        canvas_tools.addWidget(self.btn_fit)
        canvas_tools.addWidget(self.btn_reset_zoom)
        canvas_tools.addWidget(self.btn_zoom_in)
        canvas_tools.addWidget(self.btn_zoom_out)
        canvas_tools.addSpacing(10)
        canvas_tools.addWidget(lbl_hint)
        canvas_tools.addStretch()

        center_layout.addLayout(canvas_tools)

        # Scene & View
        self.graphics_scene = QGraphicsScene(0, 0, 1600, 900)
        self.graphics_view = StrategyGraphicsView(self.graphics_scene)
        self.graphics_view.canvas_double_clicked.connect(self.on_canvas_double_clicked)
        center_layout.addWidget(self.graphics_view, stretch=1)

        self.main_splitter.addWidget(center_widget)

        # =========================================================================
        # 3. RIGHT PANEL: Point Property Inspector
        # =========================================================================
        right_widget = QGroupBox("⚙️ Point Inspector")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)

        self.lbl_point_idx = QLabel("Selected Point: None")
        self.lbl_point_idx.setStyleSheet("font-size: 14px; font-weight: 800; color: #60A5FA;")
        right_layout.addWidget(self.lbl_point_idx)

        # Unit / Troop
        right_layout.addWidget(QLabel("Unit / Troop:"))
        self.combo_unit = QComboBox()
        for u in UNIT_CATALOG:
            self.combo_unit.addItem(f"{u['name']} ({u['type']})", u['id'])
        self.combo_unit.currentIndexChanged.connect(self.on_inspector_changed)
        right_layout.addWidget(self.combo_unit)

        # Tag / Phase
        right_layout.addWidget(QLabel("Tag / Phase:"))
        self.combo_tag = QComboBox()
        self.combo_tag.addItems(PRESET_TAGS)
        self.combo_tag.currentIndexChanged.connect(self.on_inspector_changed)
        right_layout.addWidget(self.combo_tag)

        # Coordinates
        coord_layout = QHBoxLayout()
        vbox_x = QVBoxLayout()
        vbox_x.addWidget(QLabel("X (0..1600):"))
        self.spin_x = QSpinBox()
        self.spin_x.setRange(0, 1600)
        self.spin_x.valueChanged.connect(self.on_inspector_coord_changed)
        vbox_x.addWidget(self.spin_x)

        vbox_y = QVBoxLayout()
        vbox_y.addWidget(QLabel("Y (0..900):"))
        self.spin_y = QSpinBox()
        self.spin_y.setRange(0, 900)
        self.spin_y.valueChanged.connect(self.on_inspector_coord_changed)
        vbox_y.addWidget(self.spin_y)

        coord_layout.addLayout(vbox_x)
        coord_layout.addLayout(vbox_y)
        right_layout.addLayout(coord_layout)

        # Delay & Repeat
        param_layout = QHBoxLayout()
        vbox_rep = QVBoxLayout()
        vbox_rep.addWidget(QLabel("Repeat Count:"))
        self.spin_repeat = QSpinBox()
        self.spin_repeat.setRange(1, 100)
        self.spin_repeat.valueChanged.connect(self.on_inspector_changed)
        vbox_rep.addWidget(self.spin_repeat)

        vbox_del = QVBoxLayout()
        vbox_del.addWidget(QLabel("Delay (sec):"))
        self.spin_delay = QDoubleSpinBox()
        self.spin_delay.setRange(0.0, 30.0)
        self.spin_delay.setSingleStep(0.1)
        self.spin_delay.setValue(0.5)
        self.spin_delay.valueChanged.connect(self.on_inspector_changed)
        vbox_del.addWidget(self.spin_delay)

        param_layout.addLayout(vbox_rep)
        param_layout.addLayout(vbox_del)
        right_layout.addLayout(param_layout)

        # Enabled Checkbox
        self.chk_enabled = QCheckBox("Enable this deploy point")
        self.chk_enabled.setChecked(True)
        self.chk_enabled.toggled.connect(self.on_inspector_changed)
        right_layout.addWidget(self.chk_enabled)

        right_layout.addStretch()

        self.main_splitter.addWidget(right_widget)

        # Set stretch factors for splitter (Left=320, Center=Expanded, Right=260)
        self.main_splitter.setSizes([320, 750, 260])
        main_layout.addWidget(self.main_splitter, stretch=1)

    def update_frame(self, frame):
        """Live stream screenshot frame update for the interactive visual canvas."""
        if frame is None or not hasattr(frame, 'shape'):
            return
        self.current_frame = frame
        try:
            h, w, c = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            bytes_per_line = c * w
            qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pix = QPixmap.fromImage(qimg)
            if pix.isNull():
                return
            pix = pix.scaled(1600, 900, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

            if hasattr(self, 'bg_item') and self.bg_item is not None and self.bg_item.scene() == self.graphics_scene:
                self.bg_item.setPixmap(pix)
            else:
                if hasattr(self, 'bg_item') and self.bg_item is not None:
                    try:
                        self.graphics_scene.removeItem(self.bg_item)
                    except Exception:
                        pass
                self.bg_item = QGraphicsPixmapItem(pix)
                self.bg_item.setZValue(0)
                self.graphics_scene.addItem(self.bg_item)
        except Exception as e:
            print("Error updating frame in StrategyTab:", e)

    def load_battlefield_background(self):
        self.graphics_scene.clear()
        self.markers.clear()
        self.bg_item = None

        if hasattr(self, 'current_frame') and self.current_frame is not None:
            self.update_frame(self.current_frame)
            return

        # Try to load current device screenshot or fallback
        screen_path = os.path.join("temp", "screen.png")
        if os.path.exists(screen_path):
            pix = QPixmap(screen_path)
            if not pix.isNull():
                pix = pix.scaled(1600, 900, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                self.bg_item = QGraphicsPixmapItem(pix)
                self.bg_item.setZValue(0)
                self.graphics_scene.addItem(self.bg_item)
                return

        # Fallback dark tactical grid
        img = QImage(1600, 900, QImage.Format_RGB32)
        img.fill(QColor("#111827"))
        pix = QPixmap.fromImage(img)
        self.bg_item = QGraphicsPixmapItem(pix)
        self.bg_item.setZValue(0)
        self.graphics_scene.addItem(self.bg_item)

        # Grid lines
        pen = QPen(QColor("#1F2937"), 1, Qt.DashLine)
        for x in range(0, 1600, 100):
            line = self.graphics_scene.addLine(x, 0, x, 900, pen)
            line.setZValue(1)
        for y in range(0, 900, 100):
            line = self.graphics_scene.addLine(0, y, 1600, y, pen)
            line.setZValue(1)

        # Center crosshair
        center_pen = QPen(QColor("#374151"), 2)
        self.graphics_scene.addLine(800, 0, 800, 900, center_pen).setZValue(2)
        self.graphics_scene.addLine(0, 450, 1600, 450, center_pen).setZValue(2)

    # --- CONFIG MANAGEMENT LOGIC ---

    def populate_config_list(self):
        self._block_signals = True
        self.list_configs.clear()

        for idx, cfg in enumerate(self.random_configs):
            pts = len(cfg.get("deploy_actions", []))
            name = cfg.get("name", f"Config {idx + 1}")
            enabled = cfg.get("enabled", True)

            item = QListWidgetItem()
            item.setText(f"{name} ({pts} pts)")
            item.setCheckState(Qt.Checked if enabled else Qt.Unchecked)
            item.setData(Qt.UserRole, idx)

            self.list_configs.addItem(item)

        if 0 <= self.active_config_index < self.list_configs.count():
            self.list_configs.setCurrentRow(self.active_config_index)

        self.update_active_summary_label()
        self._block_signals = False

    def update_active_summary_label(self):
        if 0 <= self.active_config_index < len(self.random_configs):
            cfg = self.random_configs[self.active_config_index]
            self.lbl_active_summary.setText(f"📂 Active: {cfg.get('name')} ({len(self.deploy_actions)} points)")

    def sync_active_config_actions(self):
        if 0 <= self.active_config_index < len(self.random_configs):
            self.random_configs[self.active_config_index]["deploy_actions"] = copy.deepcopy(self.deploy_actions)

    def on_mode_changed(self, index: int):
        if self._block_signals:
            return
        self.random_mode = "Sequential" if index == 0 else "Random"
        self.mark_unsaved()

    def on_config_selected(self):
        if self._block_signals:
            return

        row = self.list_configs.currentRow()
        if row < 0 or row >= len(self.random_configs):
            return

        self.sync_active_config_actions()
        self.active_config_index = row
        self.deploy_actions = copy.deepcopy(self.random_configs[row].get("deploy_actions", []))
        self.selected_action_index = 0 if self.deploy_actions else -1

        self.update_active_summary_label()
        self.populate_action_table()
        self.build_markers()

        if self.deploy_actions:
            self.select_action(0)

    def on_configs_reordered(self):
        if self._block_signals:
            return
        # Reconstruct random_configs array based on ListWidget item order
        new_configs = []
        for row in range(self.list_configs.count()):
            item = self.list_configs.item(row)
            orig_idx = item.data(Qt.UserRole)
            if 0 <= orig_idx < len(self.random_configs):
                cfg = self.random_configs[orig_idx]
                cfg["enabled"] = (item.checkState() == Qt.Checked)
                new_configs.append(cfg)

        self.random_configs = new_configs
        self.active_config_index = max(0, self.list_configs.currentRow())
        self.populate_config_list()
        self.mark_unsaved()

    def add_config(self):
        name, ok = QInputDialog.getText(self, "Tạo Config mới", "Tên Strategy Config:")
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

            self.populate_config_list()
            self.populate_action_table()
            self.build_markers()
            self.mark_unsaved()

    def duplicate_config(self):
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

        self.populate_config_list()
        self.populate_action_table()
        self.build_markers()
        self.mark_unsaved()

    def rename_config(self):
        if not (0 <= self.active_config_index < len(self.random_configs)):
            return

        curr_name = self.random_configs[self.active_config_index].get("name", "")
        name, ok = QInputDialog.getText(self, "Đổi tên Config", "Tên mới:", text=curr_name)
        if ok and name.strip():
            self.random_configs[self.active_config_index]["name"] = name.strip()
            self.populate_config_list()
            self.mark_unsaved()

    def delete_config(self):
        if len(self.random_configs) <= 1:
            QMessageBox.warning(self, "Cảnh báo", "Phải giữ lại ít nhất 1 Config!")
            return

        if 0 <= self.active_config_index < len(self.random_configs):
            self.random_configs.pop(self.active_config_index)
            self.active_config_index = max(0, self.active_config_index - 1)
            self.deploy_actions = copy.deepcopy(self.random_configs[self.active_config_index].get("deploy_actions", []))

            self.populate_config_list()
            self.populate_action_table()
            self.build_markers()
            self.mark_unsaved()

    # --- DEPLOY ACTIONS TABLE & MARKERS LOGIC ---

    def populate_action_table(self):
        self._block_signals = True
        self.table_actions.setRowCount(0)

        for idx, act in enumerate(self.deploy_actions):
            row = self.table_actions.rowCount()
            self.table_actions.insertRow(row)

            # #
            item_num = QTableWidgetItem(f"#{idx + 1}")
            item_num.setData(Qt.UserRole, idx)
            item_num.setTextAlignment(Qt.AlignCenter)

            # Unit
            unit_name = act.get("unit_name", act.get("unit_id", "Dragon"))
            item_unit = QTableWidgetItem(unit_name)

            # Coord
            coord_str = f"({act.get('x', 800)}, {act.get('y', 450)})"
            item_coord = QTableWidgetItem(coord_str)
            item_coord.setTextAlignment(Qt.AlignCenter)

            # Repeat
            item_rpt = QTableWidgetItem(f"x{act.get('repeat_count', 1)}")
            item_rpt.setTextAlignment(Qt.AlignCenter)

            # Delay
            item_delay = QTableWidgetItem(f"{act.get('delay', 0.5)}s")
            item_delay.setTextAlignment(Qt.AlignCenter)

            self.table_actions.setItem(row, 0, item_num)
            self.table_actions.setItem(row, 1, item_unit)
            self.table_actions.setItem(row, 2, item_coord)
            self.table_actions.setItem(row, 3, item_rpt)
            self.table_actions.setItem(row, 4, item_delay)

        self._block_signals = False

    def build_markers(self):
        self._block_signals = True
        # Keep background items (ZValue < 5)
        for item in list(self.graphics_scene.items()):
            if item.zValue() >= 5:
                self.graphics_scene.removeItem(item)

        self.markers.clear()
        for idx, act in enumerate(self.deploy_actions):
            marker = StrategyMarkerItem(idx, act, self)
            self.graphics_scene.addItem(marker)
            self.markers.append(marker)

        self._block_signals = False

    def select_action(self, index: int):
        if not (0 <= index < len(self.deploy_actions)):
            self.selected_action_index = -1
            self.lbl_point_idx.setText("Selected Point: None")
            return

        self._block_signals = True
        self.selected_action_index = index
        act = self.deploy_actions[index]

        # Update Inspector controls
        self.lbl_point_idx.setText(f"Selected Point: #{index + 1}")

        # Unit combo
        u_idx = self.combo_unit.findData(act.get("unit_id", "dragon"))
        if u_idx >= 0:
            self.combo_unit.setCurrentIndex(u_idx)

        # Tag combo
        t_idx = self.combo_tag.findText(act.get("tag", "Main Army"))
        if t_idx >= 0:
            self.combo_tag.setCurrentIndex(t_idx)

        self.spin_x.setValue(int(act.get("x", 800)))
        self.spin_y.setValue(int(act.get("y", 450)))
        self.spin_repeat.setValue(int(act.get("repeat_count", 1)))
        self.spin_delay.setValue(float(act.get("delay", 0.5)))
        self.chk_enabled.setChecked(bool(act.get("enabled", True)))

        # Update marker highlights
        for i, m in enumerate(self.markers):
            m.update_appearance(i == index)

        # Highlight table row
        for row in range(self.table_actions.rowCount()):
            item = self.table_actions.item(row, 0)
            if item and item.data(Qt.UserRole) == index:
                self.table_actions.selectRow(row)
                break

        self._block_signals = False

    def on_action_table_selected(self):
        if self._block_signals:
            return
        selected_rows = self.table_actions.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            item = self.table_actions.item(row, 0)
            if item:
                orig_idx = item.data(Qt.UserRole)
                if orig_idx is not None:
                    self.select_action(orig_idx)

    def on_marker_dragged(self, index: int, x: int, y: int):
        if not (0 <= index < len(self.deploy_actions)):
            return

        self.deploy_actions[index]["x"] = x
        self.deploy_actions[index]["y"] = y

        if index == self.selected_action_index:
            self._block_signals = True
            self.spin_x.setValue(x)
            self.spin_y.setValue(y)
            self._block_signals = False

        # Update cell in table
        for row in range(self.table_actions.rowCount()):
            item = self.table_actions.item(row, 0)
            if item and item.data(Qt.UserRole) == index:
                self.table_actions.item(row, 2).setText(f"({x}, {y})")
                break

        self.mark_unsaved()

    def on_inspector_coord_changed(self):
        if self._block_signals or not (0 <= self.selected_action_index < len(self.deploy_actions)):
            return

        x = self.spin_x.value()
        y = self.spin_y.value()
        idx = self.selected_action_index

        self.deploy_actions[idx]["x"] = x
        self.deploy_actions[idx]["y"] = y

        if idx < len(self.markers):
            m = self.markers[idx]
            m._updating_from_code = True
            m.setPos(x, y)
            m._updating_from_code = False

        for row in range(self.table_actions.rowCount()):
            item = self.table_actions.item(row, 0)
            if item and item.data(Qt.UserRole) == idx:
                self.table_actions.item(row, 2).setText(f"({x}, {y})")
                break

        self.mark_unsaved()

    def on_inspector_changed(self):
        if self._block_signals or not (0 <= self.selected_action_index < len(self.deploy_actions)):
            return

        idx = self.selected_action_index
        unit_id = self.combo_unit.currentData()
        unit_name = self.combo_unit.currentText().split(" (")[0]
        tag_val = self.combo_tag.currentText()
        repeat_cnt = self.spin_repeat.value()
        delay_val = self.spin_delay.value()
        is_enabled = self.chk_enabled.isChecked()

        self.deploy_actions[idx].update({
            "unit_id": unit_id,
            "unit_name": unit_name,
            "tag": tag_val,
            "repeat_count": repeat_cnt,
            "delay": delay_val,
            "enabled": is_enabled
        })

        if idx < len(self.markers):
            self.markers[idx].action_data = self.deploy_actions[idx]
            self.markers[idx].update_appearance(idx == self.selected_action_index)

        self.populate_action_table()
        self.select_action(idx)
        self.mark_unsaved()

    def on_canvas_double_clicked(self, x: int, y: int):
        new_idx = len(self.deploy_actions)
        act = {
            "id": f"act_{new_idx + 1}",
            "unit_id": "dragon",
            "unit_name": "Dragon",
            "unit_type": "troop",
            "x": x,
            "y": y,
            "repeat_count": 1,
            "delay": 0.5,
            "enabled": True,
            "tag": "Main Army"
        }
        self.deploy_actions.append(act)
        self.populate_action_table()
        self.build_markers()
        self.select_action(new_idx)
        self.mark_unsaved()

    # --- POINT EDIT BUTTONS ---

    def add_point(self):
        self.on_canvas_double_clicked(800, 450)

    def duplicate_point(self):
        if not (0 <= self.selected_action_index < len(self.deploy_actions)):
            return
        idx = self.selected_action_index
        act = copy.deepcopy(self.deploy_actions[idx])
        act["x"] = min(1600, act.get("x", 800) + 25)
        act["y"] = min(900, act.get("y", 450) + 25)
        self.deploy_actions.insert(idx + 1, act)

        self.populate_action_table()
        self.build_markers()
        self.select_action(idx + 1)
        self.mark_unsaved()

    def delete_point(self):
        if not (0 <= self.selected_action_index < len(self.deploy_actions)):
            return
        idx = self.selected_action_index
        self.deploy_actions.pop(idx)

        self.populate_action_table()
        self.build_markers()
        if self.deploy_actions:
            self.select_action(min(idx, len(self.deploy_actions) - 1))
        else:
            self.select_action(-1)
        self.mark_unsaved()

    def delete_point_at_index(self, index: int):
        if 0 <= index < len(self.deploy_actions):
            self.selected_action_index = index
            self.delete_point()

    def duplicate_point_at_index(self, index: int):
        if 0 <= index < len(self.deploy_actions):
            self.selected_action_index = index
            self.duplicate_point()

    def toggle_point_enabled(self, index: int):
        if 0 <= index < len(self.deploy_actions):
            curr = self.deploy_actions[index].get("enabled", True)
            self.deploy_actions[index]["enabled"] = not curr
            if index < len(self.markers):
                self.markers[index].update_appearance(index == self.selected_action_index)
            self.populate_action_table()
            self.mark_unsaved()

    def move_point_up(self):
        idx = self.selected_action_index
        if idx > 0:
            self.deploy_actions[idx], self.deploy_actions[idx - 1] = self.deploy_actions[idx - 1], self.deploy_actions[idx]
            self.populate_action_table()
            self.build_markers()
            self.select_action(idx - 1)
            self.mark_unsaved()

    def move_point_down(self):
        idx = self.selected_action_index
        if idx < len(self.deploy_actions) - 1:
            self.deploy_actions[idx], self.deploy_actions[idx + 1] = self.deploy_actions[idx + 1], self.deploy_actions[idx]
            self.populate_action_table()
            self.build_markers()
            self.select_action(idx + 1)
            self.mark_unsaved()

    def fit_canvas(self):
        self.graphics_view.fitInView(0, 0, 1600, 900, Qt.KeepAspectRatio)

    def reset_canvas_zoom(self):
        self.graphics_view.resetTransform()

    def mark_unsaved(self):
        self.sync_active_config_actions()
        self.populate_config_list()
        self.status_badge.setText("⚠️ Unsaved")
        self.status_badge.setStyleSheet("background-color: #991B1B; color: #FCA5A5; padding: 4px 10px; border-radius: 10px; font-weight: bold;")
        self.config_changed.emit()

    def mark_saved(self):
        self.status_badge.setText("✅ Synced")
        self.status_badge.setStyleSheet("background-color: #065F46; color: #34D399; padding: 4px 10px; border-radius: 10px; font-weight: bold;")

    def save_to_file(self):
        self.mark_saved()

    # --- DATA SERIALIZATION / INTERACTION WITH BOT_PAGE ---

    def apply_data(self, data: dict):
        self._block_signals = True
        self.random_mode = data.get("random_mode", "Sequential")
        raw_cfgs = data.get("random_configs", [])

        if not raw_cfgs:
            legacy_actions = data.get("deploy_actions", [])
            self.random_configs = [{
                "id": "cfg_1",
                "name": "Config 1",
                "enabled": True,
                "deploy_actions": copy.deepcopy(legacy_actions)
            }]
        else:
            self.random_configs = copy.deepcopy(raw_cfgs)

        self.active_config_index = 0
        if self.random_configs:
            self.deploy_actions = copy.deepcopy(self.random_configs[0].get("deploy_actions", []))
        else:
            self.deploy_actions = []

        self.combo_mode.setCurrentIndex(0 if self.random_mode == "Sequential" else 1)
        self.populate_config_list()
        self.populate_action_table()
        self.build_markers()

        if self.deploy_actions:
            self.select_action(0)

        self.mark_saved()
        self._block_signals = False

    def get_data(self) -> dict:
        self.sync_active_config_actions()
        return {
            "random_mode": self.random_mode,
            "random_configs": self.random_configs,
            "deploy_actions": self.deploy_actions
        }
