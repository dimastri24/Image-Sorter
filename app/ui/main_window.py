import os
from tkinter import (
    BOTH,
    END,
    Button,
    Entry,
    Frame,
    Label,
    Listbox,
    StringVar,
    Tk,
    filedialog,
    messagebox,
)

from PIL import Image, ImageTk

from ..config.settings import THUMBNAIL_SIZE
from ..services.image_service import ImageService


class MainWindow:
    def __init__(self, root: Tk, image_service: ImageService) -> None:
        self.root = root
        self.image_service = image_service
        self.current_photo: ImageTk.PhotoImage | None = None
        self.folder_query = StringVar()
        self.filtered_folders: list[str] = []

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

        self.folder_list = Listbox(right_frame, width=30)
        self.folder_list.pack()

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
            self.update_folder_list()

    def update_folder_list(self) -> None:
        self.folder_list.delete(0, END)
        self.filtered_folders = self.get_filtered_folders()
        for folder in self.filtered_folders:
            self.folder_list.insert(END, self.get_folder_display_name(folder))
        self.update_add_folder_state()

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
            self.show_next_image()

    def get_selected_folder(self) -> str | None:
        selection = self.folder_list.curselection()
        if not selection:
            return None

        return self.filtered_folders[selection[0]]

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
