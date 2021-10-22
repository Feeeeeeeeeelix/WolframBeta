from tkinter import *
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


matplotlib.use('TkAgg')
plt.rcParams["mathtext.fontset"] = "cm"



def show():
	text = inputentry.get()
	text = r"$"+text+"$"
	wx.clear()
	wx.text(0.1, 0.5, text, fontsize = 8)
	canvas.draw()


root = Tk()

sw = root.winfo_screenwidth()		#1680
sh = root.winfo_screenheight()		#1050

root.geometry(f"{sw}x{sh}")
root.title("Wolframbeta")



	# Topframe
topframe = Frame(root, borderwidth=3, relief="raised")
topframe.place(y = 0, relx = 0.1, relheight = 0.1, relwidth=0.9)

logopic = PhotoImage(file="logo.png").subsample(2,2)
logo = Label(topframe, image=logopic)
logo.place(relx = 0.45, rely = 0.35)


	# Leftframe
leftframe = Frame(root, borderwidth=3, bg="#1e3799")
leftframe.place(y = 0, x = 0, relheight = 1, relwidth = 0.1)

bttn1 = Button(leftframe, text = "Analysis", bg = "#1e3799", fg = "white", highlightthickness = 0, highlightbackground = "#1e3799")
bttn1.place(rely = 0.001, x = 0, relwidth = 1, relheight = 0.09)

bttn2 = Button(leftframe, text = "Algebra", bg = "#1e3799", fg = "white", highlightthickness = 0)
bttn2.place(rely = 0.101, x = 0, relwidth = 1, relheight = 0.09)

bttn3 = Button(leftframe, text = "Numbers", bg = "#1e3799", fg = "white")
bttn3.place(rely = 0.201, x = 0, relwidth = 1, relheight = 0.09)


	# Mittleframe
mittleframe = Frame(root, borderwidth=3, relief="raised")
mittleframe.place(rely = 0.1, relx = 0.1, relheight = 0.8, relwidth=0.9)




inputframe = Frame(mittleframe, highlightbackground = "#1e3799", highlightthickness = 3)
inputframe.place(relx = 0.1, rely = 0.2, relwidth = 0.3, relheight = 0.6)

inputentry = Entry(inputframe)
inputentry.place(x = 0, y = 0, relwidth = 1, relheight = 1)
inputentry.insert(0, "\sin(x) = \sum_{n=0}^\infty (-1)^n\cdot \\frac{x^{2n+1}}{(2n+1)!}")


equal_bttn = Frame(mittleframe)#, highlightbackground = "#1e3799", highlightthickness = 3)
equal_bttn.place(relx = 0.45, rely = 0.45, relwidth = 0.1, relheight=0.1)
bttn = Button(equal_bttn, text = "=", command = show, highlightbackground = "#1e3799", highlightthickness = 3)
bttn.pack(expand=1, fill="both")

outputframe = Frame(mittleframe, highlightbackground = "#1e3799", highlightthickness = 3)
outputframe.place(relx = 0.6, rely = 0.2, relwidth = 0.3, relheight=0.6)

fig = matplotlib.figure.Figure(figsize=(1,1), dpi=200)
wx = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=outputframe)
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=0)
canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
wx.get_xaxis().set_visible(False)
wx.get_yaxis().set_visible(False)


show()

	# Bottomframe
bottomframe = Label(root, borderwidth=3, relief="raised")
bottomframe.place(relx = 0.1, rely = 0.9, relwidth = 0.9, relheight = 0.1)

exitbutton = Button(bottomframe, text = "Exit", command = exit, highlightthickness=1.5, highlightbackground="red")
exitbutton.place(relx = 0.85, rely = 0.2, relwidth=0.1, relheight=0.6)





root.bind("<Return>", quit)
root.mainloop()
