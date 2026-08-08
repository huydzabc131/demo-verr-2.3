import os
import json
from typing import Callable, Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QFrame,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDialog
from core.config_manager import ConfigProfileManager, ProfileDialog, ConfigStorage
from gui.config_preview_dialog import ConfigPreviewDialog


class ProfileBar(QFrame):
    """Profile Management Control Bar Widget."""

    profile_changed = Signal(dict)   # Emits loaded profile dictionary when active profile changes
    profile_saved = Signal(dict)     # Emits saved profile dictionary when explicitly saved

    def __init__(self,
                 manager: ConfigProfileManager,
                 get_current_ui_config: Callable[[], Dict[str, Any]],
                 apply_config_to_ui: Callable[[Dict[str, Any]], None],
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.manager = manager
        self.get_current_ui_config = get_current_ui_config
        self.apply_config_to_ui = apply_config_to_ui
        self._is_updating_ui = False

        self.setObjectName("profileBarFrame")
        self.setStyleSheet("""
            QFrame#profileBarFrame {
                background-color: #18181B;
                border: 1px solid #27272A;
                border-radius: 8px;
                padding: 4px 10px;
            }
            QLabel {
                color: #A1A1AA;
                font-size: 12px;
                font-weight: 700;
            }
            QComboBox {
                background-color: #09090B;
                border: 1px solid #3F3F46;
                border-radius: 6px;
                padding: 4px 10px;
                color: #F4F4F5;
                font-weight: 600;
                min-width: 130px;
            }
            QComboBox:hover {
                border-color: #3B82F6;
            }
            QPushButton {
                background-color: #27272A;
                color: #F4F4F5;
                font-weight: 600;
                font-size: 11px;
                border-radius: 5px;
                border: 1px solid #3F3F46;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #3F3F46;
                border-color: #60A5FA;
            }
            QPushButton#btnSave {
                background-color: #10B981;
                border-color: #059669;
                color: #FFFFFF;
                font-weight: 700;
            }
            QPushButton#btnSave:hover {
                background-color: #059669;
            }
            QPushButton#btnNew {
                background-color: #2563EB;
                border-color: #1D4ED8;
                color: #FFFFFF;
                font-weight: 700;
            }
            QPushButton#btnNew:hover {
                background-color: #1D4ED8;
            }
            QPushButton#btnDelete {
                background-color: #18181B;
                color: #EF4444;
                border-color: #7F1D1D;
            }
            QPushButton#btnDelete:hover {
                background-color: #DC2626;
                color: #FFFFFF;
            }
        """)

        self.init_ui()
        self.refresh_profile_list()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(8)

        # Title Label
        title_icon = QLabel("📁 Config Profile:")
        layout.addWidget(title_icon)

        # Profile Selector Combobox
        self.profile_combo = QComboBox()
        self.profile_combo.currentIndexChanged.connect(self.on_combo_index_changed)
        layout.addWidget(self.profile_combo)

        # Unsaved changes status badge
        self.status_badge = QLabel("✓ Đã đồng bộ")
        self.status_badge.setStyleSheet("color: #10B981; font-weight: bold; background-color: #064E3B; padding: 3px 8px; border-radius: 4px; font-size: 11px;")
        layout.addWidget(self.status_badge)

        self.btn_preview = QPushButton("👁️ Preview")
        self.btn_preview.setToolTip("Xem và chỉnh sửa trực quan Config Deploy trên bản đồ battlefield")
        self.btn_preview.setStyleSheet("background-color: #312E81; color: #818CF8; border-color: #4338CA; font-weight: 700;")
        self.btn_preview.clicked.connect(self.preview_config)

        self.btn_save = QPushButton("💾 Save")
        self.btn_save.setObjectName("btnSave")
        self.btn_save.setToolTip("Lưu toàn bộ cấu hình hiện tại vào Profile")
        self.btn_save.clicked.connect(self.save_profile)

        self.btn_new = QPushButton("➕ New")
        self.btn_new.setObjectName("btnNew")
        self.btn_new.setToolTip("Tạo Profile cấu hình mới")
        self.btn_new.clicked.connect(self.new_profile)

        self.btn_rename = QPushButton("✏️ Rename")
        self.btn_rename.setToolTip("Đổi tên Profile đang chọn")
        self.btn_rename.clicked.connect(self.rename_profile)

        self.btn_duplicate = QPushButton("📋 Duplicate")
        self.btn_duplicate.setToolTip("Nhân bản Profile hiện tại")
        self.btn_duplicate.clicked.connect(self.duplicate_profile)

        self.btn_delete = QPushButton("🗑️ Delete")
        self.btn_delete.setObjectName("btnDelete")
        self.btn_delete.setToolTip("Xóa Profile đang chọn")
        self.btn_delete.clicked.connect(self.delete_profile)

        self.btn_import = QPushButton("📥 Import")
        self.btn_import.setToolTip("Nhập Profile từ file .json")
        self.btn_import.clicked.connect(self.import_profile)

        self.btn_export = QPushButton("📤 Export")
        self.btn_export.setToolTip("Xuất Profile hiện tại ra file .json")
        self.btn_export.clicked.connect(self.export_profile)

        layout.addWidget(self.btn_preview)
        layout.addWidget(self.btn_save)
        layout.addWidget(self.btn_new)
        layout.addWidget(self.btn_rename)
        layout.addWidget(self.btn_duplicate)
        layout.addWidget(self.btn_delete)
        layout.addWidget(self.btn_import)
        layout.addWidget(self.btn_export)

        layout.addStretch()

    def mark_unsaved(self):
        """Called whenever any control on UI is modified by user."""
        if self._is_updating_ui:
            return
        self.manager.is_modified = True
        self.status_badge.setText("● Unsaved Changes")
        self.status_badge.setStyleSheet("color: #F59E0B; font-weight: bold; background-color: #312E81; padding: 3px 8px; border-radius: 4px; font-size: 11px;")

    def mark_saved(self):
        self.manager.is_modified = False
        self.status_badge.setText("✓ Đã đồng bộ")
        self.status_badge.setStyleSheet("color: #10B981; font-weight: bold; background-color: #064E3B; padding: 3px 8px; border-radius: 4px; font-size: 11px;")

    def refresh_profile_list(self):
        self._is_updating_ui = True
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()

        profiles = self.manager.get_profile_names()
        for p in profiles:
            self.profile_combo.addItem(p)

        active_name = self.manager.active_profile_name
        idx = self.profile_combo.findText(active_name)
        if idx >= 0:
            self.profile_combo.setCurrentIndex(idx)

        self.profile_combo.blockSignals(False)
        self._is_updating_ui = False
        self.update_buttons_state()

    def update_buttons_state(self):
        current_prof = self.profile_combo.currentText()
        is_default = (current_prof == "Default")
        self.btn_rename.setEnabled(not is_default)
        self.btn_delete.setEnabled(not is_default)

    def on_combo_index_changed(self, index: int):
        if self._is_updating_ui or index < 0:
            return

        target_profile = self.profile_combo.itemText(index)
        current_active = self.manager.active_profile_name

        if target_profile == current_active:
            return

        # Check for unsaved changes prompt
        if self.manager.is_modified:
            box = QMessageBox(self)
            box.setWindowTitle("Lưu thay đổi?")
            box.setText(f"Bạn có muốn lưu các thay đổi vào Profile '{current_active}' trước khi chuyển sang '{target_profile}'?")
            box.setStyleSheet("""
                QMessageBox { background-color: #18181B; }
                QLabel { color: #F4F4F5; font-size: 13px; }
                QPushButton { padding: 6px 14px; font-weight: bold; border-radius: 4px; }
            """)
            save_btn = box.addButton("Save", QMessageBox.AcceptRole)
            dont_save_btn = box.addButton("Don't Save", QMessageBox.DestructiveRole)
            cancel_btn = box.addButton("Cancel", QMessageBox.RejectRole)

            box.exec()

            clicked = box.clickedButton()
            if clicked == save_btn:
                self.save_profile()
            elif clicked == cancel_btn:
                # Revert selection back without switching
                self._is_updating_ui = True
                old_idx = self.profile_combo.findText(current_active)
                if old_idx >= 0:
                    self.profile_combo.setCurrentIndex(old_idx)
                self._is_updating_ui = False
                return
            # If "Don't Save" clicked, proceed to switch without saving

        # Perform profile switch
        self.switch_to_profile(target_profile)

    def switch_to_profile(self, profile_name: str):
        self.manager.set_active_profile_name(profile_name)
        active_prof = self.manager.get_active_profile()
        config_data = active_prof.to_dict()

        self._is_updating_ui = True
        self.apply_config_to_ui(config_data)
        self._is_updating_ui = False

        self.mark_saved()
        self.update_buttons_state()
        self.profile_changed.emit(config_data)

    def save_profile(self):
        curr_data = self.get_current_ui_config()
        self.manager.save_active_profile(curr_data)
        self.mark_saved()
        self.profile_saved.emit(curr_data)

    def new_profile(self):
        dlg = ProfileDialog("Tạo Profile Mới", "Nhập tên Profile mới:", "Farm Strategy 1", self)
        if dlg.exec() == ProfileDialog.Accepted:
            new_name = dlg.get_input()
            if not new_name:
                return

            if new_name in self.manager.get_profile_names():
                QMessageBox.warning(self, "Trùng tên", f"Profile '{new_name}' đã tồn tại!")
                return

            current_ui_data = self.get_current_ui_config()
            self.manager.create_profile(new_name, current_ui_data)
            self.refresh_profile_list()
            self.mark_saved()
            self.profile_changed.emit(current_ui_data)

    def rename_profile(self):
        curr_name = self.manager.active_profile_name
        if curr_name == "Default":
            QMessageBox.information(self, "Thông báo", "Không thể đổi tên Profile 'Default'!")
            return

        dlg = ProfileDialog("Đổi Tên Profile", "Nhập tên mới cho Profile:", curr_name, self)
        if dlg.exec() == ProfileDialog.Accepted:
            new_name = dlg.get_input()
            if not new_name or new_name == curr_name:
                return

            if new_name in self.manager.get_profile_names():
                QMessageBox.warning(self, "Trùng tên", f"Profile '{new_name}' đã tồn tại!")
                return

            self.manager.rename_profile(curr_name, new_name)
            self.refresh_profile_list()

    def duplicate_profile(self):
        curr_name = self.manager.active_profile_name
        default_dup_name = f"{curr_name} Copy"
        dlg = ProfileDialog("Nhân Bản Profile", "Nhập tên cho bản sao:", default_dup_name, self)
        if dlg.exec() == ProfileDialog.Accepted:
            new_name = dlg.get_input()
            if not new_name:
                return

            if new_name in self.manager.get_profile_names():
                QMessageBox.warning(self, "Trùng tên", f"Profile '{new_name}' đã tồn tại!")
                return

            current_ui_data = self.get_current_ui_config()
            self.manager.duplicate_profile(curr_name, new_name)
            self.refresh_profile_list()
            self.mark_saved()
            self.profile_changed.emit(current_ui_data)

    def delete_profile(self):
        curr_name = self.manager.active_profile_name
        if curr_name == "Default":
            QMessageBox.warning(self, "Không thể xóa", "Profile 'Default' là cấu hình mặc định và không thể xóa!")
            return

        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa Profile '{curr_name}' không?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.manager.delete_profile(curr_name)
            self.refresh_profile_list()
            active_data = self.manager.get_active_profile().to_dict()
            self._is_updating_ui = True
            self.apply_config_to_ui(active_data)
            self._is_updating_ui = False
            self.mark_saved()
            self.profile_changed.emit(active_data)

    def import_profile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Nhập File Profile", "", "JSON Files (*.json)")
        if not file_path or not os.path.exists(file_path):
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            base_name = os.path.splitext(os.path.basename(file_path))[0]
            dlg = ProfileDialog("Import Profile", "Nhập tên cho Profile được import:", base_name, self)
            if dlg.exec() == ProfileDialog.Accepted:
                prof_name = dlg.get_input()
                if not prof_name:
                    return

                if prof_name in self.manager.get_profile_names():
                    QMessageBox.warning(self, "Trùng tên", f"Profile '{prof_name}' đã tồn tại!")
                    return

                self.manager.create_profile(prof_name, data)
                self.refresh_profile_list()
                self._is_updating_ui = True
                self.apply_config_to_ui(data)
                self._is_updating_ui = False
                self.mark_saved()
                self.profile_changed.emit(data)
                QMessageBox.information(self, "Thành công", f"Đã nhập Profile '{prof_name}' thành công!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi Import", f"Không thể đọc file JSON profile: {e}")

    def export_profile(self):
        curr_name = self.manager.active_profile_name
        curr_data = self.get_current_ui_config()

        default_file = f"{curr_name}.json"
        file_path, _ = QFileDialog.getSaveFileName(self, "Xuất File Profile", default_file, "JSON Files (*.json)")
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(curr_data, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Thành công", f"Đã xuất Profile '{curr_name}' ra:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi Export", f"Không thể xuất file profile: {e}")

    def preview_config(self):
        curr_name = self.manager.active_profile_name
        curr_data = self.get_current_ui_config()

        dlg = ConfigPreviewDialog(curr_name, curr_data, parent=self)
        if dlg.exec() == QDialog.Accepted:
            updated_data = dlg.get_updated_config()
            self.apply_config_to_ui(updated_data)
            self.mark_unsaved()
            self.profile_changed.emit(updated_data)
