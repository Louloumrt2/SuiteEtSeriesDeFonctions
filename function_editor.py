import ttkbootstrap as ttk
from SFonction import SFonction
from myttkfuncs import gen_combo_selector, gen_spin_selector, gen_entry_field, space
from decimal_entry import decimal_entry, BoundsError
from myttkfuncs import gen_combo_selector, gen_spin_selector, gen_entry_field, space
from input_dialog import Input_Dialog

class ParameterLinker(ttk.Frame) : 
    # Permet de lier les paramètres d'une fonction à des éléments graphiques
    def __init__(self, master, sfonction : SFonction, parameter_name : str, label_text : str, decimal = True, default="0") :
        super().__init__(master)
        
        self.sfonction = sfonction
        self.parameter_name = parameter_name

        self.label_and_entry_frame = ttk.Frame(self)
        self.label = ttk.Label(self.label_and_entry_frame, text=label_text)
        self.label.pack(side='left')

        if parameter_name == "nom" :
            self.var = sfonction.nom
        else :
            self.var = ttk.StringVar(value = getattr(sfonction, parameter_name, default))
        
        if decimal :
            self.entry = decimal_entry(self.label_and_entry_frame, textvariable=self.var)
        else :
            self.entry = ttk.Entry(self.label_and_entry_frame, textvariable=self.var)

        self.entry.pack(side='left', expand=True, fill='x')
        self.entry.bind("<FocusOut>", lambda e : self.update_value())

        self.label_and_entry_frame.pack(fill='x', expand=True)
    
    def update_value(self) :
        value = self.entry.get()
        # print(self.parameter_name,":",value)
        try :

            if self.parameter_name == "nom" :
                self.sfonction.set_name(value)
            else :
                self.sfonction.change_var(self.parameter_name, value)
                # print("Updated", self.parameter_name, "to", self.sfonction.__dict__[self.parameter_name])
            
        except BoundsError as e : print("Oh...", e)
    
    def get(self) :
        return self.entry.get()
    
    def change_sfonction(self, new_sfonction : SFonction, default="0") :
        self.sfonction = new_sfonction
        if self.parameter_name == "nom" :
            self.var = new_sfonction.nom
            self.entry.config(textvariable=self.var)
        else :
            self.var.set(getattr(new_sfonction, self.parameter_name, default))
    
    
        

class SFunction_Editor(ttk.Frame) :
    def __init__(self, master, sfonction : SFonction) :
        
        super().__init__(master)
        self.pack(fill="both", expand=True)
        
        self.actual_sfonction = sfonction

        ttk.Label(self, text="EDITEUR DE SUITE/SERIE DE FONCTION").pack(pady=10)
        space(self, 10)



        # Nom de la fonction
        name_linker = ParameterLinker(self, sfonction, "nom", "Nom de la fonction : ", decimal=False)
        name_linker.pack(fill='x', expand=True, pady=5)

        # Suite / Série de la fonction
        name_linker = ParameterLinker(self, sfonction, "fonction", "Fn(x) = ", decimal=False)
        name_linker.pack(fill='x', expand=True, pady=5)

        # Variations de x
        ttk.Label(self, text="Bornes x :").pack(pady=5)

        min_max_x = ttk.Frame(self)

        min_x_f = ParameterLinker(min_max_x, sfonction, "minX", "Minimum de x : ")
        min_x_f.pack(side='left', fill='x', expand=True, padx=5)

        min_x_f = ParameterLinker(min_max_x, sfonction, "maxX", "Maximum de x : ")
        min_x_f.pack(side='left', fill='x', expand=True, padx=5)

        min_max_x.pack(fill='x', expand=True)

        nb_point = ParameterLinker(self, sfonction, "nbrPoint", "Nombre de point généré : ", default="100")
        nb_point.pack(fill='x', expand=True)

        ttk.Label(self,text="(Plus de point génère une courbe plus lisse et précise, mais augmente le temps de calcul.)").pack(pady=5, expand=True, fill='x')



        
        # Min/Max de N

        space(self, 10)

        ttk.Label(self, text="Variations de n :").pack(pady=5)

        min_max_n = ttk.Frame(self)

        min_n_f = ParameterLinker(min_max_n, sfonction, "minN", "Minimum de n : ")
        min_n_f.pack(side='left', fill='x', expand=True, padx=5)

        min_n_f = ParameterLinker(min_max_n, sfonction, "maxN", "Maximum de n : ")
        min_n_f.pack(side='left', fill='x', expand=True, padx=5)

        min_max_n.pack(fill='x', pady=5, expand=True)

        incr_n = ParameterLinker(self, sfonction, "incrN", "Incrément de n : ")
        incr_n.pack(side='left', fill='x', expand=True)

        space(self, 10)

        def on_closing():
            self.update_all()
            master.destroy()

        master.protocol("WM_DELETE_WINDOW", on_closing)



    def update_all(self) :
        for child in self.winfo_children() :
            if isinstance(child, ParameterLinker) :
                child.update_value()
    
    def update_states(self) :
        ...


    DEFAULT = {
        "fonction" : "x/n",
        "minN" : "1",
        "maxN" : "100",
        "incrN" : "1",
        "minX" : "-20",
        "maxX" : "20",
        "minY" : "-10",
        "maxY" : "10",
        "nbPoint" : "100"
    }
    
    def change_sfonction(self, new_sfonction : SFonction) :
        self.actual_sfonction = new_sfonction
        for child in self.winfo_children() :
            if isinstance(child, ParameterLinker) :
                try :
                    child.change_sfonction(new_sfonction, default= SFunction_Editor.DEFAULT.get(child.parameter_name, "0"))
                except Exception as e :
                    pass 
    

if __name__ == "__main__":
    app = ttk.Window()
    sfunc = SFonction(nom="f", fonction="x", minN="1")
    from json_export_manager import sfunction_manager
    manager = sfunction_manager(app, directory="auto_saves/")
    editor = SFunction_Editor(app, sfunc)
    
    # Update All avant de fermer l'application pour sauvegarder les modifications
    
    app.mainloop()
    manager.export_to_json(sfunc,"modified_func.json")


