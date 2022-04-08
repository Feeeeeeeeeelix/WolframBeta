from tkinter import Tk, Frame, Label, Entry, Button, PhotoImage, StringVar, Radiobutton

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from FunctionClass import *
from functions import *

lblue = "#1e3799"
dblue = "#001B81"
lgray = "#d9d9d9"
dgray = "#404040"

# Deutsch: 0, Francais: 1, English: 2
lang = 0

default_frame = 1
min_window = True

"""todo:
Analysis: graph implementieren
matrizen implementieren
ein paar kürzungen (kein 2x^3 = 2*3*x^2)
language überall änderbar
angepasste größe der latex outputs
Katalog aller Funktionen
"""


def toggle_lang(language):
    global lang
    lang = language
    print(f"changed language to {lang}")


def raise_error(error):
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
        # nur costum text gegeben
        return error


class AlgebraFrame(Frame):
    def __init__(self, container):
        super().__init__(container)
        
        self.memory = {}
        self.input = ""
        
        self.io_frame = Frame(self)
        self.io_frame.place(relx=0.2, rely=0.1, relwidth=0.6, relheight=0.8)
        self.io_frame.focus_set()
        
        # Entry for user input
        self.input_entry = Entry(self.io_frame, bd=2, relief="solid", highlightthickness=0, justify="center")
        self.input_entry.place(relx=0.1, rely=0, relwidth=0.8, relheight=0.2)
        self.input_entry.focus_set()
        
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
        
        self.elements = [self, self.io_frame, self.input_entry,
                         self.einstellungs_frame, self.error_label,
                         self.enter_button, self.latex_io]
        
        self.input_entry.bind("<Return>", self.commit_input)
    
    def commit_input(self, event=None):
        self.input = self.input_entry.get()
        if not self.input:
            return None
        if self.input in self.memory:
            # Wenn das Eingegebene schon berechnet wurde, dann soll das gespeicherte Ergebnis angezeigt werden
            self.show_answer(self.memory[self.input])
        else:
            answers = self.interprete(self.input)
            if not answers: return None
            self.show_answer(answers)
            self.memory[self.input] = [*answers]
    
    def interprete(self, user_input):
        user_input = user_input.replace(" ", "").replace("**", "^")
        user_input = user_input.replace("²", "^2").replace("³", "^3")
        user_input = user_input.replace("pi", "π")
        for chr in user_input:
            if chr not in ".,+-*/()_^`'! π=3" + '"' + NUMBERS + ALPHABET:
                self.show_error(f"Invalid input: '{chr}'")
                return None
        
        self.show_einstellungen() if "Int" in user_input else self.hide_einstellungen()
        
        try:
            if "=" in user_input:
                # Gleichheit überprüfen
                n = user_input.find("=")
                lp = parse_ws(user_input[:n])
                rp = user_input[n + 1:]
                if "=" in rp[1:]:
                    self.show_error(f"Invalid input")
                    return None
                input_latex = f"{write_latex_ws(lp)} == {write_latex_ws(parse_ws(rp))}"
                print(input_latex)
                output_latex = eval("write(lp) == write(parse(rp))")
            
            else:
                # sonstige Berechnungen
                input_latex = write_latex_ws(parse_ws(user_input))
                output_latex = parse(user_input, ableiten=True)
                try:
                    output_latex = eval(write(output_latex))
                except:
                    output_latex = write_latex(output_latex)
        except Exception as error:
            self.show_error(raise_error(error))
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
    
    def switch_color(self):
        # refresh the canvas
        self.show_answer()


class EntryLine(Frame):
    # einzelne Zeile im AnalysisFrame
    def __init__(self, container, super_):
        super().__init__(container, height=40, bg="red", bd=1, relief="groove")
        
        self.fr = Frame(self, height=30)
        self.fr.pack(side="top", expand=1, fill="both")
        
        self.bttn = Button(self.fr, takefocus=0, bd=0, bg="white", highlightthickness=0)
        self.bttn.pack(side="left", fill="both")
        
        self.pfeil = Label(self.fr, takefocus=0, text=" > ", bg="white", fg="black", height=2)
        self.pfeil.pack(side="left", fill="both")
        
        self.entry = Entry(self.fr, takefocus=1, bd=0, highlightthickness=0, fg="black", bg="white")
        self.entry.pack(side="left", fill="both", expand=True)
        self.entry.focus_set()
        
        self.error_label = Label(self, takefocus=0, height=0, fg="red")
        self.error_label.pack(side="bottom", fill="x", expand=0)
        
        self.entry.bind("<Return>", lambda _: super_.enter_pressed(self))
        self.entry.bind("<BackSpace>", lambda _: super_.destroy_line(self) if not self.entry.get() else 0)


class AnalysisFrame(Frame):
    def __init__(self, container):
        super().__init__(container)
        
        # Entry lines Frame
        self.entry_lines_frame = Frame(self, bg="white", bd=1, relief="solid")
        self.entry_lines_frame.place(relx=0.1, rely=0.05, relheight=0.4, relwidth=0.35)
        self.entry_lines_frame.focus_set()
        
        self.lines = []
        
        self.line = EntryLine(self.entry_lines_frame, self)
        self.line.pack(fill="x")
        self.line.entry.focus_set()
        self.lines.append(self.line)
        
        # single entry Frame
        
        self.entry_frame = Frame(self, bd=1, relief="raised")
        self.entry_frame.place(relx=0.1, rely=0.55, relwidth=0.35, relheight=0.1)
        
        # latex output frame
        
        self.output_frame = Frame(self, bd=1, relief="raised")
        self.output_frame.place(relx=0.1, rely=0.7, relwidth=0.35, relheight=0.25)
        
        # Canvas Frame
        self.canvas_frame = Frame(self)
        self.canvas_frame.place(relx=0.5, rely=0.05, relheight=0.9, relwidth=0.45)
        
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.subplot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def enter_pressed(self, obj):
        self.submit_input(obj.entry.get())
        
        index = self.lines.index(obj)
        
        if self.check_line(index + 1):
            self.lines[index + 1].entry.focus_set()

        else:
            self.new_line = EntryLine(self.entry_lines_frame, self)
            self.new_line.pack(fill="x")
            self.new_line.entry.focus_set()
            self.lines.append(self.new_line)
    
    def destroy_line(self, obj):
        index = self.lines.index(obj)
        if self.check_line(index + 1):
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
        
    def submit_input(self, user_input):
        def rrange(a, b, n=1):
            l, x = [], a
            while x < b:
                l.append(x)
                x += n
            return l
    
        self.x = rrange(0, 40, 0.1)
        self.y = [exp(-x / 10) * sin(x) for x in self.x]
    
        self.subplot.plot(self.x, self.y)
        
    def switch_color(self):
        pass

    def interprete(self, user_input, n):
        user_input = user_input.replace(" ", "").replace("**", "^")
        user_input = user_input.replace("²", "^2").replace("³", "^3")
        user_input = user_input.replace("pi", "π")
        for chr in user_input:
            if chr not in ".,+-*/()_^`'! π=3" + '"' + NUMBERS + ALPHABET:
                self.show_error(f"Invalid input: '{chr}'", n)
                return None
    
        try:
            pass
        except Exception as error:
            self.show_error(raise_error(error), n)
            return None
    
        return

    def show_error(self, error, n):
        self.lines[n].error_label.config(text=error)
        if error: print(f"Error: {error}")


class MatrixInterface:
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
                entry = Entry(container, width=2)
                entry.grid(row=n, column=m)
                row.append(entry)
            entries.append(row)
        return entries
    
    def save_values(self):
        self.values = [[entry.get() for entry in row] for row in self.entries]
    
    def get_values(self):
        self.save_values()
        return self.values
    
    def show(self):
        self.values_frame.pack(fill="both", expand=True)
        self.name_entry.delete(0)
        self.name_entry.insert(0, self.name)
        
    def hide(self):
        self.values_frame.pack_forget()
        self.name_entry.delete(0)


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
        Button(self.vorschlag_frame, text="Random", command=None).pack(side="left")
        Button(self.vorschlag_frame, text="RandomSym", command=None).pack(side="left")
        
        Button(self.matrix_frame, text="Delete Matrix", command=self.delete_matrix).grid(row=0, column=2)
        Button(self.matrix_frame, text="Save", command=self.submit_matrix).grid(row=2, column=2)
        
        self.error_label = Label(self, fg="red", text="jgnelvjerijbvi")
        self.error_label.place(relx=0.45, rely=0.5, relheight=0.05, relwidth=0.45)
        
        # Entry Frame
        self.entry_frame = Frame(self, bd=1, relief="raised")
        self.entry_frame.place(relx=0.1, rely=0.4, relwidth=0.3, relheight=0.1)
        
        # Output Frame
        self.output_frame = Frame(self, bd=1, relief="raised")
        self.output_frame.place(relx=0.1, rely=0.55, relwidth=0.8, relheight=0.45)
        
        self.show_matrix()
    
    def delete_matrix(self):
        self.matrices.remove(self.current_matrix)
        self.refresh_auswahl()
        self.current_matrix.hide()
        m = self.current_matrix
        del m
        self.show_matrix()

    def submit_matrix(self):
        self.current_matrix.save_values()
        name = self.name_entry.get()
        if not name:
            self.show_error("No name")
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
            self.current_matrix = MatrixInterface(self, "", 3, 3)
            self.current_matrix.show()
        else:
            self.current_matrix.hide()
            self.current_matrix = matrix
            self.current_matrix.show()
        

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
        self.top_frame.place(y=0, x=0, relheight=0.1, relwidth=1)
        
        self.top_frame.columnconfigure(0, weight=1)
        self.top_frame.columnconfigure(1, weight=5)
        self.top_frame.columnconfigure(2, weight=1)
        self.top_frame.rowconfigure(0, weight=1)
        
        # Colormode Buttons
        # self.cm_frame = Frame(self.top_frame)
        # self.cm_frame.grid(row=0, column=0)
        
        # self.lm_button = Button(self.cm_frame, bd=0, highlightbackground="#707070",
        #                         image=self.lightmode_image, command=self.switch_color_mode)
        # self.lm_button.grid(row=0, column=0, ipadx=3, ipady=3)
        
        self.lightmode_image = PhotoImage(file="../pictures/lm.png").subsample(4, 4)
        self.darkmode_image = PhotoImage(file="../pictures/dm.png").subsample(4, 4)
        self.cm_button = Button(self.top_frame, bd=0, highlightbackground="#707070",
                                image=self.darkmode_image, command=self.switch_color_mode)
        self.cm_button.grid(row=0, column=0)
        
        # Logo
        self.logo_pic = PhotoImage(file="../pictures/logo.png").subsample(2, 2)
        self.logo = Label(self.top_frame, image=self.logo_pic)
        self.logo.grid(row=0, column=1, sticky="news")
        
        # Language Buttons
        self.lang_frame = Frame(self.top_frame)
        self.lang_frame.grid(row=0, column=2)
        
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
        self.left_frame.place(rely=0.1, x=0, relheight=0.9, relwidth=0.07)
        
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
        
        self.elements = [self.top_frame, self.logo, self.cm_button,
                         self.lang_frame, self.de_button, self.fr_button, self.gb_button,
                         self.bottom_frame, self.exit_button]
        
        self.algebra_frame = self.analysis_frame = self.matrix_frame = self.code_frame = None
        self.current_frame = Frame(self)
        self.toggle_main_frame(default_frame)
        
        self.bind("<KP_Enter>", self.exit_screen)
    
    def toggle_main_frame(self, n):
        frame = (self.algebra_frame, self.analysis_frame, self.matrix_frame, self.code_frame)[n]
        
        if frame is None:
            # initiate frame objects
            if n == 0:
                self.algebra_frame = AlgebraFrame(self)
                self.algebra_frame.focus_set()
                self.elements += self.algebra_frame.elements
            elif n == 1:
                self.analysis_frame = AnalysisFrame(self)
            elif n == 2:
                self.matrix_frame = MatrixFrame(self)
            elif n == 3:
                self.code_frame = CodeFrame(self)
        
        frame = (self.algebra_frame, self.analysis_frame, self.matrix_frame, self.code_frame)[n]
        self.current_frame.place_forget()
        self.current_frame = frame
        self.current_frame.place(rely=0.1, relx=0.07, relheight=0.8, relwidth=0.93)
        self.current_frame.focus_set()
    
    def switch_color_mode(self):
        self.color_mode = not self.color_mode
        self.cm_button.config(image=[self.lightmode_image, self.darkmode_image][not self.color_mode])
        
        for container in self.elements:
            if type(container) == Entry:
                container["fg"] = ["black", "white"][self.color_mode]
                container["bg"] = ["white", "#505050"][self.color_mode]
            elif type(container) == Button:
                container["bg"] = [lgray, dgray][self.color_mode]
                container["activebackground"] = ["#ececec", "#4c4c4c"][self.color_mode]
                container["activeforeground"] = ["black", "#f0f0f0"][self.color_mode]
                container["fg"] = ["black", "#f0f0f0"][self.color_mode]
            else:
                container["bg"] = [lgray, dgray][self.color_mode]
                
        self.current_frame.switch_color()
    
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
    
    def exit_screen(self, event=None):
        self.destroy()
        # print(f"{self.algebra_frame.memory = }")


if __name__ == "__main__":
    app = MainScreen()
    app.mainloop()
