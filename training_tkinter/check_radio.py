from tkinter import * 
import ttkbootstrap as ttk

w = ttk.Window( title="Radio et check", themename="darkly")

def addquestion(check : ttk.Checkbutton, i) -> None :
    check.configure(text= f"adherer {i}?")

def removequestion(check : ttk.Checkbutton, i) -> None :
    check.configure(text= f"Canal {i}")

# def gen_decal(check : ttk.Checkbutton) :
#     def decal(motionevent, lastxy=[]) :
#         if motionevent == "leave" :
#             lastxy.clear()
#             base_text = check.cget("text").strip()
#             check.configure(text = base_text)
        
#         else :
#             x, y = motionevent.x, motionevent.y
#             if not lastxy : lastxy.extend([x,y])
#             else :
#                 dx = x - lastxy[0]

#                 base_text = check.cget("text")

#                 check.configure(text = " "*(dx//3) + base_text + " "*(dx<0 and (-dx)//3))
#     return decal




les_selections = [ttk.BooleanVar() for _ in range(5)]
for i in range(5) :
    (check := ttk.Checkbutton(w, variable=les_selections[i], text=f"Canal {i}")).pack(pady=(0 if i<5 else 15))
    # decal_func = gen_decal(check)
    check.bind("<Enter>", (lambda check, i : lambda event : addquestion(check, i))(check, i)) # un lambda qui génère un lambda est la solution que j'ai trouvé pour "encapsuler" le lambda dans un environnement local
    check.bind("<Leave>", (lambda check, i : lambda event : removequestion(check, i))(check, i))
    # check.bind("<Leave>", (lambda decal_func : lambda event : decal_func("leave"))(decal_func))
    # check.bind("<Motion>", decal_func)


setspace = lambda y : (ttk.Frame(w)).pack(pady=y)
setspace(20)

radio_act = ttk.StringVar(w, value="Aucune radio")

for i in ("Skyrock", "NRJ", "France Radio") :
    (ttk.Radiobutton(w, text=i, value=i, variable=radio_act)).pack()






setspace(20)

def gen_combo_selector(master, present_text, items, sep_size=3) -> tuple[ttk.Frame, ttk.StringVar, ttk.Combobox] :
    a_result = ttk.StringVar()
    frame = ttk.Frame()
    a_combo = ttk.Combobox(frame, textvariable=a_result, values=items, state='readonly')

    a_combo.pack(side="right")
    ttk.Label(frame, text=present_text).pack(side='right', pady=sep_size)


    return frame, a_result, a_combo

def gen_spin_selector(master, present_text, items, sep_size=3) -> tuple[ttk.Frame, ttk.StringVar, ttk.Spinbox] :
    a_result = ttk.StringVar()
    frame = ttk.Frame(master)
    a_spin = ttk.Spinbox(frame, textvariable=a_result, values=items, state='readonly')

    a_spin.pack(side="right")
    ttk.Label(frame, text=present_text).pack(side='right', pady=sep_size)


    return frame, a_result, a_spin


items = ('1 centime', "1 euro", '5 euros', '100 euros')
don = ttk.StringVar()
f, res, combo = gen_combo_selector(w, "don : ", items)
f.pack()

generous_var = ttk.StringVar(value="")
generous_label = ttk.Label(textvariable=generous_var)
generous_label.pack()

def change_smooth(strvar : ttk.StringVar, text : str, duration : int = 100, text_init = None, root=w) :

    act = strvar.get()
    if text_init is None : text_init = act

    if text==act : return True

    if (start:=text.startswith(act))  :
        # On doit rajouter les lettres manquantes
        strvar.set(act + text[len(act)]) # on en change une
    else :
        strvar.set(act[:-1])
    
    w.after(duration//(1 if start else 2), (lambda s, t, d, ti, r : lambda : change_smooth(s, t, d, ti, r))(strvar, text, duration, text_init, root))
        

combo.bind('<<ComboboxSelected>>', lambda event : change_smooth(generous_var, "Vous êtes TRES généreux !!" if res.get()=="100 euros" else ("Vous êtes généreux !!" if res.get()=="5 euros" else "")))

setspace(20)
f2, res2, spin = gen_spin_selector(w, "Envie d'écouter de la musique : ", ('un peu', 'assez', 'pas mal', 'plutot', 'oui', 'vraiment', 'enormement', 'hyper', 'mega'))
f2.pack()

def reset_all(event) :
    for var in les_selections :
        var.set(False)
    
    res.set("")
    radio_act.set("Aucune Radio")

w.geometry("500x500")
w.bind("<Alt-KeyPress-a>", reset_all)

w.mainloop()

