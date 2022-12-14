import tkinter as tk
import numpy as np
from PIL import ImageTk, Image

class App:
    def __init__(self, width: int, height: int, bombs: int):
        self.root = tk.Tk()
        self.root.title("Minesweeper in tkinter")

        self.width, self.height = width, height
        self.root.geometry(f"{self.width*25}x{self.height*25}")
        self.root.minsize(self.width*15, self.height*15)

        self.load_tile_images()

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.frame = tk.Frame(self.root)
        self.frame.grid(row=0, column=0, sticky="news")
        self.frame.bind("<Configure>", self.on_window_resize)

        self.cells = [[None for j in range(self.width)] for i in range(self.height)]

        for r in range(self.height):
            for c in range(self.width):
                tk_frame = tk.Frame(self.frame)
                tk_frame.grid(row=r, column=c, sticky="news")
                tk_frame.bind("<Button-1>", self.reveal)
                tk_frame.bind("<Button-3>", self.mark)
                tk_label = tk.Label(tk_frame)
                tk_label.pack()
                self.cells[r][c] = [tk_frame, ""]
                self.update_tile_image(r, c)
            
        self.frame.columnconfigure(tuple(range(self.width)), weight=1)
        self.frame.rowconfigure(tuple(range(self.height)), weight=1)

        self.game_started = False
        self.bombs = bombs
        
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
            "5": tiles[8], "6": tiles[9], "7": tiles[10], "8": tiles[11]
        }

    def update_tile_image(self, r, c):
        tk_frame = self.cells[r][c][0]
        label = self.cells[r][c][1]
        # tile_size = (tk_frame.winfo_width(), tk_frame.winfo_height())
        tile_size = (25,25)
        img = self.tile_images[label].resize(tile_size)
        photo_img = ImageTk.PhotoImage(img)
        tk_label = tk_frame.winfo_children()[0]
        tk_label.configure(image=photo_img)
        tk_label.image = photo_img

    def on_window_resize(self, event: tk.Event):
        # tile_size = (event.width // self.width, event.height // event.width)
        print("resize")
        for r in range(self.height):
            for c in range(self.width):
                self.update_tile_image(r, c)

    def place_bombs(self, r, c):
        safe_cells = 9
        if (r in [0, self.height-1] and c in [0, self.width-1]): 
            safe_cells -= 5
        if (r == 0 or r == self.height-1) ^ (c == 0 or c == self.width-1): 
            safe_cells -= 3
        p = 1 / (self.width*self.height - safe_cells)
        mask = np.full((self.height,self.width), p)
        # Using slice set surrunding cells as zero
        mask[max(r-1,0) : min(r+2,self.height)  ,  max(c-1,0) : min(c+2,self.width)] = 0
        # Flattened indices place bombs using numpy choice. Uniform distribution along every index
        bomb_indices = np.random.choice(self.width*self.height, self.bombs, replace=False, p = mask.flatten())
        # Create flattened board
        self.board = np.zeros((self.height*self.width))
        # Bomb indices get value of -1
        self.board[bomb_indices] = -1
        # Turn the very long array into a matrix
        self.board = self.board.reshape((self.height, self.width))

    def count_bombs(self):
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r,c] == -1: continue
                self.board[r,c] = list(self.get_surrounding_cells(r, c)).count(-1)

    def get_surrounding_cells(self, row, column):
        for r in range(max(row-1, 0), min(row+2, self.height)):
            for c in range(max(column-1, 0), min(column+2, self.width)):
                yield self.board[r,c]

    def reveal(self, event: tk.Event):
        info = event.widget.grid_info()
        row, column = info["row"], info["column"]
        if not self.game_started:
            self.place_bombs(row, column)
            self.count_bombs()
        if self.cells[row][column][1] == "":
            label = str(int(self.board[row,column]))
            self.cells[row][column][1] = label
            self.update_tile_image(row, column)

    def mark(self, event: tk.Event):
        info = event.widget.grid_info()
        row, column = info["row"], info["column"]
        print(row, column)
        label = self.cells[row][column][1]
        if label == "":
            event.widget.configure(bg="green")
            label = "safe"
        elif label == "safe":
            event.widget.configure(bg="blue")
            label = "unsure"
        elif label == "unsure":
            event.widget.configure(bg="white")
            label = ""
        self.cells[row][column][1] = label


if __name__ == "__main__":
    app = App(16, 16, 99)
    app.root.mainloop()