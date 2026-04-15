import json
import os

DEFAULT_SETTINGS = {
    "version": 1,
    "features": {
        "audio": {
            "dynamicRange": {
                "enabled": False,
                "level": "medium"
            },
            "subtitles": {
                "enabled": False,
                "color": "White",
                "position": "Bottom",
                "background": False,
                "bg_opacity": 60,
                "font_size": 18
            }
        },
        "visual": {
            "colorblind": {
                "enabled": False,
                "type": "None",
                "slider": 0
            },
            "contrast": {
                "enabled": False,
                "slider": 50
            },
            "poi": {
                "magnifier_enabled": False,
                "zoom": 1
            }
        }
    }
}


class SettingsManager:
    def __init__(self, path="enable_games_settings.json"):
        self.path = path

    def load_file(self):
        if not os.path.exists(self.path):
            return json.loads(json.dumps(DEFAULT_SETTINGS))
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_file(self, settings: dict):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)

    def build_from_visual_menu(self, visual_menu) -> dict:
        return {
            "visual": {
                "colorblind": {
                    "enabled": visual_menu.chkColorBlind.isChecked(),
                    "type": visual_menu.comboxColorBlindType.currentText(),
                    "slider": visual_menu.slideColorBlindIntensity.value()
                },
                "contrast": {
                    "enabled": visual_menu.chkContrast.isChecked(),
                    "slider": visual_menu.sliderContrastScreen.value()
                },
                "poi": {
                    "magnifier_enabled": visual_menu.chkPoiMagnifier.isChecked(),
                    "zoom": visual_menu.sldPoiZoom.value()
                }
            }
        }

    def build_from_audio_menu(self, audio_menu) -> dict:
        return {
            "audio": {
                "dynamicRange": {
                    "enabled": True,
                    "level": audio_menu.cmbRange.currentText().strip()
                },
                "subtitles": {
                    "enabled": audio_menu.chkSubtitleEnabled.isChecked(),
                    "color": audio_menu.cmbSubtitleColor.currentText(),
                    "position": audio_menu.cmbSubtitlePosition.currentText(),
                    "background": audio_menu.chkSubtitleBackground.isChecked(),
                    "bg_opacity": audio_menu.sldSubtitleBgOpacity.value(),
                    "font_size": audio_menu.spnSubtitleFontSize.value()
                }
            }
        }

    def merge_sections(self, base: dict, updates: dict) -> dict:
        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                self.merge_sections(base[key], value)
            else:
                base[key] = value
        return base

    def save_visual_menu(self, visual_menu):
        settings = self.load_file()
        visual_settings = self.build_from_visual_menu(visual_menu)
        self.merge_sections(settings["features"], visual_settings)
        self.save_file(settings)
        print(f"Visual settings saved to {self.path}")

    def save_audio_menu(self, audio_menu):
        settings = self.load_file()
        audio_settings = self.build_from_audio_menu(audio_menu)
        self.merge_sections(settings["features"], audio_settings)
        self.save_file(settings)

    def apply_to_visual_menu(self, visual_menu, settings: dict):
        visual = settings.get("features", {}).get("visual", {})

        cb = visual.get("colorblind", {})
        ct = visual.get("contrast", {})
        poi = visual.get("poi", {})

        # Colorblind
        visual_menu.chkColorBlind.setChecked(cb.get("enabled", False))

        cb_type = cb.get("type", "None")
        idx = visual_menu.comboxColorBlindType.findText(cb_type)
        if idx >= 0:
            visual_menu.comboxColorBlindType.setCurrentIndex(idx)
        visual_menu.colorblindType = cb_type

        visual_menu.slideColorBlindIntensity.setValue(cb.get("slider", 0))

        # Contrast
        visual_menu.chkContrast.setChecked(ct.get("enabled", False))
        visual_menu.sliderContrastScreen.setValue(ct.get("slider", 50))

        # POI
        visual_menu.chkPoiMagnifier.setChecked(poi.get("magnifier_enabled", False))
        visual_menu.sldPoiZoom.setValue(poi.get("zoom", 1))
        visual_menu.update_poi_zoom_label(visual_menu.sldPoiZoom.value())

        # Refresh preview + overlay
        visual_menu.colorblind_intensity(visual_menu.slideColorBlindIntensity.value())
        visual_menu.screen_contrast_correction(visual_menu.sliderContrastScreen.value())
        visual_menu.visual_settings_enabled()

    def apply_to_audio_menu(self, audio_menu, settings: dict):
        audio = settings.get("features", {}).get("audio", {})

        dyn = audio.get("dynamicRange", {})
        level = dyn.get("level", "Medium")
        idx = audio_menu.cmbRange.findText(level)
        if idx >= 0:
            audio_menu.cmbRange.setCurrentIndex(idx)

        subs = audio.get("subtitles", {})
        audio_menu.chkSubtitleEnabled.setChecked(subs.get("enabled", False))

        idx = audio_menu.cmbSubtitleColor.findText(subs.get("color", "White"))
        if idx >= 0:
            audio_menu.cmbSubtitleColor.setCurrentIndex(idx)

        idx = audio_menu.cmbSubtitlePosition.findText(subs.get("position", "Bottom"))
        if idx >= 0:
            audio_menu.cmbSubtitlePosition.setCurrentIndex(idx)

        audio_menu.chkSubtitleBackground.setChecked(subs.get("background", False))
        audio_menu.sldSubtitleBgOpacity.setValue(subs.get("bg_opacity", 60))
        audio_menu.spnSubtitleFontSize.setValue(subs.get("font_size", 18))

        audio_menu.update_subtitle_preview()

    def load_into_visual_menu(self, visual_menu):
        settings = self.load_file()
        self.apply_to_visual_menu(visual_menu, settings)
        print(f"Visual settings loaded from {self.path}")

    def load_into_audio_menu(self, audio_menu):
        settings = self.load_file()
        self.apply_to_audio_menu(audio_menu, settings)