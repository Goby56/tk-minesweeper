import tkinter as tk
from PIL import Image, ImageTk
import json

class Menu:
    def __init__(self, root: tk.Tk, frame: tk.Tk, menu_images: list, switch_frame_func: callable):
        self.root = root
        self.frame = frame
        self.menu_images = menu_images
        self.switch_frame = switch_frame_func
        self.root.resizable(False, False)

        with open("config.json", "r") as f:
            self.config = json.load(f)
            self.cell_size = self.config["cell_size"]

        self.rows = self.config["default_grid"]["y"]
        self.columns = self.config["default_grid"]["x"]
        self.bombs = self.config["default_bomb_amount"]

        width = self.columns * self.cell_size
        height = (self.rows+2)*self.cell_size
        self.root.geometry(f"{width}x{height}")

        self.initialize_layout()

    def initialize_layout(self):
        self.start_game_button = tk.Label(self.frame, relief=tk.RAISED, borderwidth=8)
        self.start_game_button.grid(row=1, column=0, columnspan=3, pady=self.cell_size, sticky="")
        photo_img = ImageTk.PhotoImage(self.menu_images["start"].resize((self.cell_size*5, self.cell_size*2)))
        self.start_game_button.configure(image=photo_img)
        self.start_game_button.image = photo_img
        self.start_game_button.bind("<Button-1>", lambda event: self.switch_frame(dimensions=(self.rows, self.columns), number_of_bombs=self.bombs))
        
        self.row_select = tk.Label(self.frame, relief=tk.SUNKEN, borderwidth=5)
        self.row_select.grid(row=2, column=1, padx=self.cell_size*0.25)
        self.row_select.bind("<MouseWheel>", lambda event: self.on_widget_scrolled(widget="rows", event=event))

        self.column_select = tk.Label(self.frame, relief=tk.SUNKEN, borderwidth=5)
        self.column_select.grid(row=2, column=0, padx=self.cell_size*0.25)
        self.column_select.bind("<MouseWheel>", lambda event: self.on_widget_scrolled(widget="columns", event=event))
        
        self.bomb_amount_select = tk.Label(self.frame, relief=tk.SUNKEN, borderwidth=5)
        self.bomb_amount_select.grid(row=2, column=2, padx=self.cell_size*0.25)
        self.bomb_amount_select.bind("<MouseWheel>", lambda event: self.on_widget_scrolled(widget="bombs", event=event))

        self.frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.dynamic_widgets = {"rows": self.row_select, "columns": self.column_select, "bombs": self.bomb_amount_select}

        self.update_widget_image(widget="rows")
        self.update_widget_image(widget="columns")
        self.update_widget_image(widget="bombs")

    def on_widget_scrolled(self, widget: str, event: tk.Event):
        value = getattr(self, widget)
        setattr(self, widget, max(4, min(value + event.delta // 120, 99)))
        self.update_widget_image(widget)

    def update_widget_image(self, widget: str):
        value = str(getattr(self, widget))
        if len(value) == 1:
            value = "0" + value
        label_img = self.menu_images[widget].resize((self.cell_size, int(self.cell_size * 1.5)))
        tens_img = self.menu_images[value[0]].resize((self.cell_size, int(self.cell_size * 1.5)))
        ones_img = self.menu_images[value[1]].resize((self.cell_size, int(self.cell_size * 1.5)))

        target_width = self.cell_size * 3
        target_height = int(self.cell_size * 1.5)
        img = Image.new("RGB", (target_width, target_height))
        img.paste(label_img, (0, 0))
        img.paste(tens_img, (self.cell_size, 0))
        img.paste(ones_img, (self.cell_size * 2, 0))

        photo_img = ImageTk.PhotoImage(img)
        self.dynamic_widgets[widget].configure(image=photo_img)
        self.dynamic_widgets[widget].image = photo_img

if __name__ == "__main__":
    print("menu.py is not a runnable file, try main.py")