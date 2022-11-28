import tkinter as tk
import numpy as np

rows, columns = 16, 24

root = tk.Tk()
root.title("Minesweeper")
root.geometry(f"680x595")
root.resizable(False,False)

frame = tk.Frame(root, width = 680, height = 595, relief = tk.RAISED, borderwidth = 10)
frame.grid(row=0, column=1, sticky="news")

menu = tk.Frame(frame, width = 644, height = 80, relief = tk.SUNKEN, borderwidth = 10)
menu.grid(row=1, column=1)

field = tk.Frame(frame, width = 660, height = 450, relief = tk.SUNKEN, borderwidth = 10)
field.grid(row=3, column=1)

seperator1 = tk.Canvas(frame, width = 640, height = 5)
seperator1.grid(row=0, column=1)

seperator2 = tk.Canvas(frame, width = 640, height = 5)
seperator2.grid(row=2, column=1)

seperator3 = tk.Canvas(frame, width = 640, height = 5)
seperator3.grid(row=4, column=1)

seperator4 = tk.Canvas(frame, width = 5, height = 560)
seperator4.grid(row=0, column=0, rowspan = 4)

seperator5 = tk.Canvas(frame, width = 5, height = 560)
seperator5.grid(row=0, column=2, rowspan = 4)

number_of_bombs = 64

def surrounding_cells(pos, array, replace_zero = False, get_list = False):
    count = 0
    surrounding_list = []
    for r in range(pos[0]-1, pos[0]+2):
            for c in range(pos[1]-1, pos[1]+2):
                if r >= 0 and r < rows and c >= 0 and c < columns:
                    count += 1
                    if replace_zero is True:
                        array[r][c] = 0
                    if get_list is True:
                        surrounding_list.append(array[r][c])
    if replace_zero is True:
        return array
    elif get_list is True:
        return surrounding_list
    else:
        return count

def all_cells():
    for r in range(rows):
        for c in range(columns):
            if cells[r][c] != BombCell:
                surrounding_cells((r,c), cells, get_list = True)

def smiley_function():
    uncovered_list = np.empty((rows, columns), dtype = np.int16)
    for r in range(rows):
        for c in range(columns):
            if cells[r][c] != BombCell:
                print(cells[r][c])
                #uncovered_list[r][c] = 88
    #         elif cells[r][c].uncovered == True:
    #             uncovered_list[r][c] = 99 
    #         else:
    #             uncovered_list[r][c] = cells[r][c].number
    # print("")
    # print("")
    # print("")
    # print("")
    # print(uncovered_list)
    

first_click = True

class Cell(tk.Button):
    def __init__(self, master, pos, number = 0, text = ""):
        super().__init__(master, command = self.command, text = text, width = 2, height = 1, borderwidth = 3)
        self.bind("<Button-3>", self.flag)
        self.grid(row = pos[0], column = pos[1])
        self.pos = pos
        self.number = number
        self.text = text
        self.uncovered = False
        self.flagged = False

    def __str__(self):
        return f"Cell at {self.pos} with number {self.number} and state {self.uncovered}"

    def command(self):
        global first_click
        if first_click == True:
            BombCell.place(self.pos)
            NumberedCell.place(self)
            first_click = False
        if self.cget("text") not in ["","F","?"]:
            NumberedCell.quick_reveal(self, self.pos)
        else:
            NumberedCell.reveal(self, self.pos, self.number)

    def flag(self, event):
        if self.uncovered == False: 
            if self.cget("text") == "":
                self.configure(text = "F")
                self.flagged = True
            elif self.cget("text") == "F":
                self.configure(text = "?")
                self.flagged = False
            elif self.cget("text") == "?":
                self.configure(text = "")
                self.flagged = False


class BombCell(Cell):
    def __init__(self, master, pos, text = ""):
        super().__init__(master, pos, text = text)

    def __str__(self):
        return f"BombCell at {self.pos}\n"

    def reveal(self):
        for r in range(rows):
            for c in range(columns):
                if cells[r][c] == BombCell:
                    BombCell(field, (r,c), text = "B")            
                    
    def place(pos):
        mask = np.zeros((rows, columns), dtype=np.float64)
        p = 1 / (rows*columns - surrounding_cells(pos, None))
        mask += p
        mask = surrounding_cells(pos, mask, replace_zero=True).flat
        cells.flat[np.random.choice(rows*columns, number_of_bombs, replace=False, p = mask)] = BombCell


class NumberedCell(Cell):
    def __init__(self, master, number, pos):
        super().__init__(master, pos, number = number)
        
        
    def __str__(self):
        return f"NumberedCell at {self.pos} with number {self.number}\n"

    def place(self):
            for r in range(rows):
                for c in range(columns):
                    if cells[r][c] != BombCell:
                        number = 0
                        for cell in surrounding_cells((r,c), cells, get_list = True):
                            if cell == BombCell:
                                number += 1
                        cells[r][c] = NumberedCell(field, number, (r,c))

    def reveal(self, pos, number):
        if number == 0 and cells[pos[0]][pos[1]] != BombCell:
            NumberedCell.reveal_recursively(pos)
        elif cells[pos[0]][pos[1]] == BombCell:
            BombCell.reveal(self)
        else:
            cells[pos[0]][pos[1]].configure(text = number, relief = tk.FLAT)
            cells[pos[0]][pos[1]].uncovered = True

    def quick_reveal(self, pos):
        count = 0
        for cell in surrounding_cells((pos), cells, get_list = True):
            if cell != BombCell and cells[pos[0]][pos[1]].flagged == True:  
                print("reveal all bombs")  
                BombCell.reveal()
                break
            if cell == BombCell and cell.flagged == True:
                print("successfully flagged bomb")
                count += 1
        if count == cells[pos[0]][pos[1]].number:
            print("execute quick_reveal")
            
        
        

    def reveal_recursively(pos): 
            for r in range(pos[0]-1, pos[0]+2):
                for c in range(pos[1]-1, pos[1]+2):
                    if r >= 0 and r < rows and c >= 0 and c < columns:
                        if cells[r][c].uncovered == False:
                            cells[r][c].uncovered = True
                            cells[r][c].configure(text = "", relief = tk.FLAT)
                            if cells[r][c].number == 0:
                                NumberedCell.reveal_recursively((r,c))
                            else:
                                cells[r][c].configure(text = cells[r][c].number, relief = tk.FLAT)
                                continue
                        
cells = np.empty((rows, columns), dtype = Cell)

smiley = tk.Button(menu, width = 20, height = 1, borderwidth = 10, command = smiley_function)
smiley.pack()

for r in range(rows):
    for c in range(columns):
        cells[r][c] = Cell(field, (r,c))

root.mainloop()