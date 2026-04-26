import ttkbootstrap as ttk
from SFonction import SFonction
from editablelabel import editable_sfunc_name
from input_dialog import Input_Dialog

nothing = lambda : None # Fonction vide pour les callbacks par défaut

class Function_Editor(ttk.Frame):
    def __init__(self, master, sfonction : SFonction, select_callback = nothing, delete_callback = nothing, dupliquer_callback = nothing, export_callback = nothing) :
        super().__init__(master)

        self.sfonction = sfonction
        self.selected = ttk.BooleanVar(value=False)

        self.editable_label = editable_sfunc_name(self, sfonction)
        self.editable_label.pack(fill="x", expand=True)

        self.use_button = ttk.Button(self, text="Utiliser", command=nothing)
        self.use_button.pack(side="left", padx=5, pady=5)

        # Le bouton de sélection est un toggle button qui permet de sélectionner/désélectionner la fonction pour l'exportation multiple
        self.select_button = ttk.Checkbutton(self, text="Sélectionner", variable=self.selected, command=select_callback)
        self.select_button.pack(side="left", padx=5, pady=5)

        self.delete_button = ttk.Button(self, text="Supprimer", command=delete_callback)
        self.delete_button.pack(side="left", padx=5, pady=5)

        self.delete_button = ttk.Button(self, text="Dupliquer", command=dupliquer_callback)
        self.delete_button.pack(side="left", padx=5, pady=5)

        self.export_button = ttk.Button(self, text="Exporter", command= export_callback)
        self.export_button.pack(side="left", padx=5, pady=5)

        

class Menu_SFonction:
    # Les Menu_SFonction permettent de regrouper une collection de fonctions en une liste déroulante.
    # Chaque ligne contient le nom de la fonction, ainsi qu'un bouton Utiliser et Selectionner
    # Le haut du menu contient un bouton Export

    def __init__(self, master) :
        self.frame = ttk.Frame(master)
        

        self.sfonctions : list[SFonction] = [] 

        self.sfunction_manager = None # Le manager de sfonctions associé à ce menu (pour pouvoir faire le lien entre les fonctions et leurs chemins d'exportation respectifs)

        # Ajout du bouton Exporter tout en haut du menu
        self.export_selection_button = ttk.Button(self.frame, text="Exporter la sélection", command=self.export_selected)
        self.export_selection_button.pack(fill="x", padx=5, pady=5)

        self.export_all_button = ttk.Button(self.frame, text="Exporter tout", command=self.export_all)
        self.export_all_button.pack(fill="x", padx=5, pady=5)

        self.import_button = ttk.Button(self.frame, text="Importer une suite/série de fonction", command=self.ask_import_sfonction)
        self.import_button.pack(fill="x", padx=5, pady=5)

        self.import_zip_tar = ttk.Frame(self.frame)
        self.import_zip_tar.pack(fill="x", padx=5, pady=5)

        self.import_zip_button = ttk.Button(self.import_zip_tar, text="Importer depuis un zip", command=self.ask_import_sfonctions_from_zip)
        self.import_zip_button.pack(side="left", fill="x", expand=True, padx=5)
        self.import_tar_button = ttk.Button(self.import_zip_tar, text="Importer depuis un tar", command=self.ask_import_sfonctions_from_tar)
        self.import_tar_button.pack(side="left", fill="x", expand=True, padx=5)


        self.scroll_frame = ttk.Scrollbar(self.frame)
        self.canvas = ttk.Canvas(self.frame, yscrollcommand=self.scroll_frame.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll_frame.config(command=self.canvas.yview)
        self.scroll_frame.pack(side="right", fill="y")
        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw", width=self.frame.winfo_width()-10)

        def update_scrollregion(event) :
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            self.inner_frame.bind("<Configure>", update_scrollregion)
        
        def on_mousewheel(event) :
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)

        self.update_export_buttons_state() # Désactiver les boutons d'exportation
    

    def add_to_selection(self, sfonction_editor : Function_Editor) :
        sfonction_editor.selected.set(True)
        self.update_export_buttons_state()

    def update_export_buttons_state(self) :
        if (self.sfunction_manager is None) or (not self.sfonctions) :
            self.export_selection_button.config(state="disabled")
            self.export_all_button.config(state="disabled")
            return
        
        self.export_all_button.config(state="enabled")

        if self.get_selected_sfonctions() :
            self.export_selection_button.config(state="enabled")
        else :
            self.export_selection_button.config(state="disabled")
        

    def add_sfonction(self, sfonction : SFonction) :
        if sfonction not in self.sfonctions :
            editor = Function_Editor(self.inner_frame, sfonction, select_callback=self.update_export_buttons_state, delete_callback= lambda sfun=sfonction : self.remove_sfonction(sfun), dupliquer_callback = lambda sfun=sfonction : self.add_sfonction(sfun.duplicate()), export_callback= lambda sfun=sfonction : self.export_one(sfun))
            editor.pack(fill="x", expand=True, padx=5, pady=5)
            self.sfonctions.append(sfonction)
            self.update_export_buttons_state()

            self.inner_frame.update_idletasks()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

            # Ajouter la fonction au manager si elle n'y est pas déjà (sert si on crée une nouvelle fonction à partir de l'interface, pour qu'elle soit automatiquement ajoutée au manager et puisse être exportée)
            if self.sfunction_manager is not None and sfonction not in self.sfunction_manager.all_sfunctions :
                self.sfunction_manager.add_sfonction(sfonction, export_path=sfonction.get_name() + ".json")
    
    def add_manager(self, manager) :
        self.sfunction_manager = manager
        self.update_export_buttons_state()
        
    def get_selected_sfonctions(self) -> list[SFonction] :
        return [editor.sfonction for editor in self.frame.winfo_children() if isinstance(editor, Function_Editor) and editor.selected.get()]


    def export_selected(self) :
        if self.sfunction_manager is None :
            return
        
        
        nom_chemin = Input_Dialog(self.frame, title="Exporter la sélection", label_text="Quel sera le nom du zip/tar d'exportation ? (entrez .zip ou .tar à la fin) ").result or ""
        if not nom_chemin.endswith(".zip") and not nom_chemin.endswith(".tar") :
            # Dialogue d'erreur pour indiquer que le nom du fichier doit se terminer par .zip ou .tar
            from tkinter import messagebox
            messagebox.showerror("Erreur", "Le nom du fichier doit se terminer par .zip ou .tar")
            return
        else: 
            extension = nom_chemin.split(".")[-1]
            
            if extension == "zip" :
                self.sfunction_manager.export_as_zip(self.get_selected_sfonctions(), "".join(nom_chemin.split(".")[:-1]), path="exports/")
            else :
                self.sfunction_manager.export_as_tar(self.get_selected_sfonctions(), "".join(nom_chemin.split(".")[:-1]), path="exports/")
    
    def export_one(self, sfonction : SFonction):
        # Demander où l'exporter et a quel nom, puis l'exporter en json
        if self.sfunction_manager is None :
            return
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(title="Exporter la fonction", defaultextension=".json", filetypes=[("Fichiers JSON", "*.json")], initialdir="")
        if file_path :
            self.sfunction_manager.export_to_json(sfonction, file_path, ignore_directory = True) # on split pour ne garder que le nom du fichier et pas le chemin complet
    
    def export_all(self) :
        if self.sfunction_manager is None :
            return
        
        
        nom_chemin = Input_Dialog(self.frame, title="Exporter toutes les suites/séries de fonction", label_text="Quel sera le nom du zip/tar d'exportation ? (entrez .zip ou .tar à la fin) ").result or ""
        if not nom_chemin.endswith(".zip") and not nom_chemin.endswith(".tar") :
            # Dialogue d'erreur pour indiquer que le nom du fichier doit se terminer par .zip ou .tar
            from tkinter import messagebox
            messagebox.showerror("Erreur", "Le nom du fichier doit se terminer par .zip ou .tar")
            return
        else: 
            extension = nom_chemin.split(".")[-1]
            
            if extension == "zip" :
                self.sfunction_manager.export_as_zip(self.sfonctions, "".join(nom_chemin.split(".")[:-1]), path="exports/")
            else :
                self.sfunction_manager.export_as_tar(self.sfonctions, "".join(nom_chemin.split(".")[:-1]), path="exports/")
    
    
    def remove_sfonction(self, sfonction : SFonction) :
        for child in self.inner_frame.winfo_children() :
            if isinstance(child, Function_Editor) and child.sfonction == sfonction :
                child.destroy()
                break
        
        try :
            self.sfonctions.remove(sfonction)
        except ValueError : pass

        self.update_export_buttons_state()
    
    def import_sfonction(self, path) :
        if self.sfunction_manager is not None :
            try :
                new_func = self.sfunction_manager.import_from_path(path, ignore_directory=True)
                self.add_sfonction(new_func)
            except Exception as e :
                from tkinter import messagebox
                messagebox.showerror("Erreur", f"Une erreur est survenue lors de l'importation de la fonction : {e}")
    
    def ask_import_sfonction(self) :
        if self.sfunction_manager is not None :
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(title="Importer une fonction", filetypes=[("Fichiers JSON", "*.json")], initialdir="")

            if file_path :
                self.import_sfonction(file_path)
    
    def ask_import_sfonctions_from_zip(self) :
        if self.sfunction_manager is not None :
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(title="Importer des fonctions depuis un zip", filetypes=[("Fichiers ZIP", "*.zip")], initialdir="")
            if file_path :
                self.sfunction_manager.import_from_zip(file_path, menu_aking=self) # on passe le menu actuel pour que les fonctions importées soient automatiquement ajoutées au menu
    
    def ask_import_sfonctions_from_tar(self) :
        if self.sfunction_manager is not None :
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(title="Importer des fonctions depuis un tar", filetypes=[("Fichiers TAR", "*.tar")], initialdir="")
            if file_path :
                self.sfunction_manager.import_from_tar(file_path, menu_aking=self) # on passe le menu actuel pour que les fonctions importées soient automatiquement ajoutées au menu



if __name__ == "__main__":
    root = ttk.Window()
    menu = Menu_SFonction(root)
    menu.frame.pack(fill="both", expand=True)

    from json_export_manager import sfunction_manager
    manager = sfunction_manager(root, directory="auto_saves/")
    menu.add_manager(manager)

    sfunc1 = SFonction(nom="Suite de fonctions sans nom 1")
    sfunc2 = SFonction(nom="Suite de fonctions sans nom 2")

    menu.add_sfonction(sfunc1)
    menu.add_sfonction(sfunc2)

    root.mainloop()

    print("Exportation en cours...")
    manager.export_all_to_json()