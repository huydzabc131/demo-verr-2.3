import os
import json
import math
import numpy as np
import cv2
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
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
    {"id": "baby_dragon", "name": "Baby Dragon", "type": "troop"},
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


class PreviewGraphicsView(QGraphicsView):
    """Custom QGraphicsView with mouse wheel zoom and middle button pan."""

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
        self.setStyleSheet("QGraphicsView { border: 2px solid #3F3F46; background-color: #0A0A0C; border-radius: 8px; }")

        self._is_panning = False
        self._pan_start = QPointF()

    def wheelEvent(self, event):
        """Zoom in/out with mouse wheel."""
        zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15
        self.scale(zoom_factor, zoom_factor)

    def mousePressEvent(self, event):
        """Middle mouse press triggers panning mode."""
        if event.button() == Qt.MiddleButton:
            self._is_panning = True
            self._pan_start = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Pan view when middle mouse button is held."""
        if self._is_panning:
            delta = event.position() - self._pan_start
            self._pan_start = event.position()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - int(delta.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(delta.y()))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Release panning mode."""
        if event.button() == Qt.MiddleButton:
            self._is_panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)


class DeployMarkerItem(QGraphicsEllipseItem):
    """Interactive Deploy Point Marker on QGraphicsScene."""

    def __init__(self, index: int, action_data: Dict[str, Any], parent_dialog):
        super().__init__(-14, -14, 28, 28)
        self.index = index
        self.action_data = action_data
        self.dialog = parent_dialog
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
        if selected:
            self.setPen(QPen(QColor("#00D7FF"), 3))
            self.setBrush(QBrush(QColor("#3B82F6" if enabled else "#6B7280")))
            self.setZValue(20)
        else:
            self.setPen(QPen(QColor("#FFFFFF"), 2))
            self.setBrush(QBrush(QColor("#10B981" if enabled else "#3F3F46")))
            self.setZValue(10)

    def contextMenuEvent(self, event):
        menu = QMenu()
        act_del = menu.addAction("🗑️ Delete Point")
        act_dup = menu.addAction("📋 Duplicate Point")
        act_toggle = menu.addAction("👁️ Toggle Enabled/Disabled")

        exec_fn = getattr(menu, 'exec', None) or getattr(menu, 'exec_', None)
        chosen = exec_fn(event.screenPos())
        if chosen == act_del:
            self.dialog.delete_point_at_index(self.index)
        elif chosen == act_dup:
            self.dialog.duplicate_point_at_index(self.index)
        elif chosen == act_toggle:
            self.dialog.toggle_point_enabled(self.index)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and not self._updating_from_code:
            if self.dialog:
                new_pos = value
                x = max(0, min(1600, int(new_pos.x())))
                y = max(0, min(900, int(new_pos.y())))
                self.dialog.on_marker_position_changed(self.index, x, y)

        elif change == QGraphicsItem.ItemSelectedHasChanged:
            is_sel = bool(value)
            self.update_appearance(is_sel)
            if is_sel and self.dialog and not self._updating_from_code:
                self.dialog.on_marker_selected(self.index)

        return super().itemChange(change, value)


class ConfigPreviewDialog(QDialog):
    """Visual Config Preview and Interactive Deploy Point Editor Dialog."""

    def __init__(self, profile_name: str, config_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.profile_name = profile_name
        self.config_data = json.loads(json.dumps(config_data))  # Deep copy

        self.random_mode = self.config_data.get("random_mode", "Sequential")
        raw_cfgs = self.config_data.get("random_configs", [])
        if not raw_cfgs:
            raw_cfgs = [{
                "id": "cfg_1",
                "name": "Config 1",
                "enabled": True,
                "deploy_actions": self.config_data.get("deploy_actions", [])
            }]
        self.random_configs = raw_cfgs
        self.active_config_index = 0
        self.deploy_actions = self.random_configs[0].get("deploy_actions", [])

        self.selected_index = -1
        self._block_signals = False
        self.markers: List[DeployMarkerItem] = []
        self.current_frame = None
        self.bg_item = None

        self.setWindowTitle(f"🔍 Visual Config Preview & Deploy Editor - [{profile_name}]")
        self.resize(1280, 800)
        self.setMinimumSize(960, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #121214;
                color: #F4F4F5;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QGroupBox {
                background-color: #18181B;
                border: 1px solid #27272A;
                border-radius: 8px;
                font-weight: 700;
                color: #60A5FA;
                margin-top: 8px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 2px 6px;
                background-color: #27272A;
                border-radius: 4px;
                color: #93C5FD;
            }
            QPushButton {
                background-color: #27272A;
                color: #F4F4F5;
                font-weight: 600;
                border-radius: 6px;
                border: 1px solid #3F3F46;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #3F3F46;
                border-color: #60A5FA;
            }
            QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #09090B;
                border: 1px solid #3F3F46;
                border-radius: 6px;
                padding: 5px 10px;
                color: #F4F4F5;
            }
            QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #3B82F6;
            }
            QLabel {
                color: #A1A1AA;
                font-size: 12px;
                font-weight: 600;
            }
        """)

        self.init_ui()
        self.load_battlefield_background()
        self.update_config_dropdown()
        self.build_markers()
        self.populate_table()

        if self.deploy_actions:
            self.select_action(0)


    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Header Toolbar
        header_box = QHBoxLayout()
        header_title = QLabel(f"🗺️ Battlefield Deploy Preview: {self.profile_name}")
        header_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #F4F4F5;")

        header_box.addWidget(header_title)
        header_box.addSpacing(15)

        header_box.addWidget(QLabel("Editing Config:"))
        self.combo_dialog_config = QComboBox()
        self.combo_dialog_config.setMinimumWidth(180)
        self.combo_dialog_config.currentIndexChanged.connect(self.on_dialog_config_changed)
        header_box.addWidget(self.combo_dialog_config)

        header_box.addStretch()

        self.btn_fit = QPushButton("🔍 Fit to Window")
        self.btn_fit.setToolTip("Thu/phóng vừa màn hình")
        self.btn_fit.clicked.connect(self.fit_to_window)

        self.btn_reset_zoom = QPushButton("1:1 Reset Zoom")
        self.btn_reset_zoom.setToolTip("Khôi phục tỷ lệ 100%")
        self.btn_reset_zoom.clicked.connect(self.reset_zoom)

        self.btn_save_changes = QPushButton("💾 Save Config")
        self.btn_save_changes.setStyleSheet("background-color: #10B981; color: white; font-weight: bold;")
        self.btn_save_changes.clicked.connect(self.accept)

        self.btn_cancel = QPushButton("✖ Close")
        self.btn_cancel.clicked.connect(self.reject)

        header_box.addWidget(self.btn_fit)
        header_box.addWidget(self.btn_reset_zoom)
        header_box.addWidget(self.btn_save_changes)
        header_box.addWidget(self.btn_cancel)

        main_layout.addLayout(header_box)

        # Main Splitter: Left (List) | Center (Canvas) | Right (Inspector)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        # --- LEFT PANEL: Deploy List ---
        left_box = QGroupBox("📋 Sequence List")
        left_layout = QVBoxLayout(left_box)
        left_layout.setContentsMargins(8, 10, 8, 8)

        self.table_view = QTableWidget()
        self.table_view.setColumnCount(5)
        self.table_view.setHorizontalHeaderLabels(["#", "Unit", "Coords", "Repeat", "Delay"])
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
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
        left_layout.addWidget(self.table_view)

        # List Action Buttons
        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("➕ Add Point")
        self.btn_add.setStyleSheet("background-color: #2563EB; color: white;")
        self.btn_add.clicked.connect(self.add_point)

        self.btn_delete = QPushButton("🗑️ Delete")
        self.btn_delete.setStyleSheet("background-color: #DC2626; color: white;")
        self.btn_delete.clicked.connect(self.delete_point)

        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_delete)
        left_layout.addLayout(btn_row)

        splitter.addWidget(left_box)

        # --- CENTER PANEL: Canvas QGraphicsView ---
        center_box = QGroupBox("🗺️ Interactive Battlefield Canvas")
        center_layout = QVBoxLayout(center_box)
        center_layout.setContentsMargins(8, 10, 8, 8)

        self.scene = QGraphicsScene(0, 0, 1600, 900)
        self.graphics_view = PreviewGraphicsView(self.scene, self)
        center_layout.addWidget(self.graphics_view)

        self.hint_label = QLabel("💡 Drag marker trên canvas để đổi vị trí. Roll mouse wheel = Zoom. Hold Middle Mouse = Pan view.")
        self.hint_label.setStyleSheet("color: #F59E0B; font-size: 11px; padding: 4px;")
        center_layout.addWidget(self.hint_label)

        splitter.addWidget(center_box)

        # --- RIGHT PANEL: Inspector ---
        right_box = QGroupBox("⚙️ Point Inspector")
        right_layout = QVBoxLayout(right_box)
        right_layout.setContentsMargins(10, 14, 10, 10)
        right_layout.setSpacing(12)

        # Unit Selector
        right_layout.addWidget(QLabel("Troop / Unit:"))
        self.combo_unit = QComboBox()
        for u in UNIT_CATALOG:
            self.combo_unit.addItem(f"{u['name']} ({u['type']})", u['id'])
        self.combo_unit.currentIndexChanged.connect(self.on_inspector_changed)
        right_layout.addWidget(self.combo_unit)

        # X Coordinate
        right_layout.addWidget(QLabel("X Coordinate:"))
        self.spin_x = QSpinBox()
        self.spin_x.setRange(0, 1600)
        self.spin_x.valueChanged.connect(self.on_inspector_coord_changed)
        right_layout.addWidget(self.spin_x)

        # Y Coordinate
        right_layout.addWidget(QLabel("Y Coordinate:"))
        self.spin_y = QSpinBox()
        self.spin_y.setRange(0, 900)
        self.spin_y.valueChanged.connect(self.on_inspector_coord_changed)
        right_layout.addWidget(self.spin_y)

        # Repeat
        right_layout.addWidget(QLabel("Repeat Count:"))
        self.spin_repeat = QSpinBox()
        self.spin_repeat.setRange(1, 100)
        self.spin_repeat.valueChanged.connect(self.on_inspector_changed)
        right_layout.addWidget(self.spin_repeat)

        # Delay
        right_layout.addWidget(QLabel("Delay (Seconds):"))
        self.spin_delay = QDoubleSpinBox()
        self.spin_delay.setRange(0.05, 10.0)
        self.spin_delay.setSingleStep(0.1)
        self.spin_delay.valueChanged.connect(self.on_inspector_changed)
        right_layout.addWidget(self.spin_delay)

        right_layout.addStretch()
        splitter.addWidget(right_box)

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 5)
        splitter.setStretchFactor(2, 2)

        main_layout.addWidget(splitter)

    def update_frame(self, frame):
        """Live stream frame update for preview dialog."""
        if frame is None or not hasattr(frame, 'shape'):
            return
        self.current_frame = frame
        try:
            h, w, c = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            q_img = QImage(rgb.data, w, h, c * w, QImage.Format_RGB888)
            pix = QPixmap.fromImage(q_img)
            if pix.isNull():
                return
            pix = pix.scaled(1600, 900, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

            if hasattr(self, 'bg_item') and self.bg_item is not None and self.bg_item.scene() == self.scene:
                self.bg_item.setPixmap(pix)
            else:
                if hasattr(self, 'bg_item') and self.bg_item is not None:
                    try:
                        self.scene.removeItem(self.bg_item)
                    except Exception:
                        pass
                self.bg_item = QGraphicsPixmapItem(pix)
                self.bg_item.setZValue(0)
                self.scene.addItem(self.bg_item)
        except Exception as e:
            print("Error updating frame in ConfigPreviewDialog:", e)

    def load_battlefield_background(self):
        """Loads screen screenshot or generates a dark tactical grid background."""
        self.bg_item = None
        if hasattr(self, 'current_frame') and self.current_frame is not None:
            self.update_frame(self.current_frame)
            return

        bg_pixmap = None
        if os.path.exists("temp/screen.png"):
            bg_pixmap = QPixmap("temp/screen.png")

        if not bg_pixmap or bg_pixmap.isNull():
            # Generate tactical battlefield grid image 1600x900
            bg = np.zeros((900, 1600, 3), dtype=np.uint8)
            bg[:, :] = (20, 24, 30)
            for x in range(0, 1600, 100):
                cv2.line(bg, (x, 0), (x, 900), (35, 42, 52), 1)
            for y in range(0, 900, 100):
                cv2.line(bg, (0, y), (1600, y), (35, 42, 52), 1)
            cv2.putText(bg, "TACTICAL BATTLEFIELD CANVAS (1600 x 900)", (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 116, 139), 2)
            
            rgb = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)
            q_img = QImage(rgb.data, 1600, 900, 3 * 1600, QImage.Format_RGB888)
            bg_pixmap = QPixmap.fromImage(q_img)

        self.bg_item = QGraphicsPixmapItem(bg_pixmap)
        self.bg_item.setZValue(0)
        self.scene.addItem(self.bg_item)

    def build_markers(self):
        """Create QGraphicsItem markers for all deploy points."""
        # Clear old markers
        for m in self.markers:
            self.scene.removeItem(m)
        self.markers.clear()

        for idx, act in enumerate(self.deploy_actions):
            marker = DeployMarkerItem(idx, act, self)
            self.scene.addItem(marker)
            self.markers.append(marker)

    def populate_table(self):
        """Populate left table view."""
        self._block_signals = True
        self.table_view.setRowCount(0)

        for idx, act in enumerate(self.deploy_actions):
            row = self.table_view.rowCount()
            self.table_view.insertRow(row)

            item_num = QTableWidgetItem(f"#{idx + 1}")
            item_num.setFont(QFont("Consolas", 9, QFont.Bold))
            item_num.setData(Qt.UserRole, idx)

            item_unit = QTableWidgetItem(act.get("unit_name", "Unit"))
            item_coords = QTableWidgetItem(f"({act.get('x', 0)}, {act.get('y', 0)})")
            item_repeat = QTableWidgetItem(f"x{act.get('repeat_count', 1)}")
            item_delay = QTableWidgetItem(f"{act.get('delay', 0.5)}s")

            for item in [item_num, item_unit, item_coords, item_repeat, item_delay]:
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)

            self.table_view.setItem(row, 0, item_num)
            self.table_view.setItem(row, 1, item_unit)
            self.table_view.setItem(row, 2, item_coords)
            self.table_view.setItem(row, 3, item_repeat)
            self.table_view.setItem(row, 4, item_delay)

        self._block_signals = False

    def select_action(self, index: int):
        """Select deploy action at index."""
        if not (0 <= index < len(self.deploy_actions)):
            return

        self.selected_index = index
        self._block_signals = True

        act = self.deploy_actions[index]

        # 1. Update Inspector Controls
        self.spin_x.setValue(act.get("x", 800))
        self.spin_y.setValue(act.get("y", 450))
        self.spin_repeat.setValue(act.get("repeat_count", 1))
        self.spin_delay.setValue(act.get("delay", 0.5))

        unit_idx = self.combo_unit.findData(act.get("unit_id", "dragon"))
        if unit_idx >= 0:
            self.combo_unit.setCurrentIndex(unit_idx)

        # 2. Update Table Selection
        for row in range(self.table_view.rowCount()):
            item = self.table_view.item(row, 0)
            if item and item.data(Qt.UserRole) == index:
                self.table_view.selectRow(row)
                break

        # 3. Update Canvas Selection & Focus
        for idx, m in enumerate(self.markers):
            if idx == index:
                m._updating_from_code = True
                m.setSelected(True)
                m.update_appearance(True)
                m._updating_from_code = False
                # Focus canvas on selected marker
                self.graphics_view.centerOn(m)
            else:
                m._updating_from_code = True
                m.setSelected(False)
                m.update_appearance(False)
                m._updating_from_code = False

        self._block_signals = False

    # --- TWO-WAY SYNCHRONIZATION HANDLERS ---
    def on_marker_position_changed(self, index: int, x: int, y: int):
        """Called in real-time when user drags a marker on canvas."""
        if self._block_signals or not (0 <= index < len(self.deploy_actions)):
            return

        self.deploy_actions[index]["x"] = x
        self.deploy_actions[index]["y"] = y

        # Update table cell directly without rebuild
        for row in range(self.table_view.rowCount()):
            item = self.table_view.item(row, 0)
            if item and item.data(Qt.UserRole) == index:
                coord_item = self.table_view.item(row, 2)
                if coord_item:
                    coord_item.setText(f"({x}, {y})")
                break

        # If this marker is currently selected, update inspector spinboxes directly
        if index == self.selected_index:
            self._block_signals = True
            self.spin_x.setValue(x)
            self.spin_y.setValue(y)
            self._block_signals = False

    def on_marker_selected(self, index: int):
        """Called when user clicks a marker on canvas."""
        if not self._block_signals:
            self.select_action(index)

    def on_table_selection_changed(self):
        """Called when user selects a row in the sequence table."""
        if self._block_signals:
            return

        selected_rows = self.table_view.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            idx_item = self.table_view.item(row, 0)
            if idx_item:
                orig_index = idx_item.data(Qt.UserRole)
                if orig_index is not None:
                    self.select_action(orig_index)

    def on_inspector_coord_changed(self):
        """Called when user edits X or Y spinbox in Right Inspector."""
        if self._block_signals or not (0 <= self.selected_index < len(self.deploy_actions)):
            return

        x = self.spin_x.value()
        y = self.spin_y.value()
        idx = self.selected_index

        self.deploy_actions[idx]["x"] = x
        self.deploy_actions[idx]["y"] = y

        # Move marker on canvas directly
        if idx < len(self.markers):
            m = self.markers[idx]
            m._updating_from_code = True
            m.setPos(x, y)
            m._updating_from_code = False

        # Update table cell
        for row in range(self.table_view.rowCount()):
            item = self.table_view.item(row, 0)
            if item and item.data(Qt.UserRole) == idx:
                coord_item = self.table_view.item(row, 2)
                if coord_item:
                    coord_item.setText(f"({x}, {y})")
                break

    def on_inspector_changed(self):
        """Called when user edits Unit, Repeat, or Delay in Right Inspector."""
        if self._block_signals or not (0 <= self.selected_index < len(self.deploy_actions)):
            return

        idx = self.selected_index
        unit_id = self.combo_unit.currentData()
        unit_name = self.combo_unit.currentText().split(" (")[0]
        repeat_cnt = self.spin_repeat.value()
        delay_val = self.spin_delay.value()

        self.deploy_actions[idx].update({
            "unit_id": unit_id,
            "unit_name": unit_name,
            "repeat_count": repeat_cnt,
            "delay": delay_val
        })

        if idx < len(self.markers):
            self.markers[idx].setToolTip(f"#{idx + 1}: {unit_name}")

        # Update table row cells
        for row in range(self.table_view.rowCount()):
            item = self.table_view.item(row, 0)
            if item and item.data(Qt.UserRole) == idx:
                self.table_view.item(row, 1).setText(unit_name)
                self.table_view.item(row, 3).setText(f"x{repeat_cnt}")
                self.table_view.item(row, 4).setText(f"{delay_val}s")
                break

    # --- LIST ACTIONS (Add / Delete) ---
    def add_point(self):
        new_idx = len(self.deploy_actions)
        act = {
            "id": f"act_{new_idx + 1}",
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
        self.deploy_actions.append(act)
        self.build_markers()
        self.populate_table()
        self.select_action(new_idx)

    def delete_point(self):
        if 0 <= self.selected_index < len(self.deploy_actions):
            self.deploy_actions.pop(self.selected_index)
            if self.selected_index >= len(self.deploy_actions):
                self.selected_index = len(self.deploy_actions) - 1

            self.build_markers()
            self.populate_table()
            if self.deploy_actions:
                self.select_action(max(0, self.selected_index))

    # --- ZOOM & PAN CONTROLS ---
    def fit_to_window(self):
        self.graphics_view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def reset_zoom(self):
        self.graphics_view.resetTransform()

    def update_config_dropdown(self):
        """Populates config selector combo in dialog header if present."""
        if hasattr(self, "combo_dialog_config"):
            self._block_signals = True
            self.combo_dialog_config.clear()
            for idx, cfg in enumerate(self.random_configs):
                pts = len(cfg.get("deploy_actions", []))
                self.combo_dialog_config.addItem(f"{cfg.get('name', f'Config {idx+1}')} ({pts} points)", idx)
            if 0 <= self.active_config_index < self.combo_dialog_config.count():
                self.combo_dialog_config.setCurrentIndex(self.active_config_index)
            self._block_signals = False

    def sync_active_dialog_config(self):
        if 0 <= self.active_config_index < len(self.random_configs):
            self.random_configs[self.active_config_index]["deploy_actions"] = json.loads(json.dumps(self.deploy_actions))

    def on_dialog_config_changed(self, idx: int):
        if self._block_signals or idx < 0 or idx >= len(self.random_configs):
            return
        self.sync_active_dialog_config()
        self.active_config_index = idx
        self.deploy_actions = json.loads(json.dumps(self.random_configs[idx].get("deploy_actions", [])))
        self.build_markers()
        self.populate_table()
        if self.deploy_actions:
            self.select_action(0)

    def delete_point_at_index(self, index: int):
        if 0 <= index < len(self.deploy_actions):
            self.selected_index = index
            self.delete_point()

    def duplicate_point_at_index(self, index: int):
        if 0 <= index < len(self.deploy_actions):
            act = json.loads(json.dumps(self.deploy_actions[index]))
            act["x"] = min(1600, act.get("x", 800) + 25)
            act["y"] = min(900, act.get("y", 450) + 25)
            self.deploy_actions.insert(index + 1, act)
            self.build_markers()
            self.populate_table()
            self.select_action(index + 1)

    def toggle_point_enabled(self, index: int):
        if 0 <= index < len(self.deploy_actions):
            curr = self.deploy_actions[index].get("enabled", True)
            self.deploy_actions[index]["enabled"] = not curr
            if index < len(self.markers):
                self.markers[index].update_appearance(index == self.selected_index)
            self.populate_table()
            if index == self.selected_index:
                self.select_action(index)

    def get_updated_config(self) -> Dict[str, Any]:
        """Return the updated config data."""
        self.sync_active_dialog_config()
        self.config_data["random_mode"] = self.random_mode
        self.config_data["random_configs"] = self.random_configs
        self.config_data["deploy_actions"] = self.deploy_actions
        return self.config_data
