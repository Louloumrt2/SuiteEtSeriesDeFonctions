import ttkbootstrap as ttk

def gen_combo_selector(master, present_text, items, sep_size=3, str_var=None) -> tuple[ttk.Frame, ttk.StringVar, ttk.Combobox] :
    a_result = str_var or ttk.StringVar(master)
    frame = ttk.Frame(master)
    a_combo = ttk.Combobox(frame, textvariable=a_result, values=items, state='readonly')

    a_combo.pack(side="right")
    ttk.Label(frame, text=present_text).pack(side='right', pady=sep_size)


    return frame, a_result, a_combo

def gen_spin_selector(master, present_text, items, sep_size=3, str_var=None) -> tuple[ttk.Frame, ttk.StringVar, ttk.Spinbox] :
    a_result = str_var or ttk.StringVar(master)
    frame = ttk.Frame(master)
    a_spin = ttk.Spinbox(frame, textvariable=a_result, values=items, state='readonly')

    a_spin.pack(side="right")
    ttk.Label(frame, text=present_text).pack(side='right', pady=sep_size)


    return frame, a_result, a_spin

def gen_entry_field(master, present_text, sep_size=3, str_var=None) -> tuple[ttk.Frame, ttk.StringVar, ttk.Entry] :
    a_result = str_var or ttk.StringVar(master)
    frame = ttk.Frame(master)
    a_field = ttk.Entry(frame, textvariable=a_result)

    
    ttk.Label(frame, text=present_text).pack(side='left', pady=sep_size)
    a_field.pack(fill="x")


    return frame, a_result, a_field

def space(master, quantity : int=10) -> None :
    """Définit un espace blanc vertical de quantity pixel"""
    ttk.Frame(master).pack(pady=quantity)