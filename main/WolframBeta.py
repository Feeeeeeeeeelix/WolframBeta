from tkinter import *

from functions import *
from FunctionClass import *
from analysis import *


def calculate(userinput):
    userinput = userinput.replace(" ", "").replace("**", "^").lower()

    for i, j in enumerate(userinput):
        if j not in ".,+-*/()^`' " + NUMBERS + ALPHABET:
            return f"Invalid input: '{userinput[i]}'"

    if userinput.count("(") != userinput.count(")"):
        return "unmatched parentheses"

    userinput = userinput.replace("pi", "π")

    userinput = userinput.lstrip().rstrip()
    answer = userinput

    # Derivative
    def derivative(userinput, var):
        try:
            F = Function(userinput, var)
            answer = F.diff().str
        except Exception as error:
            return error
        return answer

    if userinput.startswith("d/d"):
        var = userinput[3]
        if var == " ":
            return f"Invalid syntax: {userinput[:4]}"

        userinput = userinput[4:].lstrip()
        print(userinput, var)
        return derivative(userinput, var)

    elif userinput.startswith("(") and userinput.endswith((")'", ")`")):
        userinput = userinput[1:-2]
        return derivative(userinput, "x")

    elif userinput.endswith("'"):
        userinput = userinput[:-1]
        return derivative(userinput, "x")

    try:
        F = Function(userinput, "x")
        answer = F.str
    except Exception as error:
        return error

    try:
        answer += f"\n\n≈{eval(answer)}"
    except Exception:
        pass

    return answer


def show_answer(event=None):
    userinput = inputentry.get().lower()
    answer = calculate(userinput)

    # text = r"${}$".format(answer)

    outlabel["text"] = answer


# wx.clear()
# wx.text(0.1, 0.5, answer, fontsize = 8)
# canvas.draw()


root = Tk()

sw = root.winfo_screenwidth()  # 1680
sh = root.winfo_screenheight()  # 1050
sh, sw = 500, 700

root.geometry(f"{sw}x{sh}")
root.title("Wolframbeta")

lblue = "#1e3799"
dblue = "#001B81"

# Topframe
topframe = Frame(root, borderwidth=3, relief="raised")
topframe.place(y=0, relx=0.1, relheight=0.1, relwidth=0.9)

logopic = PhotoImage(file="logo.png").subsample(2, 2)
logo = Label(topframe, image=logopic)
logo.place(relx=0.45, rely=0.35)

# Leftframe
leftframe = Frame(root, bg=lblue)
leftframe.place(y=0, x=0, relheight=1, relwidth=0.1)

# whitebg = Label(leftframe)
# whitebg.place(rely = 0.01, relx = 0.05, relwidth = 0.9, relheight = 0.29)

sep = Label(leftframe, bg="white")
sep.place(x=0, rely=0.299, relwidth=1, height=3)

selectframe = Frame(leftframe, bg=lblue)
selectframe.place(x=0, rely=0.305, relwidth=1, relheight=0.695)


def SelectionButtons(container, function, *names):
    buttons = []

    whitebg = Label(container)
    whitebg.place(rely=0.01, relx=0.05, relwidth=0.9, relheight=len(names) / 10 - 0.01)

    for i, name in enumerate(names):
        button = Button(container, text=name, bg=lblue, fg="white", highlightthickness=0, bd=0, activebackground=dblue,
                        activeforeground="white", command=lambda n=i + 1: eval(function)(n))
        button.place(rely=i / 10, x=0, relwidth=1, relheight=0.099)
        buttons.append(button)

    return buttons


def clear_frame():
    for widget in selectframe.winfo_children():
        widget.destroy()


selection = 0


def select(topic):
    global selection
    selection = topic if selection != topic else 0

    clear_frame()
    for i in range(3):
        buttons[i]["bg"] = lblue

    if selection == 1:
        buttons[0]["bg"] = dblue
        SelectionButtons(selectframe, "analysis", "Ableitung", "Integral", "Grenzwert", "Graph")
    if selection == 2:
        buttons[1]["bg"] = dblue
        SelectionButtons(selectframe, "algebra", "Matrizen")
    if selection == 3:
        buttons[2]["bg"] = dblue
        SelectionButtons(selectframe, "numbers", "Zahlentheorie")


def analysis(n):
    print("ana: ", n)

    if n == 1:
        inputentry.insert(0, "d/dx ")

    if n == 2:
        inputentry.insert(0, "int ")
        inputentry.insert(END, " dx")
    if n == 3:
        inputentry.insert(0, "lim x->inf ")


def algebra(n):
    print("algebra: ", n)


def numbers(n):
    print("numbers: ", n)


buttons = SelectionButtons(leftframe, "select", "Analysis", "Algebra", "Numbers")

# Mittleframe
mittleframe = Frame(root, borderwidth=3, relief="raised")
mittleframe.place(rely=0.1, relx=0.1, relheight=0.8, relwidth=0.9)

inputframe = Frame(mittleframe, highlightbackground=lblue, highlightcolor="green", highlightthickness=2, bg="white")
inputframe.place(relx=0.1, rely=0.2, relwidth=0.3, relheight=0.6)

inputentry = Entry(inputframe, bd=0, highlightthickness=1)
inputentry.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.3)
# inputentry.insert(0, "\sin(x) = \sum_{n=0}^\infty (-1)^n\cdot \\frac{x^{2n+1}}{(2n+1)!}")
inputentry.bind("<Return>", show_answer)

bttn = Button(mittleframe, text="=", command=show_answer)
bttn.place(relx=0.45, rely=0.45, relwidth=0.1, relheight=0.1)

outputframe = Frame(mittleframe, highlightbackground=lblue, highlightthickness=2)
outputframe.place(relx=0.6, rely=0.2, relwidth=0.3, relheight=0.6)

outlabel = Label(outputframe)
outlabel.pack(expand=1, fill="both")

# fig = matplotlib.figure.Figure(figsize=(1,1), dpi=200)
# wx = fig.add_subplot(111)
# canvas = FigureCanvasTkAgg(fig, master=outputframe)
# canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=0)
# canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
# wx.get_xaxis().set_visible(False)
# wx.get_yaxis().set_visible(False)


# show()

# Bottomframe
bottomframe = Label(root, borderwidth=3, relief="raised")
bottomframe.place(relx=0.1, rely=0.9, relwidth=0.9, relheight=0.1)

exitbutton = Button(bottomframe, text="Exit", command=exit, highlightthickness=1.5, highlightbackground="red")
exitbutton.place(relx=0.85, rely=0.2, relwidth=0.1, relheight=0.6)

# analysis(1)


# root.bind_all("<Return>", quit)
root.bind("<KP_Enter>", quit)
root.mainloop()

"""
root = Tk()

sw = root.winfo_screenwidth()		#1680
sh = root.winfo_screenheight()		#1050
root.geometry(f"{sw}x{sh}")
root.title("CAS")

for i in range(5):
	root.rowconfigure(i, weight=1)
	root.columnconfigure(i, weight=i%2+1)
	
	[Frame(root, borderwidth=0, relief="sunken").grid(row=i, column=j, sticky="news") for j in range(5)]


	#Entry
entry_frame = Frame(root, borderwidth=4, relief="raised")
entry_frame.grid(row=1, column=1, sticky="news", rowspan=3)

global entryspace
entryspace = Entry(root, justify="center", font=(50))
entryspace.grid(row=2, column=1, sticky="news", padx=10)

Label(entry_frame, text="Input", font=("Times", 20, "bold"), height=2).pack()


	#Solve Button
solve_button = Button(root, text="=", font=("Times", 24, "bold"), width=10, command=show_answer)
solve_button.grid(row=2, column=2)


	#Output
output_frame = Frame(root, borderwidth=4, relief="raised")
output_frame.grid(row=1, column=3, sticky="news", rowspan=3)

Label(output_frame, text="Ouput", font=("times", 20, "bold"), height=2).pack()
Frame(root, bg="white").grid(row=2, column=3, sticky="news", padx=10)

global userout_label
userout_label = Label(root, bg="white", font=20)
userout_label.grid(row=2, column=3)

	
	#Close
close_button = Button(root, text ="Close", command=exit)
close_button.grid(row=4, column=4)
root.bind("<KP_Enter>", exit)
root.bind("<Return>", show_answer)


root.mainloop()
"""

"""
	IDEEN

- (eingabe mit buttons mit den operatoren/funktionen etc)
- ausgabe mit Latex modul


- Rechnungsverlauf, in einer liste wo eingabe+antwort steht, über button erreichbar/ über der neuen rechnung





"""

"""
examples

f1 = "3x^2"
p1 = [mult, [3, ["pow", ["x", 2]]]]

f2 = "3x^2 + sin(2x)"
p2 = [add, [[mult, [3, ["pow", ["x", 2]]]],  ["sin", [mult, [2, "x"]]]]]

f3 = "ln(tan(x) + 8x^2) + exp(x^2)"
p3 = [add, [["ln", [add, [["tan", "x"], [mult, [8, ["pow", ["x", 5]]]]]]], ["exp", ["pow", ["x", 2]]]]]

"""
