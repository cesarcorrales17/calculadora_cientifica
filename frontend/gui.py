# frontend/gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from backend.parser import evaluate, CalcError

class CalcGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora Científica - Casio Style")
        self.geometry("420x600")
        self.resizable(False, False)
        self._create_widgets()
        self.expression = ""

    def _create_widgets(self):
        # Pantalla principal
        self.display = tk.Entry(self, font=("Consolas", 20), justify="right")
        self.display.pack(fill="x", padx=10, pady=10)
        # Historial (pequeño)
        self.hist = tk.Text(self, height=5, state='disabled', font=("Consolas", 10))
        self.hist.pack(fill="x", padx=10, pady=(0,10))
        # Panel de botones
        frame = ttk.Frame(self)
        frame.pack(expand=True, fill='both', padx=10, pady=10)

        buttons = [
            ['7','8','9','/','sqrt'],
            ['4','5','6','*','^'],
            ['1','2','3','-','('],
            ['0','.','=','+',')'],
            ['sin','cos','tan','ln','log'],
            ['pi','e','C','<-','ANS']
        ]

        for r, row in enumerate(buttons):
            for c, label in enumerate(row):
                b = ttk.Button(frame, text=label, command=lambda l=label: self.on_button(l))
                b.grid(row=r, column=c, padx=4, pady=4, ipadx=6, ipady=10, sticky='nsew')

        # make grid cells expand evenly
        for i in range(len(buttons)):
            frame.rowconfigure(i, weight=1)
        for j in range(len(buttons[0])):
            frame.columnconfigure(j, weight=1)

        # key bindings
        self.bind("<Return>", lambda e: self.on_button('='))
        self.bind("<BackSpace>", lambda e: self.on_button('<-'))
        self.bind("c", lambda e: self.on_button('C'))

    def on_button(self, label):
        if label == 'C':
            self.expression = ""
            self.display.delete(0, 'end')
            return
        if label == '<-':
            self.expression = self.expression[:-1]
            self.display.delete(0, 'end')
            self.display.insert(0, self.expression)
            return
        if label == '=' or label == 'ANS':
            expr = self.display.get()
            try:
                res = evaluate(expr)
            except CalcError as e:
                messagebox.showerror("Error", str(e))
                return
            # show result
            self.display.delete(0, 'end')
            self.display.insert(0, str(res))
            self._append_history(expr, res)
            self.expression = str(res)
            return
        # functions that map directly to parser names
        mapping = {'pi':'pi', 'e':'e', 'sqrt':'sqrt', 'sin':'sin','cos':'cos','tan':'tan','ln':'ln','log':'log'}
        token = mapping.get(label, label)
        self.expression += token if token not in ('=','ANS') else ''
        self.display.delete(0, 'end')
        self.display.insert(0, self.expression)

    def _append_history(self, expr, res):
        self.hist.configure(state='normal')
        self.hist.insert('end', f"{expr} = {res}\n")
        self.hist.configure(state='disabled')
        self.hist.see('end')

if __name__ == "__main__":
    app = CalcGUI()
    app.mainloop()
