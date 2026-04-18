from pathlib import Path

from ..config.settings import CONFIG_FILE, DEFAULT_TARGET_FOLDERS
from ..utils.file_utils import list_file_names, move_file, read_lines, write_lines


class ImageService:
    def __init__(self) -> None:
        self.root_folder: Path | None = None
        self.images: list[str] = []
        self.image_index = 0
        self.current_image_name: str | None = None
        self.target_folders = self.load_target_folders()

    def load_target_folders(self) -> list[str]:
        stored_folders = read_lines(CONFIG_FILE)
        if stored_folders:
            return stored_folders
        return DEFAULT_TARGET_FOLDERS.copy()

    def save_target_folders(self) -> None:
        write_lines(CONFIG_FILE, self.target_folders)

    def add_target_folder(self, folder: str) -> bool:
        folder_name = folder.strip()
        if not folder_name or folder_name in self.target_folders:
            return False

        self.target_folders.append(folder_name)
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
