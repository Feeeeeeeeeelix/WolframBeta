import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import tkinter as tk

from functions import sin, exp

LARGE_FONT = ("Verdana", 12)
root = tk.Tk()

f = Figure(figsize=(5, 5), dpi=100)
a = f.add_subplot(111)


def rrange(a, b, n=1):
    l, x = [], a
    while x < b:
        l.append(x)
        x += n
    return l

x = rrange(0, 40, 0.1)
y = [exp(-x/10)*sin(x) for x in x]

a.plot(x, y)

canvas = FigureCanvasTkAgg(f, root)
# canvas.show()
canvas.get_tk_widget().pack(fill="both", expand=True)

# toolbar = NavigationToolbar2Tk(canvas, self)
# toolbar.update()
# canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

root.mainloop()
