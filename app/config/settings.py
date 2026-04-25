from pathlib import Path

APP_TITLE = "Image Sorter"
INITIAL_WINDOW_SIZE = (1200, 720)
SOURCE_PREVIEW_SIZE = (420, 420)
FOLDER_CARD_PREVIEW_SIZE = (220, 140)
FOLDER_GRID_COLUMN_RANGE = (2, 5)
THUMBNAIL_SIZE = (300, 300)
UI_STYLE = {
    "colors": {
        "app_bg": "#eef3f8",
        "panel_bg": "#f8fbff",
        "surface_bg": "#ffffff",
        "surface_muted": "#f5f7fb",
        "primary": "#2f6fed",
        "primary_active": "#2458be",
        "neutral": "#6b7280",
        "neutral_active": "#4b5563",
        "warning": "#c2410c",
        "warning_active": "#9a3412",
        "text": "#111827",
        "text_muted": "#5b6472",
        "border": "#cfd7e3",
        "border_strong": "#b9c4d4",
        "overlay": "#111827",
        "overlay_text": "#ffffff",
        "preview_empty": "#d9e1ea",
    },
    "fonts": {
        "body": ("Segoe UI", 10),
        "body_bold": ("Segoe UI Semibold", 10),
        "title": ("Segoe UI Semibold", 11),
    },
    "spacing": {
        "section_x": 20,
        "section_y": 16,
        "control_gap": 8,
        "section_gap": 12,
    },
}

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_JSON_FILE = PROJECT_ROOT / "config-target.json"
LEGACY_CONFIG_FILE = PROJECT_ROOT / "config-target.txt"
