from tkinter import Tk, Frame, Label, Entry, Button, PhotoImage, StringVar, Radiobutton, Message, Scrollbar, Canvas

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

default_frame = 0
min_window = True

"""TODO:
AnalysisFrame
MatrixFrame
CodeFrame
ein paar kürzungen (kein 2x^3 = 2*3*x^2)
language überall änderbar
Farbe überall änderbar
angepasste größe der latex outputs
"""

algebra_help = ["""Hilfe für AlgebraFrame:

Elementare Funktionen:
* alle trigonometrischen Funktionen (sin, sinh,
arcsin, arcsinh, cos, cosh, arccos, arccosh,
tan, tanh, arctan, arctanh)
* exp(x) oder e^x
* pow(a, b) oder a^b
* sqrt(x)
* root(x, n)
* ln(x)
* log(x, n)
* C(a, b) oder aCb
* fact(n) oder n!

Funktionen:
* d/dx(f(x))
* Int(a, b, f(x), x)

Zahlentheorie:
* KgV(a, b) oder PDCM(a, b)
* ggT(a, b) oder PGCD(a, b)
* isprime(n)
* eratosthenes(n)
* prim_factors(n)
* partition(n)
"""]
analysis_help = ["""Hilfe für AnalysisFrame:
EntryLines:
Gebe einen Funktionsterm ein, es wird
automatisch ein Funktionsname generiert
und die Funktion auf dem Graph angezeigt.
Du kannst die Anzeige mit hilfe des
Knopfes ein/ausschalten, und die funktion
ändern.
Außerdem kannst du Differentialgleichungen
approximativ lösen lassen. Die gesuchte
Funktion wird auf dem Graph angezeigt

Compute Input:
gebe ein, was du berechnen willst:
* min(f) / max(f)
* f(x) = 0
* f'(x) / df(x)/dx
* f^n(a) / d^nf(a)/dx^n
* int(a, b, f(x))

"""]
matrix_help = [""]
code_help = [""]


def toggle_lang(language):
    global lang
    lang = language
    print(f"changed language to {lang}")


def format_error(error):
    # formatiert ein error code
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
    # range(), aber auch mit float abständen
    l, x = [], a
    while x < b:
        l.append(x)
        x += n
    return l


def check_and_clean(string):
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
    all_children = [top_frame] + top_frame.winfo_children()
    
    for item in all_children:
        all_children.extend(item.winfo_children())
        
    return all_children


class AlgebraFrame(Frame):
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
        Radiobutton(self.einstellungs_frame, text="Riemann", variable=self.method, value="riemann").grid(row=1, column=0, sticky="W", padx=10)
        Radiobutton(self.einstellungs_frame, text="Trapez", variable=self.method, value="trapez").grid(row=2, column=0, sticky="W", padx=10)
        Radiobutton(self.einstellungs_frame, text="Simpson", variable=self.method, value="simpson").grid(row=3, column=0, sticky="W", padx=10)

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
        
        # Help label
        self.help_label = Message(self, text=algebra_help[lang], relief="raised")
        self.help_show = False

        self.elements = get_all_children(self)

        self.input_entry.bind("<Return>", self.commit_input)
    
    def commit_input(self, event=None):
        self.rang = -1
        self.input = self.input_entry.get()
        if not self.input:
            return None
        if not (self.listed_memory and self.input == self.listed_memory[-1]):
            self.listed_memory.append(self.input)
        
        if self.input in self.memory:
            # Wenn das Eingegebene schon berechnet wurde, dann soll das gespeicherte Ergebnis angezeigt werden
            self.show_answer(self.memory[self.input])
        else:
            answers = self.interprete(self.input)
            if not answers: return None
            self.show_answer(answers)
            self.memory[self.input] = [*answers]
        
    def interprete(self, user_input):
        
        user_input = check_and_clean(user_input)
        if type(user_input) == SyntaxError:
            self.show_error(format_error(user_input))
            return None
        
        self.show_einstellungen() if "Int" in user_input else self.hide_einstellungen()
        
        try:
            if "=" in user_input:
                # Gleichheit überprüfen
                n = user_input.find("=")
                lp = parse(user_input[:n])
                rp = user_input[n + 1:]
                if "=" in rp[1:]:
                    self.show_error(f"Invalid input")
                    return None
                input_latex = f"{write_latex(lp)} == {write_latex(parse(rp))}"
                print(input_latex)
                output_latex = eval("write(lp) == write(parse(rp))")
            
            else:
                # sonstige Berechnungen
                input_latex = write_latex(parse(user_input))
                output_tree = parse(user_input, simp=True)
                try:
                    output_latex = eval(write(output_tree))
                except:
                    output_latex = write_latex(output_tree, simp=True)
        except Exception as error:
            self.show_error(format_error(error))
            return None
        
        return input_latex, output_latex
    
    def show_answer(self, answers=None):
        if not answers:
            # Figure wird nur wegen colormodechange refresht (keine answers gegeben)
            userinput_latex, output_latex = self.answers
        else:
            userinput_latex, output_latex = answers
            self.answers = answers
            
        self.show_error("")
        self.io_figure.clear()
        self.io_figure.set_facecolor(["white", "#505050"][app.color_mode])
        
        text = r"${}  =  {}$".format(userinput_latex, output_latex)
        length = len(text)
        size = int(2000 / (length + 60) + 5)
        # print(f"INPUT: {size = }, {length = }")
        if text != "$  =  $":
            self.io_figure.text(0.5, 0.5, text, fontsize=size,
                                color=["black", "white"][app.color_mode], va="center", ha="center")
        self.io_canvas.draw()
    
    def show_error(self, error):
        self.error_label.config(text=error)
        if error: print(f"Error: {error}")
    
    def show_einstellungen(self):
        self.input_entry.place(relwidth=0.55)
        self.einstellungs_frame.place(relx=0.65, y=0, relwidth=0.25, relheight=0.2)
    
    def hide_einstellungen(self):
        self.input_entry.place(relwidth=0.8)
        self.einstellungs_frame.place_forget()
    
    def refresh_integration(self, method):
        # Bei änderung der integrationsmethode (Riemann/Trapez/Simpson) wird der input erneut berechnet
        set_default_integration_method(method)
        self.show_answer(self.interprete(self.input_entry.get()))
        
    def show_last(self, dir):
        # Im entry wird bei Pfeil hoch/runter das letzte/nächste eingegebene angezeigt
        if not self.listed_memory: pass
        self.rang += dir*1 if (not self.rang == dir*len(self.listed_memory)) and (not self.rang == -dir) else 0
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, self.listed_memory[self.rang])
        
    def switch_color(self):
        # refresh the canvas
        self.show_answer()
    
    def show_help(self, force=None):
        #
        self.help_show = not self.help_show if force is None else force
        if self.help_show:
            self.help_label.place(x=10, y=0)
        else:
            self.help_label.place_forget()


class EntryLine(Frame):
    # einzelne Zeile im AnalysisFrame
    def __init__(self, container, super_):
        super().__init__(container, height=40, bd=1, relief="groove")
        self.focus_set()
        
        self.fr = Frame(self, height=30)
        self.fr.pack(side="top", expand=1, fill="both")
        self.fr.focus_set()
        
        self.bttn = Button(self.fr, takefocus=0, bd=0, bg="white", highlightthickness=0,
                           image=super_.gray_ring, command=lambda: super_.toggle_visibility(self))
        self.bttn.pack(side="left", fill="both")
        
        self.pfeil = Label(self.fr, takefocus=0, text=" > ", bg="white", fg="black", height=2)
        self.pfeil.pack(side="left", fill="both")
        
        self.entry = Entry(self.fr, takefocus=1, bd=0, highlightthickness=0, fg="black", bg="white")
        self.entry.pack(side="left", fill="both", expand=True)
        self.entry.focus_set()
        
        self.error_label = Label(self, takefocus=0, height=0, fg="red")
        # self.error_label.pack(side="bottom", fill="x", expand=0)
        
        self.entry.bind("<Return>", lambda _: super_.enter_pressed(self))
        self.entry.bind("<BackSpace>", lambda _: super_.destroy_line(self) if not self.entry.get() else 0)
        
    def show_error(self, error_message):
        self.error_label.config(text=error_message)
        self.error_label.pack(side="bottom", fill="x", expand=0)
    
    def hide_error(self):
        self.error_label.pack_forget()


class FunctionWrapper(Function):
    def __init__(self, string, variable="x", name=None, color=None, isvisible=True, entry_index=None):
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
        
        self.scrolled_frame = Frame(self.scroll_canvas, bg="blue")
        self.scrolled_frame.focus_set()
        self.canvas_window = self.scroll_canvas.create_window(0, 0, window=self.scrolled_frame, anchor="nw")
        self.scrolled_frame.bind("<Configure>", self.configure_canvas)
        
        self.gray_ring = PhotoImage(file="../pictures/Rings/gray_ring.png").subsample(3, 3)
        self.red_ring = PhotoImage(file="../pictures/Rings/red_ring.png").subsample(3, 3)

        self.lines = []
        
        self.line = EntryLine(self.scrolled_frame, self)
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
        
        self.figure = Figure(facecolor=dgray)
        self.subplot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        # self.subplot.set_facecolor("red")
        # self.figure.set_facecolor("blue")
        self.subplot.grid(True)
        
        # Help Label
        self.help_label = Message(self, text=analysis_help[lang], relief="raised")
        self.help_show = False

        self.functions = {}  # alle gespeicherte funktionen
        self.dgl = {}
        self.funcnames_order = ["f", "g", "h", "i", "j", "k", "u", "v", "p", "s", "l"]
        self.all_colors = ["r", "g", "b", "c", "m", "y", "k"]
    
    def configure_canvas(self, event):
        width = self.scroll_canvas.winfo_width()
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox(self.canvas_window))
        self.scroll_canvas.itemconfig(self.canvas_window, width=width)
    
    def add_new_func(self):
        line = self.get_first_empty_line()
        index = self.lines.index(line)
        name = self.generate_func_name()
        color = self.all_colors[index % 7]
        line.entry.insert(0, f"{name}(x) = ")
        self.functions[index] = FunctionWrapper("", "x", name, color, False, index)
        line.entry.focus_set()
    
    def add_new_dgl(self):
        line = self.get_first_empty_line()
        line.entry.insert(0, "y' = ")
        line.entry.focus_set()
    
    def get_first_empty_line(self):
        for line in self.lines:
            if not line.entry.get():
                return line
        return self.create_new_line()
        
    def create_new_line(self):
        self.new_line = EntryLine(self.scrolled_frame, self)
        self.new_line.pack(fill="x")
        self.new_line.entry.focus_set()
        self.lines.append(self.new_line)
        return self.new_line
    
    def enter_pressed(self, obj):
        obj.hide_error()
        
        index = self.lines.index(obj)
        if not self.interprete_function(obj, index):
            # Wenn es einen Fehler im input gibt, wird nicht zur nächsten Zeile gegangen
            return None
        
        if self.check_line(index + 1):
            self.lines[index + 1].entry.focus_set()

        elif obj.entry.get():
            self.create_new_line()

    def interprete_function(self, obj, n):
        entry = obj.entry
        string = entry.get()
        
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
                obj.bttn.config(image=self.red_ring)
                return True
            except Exception as error:
                self.show_error(format_error(error), n)
                return False
    
        elif "(x)=" in string[:string.index("=") + 1]:
            # eigener funktionsname gegeben oder ältere Funktion geändert
        
            func = string[string.index("=") + 1:]
            funcname = string[:string.index("(x)=")]
            if not func:
                self.show_error("Error: no input", n)
                return False
        
            if n in self.functions:
                previous_function = self.functions[n]
                # es ist nur eine Änderung einer alten schon eingegebenen Funktion
                color = previous_function.color
                isvisible = previous_function.isvisible
            else:
                color = self.all_colors[n % 7]
                isvisible = True
        
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
        n = 0
        while self.funcnames_order[n] in [f.name for f in self.functions.values()]:
            n_max = len(self.funcnames_order)
            n += 1
            if n == n_max - 1:
                # Wenn die namen aufgebraucht sind, geht es mit f_1, g_1, ... , f_2, g_2 ... weiter
                self.funcnames_order.append(f"{self.funcnames_order[(n + 1) % 11]}_{(n + 1) // 11}")
                
        return self.funcnames_order[n]
    
    def graph(self):
        # Default range:
        I_max = rrange(-5, 5, 0.01)
        
        self.subplot.clear()
        for function in self.functions.values():
            if function.isvisible:
                I, J = [], []
                for x in I_max:
                    try:
                        J.append(function(x))
                        I.append(x)
                    except Exception as e:
                        # wenn x nicht im definitionsbereich der Funktion liegt, gibts nen ValueError (wird ignoriert)
                        if type(e) is not ValueError:
                            raise e
                self.subplot.plot(I, J, color=function.color, label=f"y = {function.name}(x)")
                
        # self.subplot.spines["left"].set_position("center")
        # self.subplot.spines["bottom"].set_position("center")
        # self.subplot.spines["top"].set_color(None)
        # self.subplot.spines["right"].set_color(None)
        self.subplot.grid(True)
        
        self.subplot.legend(loc="upper left")
        self.canvas.draw()
    
    def toggle_visibility(self, obj):
        index = self.lines.index(obj)
        if index not in self.functions:
            return None
        isvisible = self.functions[index].isvisible
        self.functions[index].isvisible = not isvisible
        if isvisible:
            obj.bttn.config(image=self.gray_ring)
        else:
            obj.bttn.config(image=self.red_ring)
        self.graph()
    
    def destroy_line(self, obj):
        index = self.lines.index(obj)
        if self.check_line(index + 1) or self.check_line(index - 1) and not self.lines[index - 1].entry.get():
            self.lines[index].destroy()
            self.lines.pop(index)
            self.lines[-1].entry.focus_set()

    def check_line(self, index):
        # Überprüft, ob es eine nächste Zeile gibt
        try:
            _ = self.lines[index]
            return True
        except IndexError:
            return False

    def show_error(self, error, n=None):
        if n is not None:
            # Fehler in der n'ten EntryLine
            self.lines[n].show_error(error)
        else:
            # Fehler in dem computeentry
            self.compute_error_label.config(text=error)
        if error: print(f"Error({n}): {error}")
    
    def interprete_input(self, _=None):
        """
        * min(f) / max(f)
        * f(x) = 0 / nullstelle(f)
        * f'(x) / df(x)/dx
        * f^n(a) / d^nf(a)/dx^n
        * int(a, b, f(x))
        """
        string = self.compute_entry.get()
        
        if not string:
            return None
        string = string.replace(" ", "").replace("**", "^")
        string = string.replace("²", "^2").replace("³", "^3")
        string = string.replace("pi", "π")
        for chr in string:
            if chr not in ".,+-*/()_^`'! π=3" + '"' + NUMBERS + ALPHABET:
                self.show_error(f"Invalid input: '{chr}'")
                return None
        try:
            if "=" in string:
                pass
            else:
                
                input_latex = write_latex(parse(string))
                output_tree = parse(string, simp=True)
                try:
                    for func in self.functions.values():
                        locals()[func.name] = func
                    print(locals())
                    output_latex = eval(write(output_tree))
                except Exception as e:
                    print(f"couldnt eval {write(output_tree)}, {e}")
                    output_latex = write_latex(output_tree, simp=True)
        except Exception as error:
            self.show_error(format_error(error))
            return None
        
        self.show_answer(input_latex, output_latex)
        
    def show_answer(self, input_latex, output_latex):
        self.show_error("")
        text = rf"${input_latex} = {output_latex}$"
        self.io_figure.clear()
        self.io_figure.text(0.5, 0.5, text, size=int(100/(len(text)+50)+5), va="center", ha="center")
        self.io_canvas.draw()
        
    def show_help(self, force=None):
        self.help_show = not self.help_show if force is None else force
        
        if self.help_show:
            self.help_label.place(x=10, y=0)
        else:
            self.help_label.place_forget()
    
    def switch_color(self):
        pass


class EntryTable(Frame):
    def __init__(self, container, rows, columns):
        super().__init__(container)
        
        self.n, self.m = rows, columns
        
        self.entries = []
        self.values = []
        for m in range(self.m):
            self.columnconfigure(m, weight=1)
            column = []
            for n in range(self.n):
                self.rowconfigure(n, weight=1)
                entry = Entry(container, width=3)
                entry.grid(row=n, column=m)
                column.append(entry)
            self.entries.append(column)
            
    def get_values(self):
        self.values = [[entry.get() for entry in column] for column in self.entries]
        return self.values
    
    def insert_values(self, values):
        if len(self.entries) != len(values):
            raise TypeError("not gleiche column anzahl beim einfügen")
        for m in range(len(self.entries)):
            for n in range(m):
                entry = self.entries[m][n]
                value = values[m][n]
                entry.delete(0, "end")
                entry.insert(0, value)


class MatrixWrapper:
    def __init__(self, super_frame, name, rows, columns):
        
        self.name = name
        self.values_frame = Frame(super_frame.edit_frame)
        self.name_entry = super_frame.name_entry
        
        self.values = []
        self.entries = self.entry_gitter(self.values_frame, rows, columns)
    
    @staticmethod
    def entry_gitter(container, rows, columns):
        entries = []
        for n in range(rows):
            container.rowconfigure(n, weight=1)
            row = []
            for m in range(columns):
                container.columnconfigure(m, weight=1)
                entry = Entry(container, width=3)
                entry.grid(row=n, column=m)
                row.append(entry)
            entries.append(row)
        return entries
    
    def save_values(self):
        self.values = [[entry.get() if entry.get() else 0 for entry in row] for row in self.entries]
    
    def get_values(self):
        self.save_values()
        return self.values
    
    def show(self):
        self.values_frame.pack(fill="both", expand=True)
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, self.name)
        
    def hide(self):
        self.values_frame.pack_forget()
        self.name_entry.delete(0, "end")


class MatrixFrame(Frame):
    def __init__(self, container):
        super().__init__(container)
        
        self.matrices = []
        self.current_matrix = None
        
        # Auswahl Frame
        self.matrix_auswahl = Frame(self, bd=1, relief="raised")
        self.matrix_auswahl.place(relx=0.1, rely=0.0, relwidth=0.3, relheight=0.33)
        Button(self.matrix_auswahl, text=" + ", command=self.show_matrix, width=2, height=2).pack(side="left")
        
        # Edit Frame
        self.matrix_frame = Frame(self, bd=1, relief="raised")
        self.matrix_frame.place(relx=0.45, rely=0.0, relwidth=0.45, relheight=0.5)
        
        self.matrix_frame.rowconfigure(0, weight=1)
        self.matrix_frame.rowconfigure(1, weight=5)
        self.matrix_frame.rowconfigure(2, weight=1)
        self.matrix_frame.columnconfigure(0, weight=1)
        self.matrix_frame.columnconfigure(1, weight=5)
        self.matrix_frame.columnconfigure(2, weight=1)
        
        self.name_frame = Frame(self.matrix_frame)
        self.name_frame.grid(row=1, column=0, sticky="e")
        
        self.name_entry = Entry(self.name_frame, width=2, justify="center")
        self.name_entry.pack(side="left")
        Label(self.name_frame, text=" = ").pack(side="right")
        
        self.edit_frame = Frame(self.matrix_frame, bd=1, relief="raised")
        self.edit_frame.grid(row=1, column=1, sticky="news")
        
        self.vorschlag_frame = Frame(self.matrix_frame)
        self.vorschlag_frame.grid(row=2, column=1)
        
        Button(self.vorschlag_frame, text="ID", command=None).pack(side="left")
        Button(self.vorschlag_frame, text="Zero", command=None).pack(side="left")
        Button(self.vorschlag_frame, text="Random", command=None).pack(side="left")
        Button(self.vorschlag_frame, text="RandomSym", command=None).pack(side="left")
        
        Button(self.matrix_frame, text="Delete Matrix", command=self.delete_matrix).grid(row=0, column=2)
        Button(self.matrix_frame, text="Save", command=self.submit_matrix).grid(row=2, column=2)
        
        self.error_label = Label(self, fg="red")
        self.error_label.place(relx=0.45, rely=0.5, relheight=0.05, relwidth=0.45)
        
        # Entry Frame
        self.entry_frame = Frame(self, bd=1, relief="raised")
        self.entry_frame.place(relx=0.1, rely=0.4, relwidth=0.3, relheight=0.1)
        
        # Output Frame
        self.output_frame = Frame(self, bd=1, relief="raised")
        self.output_frame.place(relx=0.1, rely=0.55, relwidth=0.8, relheight=0.45)

        # Help Label
        self.help_label = Message(self, text=algebra_help[lang], relief="raised")
        self.help_show = False
        
        self.show_matrix()
    
    def delete_matrix(self):
        self.matrices.remove(self.current_matrix)
        self.refresh_auswahl()
        self.current_matrix.hide()
        # m = self.current_matrix
        # del m
        self.show_matrix()

    def submit_matrix(self):
        self.current_matrix.save_values()
        name = self.name_entry.get()
        if not name:
            self.show_error("No name")
        elif name in [m.name for m in self.matrices]:
            self.show_error("Name is already taken")
        elif self.current_matrix not in self.matrices:
            self.current_matrix.name = name
            self.matrices.append(self.current_matrix)
            self.refresh_auswahl()
            
    def refresh_auswahl(self):
        for auswahl in self.matrix_auswahl.winfo_children():
            auswahl.destroy()
        for matrix in self.matrices:
            Button(self.matrix_auswahl, text=matrix.name, command=lambda m=matrix: self.show_matrix(m), width=2, height=2).pack(side="left")
        Button(self.matrix_auswahl, text=" + ", command=self.show_matrix, width=2, height=2).pack(side="left")
        
    def show_error(self, error):
        self.error_label.config(text=error)
        
    def show_matrix(self, matrix=None):
        if not matrix:
            if self.current_matrix:
                self.current_matrix.hide()
            self.current_matrix = MatrixWrapper(self, "", 3, 3)
            self.current_matrix.show()
        else:
            self.current_matrix.hide()
            self.current_matrix = matrix
            self.current_matrix.show()

    def show_help(self, force=None):
        self.help_show = not self.help_show if force is None else force
    
        if self.help_show:
            self.help_label.place(x=10, y=0)
        else:
            self.help_label.place_forget()
        

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
        logo_file = "../pictures/alpha_anim.gif"
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
        self.buttons = self.selection_buttons(self.left_frame, "Algebra", "Analysis", "Matrix", "Code")
        
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
        
        self.algebra_frame = self.analysis_frame = self.matrix_frame = self.code_frame = None
        self.current_frame = Frame(self)
        self.toggle_main_frame(default_frame)
        
        self.bind("<KP_Enter>", self.exit_screen)
        
    def move_logo(self, state):
        self.logo_state = state
        self.logo.config(image=self.logo_frames[self.logo_index])
        self.logo_index += 1
        self.logo_index %= 20
        if self.logo_state:
            self.after(40, lambda:self.move_logo(self.logo_state))
    
    def toggle_main_frame(self, n):
        frame = (self.algebra_frame, self.analysis_frame, self.matrix_frame, self.code_frame)[n]
        
        if frame is None:
            # initiate frame objects
            if n == 0:
                self.algebra_frame = AlgebraFrame(self)
                self.elements.extend(get_all_children(self.algebra_frame))
            elif n == 1:
                self.analysis_frame = AnalysisFrame(self)
                self.elements.extend(get_all_children(self.analysis_frame))
            elif n == 2:
                self.matrix_frame = MatrixFrame(self)
                self.elements.extend(get_all_children(self.matrix_frame))
            elif n == 3:
                self.code_frame = CodeFrame(self)
        
        frame = (self.algebra_frame, self.analysis_frame, self.matrix_frame, self.code_frame)[n]
        self.current_frame.place_forget()
        self.current_frame = frame
        self.current_frame.show_help(False)
        self.current_frame.place(rely=0.1, relx=0.07, relheight=0.8, relwidth=0.93)
        self.current_frame.focus_set()
    
    def switch_color_mode(self):
        self.color_mode = not self.color_mode
        self.cm_button.config(image=[self.lightmode_image, self.darkmode_image][not self.color_mode])
        
        for container in self.elements:
            if type(container) == Entry:
                container["fg"] = ["black", "white"][self.color_mode]
                container["bg"] = ["white", "#505050"][self.color_mode]
                container["highlightbackground"] = [lgray, dgray][self.color_mode]
            elif type(container) == Button:
                container["fg"] = ["black", "#f0f0f0"][self.color_mode]
                container["bg"] = [lgray, dgray][self.color_mode]
                container["activeforeground"] = ["black", "#f0f0f0"][self.color_mode]
                container["activebackground"] = ["#ececec", "#4c4c4c"][self.color_mode]
                container["highlightbackground"] = [lgray, dgray][self.color_mode]
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
        # für die 4 Buttons links
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
        # die Farbe des jeweiligen buttons bleibt dunkler und das frame wird angezeigt
        for i in range(4):
            self.buttons[i]["bg"] = lblue
        self.toggle_main_frame(n)
        self.buttons[n]["bg"] = dblue
    
    def show_help(self):
        self.current_frame.show_help()
    
    def exit_screen(self, event=None):
        self.destroy()
        # print(f"{self.algebra_frame.memory = }")


if __name__ == "__main__":
    app = MainScreen()
    app.mainloop()
