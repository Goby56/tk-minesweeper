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
                # button = tk.Frame(self.frame, command=(lambda row=r, column=c: self.reveal(row, column)),
                #                             bg="white", relief="raised", highlightthickness=2)
                button = tk.Frame(self.frame, bg="white", relief="raised", highlightthickness=2, variable=tk.IntVar(0))
                button.grid(row=r, column=c, sticky="news")
                button.bind("<Button-1>", self.reveal)
                button.bind("<Button-3>", self.mark)
                self.cells[r][c] = button
            
        self.frame.columnconfigure(tuple(range(self.width)), weight=1)
        self.frame.rowconfigure(tuple(range(self.height)), weight=1)

    def reveal(self, event: tk.Event):
        info = event.widget.grid_info()
        row, column = info["row"], info["column"]
        event.widget.configure(bg="red")
        print(row, column)
        print(event.widget.variable)

    def mark(self):
        pass

    
    def register_opening(self, pos):
        if not self.game_started:
            self.create_board(pos)
            self.game_started == True
        if self.cells[pos[0]][pos[1]].is_bomb:
            for r in range(self.height):
                for c in range(self.width):
                    if self.cells[r][c].is_bomb:
                        self.cells[r][c].configure(bg="red")
            return
        
        

class Cell:
    min_width, min_height = 15, 15
    board = []
    def __init__(self, position: tuple, parent_frame: tk.Frame, is_bomb: bool, register_opening: callable):
        self.button = tk.Frame(parent_frame, bg="white", relief="raised", highlightthickness=2)
        self.button.grid(row=position[0], column=position[1], sticky="news")
        self.button.bind("<Button-1>", self.reveal)
        self.button.bind("<Button-3>", self.mark)
        
        self.position = position
        self.label = ""
        self.is_bomb = is_bomb
        self.register_opening = register_opening

    def reveal(self, event: tk.Event):
        if self.is_bomb:
            event.widget.configure(bg="red")
            return
        number = self.register_opening(self.position)
        if number == 0:
            for r in range(self.position[0]-1, self.position[0]+2):
                for c in range(self.position[1]-1, self.position[1]+2):
                    pass

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