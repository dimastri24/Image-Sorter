import os
import shutil
from tkinter import Tk, Button, Label, Listbox, filedialog, LEFT
from PIL import Image, ImageTk

class ImageSorter:
    def __init__(self):
        self.root = Tk()
        self.root.title("Image Sorter")
        
        self.root_folder = None
        self.target_folders = ["mfolder_1", "mfolder_2", "mfolder_3"]  # Add more folders as needed
        
        self.select_folder_button = Button(self.root, text="Select Image Folder", command=self.select_folder)
        self.select_folder_button.pack()

        self.image_label = Label(self.root)
        self.image_label.pack()

        self.folder_list = Listbox(self.root)
        for folder in self.target_folders:
            self.folder_list.insert("end", folder)
        self.folder_list.pack()

        self.ok_button = Button(self.root, text="OK", command=self.move_and_show_next)
        self.ok_button.pack(side=LEFT)

        self.next_button = Button(self.root, text="Skip", command=self.show_next_image)
        self.next_button.pack(side=LEFT)

        self.quit_button = Button(self.root, text="Quit", command=self.quit)
        self.quit_button.pack(side=LEFT)

        # Centering the buttons horizontally
        self.root.update_idletasks()  # Update the window to get accurate width
        width = max(self.ok_button.winfo_width(), self.next_button.winfo_width(), self.quit_button.winfo_width())
        self.ok_button.pack(fill="x", expand=True, padx=(width - self.ok_button.winfo_width()) / 2)
        self.next_button.pack(fill="x", expand=True, padx=(width - self.next_button.winfo_width()) / 2)
        self.quit_button.pack(fill="x", expand=True, padx=(width - self.quit_button.winfo_width()) / 2)

        self.root.mainloop()

    def select_folder(self):
        self.root_folder = filedialog.askdirectory()
        if self.root_folder:
            self.load_images()
            self.image_index = 0  # Initialize image_index
            self.show_next_image()

    def load_images(self):
        if self.root_folder:
            self.images = os.listdir(self.root_folder)

    def show_next_image(self):
        if self.root_folder and self.images:
            if self.image_index < len(self.images):
                image_path = os.path.join(self.root_folder, self.images[self.image_index])
                image = Image.open(image_path)
                image.thumbnail((300, 300))
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo)
                self.image_label.image = photo
                self.image_index += 1
            else:
                self.quit()

    def quit(self):
        self.root.destroy()

    def move_and_show_next(self):
        selected_index = self.folder_list.curselection()
        if selected_index and self.root_folder:
            selected_folder = self.folder_list.get(selected_index)
            self.move_image(selected_folder)
            self.show_next_image()

    def move_image(self, target_folder):
        image_path = os.path.join(self.root_folder, self.images[self.image_index - 1])
        target_path = os.path.join(self.root_folder, target_folder)
        shutil.move(image_path, target_path)
        print(f"Moved {image_path} to {target_path}")

if __name__ == "__main__":
    sorter = ImageSorter()
