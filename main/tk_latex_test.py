from tkinter import Tk, Frame, Label, Entry

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# matplotlib.use('TkAgg')
plt.rcParams["mathtext.fontset"] = "cm"

win = Tk()
sw = win.winfo_screenwidth()  # 1680
sh = win.winfo_screenheight()  # 1050
win.geometry(f"{sw}x{sh}")


def graph(text, i):
    tmptext = r"$" + text + "$"
    fig, canvas = canva[i]
    
    l = len(tmptext)
    size = int(2000/(l+50))
    
    fig.text(10/(l+18), 0.5, tmptext, fontsize=size)
    canvas.draw()
    print(f"{i}: {l = }, {size = }")


canva = []
for y in [0, 1]:
    for x in [0, 1, 2]:
        frame = Frame(win)
        frame.place(relx=.05+x*0.3, rely=.05+y*.4, relwidth=.27, relheight=0.336)
        label = Label(frame)
        label.pack()
        fig = Figure()
        canvas = FigureCanvasTkAgg(fig, master=label)
        canvas.get_tk_widget().pack(fill="both", expand=1)
        canva.append((fig, canvas))


f1 = "x^2"
f2 = r"x^2 + 34 \cdot x"
f3 = r"\frac{sin(x)}{x+ln(cos(x))} + 23"
f4 = r"\frac{sin(x)}{x+ln(cos(x))} + 23 \cdot x^{a + 3}"
f5 = r"23^x \cdot \frac{1}{tan(ln(x)) + 23 \cdot x} + 23 \cdot sin(23 \cdot x)"
f6 = r"23^x \cdot \frac{1}{tan(ln(x)) + 23 \cdot x} + 23 \cdot sin(23 \cdot x) + 23 \cdot sin(23 \cdot x)"

for i, text in enumerate([f1, f2, f3, f4, f5, f6]):
    graph(text, i)
    

win.bind('<Return>', graph)
win.bind("<KP_Enter>", quit)
win.mainloop()
