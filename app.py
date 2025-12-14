from matplotlib import pyplot as plt
import math
from math import sin,cos,sqrt,sinh,cosh,tan,tanh,log,log10,exp,modf,pow,radians,pi
import random
from random import randint,randrange,choice,choices

import tkinter as tk
import ttkbootstrap as ttk # pour avoir de plus beaux menus


w = ttk.Window(themename="darkly")

    ## Générateur exponentielle : n est multiplié par deux à chaque fois
def croissanceExpo(min,max, _) :
    assert isinstance(min,int) and isinstance(max,int)
    while min<max :
        yield min
        min *= 2

def range(min, max=None, incr=1) :
    if min and max is None :
        min, max, incr = 0, min, 1

    x = min
    while x<max :
        yield x 
        x += incr 



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

def lancerPlt(f,minN, maxN, xMin, xMax, yMin, yMax, croissance = range, pas=100, vitesse=0.1, incrN=1.):
    if not tester(f,minN, maxN, xMin, xMax, yMin, yMax, croissance, pas,vitesse) :
        error.set("Erreur détectée... vérifiez votre définition de la fonction (utilisez x et n)")
    else :
        if vitesse==0 : vitesse=0.01
        error.set("")
        plt.clf()
        continueTracing.set(True)
        plt.ylim(yMin,yMax)
        plt.xlim(xMin,xMax) 
        for n in croissance(minN,maxN+1, incrN):
            if continueTracing.get() :
                tracer(f,xMin,xMax,n, pas, couleur= valeur_to_hex(n, minN, maxN))		
                plt.pause(vitesse)
        plt.show()
        

def tester(f,minN, maxN, xMin, xMax, yMin, yMax, croissance = range, pas=150,vitesse=0.1, incrN=1.) :
    fonctionne= all(isinstance(value,int) for value in (minN,maxN,pas)) and all(isinstance(value,int) or isinstance(value,float) for value in (xMin,xMax,yMin,yMax,vitesse))
    if fonctionne :
        for n in croissance(minN,maxN+1,incrN):
            for i in range(pas) :
                try :
                    x=xMin+i*(xMax-xMin)/(pas-1)
                    eval(f)
                except ZeroDivisionError:
                    if "Division par 0" not in error.get() : error.set(error.get()+"  ... Division par 0 détectée")
                except OverflowError:
                    if "Trop grande" not in error.get() : error.set(error.get()+"  ... Valeur trop grande détectée")
                except :
                    fonctionne = False
                    break
            if fonctionne == False : break
    return fonctionne

def tracer(f : str ,xmin,xmax,n, pas, couleur=None):
    X=[]
    Y=[]
    for i in range (pas):
        x=xmin+i*(xmax-xmin)/(pas-1)
        X.append(x)
        try :
            Y.append(eval(f))
        except ZeroDivisionError :
            X.remove(x)
            if "Division par 0" not in error.get() : error.set(error.get()+"  ... Division par 0 détectée")
        except OverflowError:
                Y.append(10000000000000 if x>0 else -10000000000000)
                if "trop grande" not in error.get() : error.set(error.get()+"  ... Valeur trop grande détectée")
    if couleur :
        plt.plot(X,Y, color=couleur)
    else :
        plt.plot(X,Y)


	## Configuration des paramètres (variables tkinter)
xMin,xMax,yMin,yMax = (tk.DoubleVar(value=default) for default in (-3,3,-3,3))
nMin, nMax = tk.IntVar(value=1),tk.IntVar(value=15)
pointsGeneres = tk.IntVar(value=100)
incrN = tk.DoubleVar(value=1.)
vitesseGeneration = tk.DoubleVar(value=0.1)
dicoTypeDeCroissance = {"linéaire" : range, # Par défaut, n varie de nMin à nMax (via un range)
                        "exponentielle" : croissanceExpo} 
fonction = tk.StringVar(value="x**n")
error = tk.StringVar(value="")
continueTracing = tk.BooleanVar(value=True)

	## Configuration des menus et boutons
# Génération des lignes
lignes : list[ttk.Frame] = [ttk.Frame(master=w) for _ in range(16)]
for ligne in lignes : ligne.pack(expand=True, padx=10)
# Génération du contenu pour ces lignes
(titre := ttk.Label(master=lignes[0], text="Lanceur de fonctions", font='Arial 14')).pack()

(ttk.Label(master=lignes[1], text="Bordures de l'écran :")).pack(side='left',expand=True)

(ttk.Label(master=lignes[2], text="Minimum de x : ")).pack(side='left',expand=True)
(ttk.Entry(master=lignes[2], textvariable=xMin)).pack(side='left')
(ttk.Label(master=lignes[2], text="Maximum de x :")).pack(side='left',padx=20,expand=True)
(ttk.Entry(master=lignes[2], textvariable=xMax)).pack(side='left')

(ttk.Label(master=lignes[3], text="Minimum de y : ")).pack(side='left',expand=True)
(ttk.Entry(master=lignes[3], textvariable=yMin)).pack(side='left')
(ttk.Label(master=lignes[3], text="Maximum de y :")).pack(side='left',padx=20,expand=True)
(ttk.Entry(master=lignes[3], textvariable=yMax)).pack(side='left')

(ttk.Label(master=lignes[5], text="Fonction :")).pack()

(ttk.Label(master=lignes[6], text="Ecrivez la formule de f(x) = ")).pack(side='left')
(ttk.Entry(master=lignes[6], textvariable=fonction)).pack(side='left')

(ttk.Label(master=lignes[8], text="Variation de n :")).pack(side='left')

(ttk.Label(master=lignes[9], text="Minimum de n : ")).pack(side='left')
(ttk.Entry(master=lignes[9], textvariable=nMin)).pack(side='left')
(ttk.Label(master=lignes[9], text="Maximum de n :")).pack(side='left',padx=20,expand=True)
(ttk.Entry(master=lignes[9], textvariable=nMax)).pack(side='left')

(ttk.Label(master=lignes[10], text="Croissance de n :")).pack(side='left')
(TypdeDeCroissance := ttk.Combobox(master=lignes[10], values=("linéaire","exponentielle"))).pack(side='left')
(ttk.Entry(master=lignes[10], textvariable=incrN)).pack(side='right')
(ttk.Label(master=lignes[10], text="(Si linéaire) Incrémentation de n :")).pack(side='right',padx=20,expand=True)

TypdeDeCroissance.set("linéaire")
(ttk.Label(master=lignes[11], text="Paramètres d'affichage : ")).pack(side='left')

(ttk.Label(master=lignes[12], text="Nombre de point généré : ")).pack(side='left')
(ttk.Entry(master=lignes[12], textvariable=pointsGeneres)).pack(side='left')
(ttk.Label(master=lignes[12], text="Temps entre chaque génération : ")).pack(padx=20, side='left')
(ttk.Entry(master=lignes[12], textvariable=vitesseGeneration)).pack(side='left')

(ttk.Label(master=lignes[13], text="Lancer l'affichage de la suite : ")).pack(side='left')

(ttk.Button(master=lignes[14], text="GO",command= lambda : lancerPlt(
    f=fonction.get(),minN=nMin.get(), maxN=nMax.get(), xMin=xMin.get(), xMax=xMax.get(), yMin=yMin.get(), yMax=yMax.get(),
    croissance = dicoTypeDeCroissance.get(TypdeDeCroissance.get(),range), pas=pointsGeneres.get(), vitesse=vitesseGeneration.get(), incrN=incrN.get())
)).pack(side='left', padx=10)
(ttk.Button(master=lignes[14], text="STOP",command= lambda : (continueTracing.set(False)))).pack(side='left')

(ttk.Label(master=lignes[15], textvariable=error)).pack(side='left')



w.mainloop()