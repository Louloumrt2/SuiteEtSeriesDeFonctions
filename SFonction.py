import ttkbootstrap as ttk

class SFonction():
    def __init__(self,fonction="x/n", minN = "1", maxN = "100", incrN = "1", minX = "-20", maxX = "20", minY = "-10", maxY = "10", date = "", nbPoint = "100", nom = "Suite/Série de fonction sans nom"):
        self.fonction = fonction
        self.minN = minN
        self.maxN = maxN
        self.incrN = incrN
        self.minX = minX
        self.maxX = maxX
        self.minY = minY
        self.maxY = maxY
        self.date = date
        self.nbPoint = nbPoint
        self.nom : ttk.StringVar = ttk.StringVar(value=nom)
    
    def __str__(self):
        return self.nom.get() + (self.date and "(" + self.date + ")" or "")
    
    def set_name(self, new_name) :
        self.nom.set(new_name)
    
    def get_name(self) :
        return self.nom.get()
    
    
    def convert_to_dict(self) :
        res = {}

        res["nom"] = self.nom.get() 

        for key in ("fonction", "minN", "maxN", "incrN", "minX", "maxX", "minY", "maxY", "nbPoint", "date") :
            res[key] = getattr(self, key)
        
        return res
    
    def duplicate(self) :
        return SFonction(fonction=self.fonction, minN=self.minN, maxN=self.maxN, incrN=self.incrN, minX=self.minX, maxX=self.maxX, minY=self.minY, maxY=self.maxY, date=self.date, nom=self.get_name() + "_copy")
    

    
