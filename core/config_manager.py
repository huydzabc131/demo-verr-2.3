import os
import json
import shutil
from typing import Dict, List, Any, Optional
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QWidget
)

from PySide6.QtCore import Qt, Signal


DEFAULT_CONFIG_DATA = {
    "attack_side": "Random",
    "deploy_delay": 5,
    "return_home_delay": 5,
    "loot_enable": True,
    "min_gold": 200000,
    "min_elixir": 200000,
    "loot_mode": "Auto",
    "heroes": {
        "king": True,
        "queen": True,
        "warden": True,
        "royal_champion": True,
        "minion_prince": False,
        "duke": False
    },
    "wall_enable": True,
    "wall_resource": "Auto",
    "wall_count": 4,
    "deploy_actions": []
}


class ConfigProfile:
    """Data model representing a single configuration profile."""

    def __init__(self, name: str, data: Optional[Dict[str, Any]] = None):
        self.name: str = name
        self.data: Dict[str, Any] = data.copy() if data else DEFAULT_CONFIG_DATA.copy()

    def to_dict(self) -> Dict[str, Any]:
        return copy_deep(self.data)

    def from_dict(self, data: Dict[str, Any]):
        self.data = copy_deep(data)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        self.data[key] = value


def copy_deep(data: Any) -> Any:
    return json.loads(json.dumps(data))


class ConfigStorage:
    """Handles file system persistence for profiles and global config synchronization."""

    PROFILES_DIR = "profiles"
    INDEX_FILE = "profiles.json"
    GLOBAL_CONFIG_FILE = "config.json"

    @classmethod
    def ensure_directories(cls):
        if not os.path.exists(cls.PROFILES_DIR):
            os.makedirs(cls.PROFILES_DIR, exist_ok=True)
            # Create default preset profile files
            sample_profiles = {
                "Default": DEFAULT_CONFIG_DATA,
                "Farm Dragon": {**DEFAULT_CONFIG_DATA, "attack_side": "Random", "min_gold": 500000, "min_elixir": 500000},
                "Farm Baby": {**DEFAULT_CONFIG_DATA, "attack_side": "Left", "min_gold": 300000, "min_elixir": 300000},
                "War Dragon": {**DEFAULT_CONFIG_DATA, "attack_side": "Right", "min_gold": 0, "min_elixir": 0, "loot_enable": False},
                "Legend": {**DEFAULT_CONFIG_DATA, "attack_side": "Random", "deploy_delay": 3},
                "Clan Games": {**DEFAULT_CONFIG_DATA, "attack_side": "Random", "wall_enable": True},
                "Test": {**DEFAULT_CONFIG_DATA, "deploy_delay": 2, "return_home_delay": 3},
                "Event": {**DEFAULT_CONFIG_DATA, "attack_side": "Left"}
            }
            for prof_name, p_data in sample_profiles.items():
                cls.save_profile_data(prof_name, p_data)

    @classmethod
    def get_profile_path(cls, profile_name: str) -> str:
        # Sanitize filename
        safe_name = "".join(c for c in profile_name if c.isalnum() or c in (' ', '_', '-')).strip()
        if not safe_name:
            safe_name = "Profile"
        return os.path.join(cls.PROFILES_DIR, f"{safe_name}.json")

    @classmethod
    def load_index(cls) -> Dict[str, Any]:
        cls.ensure_directories()
        if os.path.exists(cls.INDEX_FILE):
            try:
                with open(cls.INDEX_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print("Error loading index file:", e)
        return {"active_profile": "Default"}

    @classmethod
    def save_index(cls, active_profile: str):
        cls.ensure_directories()
        try:
            data = {"active_profile": active_profile}
            with open(cls.INDEX_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print("Error saving index file:", e)

    @classmethod
    def list_profiles(cls) -> List[str]:
        cls.ensure_directories()
        profiles = []
        if os.path.exists(cls.PROFILES_DIR):
            for file_name in os.listdir(cls.PROFILES_DIR):
                if file_name.endswith(".json"):
                    prof_name = os.path.splitext(file_name)[0]
                    profiles.append(prof_name)
        
        if "Default" not in profiles:
            profiles.insert(0, "Default")
            # Create Default profile if missing
            cls.save_profile_data("Default", DEFAULT_CONFIG_DATA)
            
        profiles.sort(key=lambda x: (0 if x == "Default" else 1, x.lower()))
        return profiles

    @classmethod
    def load_profile_data(cls, profile_name: str) -> Dict[str, Any]:
        path = cls.get_profile_path(profile_name)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Merge default keys if missing
                    merged = DEFAULT_CONFIG_DATA.copy()
                    merged.update(data)
                    return merged
            except Exception as e:
                print(f"Error loading profile '{profile_name}':", e)

        # Fall back to root config.json if Default
        if profile_name == "Default" and os.path.exists(cls.GLOBAL_CONFIG_FILE):
            try:
                with open(cls.GLOBAL_CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cls.save_profile_data("Default", data)
                    return data
            except Exception as e:
                print("Error loading global config file for Default:", e)

        return DEFAULT_CONFIG_DATA.copy()

    @classmethod
    def save_profile_data(cls, profile_name: str, data: Dict[str, Any]):
        cls.ensure_directories()
        path = cls.get_profile_path(profile_name)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving profile '{profile_name}':", e)

    @classmethod
    def sync_global_config(cls, data: Dict[str, Any]):
        try:
            with open(cls.GLOBAL_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print("Error syncing global config.json:", e)

    @classmethod
    def delete_profile_file(cls, profile_name: str):
        if profile_name == "Default":
            return
        path = cls.get_profile_path(profile_name)
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Error deleting profile file '{profile_name}':", e)

    @classmethod
    def rename_profile_file(cls, old_name: str, new_name: str):
        if old_name == "Default":
            return
        old_path = cls.get_profile_path(old_name)
        new_path = cls.get_profile_path(new_name)
        if os.path.exists(old_path):
            try:
                os.rename(old_path, new_path)
            except Exception as e:
                print(f"Error renaming profile file from {old_name} to {new_name}:", e)


class ConfigProfileManager:
    """Manages profile loading, switching, saving, unsaved tracking, and synchronization."""

    def __init__(self):
        self.profiles: Dict[str, ConfigProfile] = {}
        self.active_profile_name: str = "Default"
        self.is_modified: bool = False

        self.reload_all_profiles()

    def reload_all_profiles(self):
        index_data = ConfigStorage.load_index()
        self.active_profile_name = index_data.get("active_profile", "Default")

        profile_names = ConfigStorage.list_profiles()
        self.profiles.clear()
        for name in profile_names:
            data = ConfigStorage.load_profile_data(name)
            self.profiles[name] = ConfigProfile(name, data)

        if self.active_profile_name not in self.profiles:
            self.active_profile_name = "Default"

        active_prof = self.get_active_profile()
        ConfigStorage.sync_global_config(active_prof.to_dict())
        ConfigStorage.save_index(self.active_profile_name)
        self.is_modified = False

    def get_profile_names(self) -> List[str]:
        return ConfigStorage.list_profiles()

    def get_active_profile(self) -> ConfigProfile:
        if self.active_profile_name not in self.profiles:
            data = ConfigStorage.load_profile_data(self.active_profile_name)
            self.profiles[self.active_profile_name] = ConfigProfile(self.active_profile_name, data)
        return self.profiles[self.active_profile_name]

    def set_active_profile_name(self, profile_name: str) -> bool:
        if profile_name not in ConfigStorage.list_profiles():
            return False
        
        self.active_profile_name = profile_name
        if profile_name not in self.profiles:
            data = ConfigStorage.load_profile_data(profile_name)
            self.profiles[profile_name] = ConfigProfile(profile_name, data)

        ConfigStorage.save_index(self.active_profile_name)
        active_prof = self.get_active_profile()
        ConfigStorage.sync_global_config(active_prof.to_dict())
        self.is_modified = False
        return True

    def update_active_config(self, new_data: Dict[str, Any]):
        active_prof = self.get_active_profile()
        active_prof.from_dict(new_data)
        self.is_modified = True

    def save_active_profile(self, current_data: Optional[Dict[str, Any]] = None):
        if current_data:
            self.update_active_config(current_data)
        active_prof = self.get_active_profile()
        ConfigStorage.save_profile_data(self.active_profile_name, active_prof.to_dict())
        ConfigStorage.sync_global_config(active_prof.to_dict())
        self.is_modified = False

    def create_profile(self, name: str, source_data: Dict[str, Any]) -> bool:
        clean_name = name.strip()
        if not clean_name:
            return False
        
        ConfigStorage.save_profile_data(clean_name, source_data)
        self.profiles[clean_name] = ConfigProfile(clean_name, source_data)
        self.active_profile_name = clean_name
        ConfigStorage.save_index(self.active_profile_name)
        ConfigStorage.sync_global_config(source_data)
        self.is_modified = False
        return True

    def duplicate_profile(self, source_name: str, new_name: str) -> bool:
        clean_name = new_name.strip()
        if not clean_name:
            return False

        source_data = ConfigStorage.load_profile_data(source_name)
        return self.create_profile(clean_name, source_data)

    def rename_profile(self, old_name: str, new_name: str) -> bool:
        if old_name == "Default":
            return False
        clean_name = new_name.strip()
        if not clean_name or clean_name == old_name:
            return False

        ConfigStorage.rename_profile_file(old_name, clean_name)
        if old_name in self.profiles:
            prof = self.profiles.pop(old_name)
            prof.name = clean_name
            self.profiles[clean_name] = prof

        if self.active_profile_name == old_name:
            self.active_profile_name = clean_name
            ConfigStorage.save_index(self.active_profile_name)

        return True

    def delete_profile(self, name: str) -> bool:
        if name == "Default":
            return False

        ConfigStorage.delete_profile_file(name)
        if name in self.profiles:
            del self.profiles[name]

        if self.active_profile_name == name:
            self.active_profile_name = "Default"
            ConfigStorage.save_index("Default")
            active_prof = self.get_active_profile()
            ConfigStorage.sync_global_config(active_prof.to_dict())

        self.is_modified = False
        return True


class ProfileDialog(QDialog):
    """Custom input dialog for profile management actions (New, Rename)."""

    def __init__(self, title: str, prompt: str, default_value: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(380)
        self.setStyleSheet("""
            QDialog {
                background-color: #18181B;
                border: 1px solid #3F3F46;
                border-radius: 8px;
            }
            QLabel {
                color: #F4F4F5;
                font-size: 13px;
                font-weight: 600;
            }
            QLineEdit {
                background-color: #09090B;
                border: 1px solid #3F3F46;
                border-radius: 6px;
                padding: 8px 12px;
                color: #F4F4F5;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
            }
            QPushButton {
                padding: 6px 16px;
                font-weight: 700;
                border-radius: 6px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        label = QLabel(prompt)
        self.line_edit = QLineEdit(default_value)
        self.line_edit.selectAll()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet("background-color: #2563EB; color: white;")
        self.ok_btn.clicked.connect(self.accept)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #27272A; color: white;")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)

        layout.addWidget(label)
        layout.addWidget(self.line_edit)
        layout.addLayout(btn_layout)

    def get_input(self) -> str:
        return self.line_edit.text().strip()
