from tkinter import Tk, Frame, Label, Entry, Button, PhotoImage

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from FunctionClass import Function, NUMBERS, ALPHABET, flint
from analysis import nullstellen, minimum, maximum, riemann, trapez, simpson, trapez_fehler, simpson_fehler
from functions import *

# from analysis import *


lblue = "#1e3799"
dblue = "#001B81"
selection = 0
lang = 0
# Deutsch: 0, Francais: 1, English: 2


"""
Andere Funktionen:
- nullstellen (f(x) = 0)
- min(), max()
- Fläche (integral mit Riemann, Trapez oder simpson (Auswahl))
- dafür optional fehler bestimmen


"""


def integrate(function, variable, method, lower=None, upper=None):
    return "lol"


def interprete(f):
    if f.startswith("Int") and f[-3:-1] == ")d" and isinstance(f[-1], str):
        if f[3] == "(":
            var = f[-1]
            function = Function(f[4:-3])
            return "", integrate(function, var, "riemann"), ""
        elif f[3] == "_":
            lower_bound, i = "", 4
            while f[i] in NUMBERS+",":
                lower_bound += f[i]
                i += 1
            upper_bound = ""
            i += 1
            while f[i] in NUMBERS+",":
                upper_bound += f[i]
                i += 1
            var = f[-1]
            function = Function(f[i+1:-3])
            return "", integrate(function, var, "riemann", flint(lower_bound), flint(upper_bound)), ""
    else:
        return None
    

def raise_error(error):
    print("error:", repr(error))
    print("error.args:", error.args)
    
    if error.args:
        if len(error.args) > 1:
            # Error mit verschieden Sprachen
            return error.args[lang], "", ""
        else:
            return error.args[0], "", ""
    else:
        # zb: ZeroDivisionError (hat keine args)
        # repr(error) würde ZeroDivisionError() ausgeben, man will die klammern weghaben
        return repr(error)[:-2], "", ""
    

def calculate(userinput):
    userinput = userinput.replace(" ", "").replace("**", "^")
    userinput = userinput.replace("²", "^2").replace("³", "^3")
    
    for i, j in enumerate(userinput):
        if j not in ".,+-*/()^`' " + NUMBERS + ALPHABET:
            return f"Invalid input: '{userinput[i]}'", "", ""
    if userinput.count("(") != userinput.count(")"):
        return ["Klammern unpaarig", "Il manque au moins une parenthese", "Unmatched parentheses"][lang], "", ""
    
    userinput = userinput.replace("pi", "π")
    userinput = userinput.lstrip().rstrip()
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
        maybe_something =  interprete(userinput)
        
        if not maybe_something:
            function = Function(userinput)
            
            userinput_latex = function.latex_in
            output_str = function.str_out
            output_latex = function.latex_out
        else:
            return maybe_something
           
    except Exception as error:
        return raise_error(error)
    
    try:
        # Falls man eine approximativen Wert berechnen kann
        output_str += f"\n\n≈ {eval(output_str)}"
    except Exception:
        pass
    
    return userinput_latex, output_latex, output_str


def show_answer(event=None):
    userinput = inputentry.get()
    userinput_latex, output_latex, output_str = calculate(userinput)
    print(f"{userinput_latex = }, {output_latex = }, {output_str = }")
    input_fig.clear()
    latex_input = r"${}$".format(userinput_latex)
    if latex_input != "$$":
        input_fig.text(0.2, 0.5, latex_input)
    input_canvas.draw()
    
    out_fig.clear()
    text = r"${}$".format(output_latex)
    size = int(20 - len(output_latex) / 7)
    print(f"{size = }, {len(output_latex) = }")
    if text != "$$":
        out_fig.text(size / 150, 0.45, text, fontsize=size)
    out_canvas.draw()

    outlabel["text"] = output_str


def selection_buttons(container, function, *names):
    buttons = []
    
    whitebg = Label(container)
    whitebg.place(rely=0.01, relx=0.05, relwidth=0.9, relheight=len(names) / 10 - 0.01)
    
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


def clear_frame():
    for widget in selectframe.winfo_children():
        widget.destroy()


def select(topic):
    global selection
    selection = topic if selection != topic else 0
    
    clear_frame()
    for i in range(3):
        buttons[i]["bg"] = lblue
    
    if selection == 1:
        buttons[0]["bg"] = dblue
        selection_buttons(selectframe, "analysis", "Ableitung", "Integral", "Grenzwert", "Graph")
    if selection == 2:
        buttons[1]["bg"] = dblue
        selection_buttons(selectframe, "algebra", "Matrizen")
    if selection == 3:
        buttons[2]["bg"] = dblue
        selection_buttons(selectframe, "numbers", "Zahlentheorie")


def analysis(n):
    print("ana: ", n)
    
    if n == 1:
        inputentry.insert(0, "d/dx(")
        inputentry.insert("end", ")")
    if n == 2:
        inputentry.insert(0, "Int(")
        inputentry.insert("end", ")dx")
    if n == 3:
        inputentry.insert(0, "lim x->inf ")


def algebra(n):
    print("algebra: ", n)


def numbers(n):
    print("numbers: ", n)


def create_screen():
    root = Tk()
    # matplotlib.use('TkAgg')
    plt.rcParams["mathtext.fontset"] = "cm"
    
    sw = root.winfo_screenwidth()  # 1680
    sh = root.winfo_screenheight()  # 1050
    sh, sw = 500, 700
    
    root.geometry(f"{sw}x{sh}")
    root.title("Wolframbeta")
    
    # Topframe
    topframe = Frame(root, borderwidth=3, relief="raised")
    topframe.place(y=0, relx=0.1, relheight=0.1, relwidth=0.9)
    
    logopic = PhotoImage(file="logo.png").subsample(2, 2)
    logo = Label(topframe, image=logopic)
    logo.place(relx=0.45, rely=0.35)
    
    # Leftframe
    leftframe = Frame(root, bg=lblue)
    leftframe.place(y=0, x=0, relheight=1, relwidth=0.1)
    
    sep = Label(leftframe, bg="white")
    sep.place(x=0, rely=0.299, relwidth=1, height=3)
    
    global selectframe
    selectframe = Frame(leftframe, bg=lblue)
    selectframe.place(x=0, rely=0.305, relwidth=1, relheight=0.695)
    
    global buttons
    buttons = selection_buttons(leftframe, "select", "Analysis", "Algebra", "Numbers")
    
    # Mittleframe
    mittleframe = Frame(root, borderwidth=3, relief="raised")
    mittleframe.place(rely=0.1, relx=0.1, relheight=0.8, relwidth=0.9)
    
    inputframe = Frame(mittleframe, highlightbackground=lblue, highlightcolor="green", highlightthickness=2, bg="white")
    inputframe.place(relx=0.1, rely=0.2, relwidth=0.3, relheight=0.6)
    
    global inputentry
    inputentry = Entry(inputframe, bd=0, highlightthickness=1)
    inputentry.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.3)
    
    latex_in = Label(inputframe, bg="red")
    latex_in.place(x=0, rely=0.32, relwidth=1, relheight=0.69)

    global input_fig
    global input_canvas
    input_fig = Figure()
    input_canvas = FigureCanvasTkAgg(input_fig, master=latex_in)
    input_canvas.get_tk_widget().pack(side="top", fill="both", expand=1)

    bttn = Button(mittleframe, text="=", command=show_answer)
    bttn.place(relx=0.45, rely=0.45, relwidth=0.1, relheight=0.1)
    
    outputframe = Frame(mittleframe, highlightbackground=lblue, highlightthickness=2)
    outputframe.place(relx=0.6, rely=0.2, relwidth=0.3, relheight=0.6)
    
    global outlabel
    outlabel = Label(outputframe)
    outlabel.place(x=0, y=0, relwidth=1, relheight=0.3)
    
    latexout = Label(outputframe)
    latexout.place(x=0, rely=0.3, relwidth=1, relheight=0.7)
    
    global out_fig
    global out_canvas
    out_fig = Figure()
    out_canvas = FigureCanvasTkAgg(out_fig, master=latexout)
    out_canvas.get_tk_widget().pack(side="top", fill="both", expand=1)
    
    # Bottomframe
    bottomframe = Label(root, borderwidth=3, relief="raised")
    bottomframe.place(relx=0.1, rely=0.9, relwidth=0.9, relheight=0.1)
    
    def exit_screen(event=None):
        root.destroy()
    
    exitbutton = Button(bottomframe, text=["Schließen", "Fermer", "Exit"][lang], command=exit_screen,
                        highlightthickness=1.5,
                        highlightbackground="red")
    exitbutton.place(relx=0.85, rely=0.2, relwidth=0.1, relheight=0.6)
    
    root.bind("<Return>", show_answer)
    root.bind("<KP_Enter>", exit_screen)
    root.mainloop()


if __name__ == "__main__":
    create_screen()
