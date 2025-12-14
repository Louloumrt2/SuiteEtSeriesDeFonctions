    #=================== IMPORTS ======================

from typing import Generator
from matplotlib import pyplot as plt
import math
from math import sin,cos,sqrt,sinh,cosh,tan,tanh,log,log10,exp,modf,pow,radians,pi
import random
from random import randint,randrange,choice,choices

import tkinter as tk
import ttkbootstrap as ttk # pour avoir de plus beaux menus

fonctions_math = { name: getattr(math, name) for name in dir(math) if not name.startswith("_") } # ca met toutes les fonctions de math dans un dictionnaire nom : fonction (sauf pour les )

math_globals = {
    "__builtins__": {}, # pour éviter à l'utilisateur d'écrire autre chose que des maths, a tout hasard... eval("__import__('os').system('rm -rf /')")
    **fonctions_math
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

#================= VARIABLES =====================

xMin,xMax,yMin,yMax = (ttk.DoubleVar(value=default) for default in (-3,3,-3,3)) # bordure de la fenetre plot
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



#================ INTERFACE =====================



#================= MAIN ========================

if __name__=="__main__" :
    lancer_all_plot("x**n", -2, 2, nMin=-3,nMax=3, nIncr=0.01, pause=0.05, yMin=-2, yMax=2)
    w.mainloop()
