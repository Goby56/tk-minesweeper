import tkinter as tk
from PIL import Image

import utils
from menu import Menu
from game import Game

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.title("Minesweeper in tkinter")

        self.load_images()

        self.in_game = False
        self.load_menu()

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
        self.menu = Menu(self.root, self.menu_frame, self.menu_images, self.switch_frame)

    def load_game(self, dimensions: tuple, number_of_bombs: int):
        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack(fill=tk.BOTH, expand=True)
        self.game = Game(self.root, self.game_frame, dimensions, number_of_bombs, self.tile_images, self.switch_frame)

    def load_images(self):
        img = Image.open("images/tiles.png")
        tiles = []
        img_width = img.width/4
        img_height = img.height/3
        for r, c in utils.get_matrix_indicies(3, 4):
                tiles.append(img.crop((img_width*c, img_height*r, img_width*(c+1), img_height*(r+1))))
        self.tile_images = {
            "": tiles[0], "safe": tiles[1], "-1": tiles[2], "0": tiles[3],
            "1": tiles[4], "2": tiles[5], "3": tiles[6], "4": tiles[7],
            "5": tiles[8], "6": tiles[9], "7": tiles[10], "8": tiles[11],
            "unsure": Image.open("images/qm.png"), "selected": Image.open("images/select.png"),
            "smiley": Image.open("images/smiley.png"), "sadey": Image.open("images/sadey.png"),
            "cooley": Image.open("images/cooley.png")
        }

        self.menu_images = {
            "start": Image.open("images/start.png"), "columns": Image.open("images/x.png"), "rows": Image.open("images/y.png"), 
            "bombs": Image.open("images/b.png"), "0": Image.open("images/0.png"), "1": Image.open("images/1.png"), 
            "2": Image.open("images/2.png"), "3": Image.open("images/3.png"), "4": Image.open("images/4.png"), 
            "5": Image.open("images/5.png"), "6": Image.open("images/6.png"), "7": Image.open("images/7.png"), 
            "8": Image.open("images/8.png"), "9": Image.open("images/9.png")
        }

if __name__ == "__main__":
    app = App()
    app.root.mainloop()