from tkinter import Tk, Frame, Label, Entry, Button, PhotoImage, OptionMenu, StringVar, Radiobutton

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from FunctionClass import Function, write_latex, NUMBERS, ALPHABET, flint
from analysis import nullstellen, minimum, maximum, riemann, trapez, simpson, trapez_fehler, simpson_fehler
from functions import *


lblue = "#1e3799"
dblue = "#001B81"
lgray = "#d9d9d9"
dgray = "#404040"

# Deutsch: 0, Francais: 1, English: 2
lang = 0

"""
Andere Funktionen:
- nullstellen (f(x) = 0)
- min(), max()
- Fläche (integral mit Riemann, Trapez oder simpson (Auswahl))
- dafür optional fehler bestimmen
-


todo:
alles funktionert
besseres design, struktur
graph implementieren
matrizen implementieren
ein paar kürzungen (kein 2x^3 = 2*3*x^2)
fehler: 234^(234^3) = 234^234,3 ??
"""


def toggle_lang(language):
    global lang
    lang = language
    print(f"changed language to {lang}")


class Interpreter:
    memory_dict = {}
    history = ()
    
    def __init__(self, user_input):
        if not user_input:
            return
        if user_input in self.memory_dict:
            app.show_answer(self.memory_dict[user_input])
        else:
            answers = self.calculate(user_input)
            if not answers: return
            app.show_answer(answers)
            self.memory_dict[user_input] = [*answers]
    
    @staticmethod
    def integrate(function=None, variable=None, methodstr=None, lower=None, upper=None):
        method = methodstr.get()
        global history
        if function:
            history = function, variable, lower, upper
        else:
            function, variable, lower, upper = history

        if not (lower or upper):
            return ""
        f = Function(function, variable)
        if method == "riemann":
            return riemann(f, lower, upper)
        elif method == "trapez":
            return trapez(f, lower, upper)
        elif method == "simpson":
            return simpson(f, lower, upper)

    @staticmethod
    def interprete(f):
        if f.startswith("Int") and f[-3:-1] == ")d" and isinstance(f[-1], str):
            if f[3] == "(":
                var = f[-1]
                function = f[4:-3]
                app.show_error(["Nicht berechenbar!", "Non-calculable!", "Not computable!"][lang])
                return r"\int " + write_latex(function) + " d" + var, "", ""

            elif f[3] == "_":  # "Int_12,3^1,23(f)dx"
                lower_bound, i = "", 4
                while f[i] in NUMBERS + ",eπ":
                    lower_bound += f[i]
                    i += 1
                upper_bound = ""
                i += 1
                while f[i] in NUMBERS + ",eπ":
                    upper_bound += f[i]
                    i += 1
                var = f[-1]
                function = f[i + 1:-3]

                method = StringVar(value="riemann")
                Radiobutton(app.einstellungs_frame, text="Riemann", variable=method, value="riemann").pack()
                Radiobutton(app.einstellungs_frame, text="Trapez", variable=method, value="trapez").pack()
                Radiobutton(app.einstellungs_frame, text="Simpson", variable=method, value="simpson").pack()
                method.trace("w", Interpreter.integrate)

                latex_input = rf"\int_{'{'}{lower_bound}{'}^{'}{upper_bound}{'}'}{write_latex(function)}d{var}"
                return latex_input, Interpreter.integrate(function, var, method, flint(lower_bound), flint(upper_bound)), ""
        else:
            return None

    @staticmethod
    def raise_error(error):
        # print("error:", repr(error))
        # print("error.args:", error.args)

        if error.args:
            if len(error.args) > 1:
                # Error mit verschieden Sprachen
                err = error.args[lang]
            else:
                err = error.args[0]
        else:
            # zb: ZeroDivisionError (hat keine args)
            # repr(error) würde ZeroDivisionError() ausgeben, man will die klammern weghaben
            err = repr(error)[:-2]
        app.show_error(err)

    @staticmethod
    def calculate(userinput):
        userinput = userinput.replace(" ", "").replace("**", "^")
        userinput = userinput.replace("²", "^2").replace("³", "^3")
        userinput = userinput.replace("pi", "π")

        for chr in userinput:
            if chr not in ".,+-*/()_^`' π" + NUMBERS + ALPHABET:
                app.show_error(f"Invalid input: '{chr}'")
                return
        if userinput.count("(") != userinput.count(")"):
            app.show_error(["Klammern unpaarig", "Il manque au moins une parenthese", "Unmatched parentheses"][lang])
            return
        if userinput[0] in "*/^'`":
            app.show_error(
                f"{['Erstes Zeichen kann nicht sein', 'Premier charactère ne peut pas être', 'First character cannot be'][lang]}: '{userinput[0]}'")
            return
        if userinput[-1] in "+-*/^":
            app.show_error(
                f"{['Letztes Zeichen kann nicht sein', 'Dernier charactère ne peut pas être', 'Last character cannot be'][lang]}: '{userinput[-1]}'")
            return

        output_str = userinput

        # # Derivative
        # def derivative(userinput, var):
        #     try:
        #         F = Function(userinput, var)
        #         answer = F.diff()
        #     except Exception as error:
        #         return error, None
        #     return answer.str, answer.latex
        #
        # if userinput.startswith("d/d"):
        #     var = userinput[3]
        #     if var == " ":
        #         return f"Invalid syntax: {userinput[:4]}"
        #
        #     userinput = userinput[4:].lstrip()
        #     print(userinput, var)
        #     return derivative(userinput, var)
        #
        # elif userinput.startswith("(") and userinput.endswith((")'", ")`")):
        #     userinput = userinput[1:-2]
        #     return derivative(userinput, "x")
        try:
            maybe_something = Interpreter.interprete(userinput)

            if not maybe_something:
                function = Function(userinput)

                userinput_latex = function.latex_in
                output_str = function.str_out
                output_latex = function.latex_out
            else:
                return maybe_something

        except Exception as error:
            Interpreter.raise_error(error)
            return

        try:
            # Falls man einen approximativen Wert berechnen kann
            output_str += f"\n\n≈ {eval(output_str)}"
        except Exception:
            pass

        return userinput_latex, output_latex, output_str


class AlgebraFrame(Frame):
    def __init__(self, container):
        super().__init__(container)
        
        # self.mittle_frame = Frame(self)
        # self.mittle_frame.place(rely=0.1, relx=0.1, relheight=0.8, relwidth=0.9)

        self.io_frame = Frame(self)  # , highlightbackground="red", highlightcolor="green",
        # highlightthickness=2)
        self.io_frame.place(relx=0.2, rely=0.1, relwidth=0.6, relheight=0.8)

        self.input_entry = Entry(self.io_frame, bd=2, relief="solid", highlightthickness=0, justify="center")
        self.input_entry.focus()
        self.input_entry.place(relx=0.1, rely=0., relwidth=0.8, relheight=0.2)

        self.einstellungs_frame = Frame(self.io_frame)
        # self.einstellungs_frame.place(x=0, y=0, relwidth=1, relheight=0.3)

        self.error_label = Label(self.io_frame, fg="red")
        self.error_label.place(relx=0.1, rely=0.2, relwidth=0.8, relheight=0.075)

        self.latex_io = Label(self.io_frame, bd=2, relief="solid")
        self.latex_io.place(relx=0, rely=0.45, relwidth=1, relheight=0.55)

        self.io_figure = Figure()
        self.io_canvas = FigureCanvasTkAgg(self.io_figure, master=self.latex_io)
        self.io_canvas.get_tk_widget().pack(expand=1, fill="both")

        self.enter_button = Button(self.io_frame, text="=", bd=0,
                                   highlightbackground="#707070")
        self.enter_button.place(relx=0.425, rely=0.35, relwidth=0.15, relheight=0.08)
        self.elements = [self.io_frame, self.input_entry,
                         self.einstellungs_frame, self.error_label,
                         self.enter_button, self.latex_io]

    def show_answer(self, answers):
        self.show_error("")
        userinput_latex, output_latex, output_str = answers
    
        self.io_figure.clear()
        latex_input = r"${}$".format(userinput_latex)
        length = len(latex_input)
        size = int(1800 / (length + 50))
        # print(f"INPUT: {size = }, {length = }")
        if latex_input != "$$":
            self.io_figure.text(0.5, 0.5, latex_input, fontsize=size,
                                color=["black", "white"][self.color_mode], va="center", ha="center")
        self.io_canvas.draw()
    
    def show_error(self, error):
        self.error_label.config(text=error)
        if error: print(f"Error: {error}")


class AnalysisFrame(Frame):
    def __init__(self, container):
        super().__init__(container)
        pass


class MatrixFrame(Frame):
    def __init__(self, container):
        super().__init__(container)
        pass


class CodeFrame(Frame):
    def __init__(self, container):
        super().__init__(container)
        pass


class MainScreen(Tk):
    def __init__(self):
        super().__init__()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        screen_width, screen_height = 700, 500
        
        self.geometry(f"{screen_width}x{screen_height}")
        self.title("WolframBeta")

        # 0: lightmode, 1: darkmode
        self.color_mode = 0

        # für die LaTeX schrift
        # matplotlib.use("TkAgg")
        plt.rcParams["mathtext.fontset"] = "cm"

        # Top Frame
        self.top_frame = Frame(self, bd=1, relief="solid")
        self.top_frame.place(y=0, x=0, relheight=0.1, relwidth=1)

        self.top_frame.columnconfigure(0, weight=1)
        self.top_frame.columnconfigure(1, weight=5)
        self.top_frame.columnconfigure(2, weight=1)
        self.top_frame.rowconfigure(0, weight=1)
        
        # Colormode Buttons
        self.cm_frame = Frame(self.top_frame)
        self.cm_frame.grid(row=0, column=0)
        
        self.lightmode_image = PhotoImage(file="../pictures/lm.png").subsample(4, 4)
        self.lm_button = Button(self.cm_frame, bd=0, highlightbackground="#707070",
                                image=self.lightmode_image, command=lambda: self.toggle_color_mode(0))
        self.lm_button.grid(row=0, column=0, ipadx=3, ipady=3)
        
        self.darkmode_image = PhotoImage(file="../pictures/dm.png").subsample(4, 4)
        self.dm_button = Button(self.cm_frame, bd=0, highlightbackground="#707070",
                                image=self.darkmode_image, command=lambda: self.toggle_color_mode(1))
        self.dm_button.grid(row=0, column=1, padx=4, ipadx=3, ipady=3)
        
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
        self.buttons = self.selection_buttons(self.left_frame, "select", "Analysis", "Algebra", "Numbers")

        # Bottom frame
        self.bottom_frame = Label(self)
        self.bottom_frame.place(relx=0.1, rely=0.9, relwidth=0.9, relheight=0.1)

        self.exit_button = Button(self.bottom_frame,
                                  text=["Schließen", "Fermer", "Exit"][lang],
                                  command=self.exit_screen,
                                  bd=0,
                                  highlightthickness=1.5,
                                  highlightbackground="red")
        self.exit_button.place(relx=0.85, rely=0.2, relwidth=0.1, relheight=0.6)

        self.elements = [self.top_frame, self.logo, self.cm_frame, self.lm_button, self.dm_button,
                         self.lang_frame, self.de_button, self.fr_button, self.gb_button,
                         self.bottom_frame, self.exit_button]
        
        self.algebra_frame = self.analysis_frame = self.matrix_frame = self.code_frame = None
        self.current_frame = Frame(self)
        self.toggle_main_frame(0)
        
        self.bind("<Return>", self.new_func)
        self.bind("<KP_Enter>", self.exit_screen)
    
    def initate_main_frame(self, n):
        if n == 0:
            self.algebra_frame = AlgebraFrame(self)
            return self.algebra_frame
        elif n == 1:
            self.analysis_frame = AnalysisFrame(self)
            return self.analysis_frame
        elif n == 2:
            self.matrix_frame = MatrixFrame(self)
            return self.matrix_frame
        elif n == 3:
            self.code_frame = CodeFrame(self)
            return self.code_frame
        
    def toggle_main_frame(self, n):
        frame = (self.algebra_frame, self.analysis_frame, self.matrix_frame, self.code_frame)[n]
        if frame is None:
            frame = self.initate_main_frame(n)
        self.current_frame.place_forget()
        self.current_frame = frame
        frame.place(rely=0.1, relx=0.1, relheight=0.8, relwidth=0.9)
       
    def toggle_color_mode(self, cm):
        self.color_mode = cm

        for container in self.elements:
            container["bg"] = [lgray, dgray][self.color_mode]
            if type(container) == Entry:
                container["fg"] = ["black", "white"][self.color_mode]
                container["bg"] = ["white", "#505050"][self.color_mode]
            elif type(container) == Button:
                container["activebackground"] = ["#ececec", "#4c4c4c"][self.color_mode]
                container["activeforeground"] = ["black", "#f0f0f0"][self.color_mode]
                container["fg"] = ["black", "#f0f0f0"][self.color_mode]

        self.io_figure.set_facecolor(["white", "#505050"][self.color_mode])
        self.io_canvas.draw()

    def selection_buttons(self, container, *names):
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
            white_bg.place(rely=i/4-1/500, relx=0.05, height=1, relwidth=0.9)

        return buttons

    def select_main_frame(self, n):
        for i in range(4):
            self.buttons[i]["bg"] = lblue
        self.toggle_main_frame(n)
        self.buttons[n]["bg"] = dblue

    def exit_screen(self, event=None):
        self.destroy()
        print(f"{Interpreter.memory_dict = }")


if __name__ == "__main__":
    app = MainScreen()
    app.mainloop()
