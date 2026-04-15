import os
import json
import ctypes
import subprocess
import time

from overlay import VisualSettings

# ------------------------------------------------------------------------------
# 
# Colorblind Manager Class
#
#  ------------------------------------------------------------------------------
class ColorManager:
    def __init__(self):
        self.colorblind_type = "none"
        self.colorblind_slider = 0

    def export_settings(self, cb_type, cb_slider, enabled) -> dict:
        return {
            "features": {
                "visual": {
                    "colorblind": {
                        "enabled": enabled,
                        "type": cb_type,
                        "slider": cb_slider
                    }
                }
            }
        }
    
    # ------------------------------------------------------------
    # Saving Colorblind Settings to JSON File
    def save_to_file(self, cb_type, cb_slider, enabled, path: str = "colorblind_settings.json") -> None:
        
        settings = {
            "version": 1,
            **self.export_settings(cb_type, cb_slider, enabled)
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)

        print(f"Colorblind settings saved to {path}")

    # ------------------------------------------------------------
    # Load Colorblind Settings from JSON File
    def load_from_file(self, cb_type, cb_slider, enabled, path: str = "colorblind_settings.json", apply_to_system: bool = False, parent=None) -> None:
        with open(path, "r", encoding="utf-8") as f:
            settings = json.load(f)

        colorblind = settings.get("features", {}).get("visual", {}).get("colorblind", {})
        enabled = colorblind.get("enabled")
        type = colorblind.get("type")
        slider = colorblind.get("slider")

        print(f"Colorblind settings loaded from {path}")
        return VisualSettings(
            cb_enabled = enabled,
            colorblind_type = type,
            colorblind_slider = slider,
        )



# ------------------------------------------------------------------------------
# 
# Contrast Manager Class
#
#  ------------------------------------------------------------------------------
class ContrastManager:
    def __init__(self):
        self.contrast_slider = 50

    def export_settings(self, ct_slider, enabled) -> dict:
        return {
            "features": {
                "visual": {
                    "contrast": {
                        "enabled": enabled,
                        "slider": ct_slider
                    }
                }
            }
        }

    # ------------------------------------------------------------
    # Saving Contrast Settings to JSON File
    def save_to_file(self, ct_slider, enabled, path: str = "contrast_settings.json") -> None:
        settings = {
            "version": 1,
            **self.export_settings(ct_slider, enabled)
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)

        print(f"Contrast settings saved to {path}")

    # ------------------------------------------------------------
    # Load Contrast Settings from JSON File
    def load_from_file(self, path: str = "contrast_settings.json", apply_to_system: bool = False, parent=None) -> None:
        with open(path, "r", encoding="utf-8") as f:
            settings = json.load(f)

        contrast = settings.get("features", {}).get("visual", {}).get("contrast", {})
        enabled = contrast.get("enabled")
        slider = contrast.get("slider")

        print(f"Contrast settings loaded from {path}")
        return VisualSettings(
            ct_enabled = enabled,
            contrast_slider = slider,
        )
        