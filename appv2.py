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

fonctions_math = { name: getattr(math, name) for name in dir(math) if not name.startswith("_") } # ca met toutes les fonctions de math dans un dictionnaire nom : fonction (sauf pour les )
fonctions_autorise_python = dict(int=int, max=max, min=min)


math_globals = {
    "__builtins__": {}, # pour éviter à l'utilisateur d'écrire autre chose que des maths, a tout hasard... eval("__import__('os').system('rm -rf /')")
    **fonctions_math,
    **fonctions_autorise_python
}


#============= FENETRE PRINCIPALE ================

w = ttk.Window(themename="darkly")
w.title("Visualiseur de suites et séries de fonctions")


#============= FUNCTIONS UTILES ===================
def range_(min, max=None, incr=1) : # j'ai adapté le range pour qu'il puisse prendre des decimales
    if min and max is None :
        min, max, incr = 0, min, 1

    x = min
    while x<max :
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

xMin,xMax,yMin,yMax = (ttk.DoubleVar(value=default) for default in (-10,10,-10,10)) # bordure de la fenetre plot
nMin, nMax = ttk.IntVar(value=1),tk.IntVar(value=15)
incrN = ttk.DoubleVar(value=1.) # de combien augmente n à chaque itération (pour les suites, il garde 1, pour les série, on choisis un nombre entre 0 et 1 exclus, pour obtenir les variations quand n est réel)

pointsGeneres = ttk.IntVar(value=100) # Plus il y a de points générés, moins la courbe est lisse (mais + de calculs derriere)
vitesseGeneration = ttk.DoubleVar(value=0.1) # temps de pause entre chaque itération (chaque fonction n)

dicoTypeDeCroissance = {"linéaire" : range_, # Par défaut, n varie de nMin à nMax (via un range)
                        "exponentielle" : croissanceExpo} 
fonction = ttk.StringVar(value="x**n")

error = ttk.StringVar(value="")
continueTracing = ttk.BooleanVar(value=True)

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
    for n in nCroissance(nMin, nMax, nIncr) :
        Valeurs, Erreurs  = eval_func(f, n, xMin, xMax, nbPoints)
        if Erreurs :
            print("Erreurs rencontrées pour n=",n,":",Erreurs)
        tracer(Valeurs, valeur_to_hex(n, nMin, nMax))

        plt.pause(pause)
    plt.show()

#============ FONCTIONS INTERFACE ===============

# Pour l'instant j'ai mis les constructeur de structeur préfaite dans myttkfuncs

themes = [
        "darkly",
        "superhero",
        "flatly",
        "cyborg",
        "minty"]

def changer_theme():
    temp = themes.pop(0)
    themes.append(temp)
    style = ttk.Style()
    style.theme_use(themes[0])


#================ INTERFACE =====================

# Menu des onglets:
onglets = ttk.Notebook(w)

lanceur = ttk.Frame(onglets) # La frame qui sert à définir la fonctions, et lancer l'affichage

onglets.add(lanceur, text = "Lanceur")

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
preferes = ttk.Frame(sauvegardes)
sauvegardes.add(historique, text="Historique")
sauvegardes.add(preferes, text="Favoris")

onglets.add(sauvegardes, text="Sauvegardes")


onglets.pack(fill="x")

# Fenetre de lanceur
lab_info_lanceur = ttk.Label(lanceur,text="Voici le traceur de fonction\nEntrez votre fonction et cliquez sur lancer pour afficher la suite (ou série de fonction)")
lab_info_lanceur.pack(expand=True, fill="x")

fonction_entry_frame, _, _ = gen_entry_field(lanceur, "Fn(x) = ",sep_size=1, str_var=fonction )
fonction_entry_frame.pack(fill="x")

space(lanceur, 10)

frame_nIncr = ttk.Frame(lanceur)
frame_nIncr.pack(fill="x")

labelNIncr = ttk.Label(frame_nIncr, text="Entrez le pas d'incrémentation de n (laissez à 1 si vous étudiez une suite de fonction)")

vcmd = w.register(is_float)
entry_default = ttk.StringVar(value="1")
nIncrEntry = ttk.Entry(frame_nIncr,validate='key',textvariable=entry_default, validatecommand=(vcmd, "%P"))
nIncrEntry.pack(side='right', fill='x', expand=True)
labelNIncr.pack(side='left')


go_button = ttk.Button(lanceur, text="Go", command= lambda : lancer_all_plot(fonction.get(), xMin.get(), xMax.get(), nMin=nMin.get(),nMax=nMax.get(), nIncr=to_float(nIncrEntry.get()), pause=vitesseGeneration.get(), yMin=yMin.get(), yMax=yMax.get()))


go_button.pack(fill='x', padx=30)

# Fenetre des parametres de plot




# Fenetre des parametres d'appli

switch_theme = ttk.Button(p_appli, text="Modifier theme", command=changer_theme)
switch_theme.pack(fill="x")





#================= MAIN ========================

if __name__=="__main__" :
    # lancer_all_plot("n+x", -2, 2, nMin=-3,nMax=3, nIncr=0.01, pause=0.05, yMin=-2, yMax=2)
    w.mainloop()

    

