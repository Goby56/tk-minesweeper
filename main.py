import tkinter as tk
import numpy as np
from PIL import ImageTk, Image
import time, json

from utils import Utils
from solver import Solver

class Game:
    def __init__(self, root: tk.Tk, frame: tk.Frame, dimensions: tuple, number_of_bombs: int, tile_images: list, switch_frame_func: callable):
        self.root = root
        self.frame = frame
        self.tile_images = tile_images
        self.root.resizable(True, True)

        with open("config.json", "r") as f:
            config = json.load(f)

        self.bind_keyboard_keys()

        self.outer_menu_bar = tk.Frame(self.frame, relief=tk.RAISED, borderwidth=10)
        self.outer_menu_bar.grid(row=0, column=0, sticky="news")
        self.outer_menu_bar.rowconfigure(0, weight=1)
        self.outer_menu_bar.columnconfigure(0, weight=1)

        self.inner_menu_bar = tk.Frame(self.outer_menu_bar, relief=tk.SUNKEN, borderwidth=10)
        self.inner_menu_bar.grid(row=0, column=0, sticky="news")
        self.inner_menu_bar.rowconfigure(0, weight=1)
        self.inner_menu_bar.columnconfigure(0, weight=1)
    
        self.restart_button = tk.Label(self.inner_menu_bar)
        self.restart_button.pack(pady=(10,10))
        self.restart_button.bind("<Button-1>", lambda event: switch_frame_func())

        self.game_frame = tk.Frame(self.frame, relief = tk.RAISED, borderwidth = 10)
        self.game_frame.grid(row=1, column=0, sticky="news")
        self.game_frame.bind("<Configure>", self.on_window_resize)


        self.previous_configuration = [dimensions, config["cell_size"], number_of_bombs]
        self.initialize_board(*self.previous_configuration)

    def initialize_board(self, dimensions: tuple, cell_size: int, number_of_bombs: int):
        self.rows, self.columns = dimensions
        self.tile_size = [cell_size, cell_size]
        self.root.geometry(f"{(self.columns)*cell_size}x{(self.rows+2)*cell_size}")
        self.root.minsize(self.columns*15, self.rows*15)

        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=self.rows)

        self.cell_labels = [[None for j in range(self.columns)] for i in range(self.rows)]

        for r, c in Utils.get_matrix_indicies(self.rows, self.columns):
            tk_label = tk.Label(self.game_frame)
            tk_label.grid(row=r, column=c, sticky="news")
            tk_label.bind("<Button-1>", self.clicked_on_cell)
            tk_label.bind("<Button-3>", self.mark_cell)
            self.cell_labels[r][c] = [tk_label, ""] 
            # Actual button reference, Label reference used for visuals
            self.update_tile_image(r, c)
            
        self.game_frame.columnconfigure(tuple(range(self.columns)), weight=1)
        self.game_frame.rowconfigure(tuple(range(self.rows)), weight=1)

        self.game_started = False
        self.game_over = False
        self.game_won = False
        self.number_of_bombs = number_of_bombs

        self.selected_cell = [self.rows//2 - 1, self.columns//2 - 1]

    def move_selection(self, new_pos, selected_board=True):
        r, c = new_pos
        pr, pc = self.selected_cell # Previous coordinates
        self.selected_cell = new_pos

        # Remove previous outline
        tk_label = self.cell_labels[pr][pc][0] # Grab tk.Label in cell
        label = self.cell_labels[pr][pc][1] # Label value
        img = self.tile_images[label].resize(self.tile_size) # PIL Image resized to current tile_size
        photo_img = ImageTk.PhotoImage(img) # Convert to tk image
        tk_label.configure(image=photo_img) # Set image
        tk_label.image = photo_img # Mandatory reference

        # Add outline on current selection
        tk_label: tk.Label = self.cell_labels[r][c][0] # Grab tk.Label in cell
        label = self.cell_labels[r][c][1] # Label value
        img = self.tile_images[label].resize(self.tile_size) # PIL Image resized to current tile_size
        outline_img = self.tile_images["selected"].resize(self.tile_size) 
        img.paste(outline_img, mask=outline_img)
        photo_img = ImageTk.PhotoImage(img) # Convert to tk image
        tk_label.configure(image=photo_img) # Set image
        tk_label.image = photo_img # Mandatory reference

    def clicked_on_cell(self, event: tk.Event, pos=None):
        if pos == None:
            info = event.widget.grid_info()
            row, column = info["row"], info["column"]
            self.move_selection((row, column)) # TODO Only select while holding
        else:
            row, column = pos
        if self.game_over:
            return
        if not self.game_started: # If game has not started, start it
            self.start_game(row, column)
        self.reveal_cell(row, column)
        if self.cell_labels[row][column][1] in "12345678":
            self.quick_reveal(row, column)
        self.check_for_win()

    def mark_cell(self, event: tk.Event, pos=None):
        if self.game_over:
            return
        if pos == None:
            info = event.widget.grid_info()
            row, column = info["row"], info["column"]
        else:
            row, column = pos
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
        for r, c in Utils.get_matrix_indicies(self.rows, self.columns):
            if self.cell_labels[r][c][1] == "safe":
                bombs_left -= 1
        self.root.title(f"Minesweeper in tkinter | Bombs left: {bombs_left}")
        self.check_for_win()

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
        for r, c in Utils.get_surrounding_indices(row, column, self.rows, self.columns):
            self.reveal_cell(r, c)

    def quick_reveal(self, row, column):
        number_of_surrounding_flags = 0
        for r, c in Utils.get_surrounding_indices(row, column, self.rows, self.columns):
            if self.cell_labels[r][c][1] == "safe":
                number_of_surrounding_flags += 1
        if number_of_surrounding_flags != int(self.cell_labels[row][column][1]):
            return
        for r, c in Utils.get_surrounding_indices(row, column, self.rows, self.columns):
            self.reveal_cell(r, c)

    def start_game(self, row, column):
        self.place_bombs(row, column) # Distribute bombs
        self.count_bombs() # Assign numbers to cells
        self.game_started = True
        self.start_time = time.time()

    def handle_game_over(self):
        self.game_over = True
        for r, c in Utils.get_matrix_indicies(self.rows, self.columns):
            if self.board_values[r,c] == -1:
                self.reveal_cell(r, c)
        self.update_menu_images()
        self.root.title(f"Minesweeper in tkinter | GAME OVER :(")

    def clear_board(self):
        self.game_started, self.game_over, self.game_won = False, False, False
        self.root.title(f"Minesweeper in tkinter")
        for r, c in Utils.get_matrix_indicies(self.rows, self.columns):
            self.cell_labels[r][c][1] = ""
            self.update_tile_image(r, c)
        self.update_menu_images()

    def check_for_win(self):
        for r, c in Utils.get_matrix_indicies(self.rows, self.columns):
            if self.cell_labels[r][c][1] == "":
                return
        self.game_over = True
        self.game_won = True
        self.update_menu_images()
        self.root.title(f"Minesweeper in tkinter | GAME WON in {(time.time() - self.start_time):.2f}s")

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
        for row, column in Utils.get_matrix_indicies(self.rows, self.columns):
            if self.board_values[row,column] == -1: 
                continue
            number_of_surrounding_bombs = 0
            for r, c in Utils.get_surrounding_indices(row, column, self.rows, self.columns):
                number_of_surrounding_bombs += 1 if self.board_values[r,c] == -1 else 0
            self.board_values[row,column] = number_of_surrounding_bombs

    def update_tile_image(self, r, c):
        tk_label: tk.Label = self.cell_labels[r][c][0] # Grab tk.Label in cell
        label = self.cell_labels[r][c][1] # Label value
        img = self.tile_images[label].resize(self.tile_size) # PIL Image resized to current tile_size
        photo_img = ImageTk.PhotoImage(img) # Convert to tk image
        tk_label.configure(image=photo_img) # Set image
        tk_label.image = photo_img # Mandatory reference

    def on_window_resize(self, event: tk.Event):
        self.tile_size = (event.width // self.columns, event.height // self.rows)
        for r, c in Utils.get_matrix_indicies(self.rows, self.columns):
            self.update_tile_image(r, c)
        self.update_menu_images()

    def update_menu_images(self):
        restart_button_size = (int(self.tile_size[0]*1.5), int(self.tile_size[1]*1.5))

        if self.game_won: # game won
            img = self.tile_images["cooley"].resize(restart_button_size)
        elif self.game_over and not self.game_won: # game lost
            img = self.tile_images["sadey"].resize(restart_button_size)
        else:
            img = self.tile_images["smiley"].resize(restart_button_size)

        # Smiley button
        photo_img = ImageTk.PhotoImage(img)
        self.restart_button.configure(image=photo_img)
        self.restart_button.image = photo_img
        
    def bind_keyboard_keys(self):
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

        self.root.bind("<space>", lambda event: (
            self.mark_cell(event, self.selected_cell)
        ))
        self.root.bind("<Return>", lambda event: (
            self.clicked_on_cell(event, self.selected_cell)
        ))
        self.root.bind("<Escape>", lambda event: (
            self.clear_board()
        ))

class Menu:
    def __init__(self, root: tk.Tk, frame: tk.Tk, switch_frame_func: callable):
        self.root = root
        self.frame = frame
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
        # self.root.minsize(self.columns*15, self.rows*15)

        self.load_images()

        self.initialize_layout()

        # self.start_game_button.grid(row=0, column=0, sticky="news")
        # self.start_game_button.rowconfigure(0, weight=1)
        # self.start_game_button.columnconfigure(0, weight=1)

    def initialize_layout(self):
        self.start_game_button = tk.Label(self.frame, relief=tk.RAISED, borderwidth=10)
        self.start_game_button.grid(row=1, column=0, columnspan=3, pady=self.cell_size, sticky="")
        photo_img = ImageTk.PhotoImage(self.images["start"].resize((self.cell_size*5, self.cell_size*2)))
        self.start_game_button.configure(image=photo_img)
        self.start_game_button.image = photo_img
        self.start_game_button.bind("<Button-1>", lambda event: self.switch_frame(dimensions=(self.rows, self.columns), number_of_bombs=self.bombs))
        
        self.row_select = tk.Label(self.frame, relief=tk.RAISED, borderwidth=10)
        self.row_select.grid(row=2, column=1, padx=self.cell_size*0.25)
        # photo_img = ImageTk.PhotoImage(self.images["row_select"].resize((self.cell_size*3, int(self.cell_size*1.5))))
        # self.row_select.configure(image=photo_img)
        # self.row_select.image = photo_img
        self.row_select.bind("<MouseWheel>", lambda event: self.on_widget_scrolled(widget="rows", event=event))

        self.column_select = tk.Label(self.frame, relief=tk.RAISED, borderwidth=10)
        self.column_select.grid(row=2, column=0, padx=self.cell_size*0.25)
        # photo_img = ImageTk.PhotoImage(self.images["row_select"].resize((self.cell_size*3, int(self.cell_size*1.5))))
        # self.column_select.configure(image=photo_img)
        # self.column_select.image = photo_img
        self.column_select.bind("<MouseWheel>", lambda event: self.on_widget_scrolled(widget="columns", event=event))
        
        self.bomb_amount_select = tk.Label(self.frame, relief=tk.RAISED, borderwidth=10)
        self.bomb_amount_select.grid(row=2, column=2, padx=self.cell_size*0.25)
        # photo_img = ImageTk.PhotoImage(self.images["row_select"].resize((self.cell_size*3, int(self.cell_size*1.5))))
        # self.bomb_amount_select.configure(image=photo_img)
        # self.bomb_amount_select.image = photo_img
        self.bomb_amount_select.bind("<MouseWheel>", lambda event: self.on_widget_scrolled(widget="bombs", event=event))

        self.frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.dynamic_widgets = {"rows": self.row_select, "columns": self.column_select, "bombs": self.bomb_amount_select}

        self.update_image(widget="rows")
        self.update_image(widget="columns")
        self.update_image(widget="bombs")

    def on_widget_scrolled(self, widget: str, event: tk.Event):
        value = getattr(self, widget)
        setattr(self, widget, max(4, min(value + event.delta // 120, 99)))
    
        print("rows:", self.rows, " columns:", self.columns, " bombs:", self.bombs)

    def update_image(self, widget: str):
        value = str(getattr(self, widget))
        if len(value) == 1:
            value = "0" + value
        
        label_img = self.images[widget].resize((self.cell_size, int(self.cell_size*1.5)))
        tens_img = self.images[value[0]].resize((self.cell_size, int(self.cell_size*1.5)))
        ones_img = self.images[value[1]].resize((self.cell_size, int(self.cell_size*1.5)))

        target_width = self.cell_size * 3
        target_height = int(self.cell_size * 1.5)
        img = Image.new("RGB", (target_width, target_height))
        img.paste(label_img, (0, 0))
        img.paste(tens_img, (self.cell_size * 3, 0))
        img.paste(ones_img, (self.cell_size * 6, 0))

        photo_img = ImageTk.PhotoImage(img)
        self.dynamic_widgets[widget].configure(image=photo_img)
        self.dynamic_widgets[widget].image = photo_img

    def load_images(self):
        self.images = {
            "start": Image.open("start.png"), "columns": Image.open("x.png"), "rows": Image.open("y.png"), "bombs": Image.open("b.png"),
            "0": Image.open("0.png"), "1": Image.open("1.png"), "2": Image.open("2.png"), "3": Image.open("3.png"),
            "4": Image.open("4.png"), "5": Image.open("5.png"), "6": Image.open("6.png"), "7": Image.open("7.png"),
            "8": Image.open("8.png"), "9": Image.open("9.png"), "row_select": Image.open("row_select.png")
        }
        

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.title("Minesweeper in tkinter")

        self.load_tile_images()

        self.load_menu()

        self.in_game = False

    def switch_frame(self, dimensions=None, number_of_bombs=None):
        if self.in_game or dimensions == None or number_of_bombs == None:
            self.game_frame.destroy()
            self.load_menu()
            self.in_game = False
            return
        self.menu_frame.destroy()
        self.load_game(dimensions, number_of_bombs)
        self.in_game = True

    def load_menu(self):
        self.menu_frame = tk.Frame(self.root, relief=tk.RAISED, borderwidth=10)
        self.menu_frame.pack(fill=tk.BOTH, expand=True)
        self.menu = Menu(self.root, self.menu_frame, self.switch_frame)

    def load_game(self, dimensions: tuple, number_of_bombs: int):
        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack(fill=tk.BOTH, expand=True)
        self.game = Game(self.root, self.game_frame, dimensions, number_of_bombs, self.tile_images, self.switch_frame)

    def load_tile_images(self):
        img = Image.open("tiles.png")
        tiles = []
        img_width = img.width/4
        img_height = img.height/3
        for r, c in Utils.get_matrix_indicies(3, 4):
                tiles.append(img.crop((img_width*c, img_height*r, img_width*(c+1), img_height*(r+1))))
        self.tile_images = {
            "": tiles[0], "safe": tiles[1], "-1": tiles[2], "0": tiles[3],
            "1": tiles[4], "2": tiles[5], "3": tiles[6], "4": tiles[7],
            "5": tiles[8], "6": tiles[9], "7": tiles[10], "8": tiles[11],
            "unsure": Image.open("qm.png"), "selected": Image.open("select.png"),
            "smiley": Image.open("smiley.png"), "sadey": Image.open("sadey.png"),
            "cooley": Image.open("cooley.png")
        }

if __name__ == "__main__":
    app = App()
    app.root.mainloop()