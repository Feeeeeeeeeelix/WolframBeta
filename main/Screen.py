from tkinter import *
# import matplotlib
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# matplotlib.use('TkAgg')
# plt.rcParams["mathtext.fontset"] = "cm"



def calculate():
	text = inputentry.get()
	text = r"$"+text+"$"
	outlabel["text"] = text
	# wx.clear()
	# wx.text(0.1, 0.5, text, fontsize = 8)
	# canvas.draw()


root = Tk()

sw = root.winfo_screenwidth()		#1680
sh = root.winfo_screenheight()		#1050
sw = 700
sh = 500


root.geometry(f"{sw}x{sh}")
root.title("Wolframbeta")

lblue = "#1e3799"
dblue = "#001B81"


	# Topframe
topframe = Frame(root, borderwidth=3, relief="raised")
topframe.place(y = 0, relx = 0.1, relheight = 0.1, relwidth=0.9)

logopic = PhotoImage(file="logo.png").subsample(2,2)
logo = Label(topframe, image=logopic)
logo.place(relx = 0.45, rely = 0.35)




	# Leftframe
leftframe = Frame(root, bg = lblue)
leftframe.place(y = 0, x = 0, relheight = 1, relwidth = 0.1)

whitebg = Label(leftframe)
whitebg.place(rely = 0.01, relx = 0.05, relwidth = 0.9, relheight = 0.29)

sep = Label(leftframe, bg = "white")
sep.place(x = 0, rely = 0.299, relwidth = 1, height = 2)

selectframe = Frame(leftframe, bg = lblue)
selectframe.place(x = 0, rely = 0.301, relwidth = 1, relheight = 0.69) #(nice)


def SelectionButtons(container, function, *names):
	buttons = []
	for i, name in enumerate(names):
		button = Button(container, text = name, bg = lblue, fg = "white", highlightthickness = 0, bd = 0, activebackground = dblue, activeforeground = "white", command = lambda n=i+1: eval(function)(n))
		buttons.append(button)
		button.place(rely = i/10, x = 0, relwidth = 1, relheight = 0.0985)
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
	
def algebra(n):
	print("algebra: ", n)
	
def numbers(n):
	print("numbers: ", n)


	
buttons = SelectionButtons(leftframe, "select", "Analysis", "Algebra", "Numbers")


	# Mittleframe
mittleframe = Frame(root, borderwidth=3, relief="raised")
mittleframe.place(rely = 0.1, relx = 0.1, relheight = 0.8, relwidth=0.9)




inputframe = Frame(mittleframe, highlightbackground = lblue, highlightcolor = "green", highlightthickness=2, bg = "white")
inputframe.place(relx = 0.1, rely = 0.2, relwidth = 0.3, relheight = 0.6)

inputentry = Entry(inputframe, bd=0, highlightthickness=0)
inputentry.place(relx = 0.05, rely = 0.05, relwidth = 0.9, relheight = 0.3)
inputentry.insert(0, "\sin(x) = \sum_{n=0}^\infty (-1)^n\cdot \\frac{x^{2n+1}}{(2n+1)!}")
inputentry.bind("<Return>", calculate)

bttn = Button(mittleframe, text = "=", command = calculate)
bttn.place(relx = 0.45, rely = 0.45, relwidth = 0.1, relheight=0.1)

outputframe = Frame(mittleframe, highlightbackground = lblue, highlightthickness = 2)
outputframe.place(relx = 0.6, rely = 0.2, relwidth = 0.3, relheight=0.6)

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
bottomframe.place(relx = 0.1, rely = 0.9, relwidth = 0.9, relheight = 0.1)

exitbutton = Button(bottomframe, text = "Exit", command = exit, highlightthickness=1.5, highlightbackground="red")
exitbutton.place(relx = 0.85, rely = 0.2, relwidth=0.1, relheight=0.6)





root.bind("<Return>", quit)
root.mainloop()
