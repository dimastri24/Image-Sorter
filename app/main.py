from tkinter import Tk

from .config.settings import APP_TITLE
from .services.image_service import ImageService
from .ui.main_window import MainWindow


def main() -> None:
    root = Tk()
    root.title(APP_TITLE)

    image_service = ImageService()
    MainWindow(root, image_service)

    root.mainloop()
