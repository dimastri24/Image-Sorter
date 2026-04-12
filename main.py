import os
import shutil
from tkinter import Tk, Button, Label, Listbox, filedialog, Entry, Frame
from PIL import Image, ImageTk

class ImageSorter:
    def __init__(self):
        self.root = Tk()
        self.root.title("Image Sorter")
        
        self.root_folder = None
        self.target_folders = self.load_target_folders()  # Load target folders from file
        
        # Left column for the 'Select Image Folder' button and the image label
        left_frame = Frame(self.root)
        left_frame.pack(side='left', fill='both', expand=True)

        self.select_folder_button = Button(left_frame, text="Select Image Folder", command=self.select_folder)
        self.select_folder_button.pack()

        self.image_label = Label(left_frame)  # Assuming you will configure this later to show an image
        self.image_label.pack()

        # Right column for buttons and listbox
        right_frame = Frame(self.root)
        right_frame.pack(side='right', fill='both', expand=True)

        # Frame for button group 'Select Folder', 'Add Folder', and 'Remove Folder'
        button_group_frame = Frame(right_frame)
        button_group_frame.pack(pady=20)  # Add some padding to center the group vertically

        self.select_folder_button = Button(button_group_frame, text="Select Folder", command=self.select_existing_folder)
        self.select_folder_button.pack(side='left')  # Pack buttons side by side

        self.add_folder_button = Button(button_group_frame, text="Add", command=self.add_folder)
        self.add_folder_button.pack(side='left')

        self.remove_folder_button = Button(button_group_frame, text="Remove", command=self.remove_folder)
        self.remove_folder_button.pack(side='left')

        # Listbox for folder list followed by entry for new folder
        self.new_folder_entry = Entry(right_frame, width=30)
        self.new_folder_entry.pack()

        self.folder_list = Listbox(right_frame, width=30)
        self.update_folder_list()
        self.folder_list.pack()

        # Frame for button group 'Skip', 'Move Image', and 'Quit'
        bottom_button_group_frame = Frame(right_frame)
        bottom_button_group_frame.pack(pady=20)

        self.next_button = Button(bottom_button_group_frame, text="Skip", command=self.show_next_image)
        self.next_button.pack(side='left')

        self.ok_button = Button(bottom_button_group_frame, text="Move Image", command=self.move_and_show_next)
        self.ok_button.pack(side='left')

        self.quit_button = Button(bottom_button_group_frame, text="Quit", command=self.quit)
        self.quit_button.pack(side='left')

        self.root.mainloop()

    def select_folder(self):
        self.root_folder = filedialog.askdirectory()
        if self.root_folder:
            self.load_images()
            self.image_index = 0  # Initialize image_index
            self.show_next_image()

    def select_existing_folder(self):
        folder = filedialog.askdirectory()
        if folder and folder not in self.target_folders:
            self.target_folders.append(folder)
            self.update_folder_list()
            
    def load_target_folders(self):
        if os.path.exists("config-target.txt"):
            with open("config-target.txt", "r") as f:
                return [folder.strip() for folder in f.readlines()]
        else:
            return ["mfolder_1", "mfolder_2", "mfolder_3"]

    def save_target_folders(self):
        with open("config-target.txt", "w") as f:
            for folder in self.target_folders:
                f.write(f"{folder}\n")

    def load_images(self):
        if self.root_folder:
            self.images = [item for item in os.listdir(self.root_folder) if os.path.isfile(os.path.join(self.root_folder, item))]

    def update_folder_list(self):
        self.folder_list.delete(0, "end")
        for folder in self.target_folders:
            self.folder_list.insert("end", folder)
        self.save_target_folders()

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
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        shutil.move(image_path, target_path)
        print(f"Moved {image_path} to {target_path}")

    def add_folder(self):
        new_folder = self.new_folder_entry.get()
        if new_folder and new_folder not in self.target_folders:
            self.target_folders.append(new_folder)
            self.update_folder_list()
            self.new_folder_entry.delete(0, "end")

    def remove_folder(self):
        selected_index = self.folder_list.curselection()
        if selected_index:
            selected_folder = self.folder_list.get(selected_index)
            self.target_folders.remove(selected_folder)
            self.update_folder_list()

if __name__ == "__main__":
    sorter = ImageSorter()
