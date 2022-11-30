import tkinter as tk
import numpy as np

class App:
    def __init__(self, width: int, height: int, bombs: int):
        self.root = tk.Tk()
        self.root.title("Minesweeper in tkinter")

        self.width, self.height = width, height
        self.create_board()

        self.game_started = False

    def create_board(self):
        self.root.geometry(f"{self.width*25}x{self.height*25}")
        self.root.minsize(self.width*15, self.height*15)

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.frame = tk.Frame(self.root)
        self.frame.grid(row=0, column=0, sticky="news")

        self.cells = [[None for j in range(self.width)] for i in range(self.height)]
        for r in range(self.height):
            for c in range(self.width):
                self.cells[r][c] = Cell(position=(r,c), parent_frame=self.frame, is_bomb=False, start_game_function=self.start_game)

        self.frame.columnconfigure(tuple(range(self.width)), weight=1)
        self.frame.rowconfigure(tuple(range(self.height)), weight=1)

    def start_game(self, position):
        # SAFE SPACE BECAUSE FIRST PLACEMENT
        pass

class Cell:
    min_width, min_height = 15, 15
    def __init__(self, position: tuple, parent_frame: tk.Frame, is_bomb: bool, start_game_function: callable):
        self.button = tk.Frame(parent_frame, bg="white", relief="raised", highlightthickness=2)
        self.button.grid(row=position[0], column=position[1], sticky="news")
        self.button.bind("<Button-1>", self.reveal)
        self.button.bind("<Button-3>", self.mark)

        self.position = position
        self.label = ""
        self.is_bomb = is_bomb
        self.start_game = start_game_function

    def reveal(self, event: tk.Event):
        self.start_game(self.position)
        if self.is_bomb:
            event.widget.configure(bg="red")
        

    def mark(self, event):
        if self.label == "":
            event.widget.configure(bg="green")
            self.label = "safe"
        elif self.label == "safe":
            event.widget.configure(bg="blue")
            self.label = "unsure"
        elif self.label == "unsure":
            event.widget.configure(bg="white")
            self.label = ""


if __name__ == "__main__":
    app = App(36, 24, 32)
    app.root.mainloop()