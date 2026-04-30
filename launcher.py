import ttkbootstrap as ttk
from SFonction import SFonction
from tkinter import END
from matplotlib import pyplot as plt

import math
from math import sin,cos,sqrt,sinh,cosh,tan,tanh,log,log10,exp,modf,pow,radians,pi
import random
from random import randint, randrange, choice, choices
fonctions_math = { name: getattr(math, name) for name in dir(math) if not name.startswith("_") } # ca met toutes les fonctions de math dans un dictionnaire nom : fonction (sauf pour les )
fonctions_autorise_python = dict(int=int, max=max, min=min, sum=sum, abs=abs)

class BoundsError(Exception) : pass
class NoPointError(Exception) : pass

def range_(min, max, incr=1) : # j'ai adapté le range pour qu'il puisse prendre des decimales
    x = min
    while x<=max :
        yield x 
        x += incr 


math_globals = {
    "__builtins__": {}, # pour éviter à l'utilisateur d'écrire autre chose que des maths, a tout hasard... eval("__import__('os').system('rm -rf /')") (oui Monsieur j'ai fais attention !)
    **fonctions_math,
    **fonctions_autorise_python
}

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


class ErrorLogger(ttk.Frame) :
    def __init__(self, master) :
        super().__init__(master)
        ttk.Label(text = "Erreurs rencontrées lors de calculs :").pack()

        self.text = ttk.Text(self)
        self.scroll_bar = ttk.Scrollbar(self)
        self.scroll_bar.pack(side='right', fill='y')
        self.text.pack(side='left', fill="both", expand=True)

        self.scroll_horiz_bar = ttk.Scrollbar(self)

        self.text.config(yscrollcommand=self.scroll_bar.set)
        self.scroll_bar.config(command=self.text.yview)

        self.text.config(xscrollcommand=self.scroll_bar.set)
        self.scroll_horiz_bar.config(command=self.text.xview)
    
    def add_error(self, msg : str, end="\n") :
        self.text.insert(END, msg + end)

def reduce(x : float) -> str :
    return str(x)

def replace(f : str, x : float, n : float) :
    return f.replace('x',reduce(x)).replace('n',str(n))

def tracer(valeurs : list[tuple[int,int]], couleur = None) :
    if valeurs :
        xs, ys = zip(*valeurs)
        X, Y = list(xs), list(ys)

        if couleur :
            plt.plot(X,Y, color=couleur)
        else :
            plt.plot(X,Y)

class Launcher(ttk.Frame) :
    def __init__(self, master):
        super().__init__(master)
        self.error_tab = ErrorLogger(self)
        self.sfonction = None
        self.error_tab.pack(fill="both", expand=True)

    def load_sfun(self,sfonction : SFonction) :
        self.sfonction = sfonction
    
    def start_visualisation(self, pause=0.05) :
        if not self.sfonction : self.error_tab.add_error("Vous avez tenté de lancer une visualisation sans qu'il n'y est de suite/série de fonction")

        f = self.sfonction.fonction
        infos = self.sfonction.decimals_info()
        minX, maxX, nbPoint, minY, maxY, incrN, minN, maxN = (infos[e] for e in ("minX", "maxX", "nbPoint", "minY", "maxY", "incrN", "minN", "maxN"))
        
        

        if maxX <= minX : raise BoundsError("Le minimum de x est plus grand que le maximum de x : "+str(minX)+"|"+str(maxX))
        if maxY <= minY : raise BoundsError("Le minimum de y est plus grand que le maximum de y : "+str(minY)+"|"+str(maxY))
        if nbPoint == 0 : raise NoPointError("Pas de points")

        plt.clf()
        plt.ylim(minY, maxY)
        plt.xlim(minX,maxX) 

        pas_x = int((maxX - minX) / nbPoint)

        res = {}

        for n in range_(minN, maxN, incrN or 0.1) :

            res[n] = []

            for x in range_(minX, maxX, pas_x or 0.1) :
                try :
                    y = eval(f, math_globals, {"x":x, "n":n})
                    res[n].append((x,y))
                except ZeroDivisionError :
                    self.error_tab.add_error(f"Pour n={n} et x={reduce(x)} (soit {replace(f,x,n)}) : Division par 0")
                except OverflowError :
                    self.error_tab.add_error(f"Pour n={n} et x={reduce(x)} (soit {replace(f,x,n)}) : Valeur obtenue trop élevée")
                except Exception as e :
                    self.error_tab.add_error(f"Pour n={n} et x={reduce(x)} (soit {replace(f,x,n)}) : {str(e)}")
            
            tracer(res[n], valeur_to_hex(n, minN, maxN))

            # if stop.get() : 
            #     stop.set(False)
            #     break
            # else :
            #     plt.pause(pause)

            plt.pause(pause)
        plt.show()
            




    def test_errors(self) :
        
        for i in range(10) :
            self.error_tab.add_error("erreur "+str(i))
    

if __name__ == "__main__" :
    app = ttk.Tk()
    s = SFonction(fonction="x**n", minN=0, maxN=3, incrN=0.01)
    l = Launcher(app)
    l.load_sfun(s)
    l.pack(fill="both", expand=True)
    l.start_visualisation()

    app.mainloop()
        