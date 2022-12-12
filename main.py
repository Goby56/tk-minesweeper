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

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.frame = tk.Frame(self.root)
        self.frame.grid(row=0, column=0, sticky="news")

        self.cells = [[None for j in range(self.width)] for i in range(self.height)]

        for r in range(self.height):
            for c in range(self.width):
                button = tk.Frame(self.frame, bg="white", relief="raised", highlightthickness=2)
                button.grid(row=r, column=c, sticky="news")
                button.bind("<Button-1>", self.reveal)
                button.bind("<Button-3>", self.mark)
                self.cells[r][c] = [button, ""]
            
        self.frame.columnconfigure(tuple(range(self.width)), weight=1)
        self.frame.rowconfigure(tuple(range(self.height)), weight=1)

        self.game_started = False
        self.bombs = bombs

        self.load_images()
        
    def load_images(self):
        img = Image.open("tiles.png")
        tiles = []
        img_width = img.width/4
        img_height = img.height/3
        for r in range(3):
            for c in range(4):
                tiles.append(img.crop((img_width*c, img_height*r, img_width*(c+1), img_height*(r+1))))
        self.tiles = {
            "": tiles[0], "safe": tiles[1], "-1": tiles[2], "0": tiles[3],
            "1": tiles[4], "2": tiles[5], "3": tiles[6], "4": tiles[7],
            "5": tiles[8], "6": tiles[9], "7": tiles[10], "8": tiles[11]
        }

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
            tk_label = tk.Label(event.widget, image=ImageTk.PhotoImage(self.tiles[label]))
            tk_label.pack()

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