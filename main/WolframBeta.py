from tkinter import Tk, Frame, Label, Entry, Button, PhotoImage

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
selection = 0  # Auswahl links
lang = 0  # Deutsch: 0, Francais: 1, English: 2
color_mode = 0  # 0: lightmode, 1: darkmode
figures = []  # beide (Figure, Canvas)
memory_dict = {}  # Speicher für userinputs

"""
Andere Funktionen:
- nullstellen (f(x) = 0)
- min(), max()
- Fläche (integral mit Riemann, Trapez oder simpson (Auswahl))
- dafür optional fehler bestimmen


"""


def toggle_color_mode(containers):
    global color_mode
    color_mode = 1 if color_mode == 0 else 0
    toggle_color_button.config(image=[darkmode_image, lightmode_image][color_mode], text=["Darkmode", "Lightmode"][color_mode])
    
    for container in containers:
        container["bg"] = [lgray, dgray][color_mode]
        if type(container) == Entry:
            container["fg"] = ["black", "white"][color_mode]
        elif type(container) == Button:
            container["fg"] = ["black", "white"][color_mode]
            container["activebackground"] = ["#ececec", "#4c4c4c"][color_mode]
            container["activeforeground"] = ["black", "#f0f0f0"][color_mode]
            container["fg"] = ["black", "#f0f0f0"][color_mode]
    
    (input_fig, input_canvas), (out_fig, out_canvas) = figures
    input_fig.set_facecolor(["white", "#505050"][color_mode])
    out_fig.set_facecolor(["white", "#505050"][color_mode])
    input_canvas.draw()
    out_canvas.draw()


def toggle_lang(language):
    global lang
    lang = language
    toggle_color_button.config(image=[de_flag, fr_flag, gb_flag][lang], text=["Sprache", "Langue", "Language"][lang])
    

def integrate(function, variable, method, lower=None, upper=None):
    if not (lower or upper):
        return ""
    f = Function(function, variable)
    if method == "riemann":
        return riemann(f, lower, upper)
    elif method == "trapez":
        return trapez(f, lower, upper)
    elif method == "simpson":
        return simpson(f, lower, upper)


def interprete(f):
    if f.startswith("Int") and f[-3:-1] == ")d" and isinstance(f[-1], str):
        if f[3] == "(":
            var = f[-1]
            function = f[4:-3]
            return r"\int " + write_latex(function) + " d" + var, "not computable", ""
        elif f[3] == "_":  # "Int_12,3^1,23(f)dx"
            lower_bound, i = "", 4
            while f[i] in NUMBERS + ",":
                lower_bound += f[i]
                i += 1
            upper_bound = ""
            i += 1
            while f[i] in NUMBERS + ",":
                upper_bound += f[i]
                i += 1
            var = f[-1]
            function = f[i + 1:-3]
            latex_input = rf"\int_{'{'}{lower_bound}{'}^{'}{upper_bound}{'}'}{write_latex(function)}d{var}"
            return latex_input, integrate(function, var, "riemann", flint(lower_bound), flint(upper_bound)), ""
    else:
        return None


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
    show_error(err)


def calculate(userinput):
    userinput = userinput.replace(" ", "").replace("**", "^")
    userinput = userinput.replace("²", "^2").replace("³", "^3")
    userinput = userinput.replace("pi", "π")
    
    for chr in userinput:
        if chr not in ".,+-*/()_^`' π" + NUMBERS + ALPHABET:
            show_error(f"Invalid input: '{chr}'")
            return
    if userinput.count("(") != userinput.count(")"):
        show_error(["Klammern unpaarig", "Il manque au moins une parenthese", "Unmatched parentheses"][lang])
        return
    if userinput[0] in "*/^'`":
        show_error(f"{['Erstes Zeichen kann nicht sein', 'Premier charactère ne peut pas être', 'First character cannot be'][lang]}: '{userinput[0]}'")
        return
    if userinput[-1] in "+-*/^":
        show_error(f"{['Letztes Zeichen kann nicht sein', 'Dernier charactère ne peut pas être', 'Last character cannot be'][lang]}: '{userinput[-1]}'")
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
        maybe_something = interprete(userinput)
        
        if not maybe_something:
            function = Function(userinput)
            
            userinput_latex = function.latex_in
            output_str = function.str_out
            output_latex = function.latex_out
        else:
            return maybe_something
    
    except Exception as error:
        raise_error(error)
        return
    
    
    try:
        # Falls man eine approximativen Wert berechnen kann
        output_str += f"\n\n≈ {eval(output_str)}"
    except Exception:
        pass
    
    return userinput_latex, output_latex, output_str


def get_user_input(_=None):
    # show_error("asdjugfherglerhgleruhgl")
    user_input = inputentry.get()
    if not user_input:
        return
    if user_input in memory_dict:
        show_answer(*memory_dict[user_input])
    else:
        answers = calculate(user_input)
        if not answers: return
        show_answer(*answers)
        memory_dict[user_input] = [*answers]


def show_error(err):
    error_label.config(text=err)


def show_answer(*answers):
    error_label.config(text="")
    userinput_latex, output_latex, output_str = answers
    (input_fig, input_canvas), (out_fig, out_canvas) = figures
    
    input_fig.clear()
    latex_input = r"${}$".format(userinput_latex)
    l = len(latex_input)
    size = int(1800 / (l + 50))
    # print(f"INPUT: {size = }, {len(latex_input) = }")
    if latex_input != "$$":
        input_fig.text(10 / (l + 18), 0.5, latex_input, fontsize=size, color=["black", "white"][color_mode])
    input_canvas.draw()
    
    out_fig.clear()
    text = r"${}$".format(output_latex)
    l = len(text)
    size = int(2000 / (l + 50))
    # print(f"OUTPUT: {size = }, {l = }")
    if text != "$$":
        out_fig.text(10 / (l + 18), 0.45, text, fontsize=size, color=["black", "white"][color_mode])
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
        inputentry.insert(0, "Int_ ^ (")
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
    topframe = Frame(root)
    topframe.place(y=0, relx=0.1, relheight=0.1, relwidth=0.9)
    
    topframe.columnconfigure(0, weight=5)
    topframe.rowconfigure(0, weight=1)
    
    logopic = PhotoImage(file="../pictures/logo.png").subsample(2, 2)
    logo = Label(topframe, image=logopic)
    logo.grid(row=0, column=0, sticky="news")
    
    global toggle_color_button
    global darkmode_image
    global lightmode_image
    darkmode_image = PhotoImage(file="../pictures/darkmode.png")
    lightmode_image = PhotoImage(file="../pictures/lightmode.png")
    toggle_color_button = Button(topframe,
                                 image=[darkmode_image, lightmode_image][color_mode],
                                 text=["Darkmode", "Lightmode"][color_mode],
                                 command=lambda: toggle_color_mode(containers),
                                 compound="left",
                                 bd=0,
                                 highlightbackground="#707070"
                                 )
    toggle_color_button.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
    
    global toggle_lang_button
    global de_flag
    global fr_flag
    global gb_flag
    de_flag = PhotoImage(file="../pictures/de.png")
    fr_flag = PhotoImage(file="../pictures/fr.png")
    gb_flag = PhotoImage(file="../pictures/gb.png")
    toggle_lang_button = Button(topframe,
                                text="Sprache",
                                image=de_flag,
                                compound="left",
                                command=toggle_lang,
                                bd=0,
                                highlightbackground="#707070"
                                )
    toggle_lang_button.grid(row=0, column=2, sticky="ew", padx=30, pady=10)
    
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
    mittleframe = Frame(root)
    mittleframe.place(rely=0.1, relx=0.1, relheight=0.8, relwidth=0.9)
    
    inputframe = Frame(mittleframe, highlightbackground=lblue, highlightcolor="green", highlightthickness=2)
    inputframe.place(relx=0.1, rely=0.2, relwidth=0.3, relheight=0.6)
    
    global inputentry
    inputentry = Entry(inputframe, bd=0, highlightthickness=0, justify="center")
    inputentry.place(relx=0, rely=0, relwidth=1, relheight=0.3)
    
    global error_label
    error_label = Label(inputframe, fg="red")
    error_label.place(x=0, rely=0.3, relwidth=1, relheight=0.1)
    
    latex_in = Label(inputframe)
    latex_in.place(x=0, rely=0.4, relwidth=1, relheight=0.6)
    
    input_fig = Figure()
    input_canvas = FigureCanvasTkAgg(input_fig, master=latex_in)
    input_canvas.get_tk_widget().pack()
    figures.append((input_fig, input_canvas))
    
    bttn = Button(mittleframe, text="=", command=get_user_input, bd=0, highlightbackground="#707070")
    bttn.place(relx=0.45, rely=0.45, relwidth=0.1, relheight=0.1)
    
    outputframe = Frame(mittleframe, highlightbackground=lblue, highlightthickness=2)
    outputframe.place(relx=0.6, rely=0.2, relwidth=0.3, relheight=0.6)
    
    global outlabel
    outlabel = Label(outputframe)
    outlabel.place(x=0, y=0, relwidth=1, relheight=0.3)
    
    latexout = Label(outputframe)
    latexout.place(x=0, rely=0.3, relwidth=1, relheight=0.701)
    
    out_fig = Figure()
    out_canvas = FigureCanvasTkAgg(out_fig, master=latexout)
    out_canvas.get_tk_widget().pack(side="top", fill="both", expand=1)
    figures.append((out_fig, out_canvas))
    
    # Bottomframe
    bottomframe = Label(root)
    bottomframe.place(relx=0.1, rely=0.9, relwidth=0.9, relheight=0.1)
    
    def exit_screen(event=None):
        root.destroy()
        print(f"{memory_dict = }")
    
    exitbutton = Button(bottomframe,
                        text=["Schließen", "Fermer", "Exit"][lang],
                        command=exit_screen,
                        bd=0,
                        highlightthickness=1.5,
                        highlightbackground="red")
    exitbutton.place(relx=0.85, rely=0.2, relwidth=0.1, relheight=0.6)
    
    containers = [topframe, logo, mittleframe, bottomframe, inputentry, inputframe, error_label, outlabel, bttn, toggle_color_button, toggle_lang_button,
                  exitbutton, latex_in, latexout, error_label]
    
    root.bind("<Return>", get_user_input)
    root.bind("<KP_Enter>", exit_screen)
    inputentry.focus()
    root.mainloop()


if __name__ == "__main__":
    create_screen()
