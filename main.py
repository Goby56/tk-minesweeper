import tkinter as tk
import numpy as np
from PIL import ImageTk, Image

class App:
    def __init__(self, dimensions: tuple, cell_size: int, number_of_bombs: int):
        self.root = tk.Tk()
        self.root.title("Minesweeper in tkinter")

        self.rows, self.columns = dimensions
        self.tile_size = [cell_size, cell_size]
        self.root.geometry(f"{self.columns*cell_size}x{self.rows*cell_size}")
        self.root.minsize(self.columns*15, self.rows*15)

        self.load_tile_images()

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.frame = tk.Frame(self.root)
        self.frame.grid(row=0, column=0, sticky="news")
        self.frame.bind("<Configure>", self.on_window_resize)

        self.cell_labels = [[None for j in range(self.columns)] for i in range(self.rows)]

        for r in range(self.rows):
            for c in range(self.columns):
                tk_label = tk.Label(self.frame)
                tk_label.grid(row=r, column=c, sticky="news")
                tk_label.bind("<Button-1>", self.clicked_on_cell)
                tk_label.bind("<Button-3>", self.mark_cell)
                self.cell_labels[r][c] = [tk_label, ""]
                self.update_tile_image(r, c)
            
        self.frame.columnconfigure(tuple(range(self.columns)), weight=1)
        self.frame.rowconfigure(tuple(range(self.rows)), weight=1)

        self.game_started = False
        self.game_over = False
        self.number_of_bombs = number_of_bombs

        self.selected_cell = [self.rows//2, self.columns//2]
        self.bind_navigation_keys()

    def move_selection(self, new_pos):
        row, column = new_pos
        self.selected_cell = [row, column]
        # overlay_tk_label = self.cell_labels[row][column][3]
        # img = self.tile_images["selected"].resize(self.tile_size) # PIL Image resized to current tile_size
        # photo_img = ImageTk.PhotoImage(img) # Convert to tk image
        # overlay_tk_label.configure(image=photo_img) # Set image
        # overlay_tk_label.image = photo_img # Mandatory reference

    def clicked_on_cell(self, event: tk.Event):
        info = event.widget.grid_info()
        row, column = info["row"], info["column"]
        if not self.game_started: # If game has not started, place bombs and distribute bomb numbers
            self.game_started = True
            self.place_bombs(row, column)
            self.count_bombs()
        if self.game_over:
            return
        self.reveal_cell(row, column)
        if self.cell_labels[row][column][1] in "12345678":
            self.quick_reveal(row, column)
        event.widget.configure(fg="yellow")

    def mark_cell(self, event: tk.Event):
        if self.game_over:
            return
        info = event.widget.grid_info()
        row, column = info["row"], info["column"]
        print(self.selected_cell)
        label = self.cell_labels[row][column][1]
        if label == "":
            self.cell_labels[row][column][1] = "safe"
            self.update_tile_image(row, column)
        elif label == "safe":
            self.cell_labels[row][column][1] = "unsure"
            self.update_tile_image(row, column)
        elif label == "unsure":
            self.cell_labels[row][column][1] = ""
            self.update_tile_image(row, column)
        bombs_left = self.number_of_bombs
        for r in range(self.rows):
            for c in range(self.columns):
                if self.cell_labels[r][c][1] == "safe":
                    bombs_left -= 1
        self.root.title(f"Minesweeper in tkinter | Bombs left: {bombs_left}")

    def reveal_cell(self, row, column):
        if self.cell_labels[row][column][1] != "":
            return # If cell already is opened
        label = str(int(self.board_values[row,column]))
        self.cell_labels[row][column][1] = label # Acts as opening the cell
        self.update_tile_image(row, column)
        if label == "-1":
            self.handle_game_over()
        if label != "0":
            return # If there are surrounding bombs don't reveal recursively
        for r, c in self.get_surrounding_indices(row, column):
            self.reveal_cell(r, c)

    def quick_reveal(self, row, column):
        number_of_surrounding_flags = 0
        for r, c in self.get_surrounding_indices(row, column):
            if self.cell_labels[r][c][1] == "safe":
                number_of_surrounding_flags += 1
        if number_of_surrounding_flags != int(self.cell_labels[row][column][1]):
            return
        for r, c in self.get_surrounding_indices(row, column):
            self.reveal_cell(r, c)

    def place_bombs(self, r, c):
        safe_cells = 9 # 9 cells safe in beginning
        if (r in [0, self.rows-1] and c in [0, self.columns-1]): # If near corner
            safe_cells -= 5
        if (r == 0 or r == self.rows-1) ^ (c == 0 or c == self.columns-1): # If near edge
            safe_cells -= 3
        # Uniform probability
        p = 1 / (self.columns*self.rows - safe_cells)
        mask = np.full((self.rows,self.columns), p) 
        # Using slice set surrunding cells as zero
        mask[max(r-1,0) : min(r+2,self.rows)  ,  max(c-1,0) : min(c+2,self.columns)] = 0
        # Flattened indices place bombs using numpy choice. Uniform distribution along every index
        bomb_indices = np.random.choice(self.columns*self.rows, self.number_of_bombs, replace=False, p = mask.flatten())
        # Create flattened board
        self.board_values = np.zeros((self.rows*self.columns))
        # Bomb indices get value of -1
        self.board_values[bomb_indices] = -1
        # Turn the very long array into a matrix
        self.board_values = self.board_values.reshape((self.rows, self.columns))

    def count_bombs(self):
        for row in range(self.rows):
            for column in range(self.columns):
                if self.board_values[row,column] == -1: 
                    continue
                number_of_surrounding_bombs = 0
                for r, c in self.get_surrounding_indices(row,column):
                    number_of_surrounding_bombs += 1 if self.board_values[r,c] == -1 else 0
                self.board_values[row,column] = number_of_surrounding_bombs
    
    def handle_game_over(self):
        self.game_over = True
        for row in range(self.rows):
            for column in range(self.columns):
                if self.board_values[row,column] == -1:
                    self.reveal_cell(row, column)

    def get_surrounding_indices(self, row, column):
        for r in range(max(row-1, 0), min(row+2, self.rows)):
            for c in range(max(column-1, 0), min(column+2, self.columns)):
                yield (r, c)

    def update_tile_image(self, r, c):
        tk_label: tk.Label = self.cell_labels[r][c][0] # Grab tk.Label in cell
        label = self.cell_labels[r][c][1] # Label value
        img = self.tile_images[label].resize(self.tile_size) # PIL Image resized to current tile_size
        photo_img = ImageTk.PhotoImage(img) # Convert to tk image
        tk_label.configure(image=photo_img) # Set image
        tk_label.image = photo_img # Mandatory reference

    def on_window_resize(self, event: tk.Event):
        self.tile_size = (event.width // self.columns, event.height // self.rows)
        for r in range(self.rows):
            for c in range(self.columns):
                self.update_tile_image(r, c)
        
    def load_tile_images(self):
        img = Image.open("tiles.png")
        tiles = []
        img_width = img.width/4
        img_height = img.height/3
        for r in range(3):
            for c in range(4):
                tiles.append(img.crop((img_width*c, img_height*r, img_width*(c+1), img_height*(r+1))))
        self.tile_images = {
            "": tiles[0], "safe": tiles[1], "-1": tiles[2], "0": tiles[3],
            "1": tiles[4], "2": tiles[5], "3": tiles[6], "4": tiles[7],
            "5": tiles[8], "6": tiles[9], "7": tiles[10], "8": tiles[11],
            "unsure": Image.open("qm.png"), "selected": Image.open("select.png")
        }
    
    def bind_navigation_keys(self):
        clamp_coordinate = lambda r, c: [max(min(self.rows-1, r), 0), max(min(self.columns-1, c), 0)]
        self.root.bind("w", lambda event: (
            self.move_selection(clamp_coordinate(self.selected_cell[0]-1, self.selected_cell[1]))
            ))
        self.root.bind("a", lambda event: (
            self.move_selection(clamp_coordinate(self.selected_cell[0], self.selected_cell[1]-1))
            ))
        self.root.bind("s", lambda event: (
            self.move_selection(clamp_coordinate(self.selected_cell[0]+1, self.selected_cell[1]))
            ))
        self.root.bind("d", lambda event: (
            self.move_selection(clamp_coordinate(self.selected_cell[0], self.selected_cell[1]+1))
            ))
        
if __name__ == "__main__": 
    app = App(dimensions=(16,16), cell_size=40, number_of_bombs=75)
    app.root.mainloop()