import os
import json
import ctypes
import subprocess
import time


class DynamicRangeManager:
    def __init__(self):
        self.current_level = "medium"

    def export_settings(self, combo_box) -> dict:
        level = combo_box.currentText().strip().lower()
        enabled = level in ["low (compressed)", "medium", "high (wide)"]

        return {
            "features": {
                "audio": {
                    "dynamicRange": {
                        "enabled": enabled,
                        "level": level
                    }
                }
            }
        }

    def apply_settings(self, combo_box, settings: dict, apply_to_system: bool = False, parent=None) -> None:
        dyn = settings.get("features", {}).get("audio", {}).get("dynamicRange", {})
        level = dyn.get("level", "medium").strip().lower()

        index = -1
        for i in range(combo_box.count()):
            if combo_box.itemText(i).strip().lower() == level:
                index = i
                break

        if index != -1:
            old_state = combo_box.blockSignals(True)
            combo_box.setCurrentIndex(index)
            combo_box.blockSignals(old_state)
        else:
            print(f"Dynamic range level '{level}' not found in combo box.")
            return

        self.current_level = level

        if apply_to_system and dyn.get("enabled", False):
            self.apply_to_system(level)
            if self.is_admin():
                ok = self.touch_equalizerapo_config_txt()
                if not ok:
                    print("Loaded setting, but could not reload Equalizer APO.")

    def save_to_file(self, combo_box, path: str = "dynamic_range_settings.json") -> None:
        settings = {
            "version": 1,
            **self.export_settings(combo_box)
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)

        print(f"Dynamic range settings saved to {path}")

    def load_from_file(self, combo_box, path: str = "dynamic_range_settings.json", apply_to_system: bool = False, parent=None) -> None:
        with open(path, "r", encoding="utf-8") as f:
            settings = json.load(f)

        self.apply_settings(combo_box, settings, apply_to_system=apply_to_system, parent=parent)
        print(f"Dynamic range settings loaded from {path}")

    def get_apo_file_path(self):
        return r"C:\ProgramData\EnableGames\apo_dynamic_range.txt"

    def apply_to_system(self, level: str):
        presets = {
            "low (compressed)": """
# LOW (TEST) - heavy compression, no makeup
Preamp: 40 dB
Compressor: Threshold -50 dB Ratio 20:1 Attack 1 ms Release 400 ms Knee 6 dB MakeupGain 0 dB
""",
            "medium": """
# MEDIUM (TEST) - moderate compression, no makeup
Preamp: 0 dB
Compressor: Threshold -28 dB Ratio 4:1 Attack 5 ms Release 200 ms Knee 6 dB MakeupGain 0 dB
""",
            "high (wide)": """
# HIGH (TEST) - near bypass
Preamp: 0 dB
Compressor: Threshold 0 dB Ratio 1:1 Attack 10 ms Release 200 ms Knee 0 dB MakeupGain 0 dB
"""
        }

        config_text = presets.get(level, "Preamp: 0 dB")
        file_path = self.get_apo_file_path()

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(config_text)

        print("Equalizer APO config updated.")

    def is_admin(self) -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False

    def touch_equalizerapo_config_txt(self) -> bool:
        config_txt = r"C:\Program Files\EqualizerAPO\config\config.txt"
        try:
            with open(config_txt, "r", encoding="utf-8") as f:
                content = f.read()

            content2 = content.rstrip() + "\n# touched by Enable-Games\n"

            with open(config_txt, "w", encoding="utf-8") as f:
                f.write(content2)

            return True
        except Exception as e:
            print("Could not touch config.txt:", e)
            return False

    def reload_equalizer_apo_best_effort(self) -> bool:
        editor_path = r"C:\Program Files\EqualizerAPO\Editor.exe"
        editor_dir = os.path.dirname(editor_path)

        if not os.path.exists(editor_path):
            print("Editor.exe not found:", editor_path)
            return False

        env = os.environ.copy()
        for var in (
            "QT_PLUGIN_PATH",
            "QT_QPA_PLATFORM_PLUGIN_PATH",
            "QML2_IMPORT_PATH",
            "QML_IMPORT_PATH",
        ):
            env.pop(var, None)

        try:
            p = subprocess.Popen(
                [editor_path],
                cwd=editor_dir,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(0.8)
            p.terminate()
            return True
        except Exception as e:
            print("APO reload attempt failed:", e)
            return False
