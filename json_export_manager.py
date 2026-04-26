from SFonction import SFonction
import json
import ttkbootstrap as ttk


class sfunction_manager:
    def __init__(self, window, directory=""):
        self.app = window
        self.directory = directory

        self.all_sfunctions : list[SFonction] = [] # Liste de toutes les fonctions présentes dans l'application (pour pouvoir les exporter facilement)
        self.link_to_paths : dict[str, SFonction] = {} # Dictionnaire pour faire le lien entre les fonctions et leurs chemins d'exportation respectifs (pour éviter de devoir redemander le chemin à chaque exportation)

        self.menus = {} # Dictionnaire pour faire le lien entre les fonctions et leurs menus respectifs (pour pouvoir mettre à jour les menus quand on rajoute/supprime une sfonction)
        self.selected = None # Fonction actuellement sélectionnée (pour pouvoir faire le lien entre les boutons d'édition/suppression et la fonction à éditer/supprimer)
    

    def add_sfonction(self, sfunc : SFonction, export_path : str) :
        self.all_sfunctions.append(sfunc)
        self.link_to_paths[export_path] = sfunc

        for menu in self.menus.get(sfunc, []) :
            ... 
        
    
    def import_from_path(self, file_path, ignore_directory=False) -> SFonction | None :
        with open((self.directory if not ignore_directory else "")+file_path, "r") as f :
            new_func = json.load(f, object_hook=lambda d : SFonction(**d))

            if file_path not in self.link_to_paths :
                self.add_sfonction(new_func, file_path)
            else :
                new_func.set_name(new_func.get_name() + "_bis")
                self.add_sfonction(new_func, new_func.get_name() + ".json")

            return new_func

    def export_to_json(self, sfunc : SFonction, file_path : str, ignore_directory=False) :
        if not ignore_directory :
            for link, func in self.link_to_paths.items() :
                if func == sfunc :
                    if file_path!=link :
                        # Si le nom de la fonction a changé, on supprime l'ancien json (et seulement si il était déjà dans le dossier d'exportation, sinon on ne fait rien pour éviter de supprimer un fichier qui ne serait pas lié à une fonction de l'application)
                        try :
                            import os
                            os.remove(self.directory+link) # en supposant que la fonction était déjà dans le dossier d'exportation, sinon ne supprime pas l'original
                        except FileNotFoundError : ...  
                        except Exception as e : ...   

        
        with open((self.directory if not ignore_directory else "")+file_path, "w") as f :
            json.dump(sfunc.convert_to_dict(), f, indent=4)
    
    def export_all_to_json(self) :
        for link, sfunc in self.link_to_paths.items() :
            self.export_to_json(sfunc, sfunc.get_name() + ".json")
    
    def import_all_from_directory(self) :
        import os
        for file in os.listdir(self.directory) :
            if file.endswith(".json") :
                self.import_from_path(file)
    
    def export_as_zip(self, sfonctions : list[SFonction], zip_name : str, path="") :
        import zipfile
        with zipfile.ZipFile(path+zip_name+".zip", 'w') as zipf:
            for sfunc in sfonctions :
                # Ecrire les données de la fonction dans un fichier temporaire
                with open("temp", "w") as temp_file :
                    json.dump(sfunc.convert_to_dict(), temp_file, indent=4)
                # Ajouter le fichier temporaire au zip avec le nom de la fonction
                zipf.write("temp", arcname=sfunc.get_name() + ".json")
    
    def export_as_tar(self, sfonctions : list[SFonction], tar_name : str, path="") :
        import tarfile
        with tarfile.open(path+tar_name+".tar.gz", "w:gz") as tar:
            for sfunc in sfonctions :
                # Ecrire les données de la fonction dans un fichier temporaire
                with open("temp", "w") as temp_file :
                    json.dump(sfunc.convert_to_dict(), temp_file, indent=4)
                # Ajouter le fichier temporaire au zip avec le nom de la fonction
                tar.add("temp", arcname=sfunc.get_name() + ".json")
    
    def import_from_zip(self, zip_path : str, menu_aking = None) :
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            for file in zipf.namelist() :
                if file.endswith(".json") :
                    with zipf.open(file) as f :
                        new_func = json.load(f, object_hook=lambda d : SFonction(**d))
                        self.add_sfonction(new_func, new_func.get_name() + ".json")
                        
                        if menu_aking is not None :
                            menu_aking.add_sfonction(new_func)
                        
    
    def import_from_tar(self, tar_path : str, menu_aking = None) :
        import tarfile
        with tarfile.open(tar_path, "r:gz") as tar:
            for member in tar.getmembers() :
                if member.name.endswith(".json") :
                    f = tar.extractfile(member)
                    if f is not None :
                        new_func = json.load(f, object_hook=lambda d : SFonction(**d))
                        self.add_sfonction(new_func, new_func.get_name() + ".json")

                        if menu_aking is not None :
                            menu_aking.add_sfonction(new_func)
    
if __name__ == "__main__":
    app = ttk.Window()
    manager = sfunction_manager(app, directory="auto_saves/")
    from editablelabel import editable_sfunc_name

    manager.import_all_from_directory()
    for sfunc in manager.all_sfunctions :
        editable_label = editable_sfunc_name(app, sfunc)
        editable_label.pack(padx=10, pady=10)


    app.mainloop()

    print("Exportation en cours...")
    manager.export_all_to_json()