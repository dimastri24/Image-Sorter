from pathlib import Path

APP_TITLE = "Image Sorter"
THUMBNAIL_SIZE = (300, 300)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = PROJECT_ROOT / "config-target.txt"

DEFAULT_TARGET_FOLDERS = [
    "mfolder_1",
    "mfolder_2",
    "mfolder_3",
]
