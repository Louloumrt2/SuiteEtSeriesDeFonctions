import ttkbootstrap as ttk
from SFonction import SFonction

# J'ai créer cette classe pour avoir un label sépcial pour le nom des suites/séries de fonctions qui permet d'éditer le nom de celles-ci en double cliquant dessus
class editable_sfunc_name(ttk.Frame):
    def __init__(self, master, sfonction : SFonction , lock_on_edit : list[ttk.Button] | None = None, **kwargs):
        super().__init__(master, **kwargs)

        self.lock_on_edit = lock_on_edit or []
        self.label = ttk.Label(self, textvariable=sfonction.nom)
        self.entry = ttk.Entry(self, textvariable=sfonction.nom)
        self.sfonction : SFonction = sfonction

        self.label.pack(fill="x", expand=True)
        self.label.bind("<Double-1>", self.switch_to_entry) # Double clic gauche
        self.entry.bind("<Return>", self.switch_to_label) # Touche Entrée
        self.entry.bind("<FocusOut>", self.switch_to_label) # Perte du focus

    def switch_to_entry(self, event=None):
        for lock in self.lock_on_edit :
            lock.config(state="disabled") # Eviter de pouvoir modifier les favoris/supprimer etc. pendant l'édition

        self.last_name = self.get() # Sauvegarder le nom avant modification
        self.label.pack_forget()
        self.entry.pack(fill="x", expand=True)
        self.entry.focus_set() # Mettre le focus sur l'entrée

    def switch_to_label(self, event=None):
        self.entry.pack_forget()
        for lock in self.lock_on_edit :
            lock.config(state="enabled")
        
        # Changer la fonction ayant le précédant nom par le nouveau nom
        self.label.pack(fill="x", expand=True)
        self.last_name = self.get() # Mettre à jour le dernier nom

    def get(self):
        return self.sfonction.nom.get()

    def set(self, text):
        self.sfonction.nom.set(text)


if __name__ == "__main__":
    root = ttk.Window()
    sfunc = SFonction("Suite de fonctions sans nom")
    editable_label = editable_sfunc_name(root, sfunc)
    editable_label.pack(padx=10, pady=10)
    root.mainloop()