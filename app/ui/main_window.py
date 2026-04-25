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

from ..config.settings import (
    FOLDER_CARD_PREVIEW_SIZE,
    FOLDER_GRID_COLUMN_RANGE,
    SOURCE_PREVIEW_SIZE,
    THUMBNAIL_SIZE,
)
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
        self.folder_grid_columns = FOLDER_GRID_COLUMN_RANGE[0]

        self._build_layout()
        self.update_folder_list()
        self.show_pending_message()

    def _build_layout(self) -> None:
        section_padding_x = 20
        section_padding_y = 16

        left_frame = Frame(self.root)
        left_frame.pack(
            side="left",
            fill=BOTH,
            expand=True,
            padx=(section_padding_x, section_padding_x // 2),
            pady=section_padding_y,
        )

        self.select_image_folder_button = Button(
            left_frame,
            text="Select Image Folder",
            command=self.select_image_folder,
        )
        self.select_image_folder_button.pack(anchor="w", pady=(12, 16))

        preview_width, preview_height = SOURCE_PREVIEW_SIZE
        self.source_preview_frame = Frame(
            left_frame,
            width=preview_width,
            height=preview_height,
        )
        self.source_preview_frame.pack(anchor="n", pady=(0, 16))
        self.source_preview_frame.pack_propagate(False)

        self.image_label = Label(
            self.source_preview_frame,
            width=preview_width,
            height=preview_height,
            text="Select an image folder to begin.",
        )
        self.image_label.pack(fill=BOTH, expand=True)

        navigation_button_frame = Frame(left_frame)
        navigation_button_frame.pack(anchor="w", pady=(0, 8))

        self.back_button = Button(
            navigation_button_frame,
            text="Back",
            command=self.show_previous_image,
        )
        self.back_button.pack(side="left", padx=(0, 8))

        self.skip_button = Button(
            navigation_button_frame,
            text="Skip",
            command=self.show_next_image,
        )
        self.skip_button.pack(side="left")

        right_frame = Frame(self.root)
        right_frame.pack(
            side="right",
            fill=BOTH,
            expand=True,
            padx=(section_padding_x // 2, section_padding_x),
            pady=section_padding_y,
        )

        folder_button_frame = Frame(right_frame)
        folder_button_frame.pack(anchor="w", pady=(0, 12))

        self.select_folder_button = Button(
            folder_button_frame,
            text="Select Folder",
            command=self.select_existing_folder,
        )
        self.select_folder_button.pack(side="left", padx=(0, 8))

        self.add_folder_button = Button(
            folder_button_frame,
            text="Add Folder",
            command=self.add_folder,
        )
        self.add_folder_button.pack(side="left", padx=(0, 8))

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
        self.new_folder_entry.pack(fill="x", pady=(0, 8))
        self.new_folder_entry.bind("<KeyRelease>", self.on_folder_query_changed)

        self.add_folder_hint = Label(
            right_frame,
            text='No match found. Use "Add Folder".',
        )

        folder_browser_frame = Frame(right_frame)
        folder_browser_frame.pack(fill=BOTH, expand=True, pady=(0, 12))

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
        self.bind_folder_browser_scroll(self.folder_canvas)
        self.bind_folder_browser_scroll(self.folder_grid)

        action_button_frame = Frame(right_frame)
        action_button_frame.pack(anchor="w", pady=(0, 8))

        self.move_button = Button(
            action_button_frame,
            text="Move Image",
            command=self.move_and_show_next,
        )
        self.move_button.pack(side="left", padx=(0, 8))

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

        column_count = self.get_folder_grid_column_count()
        self.folder_grid_columns = column_count

        for index, folder in enumerate(self.filtered_folders):
            row = index // column_count
            column = index % column_count
            card = self.create_folder_card(self.folder_grid, folder)
            card.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")

        max_columns = FOLDER_GRID_COLUMN_RANGE[1]
        for column in range(max_columns):
            weight = 1 if column < column_count else 0
            self.folder_grid.grid_columnconfigure(column, weight=weight)

        self.update_add_folder_state()
        self.folder_canvas.yview_moveto(0)

    def show_next_image(self) -> None:
        image_path = self.image_service.get_next_image_path()
        if image_path is None:
            self.show_empty_preview("No more images.")
            self.show_pending_message()
            return

        self.display_image(image_path)

    def show_previous_image(self) -> None:
        image_path = self.image_service.get_previous_image_path()
        if image_path is None:
            self.show_pending_message()
            return

        self.display_image(image_path)

    def display_image(self, image_path: Path) -> None:
        with Image.open(image_path) as image:
            preview = image.copy()

        preview = ImageOps.contain(preview, SOURCE_PREVIEW_SIZE)
        self.current_photo = ImageTk.PhotoImage(preview)
        self.image_label.config(image=self.current_photo, text="")

    def show_empty_preview(self, message: str) -> None:
        self.current_photo = None
        self.image_label.config(image="", text=message)

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
            self.add_folder_hint.pack(anchor="w", pady=(0, 8))
            return

        self.add_folder_hint.pack_forget()

    def create_folder_card(self, parent: Frame, folder: str) -> Frame:
        is_selected = folder == self.selected_folder
        highlight_color = "#2f6fed" if is_selected else "#d6d9df"
        card = Frame(
            parent,
            bd=0,
            highlightthickness=2 if is_selected else 1,
            highlightbackground=highlight_color,
            highlightcolor=highlight_color,
            padx=0,
            pady=0,
        )

        preview_image = self.get_folder_preview_image(folder)
        preview_width, preview_height = FOLDER_CARD_PREVIEW_SIZE
        preview_frame = Frame(card, width=preview_width, height=preview_height)
        preview_frame.pack(fill="x", expand=True)
        preview_frame.pack_propagate(False)

        preview_label = Label(
            preview_frame,
            image=preview_image,
            width=preview_width,
            height=preview_height,
            bd=0,
        )
        preview_label.image = preview_image
        preview_label.pack(fill=BOTH, expand=True)

        folder_name_label = Label(
            preview_frame,
            text=self.get_folder_display_name(folder),
            wraplength=preview_width - 24,
            justify="left",
            anchor="w",
            bg="#111827",
            fg="#ffffff",
            padx=12,
            pady=8,
        )
        folder_name_label.place(relx=0, rely=1, relwidth=1, anchor="sw")

        self.bind_folder_selection(card, folder)
        self.bind_folder_selection(preview_frame, folder)
        self.bind_folder_selection(preview_label, folder)
        self.bind_folder_selection(folder_name_label, folder)
        return card

    def bind_folder_selection(self, widget: Frame | Label, folder: str) -> None:
        widget.bind("<Button-1>", lambda _event, value=folder: self.select_folder_card(value))

    def bind_folder_browser_scroll(self, widget: Frame | Canvas) -> None:
        widget.bind("<Enter>", self.activate_folder_browser_scroll)
        widget.bind("<Leave>", self.deactivate_folder_browser_scroll)

    def select_folder_card(self, folder: str) -> None:
        self.selected_folder = folder
        self.update_folder_list()

    def activate_folder_browser_scroll(self, _event: object | None = None) -> None:
        self.root.bind_all("<MouseWheel>", self.on_folder_browser_mousewheel)
        self.root.bind_all("<Button-4>", self.on_folder_browser_mousewheel)
        self.root.bind_all("<Button-5>", self.on_folder_browser_mousewheel)

    def deactivate_folder_browser_scroll(self, _event: object | None = None) -> None:
        pointer_widget = self.root.winfo_containing(
            self.root.winfo_pointerx(),
            self.root.winfo_pointery(),
        )
        if pointer_widget and self.is_folder_browser_widget(pointer_widget):
            return

        self.root.unbind_all("<MouseWheel>")
        self.root.unbind_all("<Button-4>")
        self.root.unbind_all("<Button-5>")

    def is_folder_browser_widget(self, widget: object) -> bool:
        current = widget
        while current is not None:
            if current in {self.folder_canvas, self.folder_grid}:
                return True
            current = getattr(current, "master", None)
        return False

    def on_folder_browser_mousewheel(self, event: object) -> str | None:
        if not self.folder_browser_has_overflow():
            return "break"

        delta = getattr(event, "delta", 0)
        if delta:
            scroll_units = -int(delta / 120) if abs(delta) >= 120 else (-1 if delta > 0 else 1)
            self.folder_canvas.yview_scroll(scroll_units, "units")
            return "break"

        num = getattr(event, "num", None)
        if num == 4:
            self.folder_canvas.yview_scroll(-1, "units")
            return "break"
        if num == 5:
            self.folder_canvas.yview_scroll(1, "units")
            return "break"
        return None

    def folder_browser_has_overflow(self) -> bool:
        scroll_region = self.folder_canvas.bbox("all")
        if scroll_region is None:
            return False

        _, top, _, bottom = scroll_region
        content_height = bottom - top
        visible_height = self.folder_canvas.winfo_height()
        return content_height > visible_height

    def get_folder_grid_column_count(self) -> int:
        min_columns, max_columns = FOLDER_GRID_COLUMN_RANGE
        available_width = self.folder_canvas.winfo_width()
        card_width, _ = FOLDER_CARD_PREVIEW_SIZE
        card_spacing = 16
        minimum_column_width = card_width + card_spacing

        if available_width <= 1:
            return min_columns

        column_count = available_width // minimum_column_width
        return max(min_columns, min(max_columns, column_count))

    def get_folder_preview_image(self, folder: str) -> ImageTk.PhotoImage:
        if folder in self.folder_preview_cache:
            return self.folder_preview_cache[folder]

        preview_path = self.get_preview_image_path(folder)
        preview_size = FOLDER_CARD_PREVIEW_SIZE
        if preview_path is None:
            image = Image.new("RGB", preview_size, color="#d9d9d9")
        else:
            with Image.open(preview_path) as opened_image:
                image = ImageOps.fit(opened_image.convert("RGB"), preview_size)

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
        new_column_count = self.get_folder_grid_column_count()
        if new_column_count != self.folder_grid_columns:
            self.update_folder_list()
