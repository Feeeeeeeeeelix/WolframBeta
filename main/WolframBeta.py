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
kein
"""


def toggle_lang():
    global lang
    lang = app.lang_selection.get()


class Interpreter:
    memory_dict = {}
    history = ()
    
    def __init__(self, user_input):
        if not user_input:
            return
        if user_input in Interpreter.memory_dict:
            app.show_answer(Interpreter.memory_dict[user_input])
        else:
            answers = Interpreter.calculate(user_input)
            if not answers: return
            app.show_answer(*answers)
            Interpreter.memory_dict[user_input] = [*answers]
    
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


class Screen(Tk):
    def __init__(self):
        super().__init__()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        screen_width, screen_height = 700, 500
        
        self.geometry(f"{screen_width}x{screen_height}")
        self.title("Wolframbeta")

        # 0: lightmode, 1: darkmode
        self.color_mode = 0

        # für die LaTeX schrift
        plt.rcParams["mathtext.fontset"] = "cm"
        # matplotlib.use("TkAgg")

        # Top Frame
        self.top_frame = Frame(self)
        self.top_frame.place(y=0, relx=0.1, relheight=0.1, relwidth=0.9)

        self.top_frame.columnconfigure(0, weight=5)
        self.top_frame.rowconfigure(0, weight=1)

        self.logo_pic = PhotoImage(file="../pictures/logo.png").subsample(2, 2)
        self.logo = Label(self.top_frame, image=self.logo_pic)
        self.logo.grid(row=0, column=0, sticky="news")

        self.darkmode_image = PhotoImage(file="../pictures/darkmode.png")
        self.lightmode_image = PhotoImage(file="../pictures/lightmode.png")
        self.toggle_color_button = Button(self.top_frame,
                                          image=[self.darkmode_image, self.lightmode_image][self.color_mode],
                                          text=["Darkmode", "Lightmode"][self.color_mode],
                                          command=lambda: self.toggle_color_mode(self.container),
                                          compound="left",
                                          bd=0,
                                          highlightbackground="#707070"
                                          )
        self.toggle_color_button.grid(row=0, column=1, sticky="ew", padx=10, pady=10)

        # global toggle_lang_button
        # global de_flag
        # global fr_flag
        # global gb_flag
        # de_flag = PhotoImage(file="../pictures/de.png").subsample(3, 3)
        # fr_flag = PhotoImage(file="../pictures/fr.png")
        # gb_flag = PhotoImage(file="../pictures/gb.png")

        self.lang_selection = StringVar()
        self.toggle_lang_menu = OptionMenu(self.top_frame,
                                           self.lang_selection,
                                           "Deutsch",
                                           "Francais",
                                           "English",
                                           command=toggle_lang)
        self.toggle_lang_menu.grid(row=0, column=2, sticky="ew", padx=30, pady=10)

        # Left frame
        self.left_frame = Frame(self, bg=lblue)
        self.left_frame.place(y=0, x=0, relheight=1, relwidth=0.1)

        self.sep = Label(self.left_frame, bg="white")
        self.sep.place(x=0, rely=0.299, relwidth=1, height=3)

        self.select_frame = Frame(self.left_frame, bg=lblue)
        self.select_frame.place(x=0, rely=0.305, relwidth=1, relheight=0.695)

        self.selection = 0
        self.buttons = self.selection_buttons(self.left_frame, "select", "Analysis", "Algebra", "Numbers")

        # Mittle frame
        self.mittle_frame = Frame(self)
        self.mittle_frame.place(rely=0.1, relx=0.1, relheight=0.8, relwidth=0.9)

        self.input_frame = Frame(self.mittle_frame, highlightbackground=lblue, highlightcolor="green",
                                 highlightthickness=2)
        self.input_frame.place(relx=0.1, rely=0.2, relwidth=0.3, relheight=0.6)

        self.input_entry = Entry(self.input_frame, bd=0, highlightthickness=0, justify="center")
        self.input_entry.focus()
        self.input_entry.place(relx=0, rely=0, relwidth=1, relheight=0.3)

        self.error_label = Label(self.input_frame, fg="red")
        self.error_label.place(x=0, rely=0.3, relwidth=1, relheight=0.1)

        self.latex_in = Label(self.input_frame)
        self.latex_in.place(x=0, rely=0.4, relwidth=1, relheight=0.6)

        self.input_fig = Figure()
        self.input_canvas = FigureCanvasTkAgg(self.input_fig, master=self.latex_in)
        self.input_canvas.get_tk_widget().pack()

        self.enter_button = Button(self.mittle_frame, text="=", command=self.new_func, bd=0,
                                   highlightbackground="#707070")
        self.enter_button.place(relx=0.45, rely=0.45, relwidth=0.1, relheight=0.1)

        self.output_frame = Frame(self.mittle_frame, highlightbackground=lblue, highlightthickness=2)
        self.output_frame.place(relx=0.6, rely=0.2, relwidth=0.3, relheight=0.6)

        self.einstellungs_frame = Frame(self.output_frame)
        self.einstellungs_frame.place(x=0, y=0, relwidth=1, relheight=0.3)

        self.latex_out = Label(self.output_frame)
        self.latex_out.place(x=0, rely=0.4, relwidth=1, relheight=0.6)

        self.out_fig = Figure()
        self.out_canvas = FigureCanvasTkAgg(self.out_fig, master=self.latex_out)
        self.out_canvas.get_tk_widget().pack(side="top", fill="both", expand=1)

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

        self.container = [self.top_frame, self.logo, self.toggle_color_button, self.toggle_lang_menu,
                          self.mittle_frame, self.input_frame, self.output_frame, self.error_label,
                          self.einstellungs_frame,
                          self.enter_button, self.latex_in, self.latex_out,
                          self.bottom_frame, self.exit_button]

        self.bind("<Return>", self.new_func)
        self.bind("<KP_Enter>", self.exit_screen)

        # self.mainloop()

    def show_error(self, error):
        self.error_label.config(text=error)
        print(f"Error: {error}")
        
    def new_func(self, event=None):
        object = Interpreter(self.input_entry.get())

    def show_answer(self, *answers):
        self.show_error("")
        userinput_latex, output_latex, output_str = answers

        self.input_fig.clear()
        latex_input = r"${}$".format(userinput_latex)
        length = len(latex_input)
        size = int(1800 / (length + 50))
        # print(f"INPUT: {size = }, {length = }")
        if latex_input != "$$":
            self.input_fig.text(10 / (length + 18), 0.5, latex_input, fontsize=size, color=["black", "white"][self.color_mode])
        self.input_canvas.draw()

        self.out_fig.clear()
        text = r"${}$".format(output_latex)
        length = len(text)
        size = int(2000 / (length + 50))
        # print(f"OUTPUT: {size = }, {length = }")
        if text != "$$":
            self.out_fig.text(10 / (length + 18), 0.45, text, fontsize=size, color=["black", "white"][self.color_mode])
        self.out_canvas.draw()

        # outlabel["text"] = output_str

    def toggle_color_mode(self, containers):
        self.color_mode = 1 - self.color_mode
        self.toggle_color_button.config(image=[self.darkmode_image, self.lightmode_image][self.color_mode],
                                        text=["Darkmode", "Lightmode"][self.color_mode])

        for container in containers:
            container["bg"] = [lgray, dgray][self.color_mode]
            if type(container) == Entry:
                container["fg"] = ["black", "white"][self.color_mode]
            elif type(container) == Button:
                container["activebackground"] = ["#ececec", "#4c4c4c"][self.color_mode]
                container["activeforeground"] = ["black", "#f0f0f0"][self.color_mode]
                container["fg"] = ["black", "#f0f0f0"][self.color_mode]

        self.input_fig.set_facecolor(["white", "#505050"][self.color_mode])
        self.out_fig.set_facecolor(["white", "#505050"][self.color_mode])
        self.input_canvas.draw()
        self.out_canvas.draw()

    def clear_select_frame(self):
        for widget in self.select_frame.winfo_children():
            widget.destroy()

    @staticmethod
    def selection_buttons(container, function, *names):
        buttons = []

        white_bg = Label(container)
        white_bg.place(rely=0.01, relx=0.05, relwidth=0.9, relheight=len(names) / 10 - 0.01)

        for i, name in enumerate(names):
            button = Button(container,
                            text=name,
                            bg=lblue,
                            fg="white",
                            highlightthickness=0,
                            bd=0,
                            activebackground=dblue,
                            activeforeground="white",
                            command=lambda n=i + 1: eval(function)(n))
            button.place(rely=i / 10, x=0, relwidth=1, relheight=0.099)
            buttons.append(button)

        return buttons

    def select(self, topic):
        self.selection = topic if self.selection != topic else 0

        self.clear_select_frame()
        for i in range(3):
            self.buttons[i]["bg"] = lblue

        if self.selection == 1:
            self.buttons[0]["bg"] = dblue
            self.selection_buttons(self.select_frame, "analysis", "Ableitung", "Integral", "Grenzwert", "Graph")
        if self.selection == 2:
            self.buttons[1]["bg"] = dblue
            self.selection_buttons(self.select_frame, "algebra", "Matrizen")
        if self.selection == 3:
            self.buttons[2]["bg"] = dblue
            self.selection_buttons(self.select_frame, "numbers", "Zahlentheorie")

    def analysis(self, n):
        print("ana: ", n)

        if n == 1:
            self.input_entry.insert(0, "d/dx(")
            self.input_entry.insert("end", ")")
        if n == 2:
            self.input_entry.insert(0, "Int_^(")
            self.input_entry.insert("end", ")dx")
        if n == 3:
            self.input_entry.insert(0, "lim ")

    def algebra(self, n):
        print("algebra: ", n)

    def numbers(self, n):
        print("numbers: ", n)

    def exit_screen(self, event=None):
        self.destroy()
        print(f"{Interpreter.memory_dict = }")


if __name__ == "__main__":
    app = Screen()
    app.mainloop()
