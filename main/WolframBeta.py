from tkinter import *

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from FunctionClass import *
from functions import *
from analysis import min, minimum, max, maximum, nullstellen, der
from matrix import Matrix

lblue = "#1e3799"
dblue = "#001B81"
lgray = "#d9d9d9"
dgray = "#404040"

# Deutsch: 0, Francais: 1, English: 2
lang = 0

default_frame = 1
min_window = True

"""TODO:
CodeFrame
ein paar kürzungen (kein 2x^3 = 2*3*x^2)
language überall änderbar
Farbe überall änderbar
angepasste größe der latex outputs
"""


def toggle_lang(language):
    global lang
    lang = language
    print(f"changed language to {lang}")


def format_error(error):
    """Formatiert ein error code."""
    
    if isinstance(error, Exception):
        # Costum or automatic exceptions
        if error.args:
            if len(error.args) > 1:
                # Error mit verschieden Sprachen
                return error.args[lang]
            else:
                # nur eine sprache
                return error.args[0]
        else:
            # zb: ZeroDivisionError (hat keine args)
            # repr(error) würde ZeroDivisionError() ausgeben, man will die klammern weghaben
            return repr(error)[:-2]
    else:
        # nur costum error text gegeben
        return error


def rrange(a, b, n=1.0):
    """range(), aber auch mit float abständen."""
    l, x = [], a
    while x < b:
        l.append(x)
        x += n
    return l


def check_and_clean(string):
    """Der gegeben string wird für den parser lesbar gemacht und es werden illegale Charaktere gesucht."""
    if not string:
        return None
    string = string.replace(" ", "").replace("**", "^")
    string = string.replace("²", "^2").replace("³", "^3")
    string = string.replace("pi", "π")
    for char in string:
        if char not in ".,+-*/()_^`'! π=3" + '"' + NUMBERS + ALPHABET:
            return SyntaxError(f"Invalid input: '{char}'")
    if "++" in string or "**" in string or "//" in string or "^^" in string or ".." in string or ",," in string:
        return SyntaxError("invalid input!")
    if string[0] in "*/^).,_!=":
        return SyntaxError(f"Invalid first character: {string[0]}")
    if string[-1] in "+-*/^(.,_":
        return SyntaxError(f"Invalid last character: {string[-1]}")
    return string


def get_all_children(top_frame):
    """Vom top_frame werden alle unter widgets (children) gesucht"""
    all_children = [top_frame] + top_frame.winfo_children()
    
    for item in all_children:
        all_children.extend(item.winfo_children())
    
    return all_children


class RechnerFrame(Frame):
    def __init__(self, container):
        super().__init__(container)
        
        self.memory = {}
        self.listed_memory = []
        self.rang = -1
        self.input = ""
        
        self.io_frame = Frame(self)
        self.io_frame.place(relx=0.2, rely=0.1, relwidth=0.6, relheight=0.8)
        self.io_frame.focus_set()
        
        # Entry for user input
        self.input_entry = Entry(self.io_frame, bd=2, relief="solid", highlightthickness=0, justify="center")
        self.input_entry.place(relx=0.1, rely=0, relwidth=0.8, relheight=0.2)
        self.input_entry.focus_set()
        self.input_entry.bind("<Up>", lambda _: self.show_last(-1))
        self.input_entry.bind("<Down>", lambda _: self.show_last(+1))
        
        # settings frame for integration methods
        self.einstellungs_frame = Frame(self.io_frame, bd=2, relief="solid")
        self.lab = Label(self.einstellungs_frame,
                         text=["Integrationsmethode:", "Methode d'integration", "Integration method"][lang])
        self.lab.grid(row=0, column=0)
        Button(self.einstellungs_frame, text="X", bd=0, command=self.hide_einstellungen).grid(row=0, column=1)
        self.method = StringVar(value="riemann")
        self.method.trace("w", lambda *_: self.refresh_integration(self.method.get()))
        Radiobutton(self.einstellungs_frame, text="Riemann", variable=self.method, value="riemann").grid(row=1,
                                                                                                         column=0,
                                                                                                         sticky="W",
                                                                                                         padx=10)
        Radiobutton(self.einstellungs_frame, text="Trapez", variable=self.method, value="trapez").grid(row=2, column=0,
                                                                                                       sticky="W",
                                                                                                       padx=10)
        Radiobutton(self.einstellungs_frame, text="Simpson", variable=self.method, value="simpson").grid(row=3,
                                                                                                         column=0,
                                                                                                         sticky="W",
                                                                                                         padx=10)
        
        # Error Label für die Fehler im user input
        self.error_label = Label(self.io_frame, fg="red")
        self.error_label.place(relx=0.1, rely=0.2, relwidth=0.8, relheight=0.075)
        
        # Enter Button
        self.enter_button = Button(self.io_frame, text="=", bd=0, command=self.commit_input,
                                   highlightbackground="#707070")
        self.enter_button.place(relx=0.425, rely=0.35, relwidth=0.15, relheight=0.08)
        
        # Latex frame
        self.latex_io = Label(self.io_frame, bd=2, relief="solid")
        self.latex_io.place(relx=0, rely=0.45, relwidth=1, relheight=0.55)
        
        self.io_figure = Figure()
        self.io_canvas = FigureCanvasTkAgg(self.io_figure, master=self.latex_io)
        self.io_canvas.get_tk_widget().pack(expand=1, fill="both")
        self.answers = "", ""
        
        # clear button
        self.clear_button = Button(self, text="X", command=self.clear_frame)
        self.clear_button.place(relx=0.95, y=10)
        
        # Help label
        with open("../help/rechner_de.txt", "r") as help:
            rechner_de = help.read()
        self.help_label = Message(self, text=rechner_de, relief="raised")
        self.help_show = False
        
        self.elements = get_all_children(self)
        
        self.input_entry.bind("<Return>", self.commit_input)
    
    def commit_input(self, event=None):
        """Beim enter press vom entry wird wier geschaut ob der input schon eingegeben wurde, wenn ja wird das
        gespeicherte angezeigt, wenn nicht, wird der input interpretiert und das ergebnnis gespeichert."""
        
        self.rang = -1
        self.input = self.input_entry.get()
        if not self.input:
            return None
        if not (self.listed_memory and self.input == self.listed_memory[-1]):
            """self.listed_memory speichert nur die inputs in der reihenfolge, sodass die inputs mit den pfeiltasten
            wieder gewählt in eingefügt werden können"""
            self.listed_memory.append(self.input)
        
        if self.input in self.memory:
            """in self.memory werden die inputs und ergebnisse gespeichert. Jetzt wird das gespeicherte angezeigt"""
            self.show_answer(self.memory[self.input])
        else:
            answer = self.interprete(self.input)
            if not answer: return None
            self.show_answer(answer)
            self.memory[self.input] = answer
    
    def interprete(self, user_input):
        
        user_input = check_and_clean(user_input)
        if type(user_input) == SyntaxError:
            self.show_error(format_error(user_input))
            return None
        
        self.show_einstellungen() if "Int" in user_input else self.hide_einstellungen()
        
        try:
            if "=" in user_input:
                """Gleichheit überprüfen"""
                
                if "==" in user_input:
                    # Man soll "==" oder "=" schreiben können
                    user_input = user_input.replace("==", "=")
                n = user_input.find("=")
                
                lp_raw = user_input[:n]
                rp_raw = user_input[n + 1:]
                
                if "=" in rp_raw:
                    self.show_error(f"Invalid input")
                    return None
                
                lp, rp = parse(lp_raw, False), parse(rp_raw, False)
                lp_simp, rp_simp = write(parse(lp_raw, True)), write(parse(rp_raw, True))
                
                if isfloat(lp_simp):
                    lp_simp = round(flint(lp_simp), 10)
                if isfloat(rp_simp):
                    rp_simp = round(flint(rp_simp), 10)
                    
                if not isfloat(eq := write(parse(f"{lp_simp}-{rp_simp}", True))):
                    # gleichung lösen:
                    loesungen = nullstellen(lambda x: eval(eq), -10, 10)
                    output_latex = r"x \in \{" + str([flint(round(ans, 5)) for ans in loesungen])[1:-1] + r"\}"
                    
                else:
                    # gleichheit überprüfen
                    output_latex = eval(f"{lp_simp} == {rp_simp}")
                
                input_latex = f"{write_latex(lp)} = {write_latex(rp)}"
                return rf"{input_latex}:\/\/ {output_latex}"
            
            else:
                """Sonstige Berechnungen"""
                input_latex = write_latex(parse(user_input, False), False)
                output_tree = parse(user_input, simp=True)
                
                write_ = write(output_tree)
                try:
                    """Falls das ausgegebene zb 'sin(8)' ist, wird das berechnet"""
                    output_latex = flint(eval(str(write_)))
                except Exception:
                    """Wenn eine variable im ergebnis ist, kann es nicht berechnet werden. Dann wird nur versucht
                    das eingegebene zu vereinfachen."""
                    print(f"couldnt eval expr: {write_}")
                    output_latex = write_latex(output_tree, simp=True)
                    
                return f"{input_latex} = {output_latex}"
        
        except Exception as error:
            self.show_error(format_error(error))
            return None
    
    def show_answer(self, answers=None):
        """Die Antwort wird auf der matplotlib Figure angezeigt, damit der output in LaTeX schreibweise schön
        gerendert werden kann. Text, das mit '$' umgeben ist, wird als LaTeX code erkannt"""
        
        if answers is None:
            # Figure wird nur wegen colormodechange refresht (keine answers gegeben)
            answers = self.answers
        else:
            self.answers = answers
        
        self.show_error()
        self.io_figure.clear()
        self.io_figure.set_facecolor(["white", "#505050"][app.color_mode])
        
        text = rf"${answers}$"
        length = len(text)
        size = int(2000 / (length + 60) + 5)
        if text != "$$":
            self.io_figure.text(0.5, 0.5, text, fontsize=size,
                                color=["black", "white"][app.color_mode], va="center", ha="center")
        self.io_canvas.draw()
    
    def show_error(self, error=""):
        self.error_label.config(text=error)
        if error: print(f"Error: {error}")
    
    def show_einstellungen(self):
        """Wenn ein Intergral berechnet wird (es wird nur nach 'Int' im input gesucht), dann erscheinen einstellungen
        rechts neben dem input um die integrationsmethode zu bestimmen."""
        self.input_entry.place(relwidth=0.55)
        self.einstellungs_frame.place(relx=0.65, y=0, relwidth=0.25, relheight=0.2)
    
    def hide_einstellungen(self):
        self.input_entry.place(relwidth=0.8)
        self.einstellungs_frame.place_forget()
    
    def refresh_integration(self, method):
        """Bei änderung der integrationsmethode (Riemann/Trapez/Simpson) wird der input erneut berechnet"""
        set_default_integration_method(method)
        self.show_answer(self.interprete(self.input_entry.get()))
    
    def show_last(self, dir):
        """Im entry wird bei Pfeil hoch/runter das letzte/nächste eingegebene angezeigt"""
        if not self.listed_memory: return None
        self.rang += dir * 1 if (not self.rang == dir * len(self.listed_memory)) and (not self.rang == -dir) else 0
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, self.listed_memory[self.rang])
    
    def switch_color(self):
        """refresht den canvas"""
        self.show_answer()
    
    def show_help(self, force=None):
        """Die Hilfe oben links wird angezeigt/versteckt"""
        self.help_show = not self.help_show if force is None else force
        if self.help_show:
            self.help_label.place(x=10, y=0)
        else:
            self.help_label.place_forget()
    
    def clear_frame(self):
        """Vom 'clear' button oben rechts wird alles vom RechnerFrame gelöscht"""
        self.listed_memory = []
        self.memory = {}
        self.rang = -1
        self.input_entry.delete(0, "end")
        self.show_error()
        self.show_answer("")
        self.hide_einstellungen()
        self.show_help(False)


class EntryLine(Frame):
    """Einzelne Zeile in AnalysisFrame mit button und entry"""
    
    def __init__(self, container, super_, id_):
        super().__init__(container, height=40, bd=1, relief="groove")
        self.focus_set()
        self.super_ = super_
        self.id = id_
        self.color = None
        
        self.fr = Frame(self, height=30)
        self.fr.pack(side="top", expand=1, fill="both")
        self.fr.focus_set()
        
        self.bttn = Button(self.fr, takefocus=0, bd=0, bg="white", highlightthickness=0,
                           image=super_.rings["gray"], command=lambda: super_.toggle_visibility(self))
        self.bttn.pack(side="left", fill="both")
        
        self.pfeil = Label(self.fr, takefocus=0, text=" > ", bg="white", fg="black", height=2)
        self.pfeil.pack(side="left", fill="both")
        
        self.entry = Entry(self.fr, takefocus=1, bd=0, highlightthickness=0, fg="black", bg="white")
        self.entry.pack(side="left", fill="both", expand=True)
        self.entry.focus_set()
        
        self.error_label = Label(self, takefocus=0, height=0, fg="red")
        # wird nur wenn nötig angezeigt
        
        self.entry.bind("<Return>", lambda _: super_.enter_pressed(self))
        self.entry.bind("<BackSpace>", lambda _: super_.destroy_line(self) if not self.entry.get() else 0)
    
    def show_error(self, error_message):
        self.error_label.config(text=error_message)
        self.error_label.pack(side="bottom", fill="x", expand=0)
    
    def hide_error(self):
        self.error_label.pack_forget()
    
    def activate_bttn(self):
        """Der Button wird aktiviert indem die jeweilige Farbe (nicht mehr grau) angezeigt wird."""
        self.bttn.config(image=self.super_.rings[self.color])
    
    def disable_bttn(self):
        """Der button wird grau."""
        self.bttn.config(image=self.super_.rings["gray"])


class FunctionWrapper(Function):
    """Wrapper für eine Funktion in AnalysisFrame. Hat zusätzlich zur class Function wichtige Attribute wie
    name, Farbe, sichtbarkeit im Graph, und ID"""
    
    def __init__(self, string, variable="x", name=None, color=None, isvisible=True, entry_index=None):
        # print(f"neue funktion: {string}, {name = }")
        super().__init__(string, variable)
        self.name = name
        self.color = color
        self.isvisible = isvisible
        self.index = entry_index


class AnalysisFrame(Frame):
    """TODO:
    compute-eingabe
    Alle Farben als Ring
    Ring besser
    Funktionskatalog
    Differerentialgleichung
    graph axis
    (design)
    
    """
    
    def __init__(self, container):
        super().__init__(container)
        
        # Entry lines Frame
        self.entry_lines_outer_frame = Frame(self, bg="white", bd=1, relief="solid")
        self.entry_lines_outer_frame.place(relx=0.1, rely=0.05, relheight=0.35, relwidth=0.35)
        self.entry_lines_outer_frame.focus_set()
        
        self.scroll_canvas = Canvas(self.entry_lines_outer_frame, borderwidth=0, highlightthickness=0)
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.scroll_canvas.focus_set()
        
        self.scrollbar = Scrollbar(self.entry_lines_outer_frame, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")
        
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.scroll_canvas.yview)
        
        self.scrolled_frame = Frame(self.scroll_canvas)
        self.scrolled_frame.focus_set()
        self.canvas_window = self.scroll_canvas.create_window(0, 0, window=self.scrolled_frame, anchor="nw")
        self.entry_lines_outer_frame.bind("<Configure>", self.configure_canvas)
        self.entry_lines_outer_frame.bind("<Enter>", self.configure_canvas)
        self.configure_canvas()
        
        self.rings = {}
        for color in ["gray", "red", "green", "blue", "cyan", "magenta", "yellow", "black"]:
            self.rings[color] = PhotoImage(file=f"../pictures/Rings/{color}_ring.png").subsample(3, 3)
        
        self.lines = []
        
        self.line = EntryLine(self.scrolled_frame, self, 0)
        self.line.pack(fill="x")
        self.line.focus_set()
        self.line.entry.focus_set()
        self.lines.append(self.line)
        
        # New func or dgl buttons:
        self.new_frame = Frame(self, bd=1, relief="solid")
        self.new_frame.place(relx=0.1, rely=0.39, relwidth=0.35, relheight=0.05)
        
        self.new_frame.rowconfigure(0, weight=1)
        self.new_frame.columnconfigure(0, weight=1)
        self.new_frame.columnconfigure(1, weight=3)
        self.new_frame.columnconfigure(2, weight=3)
        
        Label(self.new_frame, text=["Neu: ", "Nouveau: ", "New: "][lang]).grid(row=0, column=0, sticky="news")
        Button(self.new_frame, text="f(x) = ...", command=self.add_new_func).grid(row=0, column=1, sticky="news")
        Button(self.new_frame, text="y' = ...", command=self.add_new_dgl).grid(row=0, column=2, sticky="news")
        
        # single entry Frame
        self.compute_frame = Frame(self, bd=1, relief="solid", highlightthickness=0)
        self.compute_frame.place(relx=0.1, rely=0.55, relwidth=0.35, relheight=0.1)
        
        self.compute_entry = Entry(self.compute_frame, justify="center")
        self.compute_entry.pack(side="left", fill="both", expand=True)
        self.compute_entry.bind("<Return>", self.interprete_input)
        
        self.submit_bttn = Button(self.compute_frame, text="?", command=self.interprete_input)
        self.submit_bttn.pack(side="right", fill="both")
        
        self.compute_error_label = Label(self, fg="red")
        self.compute_error_label.place(relx=0.1, rely=0.65, relheight=0.05, relwidth=0.35)
        
        # latex output frame
        self.output_frame = Label(self, bd=1, relief="solid")
        self.output_frame.place(relx=0.1, rely=0.7, relwidth=0.35, relheight=0.25)
        
        self.io_figure = Figure()
        self.io_canvas = FigureCanvasTkAgg(self.io_figure, master=self.output_frame)
        self.io_canvas.get_tk_widget().pack(expand=1, fill="both")
        
        # Canvas Frame
        self.canvas_frame = Frame(self)
        self.canvas_frame.place(relx=0.5, rely=0.05, relheight=0.9, relwidth=0.45)
        
        self.figure = Figure()
        self.subplot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        # self.subplot.set_facecolor("red")
        # self.figure.set_facecolor("blue")
        self.subplot.grid(True)
        
        # x-range auswahl:
        self.default_range = [-5, 5]
        self.range_frame = Frame(self)
        self.range_frame.place(relx=0.65, rely=0.95, relheight=0.05, relwidth=0.25)
        Label(self.range_frame, text="x-range: [").pack(side="left")
        self.x_min_entry = Entry(self.range_frame, width=4)
        self.x_min_entry.pack(side="left")
        self.x_min_entry.insert(0, self.default_range[0])
        Label(self.range_frame, text=", ").pack(side="left")
        self.x_max_entry = Entry(self.range_frame, width=4)
        self.x_max_entry.pack(side="left")
        self.x_max_entry.insert(0, self.default_range[1])
        Label(self.range_frame, text="]").pack(side="left")
        self.refresh_icon = PhotoImage(file="../pictures/refresh.png").subsample(30, 30)
        Button(self.range_frame, image=self.refresh_icon, command=self.refresh_max_range).pack(side="left", padx=20)
        
        # clear button
        self.clear_button = Button(self, text="X", command=self.clear_frame)
        self.clear_button.place(relx=0.95, y=10)
        
        # Help Label
        with open("../help/analysis_deutsch.txt", "r") as help_:
            ana_deutsch = help_.read()
        self.help_label = Message(self, text=ana_deutsch, relief="raised")
        self.help_show = False
        
        self.functions = {}  # alle gespeicherte funktionen
        self.dgl = {}
        self.funcnames_order = ["f", "g", "h", "i", "j", "k", "u", "v", "p", "s", "l"]
        self.all_colors = ["r", "g", "b", "c", "m", "y", "k"]
        self.color_names = {'r': 'red', 'g': 'green', 'b': 'blue', 'c': 'cyan', 'm': 'magenta',
                            'y': 'yellow', 'k': 'black'}
        self.stored_values = {}
    
    def configure_canvas(self, event=None):
        """Die EntryLines werden auf die korrekte Breite gebracht und der Frame, der sie hält, wird mit der Scrollbar
        verbunden, damit man darin scrollen kann"""
        width = self.scroll_canvas.winfo_width()
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox(self.canvas_window))
        self.scroll_canvas.itemconfig(self.canvas_window, width=width)
    
    def add_new_func(self):
        """Über den Button 'f(x) = ' unter den EntryLines wird diese Funktion aufgerufen"""
        line = self.get_first_empty_line()
        id = line.id
        name = self.generate_func_name()
        color = self.all_colors[id % 7]
        line.entry.insert(0, f"{name}(x) = ")
        self.functions[id] = FunctionWrapper("", "x", name, color, False, id)
        line.entry.focus_set()
    
    def add_new_dgl(self):
        """Über den Button "y' = " aufgerufen"""
        line = self.get_first_empty_line()
        line.entry.insert(0, "y' = ")
        line.entry.focus_set()
    
    def get_first_empty_line(self):
        """Suche erstmal eine leere zeile:"""
        for line in self.lines:
            if not line.entry.get():
                return line
        
        # Wenn keine leere Ziele gefunden wird:
        return self.create_new_line()
    
    def create_new_line(self):
        """Eine neue EntryLine wird erstellt und returned"""
        id_ = self.generate_new_id()
        self.new_line = EntryLine(self.scrolled_frame, self, id_)
        self.new_line.pack(fill="x")
        self.new_line.entry.focus_set()
        self.lines.append(self.new_line)
        return self.new_line
    
    def generate_new_id(self):
        """Jede EntryLine hat eine ID. Hier wird eine neue generiert"""
        n = 0
        _all = [line.id for line in self.lines]
        while n in _all:
            n += 1
        return n
    
    def enter_pressed(self, obj):
        """Wenn enter von der EntryLine 'obj' gedrückt wird, wird der input interpretiert und wenn es keinen fehler
        gibt, zur nächsten Zeile gesprungen"""
        obj.hide_error()
        
        id_ = obj.id
        index = self.lines.index(obj)
        if not self.interprete_function(obj):
            # Wenn es einen Fehler im input gibt, wird nicht zur nächsten Zeile gegangen
            return None
        
        if self.check_line(index + 1):
            self.lines[index + 1].entry.focus_set()
        
        elif obj.entry.get():
            self.create_new_line()
    
    def destroy_line(self, obj):
        """wenn man in einer leeren Zeile nochmal 'Delete' drückt (also die zeile löschen will), wird geschaut, ob es
        vor oder nach dieser Zeile noch eine leere Zeile gibt."""
        index = self.lines.index(obj)
        if self.check_line(index + 1) or self.check_line(index - 1) and not self.lines[index - 1].entry.get():
            self.lines[index].destroy()
            if index in self.functions:
                del self.functions[index]
            self.lines.pop(index)
            self.lines[-1].entry.focus_set()
    
    def check_line(self, index):
        """Überprüft, ob es diese Zeile gibt"""
        try:
            _ = self.lines[index]
            return True
        except IndexError:
            return False
    
    def interprete_function(self, obj):
        """Der input einer EntryLine wird interpretiert."""
        entry = obj.entry
        string = entry.get()
        n = obj.id
        
        string = check_and_clean(string)
        if type(string) == SyntaxError:
            self.show_error(format_error(string), n)
            return None
        
        if "=" not in string:
            # Funktionsterm gegeben, das geplottet werden soll
            
            name = self.generate_func_name()
            color = self.all_colors[n % 7]
            
            # Funktion draus machen:
            try:
                function = FunctionWrapper(string, "x", name, color, True, n)
                self.functions[n] = function
                entry.insert(0, f"{name}(x) = ")
                self.graph()
                obj.color = self.color_names[color]
                obj.activate_bttn()
                return True
            except Exception as error:
                # raise error
                self.show_error(format_error(error), n)
                return False
        
        elif "(x)=" in string[:string.index("=") + 1]:
            # eigener funktionsname gegeben oder ältere Funktion geändert
            
            func = string[string.index("=") + 1:]
            funcname = string[:string.index("(x)=")]
            
            if not func:
                self.show_error("Error: no input", n)
                return False
            if funcname in [func.name if n != index else "" for index, func in self.functions.items()]:
                self.show_error("Error: function name already taken", n)
                return False
            
            if n in self.functions:
                previous_function = self.functions[n]
                # es ist nur eine Änderung einer alten schon eingegebenen Funktion
                color = previous_function.color
                isvisible = previous_function.isvisible
            else:
                color = self.all_colors[n % 7]
                isvisible = True
            
            obj.color = self.color_names[color]
            obj.activate_bttn() if isvisible else obj.disable_bttn()
            
            try:
                function = FunctionWrapper(func, "x", funcname, color, isvisible, n)
                self.functions[n] = function
                self.graph()
                return True
            except Exception as error:
                self.show_error(format_error(error), n)
                return False
        
        elif string.startswith("y'="):
            pass
        
        return True
    
    def generate_func_name(self):
        """Es wird automatisch ein neuer Name für eine Funktion generiert"""
        n = 0
        while self.funcnames_order[n] in [f.name for f in self.functions.values()]:
            n_max = len(self.funcnames_order)
            n += 1
            if n == n_max - 1:
                # Wenn die namen aufgebraucht sind, geht es mit f_1, g_1, ... , f_2, g_2 ... weiter
                self.funcnames_order.append(f"{self.funcnames_order[(n + 1) % 11]}_{(n + 1) // 11}")
        
        return self.funcnames_order[n]
    
    def graph(self, new=None):
        """Von allen gespeicherten Funktionen werden alle sichtbaren geplottet. Dabei werden alle Werte gespeichert, da
        sie sonst bei jedem neuen graph() aufruf neu berechnet werden müssen"""
        
        x_min, x_max = self.default_range
        I_max = rrange(x_min, x_max, (x_max-x_min)/100)
        
        self.subplot.clear()
        for function in self.functions.values():
            if function.isvisible:
                if function.str_out in self.stored_values and not new:
                    # Die funktion wurde schon mal angezeigt und deren (x,y) werte wurden schon gespeichert
                    I, J = self.stored_values[function.str_out]
                else:
                    I, J = [], []
                    for x in I_max:
                        try:
                            J.append(function(x))
                            I.append(x)
                        except Exception as e:
                            # wenn x nicht im defbereich der Funktion liegt, gibts nen ValueError (wird ignoriert)
                            if type(e) is not ValueError:
                                raise e
                    self.stored_values[function.str_out] = [I, J]
                self.subplot.plot(I, J, color=function.color, label=f"y = {function.name}(x)")
                self.subplot.legend(loc="upper left")
        # self.subplot.spines["left"].set_position("center")
        # self.subplot.spines["bottom"].set_position("center")
        # self.subplot.spines["top"].set_color(None)
        # self.subplot.spines["right"].set_color(None)
        self.subplot.grid(True)
        self.canvas.draw()
    
    def refresh_max_range(self):
        x_min, x_max = self.x_min_entry.get(), self.x_max_entry.get()
        if not isfloat(x_min):
            # illegale eingabe
            x_min = -5
            self.x_min_entry.delete(0, "end")
            self.x_min_entry.insert(0, x_min)
        if not isfloat(x_max):
            x_max = 5
            self.x_max_entry.delete(0, "end")
            self.x_max_entry.insert(0, x_max)
        if (x_min := flint(x_min)) > (x_max := flint(x_max)):
            x_min, x_max = x_max, x_min
            self.x_min_entry.delete(0, "end")
            self.x_min_entry.insert(0, x_min)
            self.x_max_entry.delete(0, "end")
            self.x_max_entry.insert(0, x_max)
            
        self.default_range = [x_min, x_max]
        self.graph(new=True)
        
    def toggle_visibility(self, obj):
        """Wenn man auf den Farbkreis den EntryLine 'obj' drückt, wird deren sichtbarkeit getoggelt"""
        id_ = obj.id
        if id_ not in self.functions:
            return None
        isvisible = self.functions[id_].isvisible
        self.functions[id_].isvisible = not isvisible
        if isvisible:
            obj.disable_bttn()
        else:
            obj.activate_bttn()
        self.graph()
    
    def show_error(self, error, n=None):
        """Der error wird entweder unter der EntryLine mit id=n angezeigt, oder unter dem entry fpr allgemeine
        Rechnungen"""
        if n is not None:
            # Fehler in der EntryLine mit id = n
            for line in self.lines:
                if line.id == n:
                    line.show_error(error)
        else:
            # Fehler in dem computeentry
            self.compute_error_label.config(text=error)
        if error: print(f"Error({n}): {error}")
    
    def interprete_input(self, _=None):
        """
        min(f) / max(f)
        * f(x) = 0 / nullstelle(f)
        * f'(x) / df(x)/dx
        * f^n(a) / d^nf(a)/dx^n
        * int(a, b, f(x))
        """
        string = self.compute_entry.get()
        
        string = check_and_clean(string)
        if type(string) == SyntaxError:
            self.show_error(format_error(string))
            return None
        
        try:
            if "=" in string:
                pass
            else:
                
                input_latex = write_latex(parse(string))
                output_tree = parse(string, simp=True)
                print(input_latex, output_tree)
                try:
                    for func in self.functions.values():
                        locals()[func.name] = func
                    for func in SIMPLE_FUNCTIONS:
                        locals()[func] = globals()[func]
                    # print(locals())
                    w = write(output_tree)
                    print(f"write: {w}")
                    output_latex = eval(w)
                except Exception as e:
                    print(f"couldnt eval {write(output_tree)}, {e}")
                    output_latex = write_latex(output_tree, simp=True)
        except Exception as error:
            self.show_error(format_error(error))
            return None
        
        self.show_answer(input_latex, output_latex)
    
    def show_answer(self, input_latex, output_latex):
        """Der output aus der 'compute_entry' wird hier auf einer matplotlib Figure angezeigt."""
        self.show_error("")
        text = rf"${input_latex} = {output_latex}$"
        text = text if text != "$ = $" else ""
        self.io_figure.clear()
        self.io_figure.text(0.5, 0.5, text, size=int(1000 / (len(text) + 50)), va="center", ha="center")
        self.io_canvas.draw()
    
    def show_help(self, force=None):
        """Die Hilfe für den AnalysisFrame wird angezeigt/versteckt."""
        self.help_show = not self.help_show if force is None else force
        
        if self.help_show:
            self.help_label.place(x=10, y=0)
        else:
            self.help_label.place_forget()
    
    def switch_color(self):
        pass
    
    def clear_frame(self):
        """Vom 'clear' button oben rechts wird alles vom AnalysisFrame gelöscht"""
        self.functions = {}
        self.stored_values = {}
        for line in self.lines:
            line.destroy()
        self.lines = []
        self.create_new_line()
        self.graph()
        self.compute_entry.delete(0, "end")
        self.show_answer("", "")
        self.show_help(False)


class MatrixWrapper:
    def __init__(self, super_frame, name, rows, columns, id_):
        
        self.name = name
        self.id = id_
        self.values_frame = Frame(super_frame.edit_frame)
        self.name_entry = super_frame.name_entry
        self.rows_var, self.cols_var = super_frame.rows_variable, super_frame.columns_variable
        self.rows = rows
        self.columns = columns
        
        self.values = []
        self.entries = self.entry_gitter(self.values_frame, rows, columns)
    
    @staticmethod
    def entry_gitter(container, rows, columns):
        """Gibt eine Tabelle mit Entries aus, die im 'container' plaziert werden"""
        entries = []
        for n in range(rows):
            container.rowconfigure(n, weight=1)
            row = []
            for m in range(columns):
                container.columnconfigure(m, weight=1)
                entry = Entry(container, width=3, justify="center")
                entry.grid(row=n, column=m)
                row.append(entry)
            entries.append(row)
        return entries
    
    def save_values(self):
        """Die aktuellen Werte der EntryTabelle werden als float gespeichert. '' wird als 0 interpretiert"""
        self.values = [[float(entry.get()) if entry.get() else 0 for entry in row] for row in self.entries]
    
    def insert_values(self, matrix):
        """Die Werte der gegebenen 'matrix' werden in die Tabelle eingefügt"""
        self.save_values()
        if matrix.rows != self.rows or matrix.cols != self.columns:
            raise TypeError
        else:
            for n in range(len(self.values)):
                for m in range(len(self.values[0])):
                    self.entries[n][m].delete(0, "end")
                    self.entries[n][m].insert(0, matrix[n][m])
    
    def get_values(self):
        self.save_values()
        return self.values
    
    def show(self):
        """Die Tabelle mit den Werten werden im MatrixFrame angezeigt. Der name und die dimensionen acuh"""
        self.values_frame.pack(fill="both", expand=True)
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, self.name)
        self.rows_var.set(self.rows)
        self.cols_var.set(self.columns)
    
    def hide(self):
        """Die Tabelle wird vom MatrixFrame versteckt. Die Tabelle gibt es immer noch und die Werte bleiben noch drin"""
        self.values_frame.pack_forget()
        self.name_entry.delete(0, "end")


class MatrixFrame(Frame):
    def __init__(self, container):
        super().__init__(container)
        
        self.matrices = []
        self.matrices_name = {}
        self.current_matrix = None
        
        # Auswahl Frame
        self.matrix_auswahl = Frame(self, bd=1, relief="raised")
        self.matrix_auswahl.place(relx=0.1, rely=0.0, relwidth=0.3, relheight=0.2)
        Button(self.matrix_auswahl, text=" + ", command=self.show_matrix, width=2, height=2).pack(side="left",
                                                                                                  anchor="n")
        
        # Edit Frame
        self.matrix_frame = Frame(self, bd=1, relief="raised")
        self.matrix_frame.place(relx=0.45, rely=0.0, relwidth=0.45, relheight=0.5)
        
        self.matrix_frame.rowconfigure(0, weight=1)
        self.matrix_frame.rowconfigure(1, weight=5)
        self.matrix_frame.rowconfigure(2, weight=1)
        self.matrix_frame.columnconfigure(0, weight=1)
        self.matrix_frame.columnconfigure(1, weight=5)
        self.matrix_frame.columnconfigure(2, weight=1)
        
        # Name Frame
        self.name_frame = Frame(self.matrix_frame)
        self.name_frame.grid(row=1, column=0, sticky="e")
        
        self.name_entry = Entry(self.name_frame, width=2, justify="center")
        self.name_entry.pack(side="left")
        Label(self.name_frame, text=" = ").pack(side="right")
        
        # Edit Frame (EntryTable)
        self.edit_frame = Frame(self.matrix_frame, bd=1, relief="raised")
        self.edit_frame.grid(row=1, column=1, sticky="news")
        
        # Dimensions Frame
        self.dimensions_frame = Frame(self.matrix_frame)
        self.dimensions_frame.grid(row=0, column=1)
        
        Label(self.dimensions_frame, text="rows: ").pack(side="left")
        self.rows_variable = StringVar(value="3")
        self.rows_box = Spinbox(self.dimensions_frame, from_=1, to=15, width=3, textvariable=self.rows_variable,
                                justify="center")
        self.rows_box.pack(side="left", padx=10)
        self.refresh_logo = PhotoImage(file="../pictures/refresh.png").subsample(30, 30)
        Button(self.dimensions_frame, image=self.refresh_logo, command=self.refresh_dimensions, padx=20, pady=20, bd=0).pack(
            side="right",
            padx=10)
        self.columns_variable = StringVar(value="3")
        self.columns_box = Spinbox(self.dimensions_frame, from_=1, to=15, width=3, textvariable=self.columns_variable,
                                   justify="center")
        self.columns_box.pack(side="right", padx=0)
        Label(self.dimensions_frame, text="columns: ").pack(side="right", padx=10)
        
        # Vorschlag Frame (4 Buttons)
        self.vorschlag_frame = Frame(self.matrix_frame)
        self.vorschlag_frame.grid(row=2, column=1)
        
        Button(self.vorschlag_frame, text="ID", command=self.new_identity_matrix).pack(side="left")
        Button(self.vorschlag_frame, text="Zero", command=self.new_zero_matrix).pack(side="left")
        Button(self.vorschlag_frame, text="Random", command=self.new_random_matrix).pack(side="left")
        Button(self.vorschlag_frame, text="RandomSym", command=self.new_randomsym_matrix).pack(side="left")
        
        # Delet and Save Button
        self.trash_icon = PhotoImage(file="../pictures/trash.png").subsample(20, 20)
        self.save_icon = PhotoImage(file="../pictures/check.png").subsample(20, 20)
        Button(self.matrix_frame, image=self.trash_icon, command=self.delete_matrix).grid(row=0, column=2)
        Button(self.matrix_frame, image=self.save_icon, command=self.submit_matrix).grid(row=2, column=2)
        
        # Error Label
        self.error_label = Label(self, fg="red")
        self.error_label.place(relx=0.45, rely=0.5, relheight=0.05, relwidth=0.45)
        
        # Entry Frame
        self.entry_frame = Frame(self, bd=1, relief="raised", bg="white")
        self.entry_frame.place(relx=0.1, rely=0.4, relwidth=0.3, relheight=0.1)
        
        self.input_entry = Entry(self.entry_frame, bd=0, highlightthickness=0)
        self.input_entry.pack(side="left", fill="both", expand=True, padx=20)
        self.input_entry.bind("<Return>", self.interprete_input)
        self.return_icon = PhotoImage(file="../pictures/enter.png").subsample(24, 24)
        Button(self.entry_frame, image=self.return_icon, command=self.interprete_input, bg="white").pack(side="left", padx=10)
        
        # Output Frame
        self.output_frame = Label(self, bd=1, relief="raised")
        self.output_frame.place(relx=0.1, rely=0.55, relwidth=0.8, relheight=0.45)
        
        # clear button
        self.clear_button = Button(self, text="X", command=self.clear_frame)
        self.clear_button.place(relx=0.95, y=10)
        
        # Help Label
        with open("../help/matrix_deutsch.txt", "r") as help_:
            matrix_deutsch = help_.read()
        self.help_label = Text(self)
        self.help_label.insert("end", matrix_deutsch)
        self.help_label.config(state="disabled")
        self.help_show = False
        self.ignore = False
        
        self.show_matrix()
    
    def check_dimensions(self):
        """Es wird geschaut ob die gegebenen Werte n und m integer zwischen 1 und 15 sind, wenn dann werden sie
        zurückgegeben"""
        n, m = self.rows_variable.get(), self.columns_variable.get()
        try:
            n, m = int(n), int(m)
            if n < 1 or n > 15 or m < 1 or m > 15:
                raise ValueError
            self.show_error()
        except ValueError:
            self.show_error("Dimensions must be integers between 1 and 15")
            return None
        return n, m
    
    def refresh_dimensions(self, *event):
        """Vom 'ok' Button neben den dimensions wird hier eine neue matrix mit den gegebenen dimensionen erstellt"""
        if dim := self.check_dimensions():
            n, m = dim
        else:
            return None
        
        # check if there are values in der current matrix shown
        if self.check_if_values():
            if self.ignore:
                
                self.current_matrix.hide()
                id_ = self.current_matrix.id
                # Es wird die selbe ID genommen, da nur die dimensionen geändert werden
                self.current_matrix = MatrixWrapper(self, self.name_entry.get(), n, m, id_)
                self.current_matrix.show()
            else:
                raise Warning("there are still values in the grid, they will be deleted")
        else:
            self.create_new_matrix()
    
    def delete_matrix(self):
        """ vom 'X' Button wird die aktuelle Matrix gelöscht"""
        if not self.matrices:
            # Es gibt keine gespeicherte matrizen, es wird eine neue leere erstellt
            self.current_matrix.hide()
            self.create_new_matrix()
        else:
            if self.current_matrix in self.matrices:
                self.matrices.remove(self.current_matrix)
                del self.matrices_name[self.current_matrix.name]
            self.refresh_auswahl()
            self.show_matrix()
    
    def submit_matrix(self):
        """Vom 'save' Button werden die werte und der name der aktuellen Matrix gespeichert und Fehler überprüft.
        Dann werden die Werte in einer neuen Matric() Instanz gespeichert, die später genutzt werden kann"""
        self.show_error()
        self.current_matrix.save_values()
        name = self.name_entry.get()
        id_ = self.current_matrix.id
        
        if not name:
            self.show_error("No name")
        elif name in [m.name if id_ != m.id else "" for m in self.matrices]:
            self.show_error("Name is already taken")
        elif self.current_matrix not in self.matrices:
            self.matrices.append(self.current_matrix)
        
        self.current_matrix.name = name
        self.refresh_auswahl()
        self.matrices_name[name] = Matrix(self.current_matrix.get_values())
    
    def refresh_auswahl(self):
        """Die Anzeige links, die alle gespeicherten Matrizen anzeigt, wird aktualisiert"""
        for auswahl in self.matrix_auswahl.winfo_children():
            auswahl.destroy()
        for matrix in self.matrices:
            Button(self.matrix_auswahl, text=matrix.name, command=lambda m=matrix: self.show_matrix(m), width=2,
                   height=2).pack(side="left", anchor="n")
        Button(self.matrix_auswahl, text=" + ", command=self.show_matrix, width=2, height=2).pack(side="left",
                                                                                                  anchor="n")
    
    def create_new_matrix(self):
        """Eine neue Matrix wird mit den aktuellen dimensionen erstellt und angezeigt"""
        self.show_error()  # clear the error label
        
        if dim := self.check_dimensions():
            n, m = dim
            
            if cm := self.current_matrix:
                cm.hide()
            id_ = self.generate_new_id()
            self.current_matrix = MatrixWrapper(self, "", n, m, id_)
            self.current_matrix.show()
    
    def show_matrix(self, matrix=None):
        """Es wird die gegebene Matrix angezeigt (zb vom AnzeigeButton links) oder eine neue erstellt."""
        self.show_error()  # clear the error label
        
        if not matrix:
            self.create_new_matrix()
        else:
            self.current_matrix.hide()
            self.current_matrix = matrix
            self.current_matrix.show()
    
    def new_identity_matrix(self):
        """Eine Neue ID Matrix wird erstellt und eingefügt"""
        self.create_new_matrix()
        n, m = self.check_dimensions()
        if n == m:
            id_matrix = Matrix.Id(n)
            self.current_matrix.insert_values(id_matrix)
        else:
            self.show_error("dimensions are not symetric")
    
    def new_zero_matrix(self):
        self.create_new_matrix()
        n, m = self.check_dimensions()
        zero_matrix = Matrix.Zero(n, m)
        self.current_matrix.insert_values(zero_matrix)
    
    def new_random_matrix(self):
        self.create_new_matrix()
        n, m = self.check_dimensions()
        rnd_matrix = Matrix.Random(n, m)
        self.current_matrix.insert_values(rnd_matrix)
    
    def new_randomsym_matrix(self):
        self.create_new_matrix()
        n, m = self.check_dimensions()
        if n == m:
            rnds_matrix = Matrix.RandomSym(n)
            self.current_matrix.insert_values(rnds_matrix)
        else:
            self.show_error("dimensions are not symetric")
    
    def generate_new_id(self):
        """Jede Matrix hat eine ID um sie zu unterscheiden. Hier wird eine neue generiert."""
        n = 0
        all_ids = [m.id for m in self.matrices]
        while n in all_ids:
            n += 1
        return n
    
    def check_if_values(self):
        """Hier wird überprüft ob es einträge in der aktuellen matrix gibt."""
        return any([any(col) for col in self.current_matrix.get_values()])
    
    def show_error(self, error=""):
        """Der error wird unter dem matrix_edit_frame angezeigt"""
        self.error_label.config(text=error)
    
    def interprete_input(self, _=None):
        string = self.input_entry.get()
        if string in self.matrices_name:
            self.output_frame.config(text=str(self.matrices_name[string]))
    
    def show_help(self, force=None):
        """Der Hilfe für den MatrixFrame wird oben links angezeigt.
        Die Sichtbarkeit wird automatisch gewechselt, es sei denn, es wird ein bestimmter Zustand erzwungen"""
        self.help_show = not self.help_show if force is None else force
        
        if self.help_show:
            self.help_label.place(x=10, y=0)
        else:
            self.help_label.place_forget()
    
    def clear_frame(self):
        """Vom 'clear' button oben rechts wird alles vom AnalysisFrame gelöscht"""
        self.matrices = []
        self.matrices_name = {}
        self.refresh_auswahl()
        self.show_matrix()
        self.input_entry.delete(0, "end")
        self.output_frame.config(text="")
        self.show_help(False)


class CodeFrame(Frame):
    def __init__(self, container):
        super().__init__(container)
        pass


class MainScreen(Tk):
    def __init__(self):
        super().__init__()
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        if min_window:
            screen_width, screen_height = 700, 500
        
        self.geometry(f"{screen_width}x{screen_height}")
        self.title("WolframBeta")
        
        # 0: lightmode, 1: darkmode
        self.color_mode = 0
        
        # für die LaTeX schrift
        # matplotlib.use("TkAgg")
        plt.rcParams["mathtext.fontset"] = "cm"
        
        # Top Frame
        self.top_frame = Frame(self, bd=0, relief="solid")
        self.top_frame.place(y=0, relx=0.07, relheight=0.1, relwidth=0.93)
        
        self.top_frame.columnconfigure(0, weight=1)
        self.top_frame.columnconfigure(1, weight=1)
        self.top_frame.columnconfigure(2, weight=5)
        self.top_frame.columnconfigure(3, weight=1)
        self.top_frame.rowconfigure(0, weight=1)
        
        # Help Button
        self.help_button = Button(self.top_frame, text="?", command=self.show_help)
        self.help_button.grid(row=0, column=0)
        
        # Colormode Buttons
        self.lightmode_image = PhotoImage(file="../pictures/lm.png").subsample(4, 4)
        self.darkmode_image = PhotoImage(file="../pictures/dm.png").subsample(4, 4)
        self.cm_button = Button(self.top_frame, bd=0, highlightbackground="#707070",
                                image=self.darkmode_image, command=self.switch_color_mode)
        self.cm_button.grid(row=0, column=1)
        
        # Logo
        logo_file = "../pictures/logo_animation.gif"
        self.logo_frames = [PhotoImage(file=logo_file, format=f"gif -index {n}").subsample(5, 5) for n in range(20)]
        self.logo_index = 0
        self.logo_state = False
        
        self.logo = Label(self.top_frame, image=self.logo_frames[0])
        self.logo.grid(row=0, column=2, sticky="news")
        
        self.logo.bind("<Enter>", lambda _: self.move_logo(True))
        self.logo.bind("<Leave>", lambda _: self.move_logo(False))
        
        # Language Buttons
        self.lang_frame = Frame(self.top_frame)
        self.lang_frame.grid(row=0, column=3)
        
        self.de_flag = PhotoImage(file="../pictures/de.png").subsample(4, 4)
        self.de_button = Button(self.lang_frame, bd=0, highlightbackground="#707070",
                                image=self.de_flag, command=lambda: toggle_lang(0))
        self.de_button.grid(row=0, column=0, ipadx=3, ipady=3)
        
        self.fr_flag = PhotoImage(file="../pictures/fr.png").subsample(4, 4)
        self.fr_button = Button(self.lang_frame, bd=0, highlightbackground="#707070",
                                image=self.fr_flag, command=lambda: toggle_lang(1))
        self.fr_button.grid(row=0, column=1, padx=4, ipadx=3, ipady=3)
        
        self.gb_flag = PhotoImage(file="../pictures/gb.png").subsample(4, 4)
        self.gb_button = Button(self.lang_frame, bd=0, highlightbackground="#707070",
                                image=self.gb_flag, command=lambda: toggle_lang(2))
        self.gb_button.grid(row=0, column=2, ipadx=3, ipady=3)
        
        # Left frame
        self.left_frame = Frame(self, bg=lblue)
        self.left_frame.place(rely=0, x=0, relheight=1, relwidth=0.07)
        
        # self.sep = Label(self.left_frame, bg="white")
        # self.sep.place(x=0, rely=0.299, relwidth=1, height=3)
        #
        # self.selection_frame = Frame(self.left_frame, bg=lblue)
        # self.selection_frame.place(x=0, rely=0.305, relwidth=1, relheight=0.695)
        
        self.selection = 0
        self.buttons = self.selection_buttons(self.left_frame, "Rechner", "Analysis", "Matrix", "Code")
        
        # Bottom frame
        self.bottom_frame = Label(self)
        self.bottom_frame.place(relx=0.07, rely=0.9, relwidth=0.93, relheight=0.1)
        
        self.exit_button = Button(self.bottom_frame,
                                  text=["Schließen", "Fermer", "Exit"][lang],
                                  command=self.exit_screen,
                                  bd=0,
                                  highlightthickness=1.5,
                                  highlightbackground="red")
        self.exit_button.place(relx=0.85, rely=0.2, relwidth=0.1, relheight=0.6)
        
        self.elements = get_all_children(self)
        
        self.rechner_frame = self.analysis_frame = self.matrix_frame = self.code_frame = None
        self.current_frame = Frame(self)
        self.toggle_main_frame(default_frame)
        
        self.bind("<KP_Enter>", self.exit_screen)
    
    def move_logo(self, state):
        """Das logo wird animiert. Dazu müss alle 40ms ein neues frame des gifs angezeigt werden.
        Das muss manuell gemacht werden da tkinter das Anzeigen einer Animation nicht anders unterstützt."""
        
        self.logo_state = state
        self.logo.config(image=self.logo_frames[self.logo_index])
        self.logo_index += 1
        self.logo_index %= 20
        if self.logo_state:
            self.after(40, lambda: self.move_logo(self.logo_state))
    
    def toggle_main_frame(self, n):
        """ Von den blauen Buttons wird der jeweilige Frame angezeigt."""
        frame = (self.rechner_frame, self.analysis_frame, self.matrix_frame, self.code_frame)[n]
        
        if frame is None:
            # initiate frame objects
            if n == 0:
                self.rechner_frame = RechnerFrame(self)
                self.elements.extend(get_all_children(self.rechner_frame))
            elif n == 1:
                self.analysis_frame = AnalysisFrame(self)
                self.elements.extend(get_all_children(self.analysis_frame))
            elif n == 2:
                self.matrix_frame = MatrixFrame(self)
                self.elements.extend(get_all_children(self.matrix_frame))
            elif n == 3:
                self.code_frame = CodeFrame(self)
        
        frame = (self.rechner_frame, self.analysis_frame, self.matrix_frame, self.code_frame)[n]
        self.current_frame.place_forget()
        self.current_frame = frame
        self.current_frame.show_help(False)
        self.current_frame.place(rely=0.1, relx=0.07, relheight=0.8, relwidth=0.93)
        self.current_frame.focus_set()
    
    def switch_color_mode(self):
        """Von den Darkmode/lightmode button werden hier alle widgets durchgegangen und die Farbe angepasst."""
        self.color_mode = not self.color_mode
        self.cm_button.config(image=[self.lightmode_image, self.darkmode_image][not self.color_mode])
        
        for container in self.elements:
            if type(container) == Entry:
                container["fg"] = ["black", "white"][self.color_mode]
                container["bg"] = ["white", "#505050"][self.color_mode]
                # container["highlightbackground"] = [lgray, dgray][self.color_mode]
            elif type(container) == Button:
                container["fg"] = ["black", "#f0f0f0"][self.color_mode]
                container["bg"] = [lgray, dgray][self.color_mode]
                container["activeforeground"] = ["black", "#f0f0f0"][self.color_mode]
                container["activebackground"] = ["#ececec", "#4c4c4c"][self.color_mode]
                # container["highlightbackground"] = [lgray, dgray][self.color_mode]
            elif type(container) == Message:
                container["bg"] = [lgray, dgray][self.color_mode]
                container["fg"] = ["black", "white"][self.color_mode]
            else:
                container["bg"] = [lgray, dgray][self.color_mode]
        try:
            self.current_frame.switch_color()
        except:
            pass
    
    def selection_buttons(self, container, *names):
        """Erstellt die vier Buttons links."""
        buttons = []
        for i, name in enumerate(names):
            button = Button(container,
                            text=name,
                            bg=lblue,
                            fg="white",
                            highlightthickness=0,
                            bd=0,
                            activebackground=dblue,
                            activeforeground="white",
                            command=lambda n=i: self.select_main_frame(n))
            button.place(rely=i / 4, x=0, relwidth=1, relheight=1 / 4)
            buttons.append(button)
            
            white_bg = Label(container)
            white_bg.place(rely=i / 4 - 1 / 500, relx=0.05, height=1, relwidth=0.9)
        
        return buttons
    
    def select_main_frame(self, n):
        """Beim druck auf den knopf bleibt dessen Farbe dunkler, die anderen werden hell und das Frame wird angezeigt"""
        for i in range(4):
            self.buttons[i]["bg"] = lblue
        self.toggle_main_frame(n)
        self.buttons[n]["bg"] = dblue
    
    def show_help(self):
        """Vom Button '?' wird die Hilfe auf dem aktuellen Frame angezeigt."""
        self.current_frame.show_help()
    
    def exit_screen(self, event=None):
        """Vom 'Schließen' button unten rechts wird das hier aufgerufen"""
        self.destroy()


if __name__ == "__main__":
    app = MainScreen()
    app.mainloop()
