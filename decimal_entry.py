import ttkbootstrap as ttk

class BoundsError(Exception): pass # créer une erreur qui servira si xMin >= xMax 

def is_float(val):
    if val in ("", ".", "-", "-."):
        return True  # états intermédiaires acceptables
    try:
        float(val)
        return True
    except ValueError:
        return False

def to_float(val, default = 0) :
    if val in ("", ".", "-", "-.") :
        return default
    else :
        return float(val)



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