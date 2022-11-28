import tkinter as tk

class App:
    def __init__(self, width: int, height: int):
        self.root = tk.Tk()
        self.root.title("Minesweeper in tkinter")

        self.width, self.height = width, height
        self.root.geometry(f"{width*50}x{height*50}")
        self.root.minsize(width*30, height*30)

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.frame = tk.Frame(self.root)

        self.frame.grid(row=0, column=0, sticky="news")

        for x in range(self.width):
            for y in range(self.height):
                btn = tk.Button(self.frame)
                btn.grid(column=x, row=y, sticky="news")

        self.frame.columnconfigure(tuple(range(x)), weight=1)
        self.frame.rowconfigure(tuple(range(y)), weight=1)

        

if __name__ == "__main__":
    app = App(12,8)
    app.root.mainloop()