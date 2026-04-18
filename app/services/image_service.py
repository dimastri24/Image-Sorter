from pathlib import Path

from ..config.settings import CONFIG_JSON_FILE, LEGACY_CONFIG_FILE
from ..utils.file_utils import (
    ensure_directory,
    list_file_names,
    move_file,
    read_json_list,
    read_lines,
    write_json_list,
)


class ImageService:
    def __init__(self) -> None:
        self.root_folder: Path | None = None
        self.images: list[str] = []
        self.image_index = 0
        self.current_image_name: str | None = None
        self.pending_message: str | None = None
        self.target_folders = self.load_target_folders()

    def load_target_folders(self) -> list[str]:
        if CONFIG_JSON_FILE.exists():
            return read_json_list(CONFIG_JSON_FILE)

        write_json_list(CONFIG_JSON_FILE, [])

        if LEGACY_CONFIG_FILE.exists():
            return self._attempt_legacy_conversion()

        return []

    def save_target_folders(self) -> None:
        write_json_list(CONFIG_JSON_FILE, self.target_folders)

    def add_target_folder(self, folder: str) -> bool:
        folder_name = folder.strip()
        if not folder_name:
            return False

        folder_path = Path(folder_name)
        if folder_path.is_absolute():
            folder_name = str(folder_path.resolve())

        if folder_name in self.target_folders:
            return False

        self.target_folders.append(folder_name)
        self.save_target_folders()
        return True

    def create_target_folder(self, folder_name: str) -> bool:
        clean_folder_name = folder_name.strip()
        if not clean_folder_name:
            return False

        if self.root_folder is None:
            self.pending_message = "Please select a source folder first."
            return False

        folder_path = (self.root_folder / clean_folder_name).resolve()
        folder_as_text = str(folder_path)
        if folder_as_text in self.target_folders:
            return False

        ensure_directory(folder_path)
        self.target_folders.append(folder_as_text)
        self.save_target_folders()
        return True

    def remove_target_folder(self, folder: str) -> bool:
        if folder not in self.target_folders:
            return False

        self.target_folders.remove(folder)
        self.save_target_folders()
        return True

    def set_root_folder(self, folder: str) -> bool:
        folder_path = Path(folder)
        if not folder_path.is_dir():
            return False

        self.root_folder = folder_path
        self._attempt_legacy_conversion()
        self.images = list_file_names(folder_path)
        self.image_index = 0
        self.current_image_name = None
        return True

    def has_images(self) -> bool:
        return bool(self.images)

    def get_next_image_path(self) -> Path | None:
        if self.root_folder is None or self.image_index >= len(self.images):
            self.current_image_name = None
            return None

        self.current_image_name = self.images[self.image_index]
        self.image_index += 1
        return self.root_folder / self.current_image_name

    def move_current_image(self, target_folder: str) -> Path | None:
        if self.root_folder is None or self.current_image_name is None:
            return None

        source = self.root_folder / self.current_image_name
        destination_folder = self._resolve_target_folder(target_folder)
        moved_path = move_file(source, destination_folder)
        print(f"Moved {source} to {destination_folder}")
        self.current_image_name = None
        return moved_path

    def _resolve_target_folder(self, target_folder: str) -> Path:
        target_path = Path(target_folder)
        if target_path.is_absolute():
            return target_path

        if self.root_folder is None:
            return target_path

        return self.root_folder / target_path

    def consume_pending_message(self) -> str | None:
        message = self.pending_message
        self.pending_message = None
        return message

    def _attempt_legacy_conversion(self) -> list[str]:
        if not LEGACY_CONFIG_FILE.exists():
            return self.target_folders if hasattr(self, "target_folders") else []

        if self.root_folder is None:
            self.pending_message = (
                "Please select a source folder before converting target folders."
            )
            return []

        converted_folders: list[str] = []
        for folder in read_lines(LEGACY_CONFIG_FILE):
            folder_path = Path(folder)
            if not folder_path.is_absolute():
                folder_path = self.root_folder / folder_path
            converted_folders.append(str(folder_path.resolve()))

        self.target_folders = converted_folders
        self.save_target_folders()
        return converted_folders
