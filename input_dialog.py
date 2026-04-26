import ttkbootstrap as ttk 

class Input_Dialog(ttk.Toplevel):
    def __init__(self, master, title="Input", label_text="Entrez une valeur :") :
        super().__init__(master)

        self.result = None

        self.title(title)

        self.label = ttk.Label(self, text=label_text)
        self.label.pack(padx=10, pady=10)

        self.entry = ttk.Entry(self)
        self.entry.pack(padx=10, pady=10)

        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(padx=10, pady=10)

        self.ok_button = ttk.Button(self.button_frame, text="OK", command=self.on_ok)
        self.ok_button.pack(side="left", padx=5)

        self.cancel_button = ttk.Button(self.button_frame, text="Annuler", command=self.on_cancel)
        self.cancel_button.pack(side="left", padx=5)

        while self.winfo_exists() :
            self.update()
            

    def on_ok(self):
        self.result = self.entry.get()
        self.destroy()

    def on_cancel(self):
        self.destroy()