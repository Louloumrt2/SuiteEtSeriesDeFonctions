from tkinter import ttk
from SFonction import SFonction

class SFunction_Editor(ttk.Frame) :
    def __init__(self, master) :
        self.master = master
        super().__init__(master)
        self.pack(fill="both", expand=True)
