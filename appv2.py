    #=================== IMPORTS ======================

from typing import Generator
from matplotlib import pyplot as plt
import math
from math import sin,cos,sqrt,sinh,cosh,tan,tanh,log,log10,exp,modf,pow,radians,pi
import random
from random import randint,randrange,choice,choices

import tkinter as tk
import ttkbootstrap as ttk # pour avoir de plus beaux menus
from myttkfuncs import *

import os 
import json
import sys
import datetime

fonctions_math = { name: getattr(math, name) for name in dir(math) if not name.startswith("_") } # ca met toutes les fonctions de math dans un dictionnaire nom : fonction (sauf pour les )
fonctions_autorise_python = dict(int=int, max=max, min=min, sum=sum, abs=abs)


math_globals = {
    "__builtins__": {}, # pour éviter à l'utilisateur d'écrire autre chose que des maths, a tout hasard... eval("__import__('os').system('rm -rf /')")
    **fonctions_math,
    **fonctions_autorise_python
}



## NB : il arrive que suite/série de fonctions soit simplement désignée par "fonction" dans les commentaires et variables pour alléger le texte.

#============= FENETRE PRINCIPALE ================

w = ttk.Window(themename="darkly")
w.title("Visualiseur de suites et séries de fonctions")

#============= FUNCTIONS UTILES ===================
def range_(min, max=None, incr=1) : # j'ai adapté le range pour qu'il puisse prendre des decimales
    if min and max is None :
        min, max, incr = 0, min, 1

    x = min
    while x<=max :
        yield x 
        x += incr 

def croissanceExpo(min,max, _) :
    assert isinstance(min,int) and isinstance(max,int)
    while min<max :
        yield min
        min *= 2

def valeur_to_hex(n, nmin, nmax):
    """
    Convertit un nombre n en couleur hex entre vert, jaune et rouge proportionnellmenet
    """
    n = max(min(n, nmax), nmin)
    mid = (nmin + nmax) / 2

    if n <= mid: # De vert à jaune
        
        t = (n - nmin) / (mid - nmin)  
        r = int(255 * t)              
        g = 255                       
    else:  # De jaune à rouge
        t = (n - mid) / (nmax - mid)  
        r = 255                        
        g = int(255 * (1 - t))   
          
    b = 0  

    return f"#{r:02X}{g:02X}{b:02X}"

class BoundsError(Exception): pass # créer une erreur qui servira si xMin >= xMax 

def is_float(val):
    if val in ("", ".", "-", "-."):
        return True  # états intermédiaires acceptables
    try:
        float(val)
        return True
    except ValueError:
        return False

def to_float(val, for_incr=True) :
    if val in ("", ".", "-", "-.") :
        return for_incr and 1 or 0
    else :
        return float(val)


#================= VARIABLES =====================

xMin,xMax,yMin,yMax = (ttk.StringVar(value=default) for default in ("-10","10","-10","10")) # bordure de la fenetre plot (c'est des strings car c'est utilisé dans des input utilisateur (mais ne deviendra jamais autre chose que des strings))
#nMin, nMax = ttk.IntVar(value=1),tk.IntVar(value=15)
#incrN = ttk.DoubleVar(value=1.) # de combien augmente n à chaque itération (pour les suites, il garde 1, pour les série, on choisis un nombre entre 0 et 1 exclus, pour obtenir les variations quand n est réel)

pointsGeneres = ttk.IntVar(value=200) # Plus il y a de points générés, moins la courbe est lisse (mais + de calculs derriere)
vitesseGeneration = ttk.DoubleVar(value=0.1) # temps de pause entre chaque itération (chaque fonction n)

dicoTypeDeCroissance = {"linéaire" : range_, # Par défaut, n varie de nMin à nMax (via un range)
                        "exponentielle" : croissanceExpo} 
fonction = ttk.StringVar(value="x/(x**2+n)")
historique_data = {} # Dictionnaire contenant l'historique des fonctions sauvegardées
favoris_data = {} # Dictionnaire contenant les fonctions favorites

# Variables pour lui la création du plot a l'interface graphique
error = ttk.StringVar(value="")
stop = ttk.BooleanVar(value=False) # bloque la continuations du plot
nAct = ttk.DoubleVar(value=0.0)
nMaxAct = ttk.DoubleVar(value=0)

style = ttk.Style()
PADX = 30
LINE = dict(fill="x", expand=True, padx=PADX)

#============== FONCTIONS MATHS =================

def eval_func(f : str, n : float, xMin : float, xMax : float, nbPoints : int =100) -> tuple[list[tuple[int,int]], list[tuple[int, str]]] :
    """Renvoie la liste des couples (x, y) d'une fonction f : un string en fonction de n, et la liste des erreurs lors de l'évaluation de x
    La liste des x est définit par un xMin, xMax et le nombre total de points"""

    if xMax <= xMin : raise BoundsError(str(xMin)+"|"+str(xMax))

    pas_x = (xMax - xMin) / nbPoints

    res = []
    errors = [] # (x, erreur)

    for x in range_(xMin, xMax, pas_x) :
        try :
            y = eval(f, math_globals, {"x":x, "n":n})
            res.append((x, y))
        except ZeroDivisionError:
            errors.append((x, "Division par 0"))
        except OverflowError:
            errors.append((x, "Valeur obtenus trop élevée"))
        except Exception as e:
            errors.append((x, str(e)))
    
    return res, errors
    
def tracer(valeurs : list[tuple[int,int]], couleur = None) :
    if valeurs :
        xs, ys = zip(*valeurs)
        X, Y = list(xs), list(ys)

        if couleur :
            plt.plot(X,Y, color=couleur)
        else :
            plt.plot(X,Y)

def lancer_all_plot(f : str, xMin : float, xMax : float, nbPoints : int = 150, nMin = 1, nMax = 15, nIncr = 1., nCroissance = range_, yMin=-20, yMax = 20, pause=0.1) :
    plt.clf()
    plt.ylim(yMin,yMax)
    plt.xlim(xMin,xMax) 

    nMaxAct.set(nMax)
    progress["maximum"] = nMax-nMin
    stop.set(False)

    for n in nCroissance(nMin, nMax, nIncr) :
        Valeurs, Erreurs  = eval_func(f, n, xMin, xMax, nbPoints)
        if Erreurs :
            print("Erreurs rencontrées pour n=",n,":",Erreurs)

        tracer(Valeurs, valeur_to_hex(n, nMin, nMax))
        nAct.set(n)
        progress["value"] = n-nMin

        

        if stop.get() : 
            stop.set(False)
            break
        else :
            plt.pause(pause)
    else :
        progress["value"] = nMax-nMin # else pour un for : aucun break n'a eu lieu
    plt.show()

#============ FONCTIONS INTERFACE ===============

# Pour l'instant j'ai mis les constructeur de structeur préfaite dans myttkfuncs

themes = [
        "darkly",
        "superhero",
        "flatly",
        "cyborg",
        "minty"]

def next_theme() :
    act_name = style.theme.name
    if act_name in themes : return themes[(themes.index(act_name)+1) % len(themes)] 
    else : return "darkly"

def theme_act() :
    return style.theme.name

def changer_theme(theme = None):
    style.theme_use(theme or next_theme())
    style.configure(f"Fav.TButton", foreground="gold", background="#282828", selectbackground="#4B4328")


#====================== CONFIG ======================


def get_user_profil() :
    return {"theme": theme_act(),
            "default_param" : {
                "xMin" : xMin.get(), "xMax": xMax.get(), "yMin" : yMin.get(), "yMax" : yMax.get(), "vitesseGeneration" : vitesseGeneration.get()
            },
            "last_func": act_func_dict(),
            "historique": historique_data}

def save_user_profile() :
    with open("user_data/profile_saves.json", "w", encoding="utf-8") as f:
        json.dump(get_user_profil(), f, indent=4, ensure_ascii=False)

def load_config():

    # Obtention du profil

    try:
        with open("user_data/profile_saves.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError | FileNotFoundError :
        config = {}

    # Chargement des données:
    if config.get("theme") : changer_theme(config.get("theme"))

    if (param := config.get("default_param")) :
        if "xMin" in param: xMin.set(param["xMin"])
        if "xMax" in param: xMax.set(param["xMax"])
        if "yMin" in param: yMin.set(param["yMin"])
        if "yMax" in param: yMax.set(param["yMax"])
        if "vitesseGeneration" in param: vitesseGeneration.set(param["vitesseGeneration"])
    
    if "last_func" in config : update_act_func(config["last_func"])

    if "historique" in config :
        historique_data.clear()
        historique_data.update(config["historique"])

        for name, func in historique_data.items() :
            if func.get("favoris") is True :
                favoris_data[name] = func


    return config


def act_func_dict() :
    res = {}

    res["fonction"] = fonction.get()
    res["minN"] = entry_nmin.get()
    res["maxN"] = entry_nmax.get()
    res["incrN"] = nIncrVar.get()
    res["minX"] = xMin.get()
    res["maxX"] = xMax.get()
    res["minY"] = yMin.get()
    res["maxY"] = yMax.get()

    return res 

def update_act_func(dict) :
    if "fonction" in dict : fonction.set(dict["fonction"])
    if "minN" in dict : entry_nmin.set(dict["minN"])
    if "maxN" in dict : entry_nmax.set(dict["maxN"])
    if "incrN" in dict : nIncrVar.set(dict["incrN"])
    if "minX" in dict : xMin.set(dict["minX"])
    if "maxX" in dict : xMax.set(dict["maxX"])
    if "minY" in dict : yMin.set(dict["minY"])
    if "maxY" in dict : yMax.set(dict["maxY"])


    



def on_close():
    add_to_historique((f := act_func_dict()), f["fonction"]+" | "+(date:=str(datetime.datetime.now())), date)
    save_user_profile()
    stop.set(True)
    plt.close()
    w.destroy()

def stop_plot() :
    stop.set(True)

def put_on_favorite(nom : str, dico_func : dict) :
    dico_func["favoris"] = True
    favoris_data[nom] = dico_func

    try : 
        load_favoris(frame_quick_load_fav)
    except Exception :
        pass


def remove_from_favorite(nom : str) :
    if nom in favoris_data :
        favoris_data[nom]["favoris"] = False
        del favoris_data[nom]

def add_to_historique(dico_func : dict, func_name : str, date : str) -> None :
    # Ouvrir profile_saves et ajouter la fonction au dictionnaire "historique"

    if len(historique_data) > 0 and is_same(list(historique_data.values())[-1], dico_func) : return # ne pas ajouter une fonction identique à la fonction actuelle
    historique_data[func_name] = {"date": date, **dico_func}
    load_historique(historique)
    try : 
        load_historique(frame_quick_load)
    except Exception :
        pass


def reset_act_function() -> None:
    update_act_func({"fonction":"x*n", "minN":"0", "maxN":"100", "incrN":1})


def create_new_function() :
    # Ajouer la fonction actuelle à l'historique
    dico_act_func = act_func_dict()
    date = str(datetime.datetime.now())
    name = dico_act_func.get("fonction","error_function")+f" | "+date
    
    add_to_historique(dico_act_func, name, date)

    # Remettre "à plat" la fonction actuelle
    reset_act_function()

def is_same(func1 : dict, func2 : dict) -> bool :
    return all(func1.get(key) == func2.get(key) for key in ("fonction", "minN", "maxN", "incrN"))

# J'ai créer cette classe pour avoir un label sépcial pour le nom des suites/séries de fonctions qui permet d'éditer le nom de celles-ci en double cliquant dessus
class editable_label(ttk.Frame):
    def __init__(self, master, text="", lock_on_edit : list[ttk.Button] |None = None, **kwargs):
        super().__init__(master, **kwargs)

        self.lock_on_edit = lock_on_edit or []
        self.last_name = text
        self.new_name = ttk.StringVar(value=text)
        self.label = ttk.Label(self, textvariable=self.new_name)
        self.entry = ttk.Entry(self, textvariable=self.new_name)

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
        changer_nom_fonction(self.last_name, self.get()) # Cette fonction change partout le nom de la suite/serie de fonctions
        self.label.pack(fill="x", expand=True)
        self.last_name = self.get() # Mettre à jour le dernier nom

    def get(self):
        return self.new_name.get()

    def set(self, text):
        self.new_name.set(text)

def load_historique(frame_histo : ttk.Frame) :

    act_loaded = act_func_dict()
    # Petit nettoyage de printemps
    for widget in frame_histo.winfo_children() :
        widget.destroy()

    # On met une scrollbar pour défiler chaque fonction de l'historique
    scroll_histo = ttk.Scrollbar(frame_histo)
    scroll_histo.pack(side="right", fill="y")

    canvas = ttk.Canvas(frame_histo, yscrollcommand=scroll_histo.set)
    canvas.pack(side="left", fill="both", expand=True)
    scroll_histo.config(command=canvas.yview)

    # Create a frame inside the canvas
    inner_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw", width=frame_histo.winfo_width()-10)

    # Obtenir la liste des fonctions indexées par leur date
    for func_name, func_data in sorted(list(historique_data.items()), key=lambda item: item[1].get("date",""), reverse=True) :

        frame_of_func = ttk.Frame(inner_frame)
        frame_of_func.pack(fill="x", pady=2)

        def charger_fonction_wrapper(fonction=func_data) :
            def charger_fonction() :
                update_act_func(fonction)
            return charger_fonction
        

        
        
        btn = ttk.Button(frame_of_func, text="  Utiliser  ", command=charger_fonction_wrapper())
        btn.pack(fill="x", side="right", expand=False, padx=5)

        def supprimer_fonction_wrapper(name=func_name, frame_of_func=frame_of_func, frame_histo=frame_histo) :
            def supprimer_fonction() :
                if historique_data.get(name) :
                    remove_from_favorite(name)
                    del historique_data[name]
                # Supprimer le bouton de l'interface sans recharger toute l'interface avec load_historique
                frame_of_func.destroy()

                # Ceci met a jour localement l'interface en supprimant la frame de la fonction supprimée 
                # Mais cela ne modifie pas les autres instances d'historique (dans ce cas le faire)
                # refresh_other(frame_histo)
                
            return supprimer_fonction
        
        delete = ttk.Button(frame_of_func, text="  Supprimer  ", command=supprimer_fonction_wrapper())
        delete.pack(fill="x", side="right", expand=False, padx=5)
        def add_to_fav_wrapper(name=func_name, func_data=func_data, btn_fav=None, frame_histo=frame_histo) :
            def add_to_fav() :
                if func_data.get("favoris") is not True :
                    put_on_favorite(name, func_data)
                    btn_fav.config(text=" ★ ")
                else :
                    remove_from_favorite(name)
                    btn_fav.config(text=" ☆ ")
                # refresh_other(frame_histo)
            return add_to_fav
        
        to_fav = ttk.Button(frame_of_func, text=" ☆ " if func_data.get("favoris") is not True else " ★ ")
        # Rendre le bouton Jaune

        to_fav.config(style="Fav.TButton")

        to_fav.config(command=add_to_fav_wrapper(btn_fav=to_fav))
        to_fav.pack(fill="x", side="right", expand=False, padx=5)

        label_editable_name = editable_label(frame_of_func, text=func_name, lock_on_edit=[to_fav, delete, btn])
        label_editable_name.pack(fill="x", side="left", expand=True, padx=5)

        
    
    if not historique_data :
        ttk.Label(inner_frame, text="Aucune suite/série de fonctions dans l'historique").pack(pady=10)
        ttk.Label(inner_frame, text="Créez en une dans le lanceur et elle sera automatiquement ajoutée ici").pack(pady=10)
        ttk.Label(inner_frame, text="Après avoir cliqué sur 'Nouvelle fonction' ou en quittant l'application").pack(pady=10)

    # Update scroll region
    inner_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))



def refresh_other(frame_act) :
    """
    Cette fonction permet de mettre à jour les historiques et favoris de l'onglet Sauvegardes si une modification a été faite dans l'onglet Quick Load, et vice versa
    """
    if frame_act in (historique, preferes) :
        try :
            load_historique(frame_quick_load)
        except : pass
        try :
            load_favoris(frame_quick_load_fav)
        except : pass
    else :
        try :
            load_historique(historique)
        except : pass
        try :
            load_favoris(preferes)
        except : pass

def refresh_all() :
    load_historique(historique)
    load_historique(frame_quick_load)
    load_favoris(preferes)
    
def changer_nom_fonction(old_name : str, new_name : str) :
    if old_name in historique_data :
        historique_data[new_name] = historique_data.pop(old_name)
    if old_name in favoris_data :
        favoris_data[new_name] = favoris_data.pop(old_name)
    
    refresh_all()


def load_favoris(frame_fav : ttk.Frame) :
    # Petit nettoyage de printemps
    for widget in frame_fav.winfo_children() :
        widget.destroy()

    # On met une scrollbar pour défiler chaque fonction des favoris
    scroll_fav = ttk.Scrollbar(frame_fav)
    scroll_fav.pack(side="right", fill="y")

    canvas = ttk.Canvas(frame_fav, yscrollcommand=scroll_fav.set)
    canvas.pack(side="left", fill="both", expand=True)
    scroll_fav.config(command=canvas.yview)

    # Frame dans le canvas
    inner_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw", width=frame_fav.winfo_width()-10)

    # Obtenir la liste des fonctions indexées par leur date
    for func_name, func_data in sorted(list(favoris_data.items()), key=lambda item: item[1].get("date",""), reverse=True) :

        frame_of_func = ttk.Frame(inner_frame)
        frame_of_func.pack(fill="x", pady=2)

        def charger_fonction_wrapper(fonction=func_data) :
            def charger_fonction() :
                update_act_func(fonction)
            return charger_fonction
        

        

        btn = ttk.Button(frame_of_func, text="  Utiliser  ", command=charger_fonction_wrapper())
        btn.pack(fill="x", side="right", expand=False, padx=5)

        def add_to_fav_wrapper(name=func_name, func_data=func_data, btn_fav=None, frame_of_func=frame_of_func, frame_fav=frame_fav) :
            def add_to_fav() :
                if func_data.get("favoris") is not True :
                    put_on_favorite(name, func_data)
                    btn_fav.config(text=" ★ ")
                else :
                    remove_from_favorite(name)
                    frame_of_func.destroy()
                refresh_other(frame_fav)
            return add_to_fav
        
        to_fav = ttk.Button(frame_of_func, text=" ★ ")
        to_fav.config(style="Fav.TButton")

        to_fav.config(command=add_to_fav_wrapper(btn_fav=to_fav))
        to_fav.pack(fill="x", side="right", expand=False, padx=5)

        label_editable_name = editable_label(frame_of_func, text=func_name, lock_on_edit=[to_fav, btn])
        label_editable_name.pack(fill="x", side="left", expand=True, padx=5)

        
    
    if not favoris_data :
        ttk.Label(inner_frame, text="Aucune suite/série de fonctions dans les favoris").pack(pady=10)
        ttk.Label(inner_frame, text="Ajoutez en une depuis l'historique en cliquant sur ★ à côté de son nom").pack(pady=10)

    # Update scroll region
    inner_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))


#================ INTERFACE =====================

# Menu des onglets:
onglets = ttk.Notebook(w)

lanceur_et_quick_load = ttk.Frame(onglets)


onglets.add(lanceur_et_quick_load, text = "Lanceur")

parametres = ttk.Notebook(onglets) # Un sous-menu d'onglets, contenant deux onglets : Paramètre par défaut, Paramètre personnalisés
p_defaut = ttk.Frame(parametres)
p_perso = ttk.Frame(parametres)
p_appli = ttk.Frame(parametres)
parametres.add(p_defaut, text="Paramètres par défaut")
parametres.add(p_perso, text="Paramètres personnalisés")
parametres.add(p_appli, text="Paramètres d'application")

onglets.add(parametres, text = "Paramètres")

sauvegardes = ttk.Notebook(onglets)
historique = ttk.Frame(sauvegardes)

# Load l'historique en cliquant à chaque appuie sur le bouton d'historique

def historique_or_fav_selectionne(event):
    onglet = event.widget.nametowidget(event.widget.select())
    if onglet == historique:
        load_historique(historique)
    elif onglet == preferes:
        load_favoris(preferes)
sauvegardes.bind("<<NotebookTabChanged>>", historique_or_fav_selectionne)

preferes = ttk.Frame(sauvegardes)
sauvegardes.add(historique, text="Historique")
importees = ttk.Frame(sauvegardes)
sauvegardes.add(importees, text="Importées")
favoris = ttk.Frame(sauvegardes)
sauvegardes.add(preferes, text="Favoris")

onglets.add(sauvegardes, text="Sauvegardes")


onglets.pack(fill="x")



#   #   #    Fenetre de lanceur
lanceur = ttk.Frame(lanceur_et_quick_load) # La frame qui sert à définir la fonctions, et lancer l'affichage
lanceur.pack(side='left')
space(lanceur, 10)

lab_info_lanceur = ttk.Label(lanceur,text="Voici le traceur de fonction\nEntrez votre fonction et cliquez sur lancer pour afficher la suite (ou série de fonction)")
lab_info_lanceur.pack(**LINE)

fonction_entry_frame, _, _ = gen_entry_field(lanceur, "Fn(x) = ",sep_size=1, str_var=fonction )
fonction_entry_frame.pack(**LINE)

space(lanceur, 10)

# Min/Max de N
vcmd = w.register(is_float)
min_max_n = ttk.Frame(lanceur)

min_n_f = ttk.Frame(min_max_n)
minNLabel = ttk.Label(min_n_f, text="Minimum de n :")
entry_nmin = ttk.StringVar(value="1")
nMinEntry = ttk.Entry(min_n_f,validate='key',textvariable=entry_nmin, validatecommand=(vcmd, "%P"))
nMinEntry.pack(side='right', fill='x', expand=True)
minNLabel.pack(side='left')

max_n_f = ttk.Frame(min_max_n)
maxNLabel = ttk.Label(max_n_f, text="Maximum de n :")
entry_nmax = ttk.StringVar(value="15")
nMaxEntry = ttk.Entry(max_n_f,validate='key',textvariable=entry_nmax, validatecommand=(vcmd, "%P"))
nMaxEntry.pack(side='right', fill='x', expand=True)
maxNLabel.pack(side='left')

min_n_f.pack(side="left", fill="x", padx=15)
max_n_f.pack(side="right", fill="x", padx=15)
min_max_n.pack(**LINE)

space(lanceur, 10)

# Incrémenteur N
frame_nIncr = ttk.Frame(lanceur)
frame_nIncr.pack(**LINE)

labelNIncr = ttk.Label(frame_nIncr, text="Incrémentation de n (laissez à 1 si vous étudiez une suite de fonction)")

nIncrVar = ttk.StringVar(value="1")
nIncrEntry = ttk.Entry(frame_nIncr,validate='key',textvariable=nIncrVar, validatecommand=(vcmd, "%P"))
nIncrEntry.pack(side='right', fill='x', expand=True)
labelNIncr.pack(side='left')

space(lanceur, 20)

#   #   # Fenetre des parametres de plot -> reporté sur les paramètres de suite de fonctions

# Min/Max de x
min_max_x = ttk.Frame(lanceur)

min_x_f = ttk.Frame(min_max_x)
minXLabel = ttk.Label(min_x_f, text="Minimum de x :")
xMinEntry = ttk.Entry(min_x_f,validate='key',textvariable=xMin, validatecommand=(vcmd, "%P"))
xMinEntry.pack(side='right', fill='x', expand=True)
minXLabel.pack(side='left')

max_x_f = ttk.Frame(min_max_x)
maxXLabel = ttk.Label(max_x_f, text="Maximum de x :")
xMaxEntry = ttk.Entry(max_x_f,validate='key',textvariable=xMax, validatecommand=(vcmd, "%P"))
xMaxEntry.pack(side='right', fill='x', expand=True)
maxXLabel.pack(side='left')

min_x_f.pack(side="left", fill="x", padx=15)
max_x_f.pack(side="right", fill="x", padx=15)
min_max_x.pack(**LINE)

# Min/Max de y
min_max_y = ttk.Frame(lanceur)

min_y_f = ttk.Frame(min_max_y)
minYLabel = ttk.Label(min_y_f, text="Minimum de y :")
yMinEntry = ttk.Entry(min_y_f,validate='key',textvariable=yMin, validatecommand=(vcmd, "%P"))
yMinEntry.pack(side='right', fill='x', expand=True)
minYLabel.pack(side='left')

max_y_f = ttk.Frame(min_max_y)
maxYLabel = ttk.Label(max_y_f, text="Maximum de y :")
yMaxEntry = ttk.Entry(max_y_f,validate='key',textvariable=yMax, validatecommand=(vcmd, "%P"))
yMaxEntry.pack(side='right', fill='x', expand=True)
maxYLabel.pack(side='left')

min_y_f.pack(side="left", fill="x", padx=15)
max_y_f.pack(side="right", fill="x", padx=15)
min_max_y.pack(**LINE)

space(lanceur, 30)

# Lancer / Arreter le tracer
go_stop_frame = ttk.Frame(lanceur)
go_button = ttk.Button(go_stop_frame, text="Go", command= lambda : lancer_all_plot(fonction.get(),
                                                                                   xMin=to_float(xMin.get()),
                                                                                   xMax=to_float(xMax.get()),
                                                                                   nMin=to_float(entry_nmin.get()),
                                                                                   nMax=to_float(entry_nmax.get()),
                                                                                   nIncr=to_float(nIncrVar.get()),
                                                                                   pause=vitesseGeneration.get(),
                                                                                   yMin=to_float(yMin.get()),
                                                                                   yMax=to_float(yMax.get())))
stop_button = ttk.Button(go_stop_frame, text="STOP", command=stop_plot)
progress = ttk.Progressbar(
    go_stop_frame,
    orient="horizontal",
    length=300,
    mode="determinate"
)
stop_button.pack(padx=10, side="right")
progress.pack(padx=10, side="right")
go_button.pack(padx=10, side="right")
go_stop_frame.pack()

space(lanceur, 10)


# Nouvelle fonction / exporter la fonction
function_manager_frame = ttk.Frame(lanceur)
new_function_button = ttk.Button(function_manager_frame, text="Nouvelle fonction", command=create_new_function)
new_function_button.pack(side='left', padx=10)

export_function = ttk.Button(function_manager_frame, text="Exporter", command=lambda:print("Plus tard"))
function_manager_frame.pack()

#   #   # Quickload (scrollbar pour charger rapidement ce qui a été importé ou dans l'historique)

# Scrollbar en elle meme
quick_load = ttk.Notebook(lanceur_et_quick_load)
quick_load.pack(side='right', fill='both', expand=True)
frame_quick_load = ttk.Frame(lanceur_et_quick_load)
frame_quick_load_fav = ttk.Frame(lanceur_et_quick_load)
quick_load.add(frame_quick_load, text="Historique")
quick_load.add(frame_quick_load_fav, text="Favoris")
load_historique(frame_quick_load)
load_favoris(frame_quick_load_fav)

def quick_historique_or_fav_selectionne(event):
    onglet = event.widget.nametowidget(event.widget.select())
    if onglet == frame_quick_load:
        load_historique(frame_quick_load)
        pass
    elif onglet == frame_quick_load_fav:
        load_favoris(frame_quick_load_fav)
quick_load.bind("<<NotebookTabChanged>>", quick_historique_or_fav_selectionne)






# Fenetre des parametres d'appli

switch_theme = ttk.Button(p_appli, text="Modifier theme", command=changer_theme)
switch_theme.pack(fill="x")





#================= MAIN ========================

if __name__=="__main__" :
    # lancer_all_plot("n+x", -2, 2, nMin=-3,nMax=3, nIncr=0.01, pause=0.05, yMin=-2, yMax=2)


    w.protocol("WM_DELETE_WINDOW", on_close)
    profile_info = load_config()
    load_historique(frame_quick_load)
    w.mainloop()
    

    

