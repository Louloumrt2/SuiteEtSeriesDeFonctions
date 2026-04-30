import ttkbootstrap as ttk

class BoundsError(Exception): pass # créer une erreur qui servira si xMin >= xMax 

from usefull_func import is_float, to_float



class decimal_entry(ttk.Entry) :

    def __init__(self, master, **keywords):
        vcmd = master.register(is_float)
        super().__init__(master, **keywords, validate='key', validatecommand=(vcmd, "%P"))
   
    def get(self) :
        return str(to_float(super().get()))



if __name__ == "__main__":
    app = ttk.Window()
    entry = decimal_entry(app)
    entry.pack(padx=10, pady=10)
    app.mainloop()