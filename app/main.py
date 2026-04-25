from tkinter import Tk

from .config.settings import APP_TITLE, INITIAL_WINDOW_SIZE
from .services.image_service import ImageService
from .ui.main_window import MainWindow


def configure_window(root: Tk) -> None:
    width, height = INITIAL_WINDOW_SIZE
    available_width = root.winfo_vrootwidth()
    available_height = root.winfo_vrootheight()
    origin_x = root.winfo_vrootx()
    origin_y = root.winfo_vrooty()

    width = min(width, available_width)
    height = min(height, available_height)
    position_x = origin_x + max((available_width - width) // 2, 0)
    position_y = origin_y + max((available_height - height) // 2, 0)

    root.geometry(f"{width}x{height}+{position_x}+{position_y}")


def main() -> None:
    root = Tk()
    root.title(APP_TITLE)
    configure_window(root)

    image_service = ImageService()
    MainWindow(root, image_service)

    root.mainloop()
