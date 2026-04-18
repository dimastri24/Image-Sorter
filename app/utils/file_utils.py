import json
import shutil
from pathlib import Path


def read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def write_lines(path: Path, lines: list[str]) -> None:
    with path.open("w", encoding="utf-8") as file:
        for line in lines:
            file.write(f"{line}\n")


def read_json_list(path: Path) -> list[str]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, list):
        return [item for item in data if isinstance(item, str)]

    return []


def write_json_list(path: Path, items: list[str]) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(items, file, indent=2)


def list_file_names(folder: Path) -> list[str]:
    return [item.name for item in folder.iterdir() if item.is_file()]


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def move_file(source: Path, target_directory: Path) -> Path:
    ensure_directory(target_directory)
    destination = target_directory / source.name
    shutil.move(str(source), str(destination))
    return destination
