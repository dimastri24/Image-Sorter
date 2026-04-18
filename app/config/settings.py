from pathlib import Path

APP_TITLE = "Image Sorter"
THUMBNAIL_SIZE = (300, 300)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_JSON_FILE = PROJECT_ROOT / "config-target.json"
LEGACY_CONFIG_FILE = PROJECT_ROOT / "config-target.txt"
