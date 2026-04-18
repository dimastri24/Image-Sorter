import os
from pathlib import Path
from tkinter import (
    BOTH,
    LEFT,
    END,
    Button,
    Canvas,
    Entry,
    Frame,
    Label,
    Scrollbar,
    StringVar,
    Tk,
    Y,
    filedialog,
    messagebox,
)

from PIL import Image, ImageOps, ImageTk

from ..config.settings import THUMBNAIL_SIZE
from ..services.image_service import ImageService


class MainWindow:
    def __init__(self, root: Tk, image_service: ImageService) -> None:
        self.root = root
        self.image_service = image_service
        self.current_photo: ImageTk.PhotoImage | None = None
        self.folder_query = StringVar()
        self.filtered_folders: list[str] = []
        self.selected_folder: str | None = None
        self.folder_preview_cache: dict[str, ImageTk.PhotoImage] = {}

        self._build_layout()
        self.update_folder_list()
        self.show_pending_message()

    def _build_layout(self) -> None:
        left_frame = Frame(self.root)
        left_frame.pack(side="left", fill=BOTH, expand=True)

        self.select_image_folder_button = Button(
            left_frame,
            text="Select Image Folder",
            command=self.select_image_folder,
        )
        self.select_image_folder_button.pack()

        self.image_label = Label(left_frame)
        self.image_label.pack()

        right_frame = Frame(self.root)
        right_frame.pack(side="right", fill=BOTH, expand=True)

        folder_button_frame = Frame(right_frame)
        folder_button_frame.pack(pady=20)

        self.select_folder_button = Button(
            folder_button_frame,
            text="Select Folder",
            command=self.select_existing_folder,
        )
        self.select_folder_button.pack(side="left")

        self.add_folder_button = Button(
            folder_button_frame,
            text="Add Folder",
            command=self.add_folder,
        )
        self.add_folder_button.pack(side="left")

        self.remove_folder_button = Button(
            folder_button_frame,
            text="Remove",
            command=self.remove_folder,
        )
        self.remove_folder_button.pack(side="left")

        self.new_folder_entry = Entry(
            right_frame,
            width=30,
            textvariable=self.folder_query,
        )
        self.new_folder_entry.pack()
        self.new_folder_entry.bind("<KeyRelease>", self.on_folder_query_changed)

        self.add_folder_hint = Label(
            right_frame,
            text='No match found. Use "Add Folder".',
        )

        folder_browser_frame = Frame(right_frame)
        folder_browser_frame.pack(fill=BOTH, expand=True)

        self.folder_canvas = Canvas(folder_browser_frame, highlightthickness=0)
        self.folder_canvas.pack(side=LEFT, fill=BOTH, expand=True)

        folder_scrollbar = Scrollbar(
            folder_browser_frame,
            orient="vertical",
            command=self.folder_canvas.yview,
        )
        folder_scrollbar.pack(side="right", fill=Y)
        self.folder_canvas.configure(yscrollcommand=folder_scrollbar.set)

        self.folder_grid = Frame(self.folder_canvas)
        self.folder_canvas_window = self.folder_canvas.create_window(
            (0, 0),
            window=self.folder_grid,
            anchor="nw",
        )
        self.folder_grid.bind("<Configure>", self.on_folder_grid_configure)
        self.folder_canvas.bind("<Configure>", self.on_folder_canvas_configure)

        action_button_frame = Frame(right_frame)
        action_button_frame.pack(pady=20)

        self.skip_button = Button(
            action_button_frame,
            text="Skip",
            command=self.show_next_image,
        )
        self.skip_button.pack(side="left")

        self.move_button = Button(
            action_button_frame,
            text="Move Image",
            command=self.move_and_show_next,
        )
        self.move_button.pack(side="left")

        self.quit_button = Button(
            action_button_frame,
            text="Quit",
            command=self.quit,
        )
        self.quit_button.pack(side="left")

    def select_image_folder(self) -> None:
        folder = filedialog.askdirectory()
        if not folder:
            return

        if self.image_service.set_root_folder(folder):
            self.update_folder_list()
            self.show_pending_message()

        if self.image_service.has_images():
            self.show_next_image()

    def select_existing_folder(self) -> None:
        folder = filedialog.askdirectory()
        if not folder:
            return

        if self.image_service.add_target_folder(folder):
            self.update_folder_list()

    def add_folder(self) -> None:
        folder_name = self.folder_query.get()
        if self.image_service.create_target_folder(folder_name):
            self.folder_query.set("")
            self.update_folder_list()
        self.show_pending_message()

    def remove_folder(self) -> None:
        selected_folder = self.get_selected_folder()
        if selected_folder and self.image_service.remove_target_folder(selected_folder):
            self.selected_folder = None
            self.update_folder_list()

    def update_folder_list(self) -> None:
        self.filtered_folders = self.get_filtered_folders()
        if self.selected_folder not in self.filtered_folders:
            self.selected_folder = None

        for child in self.folder_grid.winfo_children():
            child.destroy()

        for index, folder in enumerate(self.filtered_folders):
            row = index // 2
            column = index % 2
            card = self.create_folder_card(self.folder_grid, folder)
            card.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")

        for column in range(2):
            self.folder_grid.grid_columnconfigure(column, weight=1)

        self.update_add_folder_state()
        self.folder_canvas.yview_moveto(0)

    def show_next_image(self) -> None:
        image_path = self.image_service.get_next_image_path()
        if image_path is None:
            self.quit()
            return

        with Image.open(image_path) as image:
            preview = image.copy()

        preview.thumbnail(THUMBNAIL_SIZE)
        self.current_photo = ImageTk.PhotoImage(preview)
        self.image_label.config(image=self.current_photo)

    def move_and_show_next(self) -> None:
        selected_folder = self.get_selected_folder()
        if selected_folder:
            self.image_service.move_current_image(selected_folder)
            self.refresh_folder_preview(selected_folder)
            self.update_folder_list()
            self.show_next_image()

    def get_selected_folder(self) -> str | None:
        return self.selected_folder

    def quit(self) -> None:
        self.root.destroy()

    def show_pending_message(self) -> None:
        message = self.image_service.consume_pending_message()
        if message:
            messagebox.showerror("Error", message)

    def get_folder_display_name(self, folder: str) -> str:
        normalized_folder = folder.rstrip("\\/")
        folder_name = os.path.basename(normalized_folder)
        if folder_name:
            return folder_name
        return folder

    def on_folder_query_changed(self, _event: object | None = None) -> None:
        self.update_folder_list()

    def get_filtered_folders(self) -> list[str]:
        query = self.folder_query.get().strip().lower()
        if not query:
            return list(self.image_service.target_folders)

        filtered_folders: list[str] = []
        for folder in self.image_service.target_folders:
            if query in self.get_folder_display_name(folder).lower():
                filtered_folders.append(folder)
        return filtered_folders

    def update_add_folder_state(self) -> None:
        query = self.folder_query.get().strip()
        should_show_hint = bool(query) and not self.filtered_folders

        if should_show_hint:
            self.add_folder_hint.pack()
            return

        self.add_folder_hint.pack_forget()

    def create_folder_card(self, parent: Frame, folder: str) -> Frame:
        is_selected = folder == self.selected_folder
        relief = "solid" if is_selected else "groove"
        border_width = 2 if is_selected else 1

        card = Frame(parent, bd=border_width, relief=relief, padx=8, pady=8)

        preview_image = self.get_folder_preview_image(folder)
        preview_label = Label(card, image=preview_image, width=120, height=120)
        preview_label.image = preview_image
        preview_label.pack()

        folder_name_label = Label(
            card,
            text=self.get_folder_display_name(folder),
            wraplength=120,
            justify="center",
        )
        folder_name_label.pack(pady=(8, 0))

        self.bind_folder_selection(card, folder)
        self.bind_folder_selection(preview_label, folder)
        self.bind_folder_selection(folder_name_label, folder)
        return card

    def bind_folder_selection(self, widget: Frame | Label, folder: str) -> None:
        widget.bind("<Button-1>", lambda _event, value=folder: self.select_folder_card(value))

    def select_folder_card(self, folder: str) -> None:
        self.selected_folder = folder
        self.update_folder_list()

    def get_folder_preview_image(self, folder: str) -> ImageTk.PhotoImage:
        if folder in self.folder_preview_cache:
            return self.folder_preview_cache[folder]

        preview_path = self.get_preview_image_path(folder)
        if preview_path is None:
            image = Image.new("RGB", (120, 120), color="#d9d9d9")
        else:
            with Image.open(preview_path) as opened_image:
                image = ImageOps.fit(opened_image.convert("RGB"), (120, 120))

        preview_image = ImageTk.PhotoImage(image)
        self.folder_preview_cache[folder] = preview_image
        return preview_image

    def refresh_folder_preview(self, folder: str) -> None:
        self.folder_preview_cache.pop(folder, None)

    def get_preview_image_path(self, folder: str) -> Path | None:
        folder_path = Path(folder)
        if not folder_path.is_dir():
            return None

        supported_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}
        for item in folder_path.iterdir():
            if item.is_file() and item.suffix.lower() in supported_extensions:
                return item
        return None

    def on_folder_grid_configure(self, _event: object | None = None) -> None:
        self.folder_canvas.configure(scrollregion=self.folder_canvas.bbox("all"))

    def on_folder_canvas_configure(self, event: object) -> None:
        width = getattr(event, "width", 0)
        self.folder_canvas.itemconfigure(self.folder_canvas_window, width=width)
