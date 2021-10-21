from tkinter import *
# from tkinter import ttk

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


matplotlib.use('TkAgg')

plt.rcParams["mathtext.fontset"] = "cm"



# win = Tk()

# # Set the size of the window
# # win.geometry("700x350")

# # Set the title of the window
# # win.title("LaTex Viewer")

# # Define a function to get the figure output
# def graph(text):
   # # Get the Entry Input
   # tmptext = entry.get()
   # tmptext = r"$"+tmptext+"$"
   # # Clear any previous Syntax from the figure
   # wx.clear()
   # wx.text(0.2, 0.6, tmptext, fontsize = 20)
   # canvas.draw()
# # Create a Frame object
# frame = Frame(win)
# frame.pack()
# # Create an Entry widget
# var = StringVar()
# entry = Entry(frame, width=70, textvariable=var)
# entry.pack()

# # Add a label widget in the frame
# label = Label(frame)
# label.pack()

# # Define the figure size and plot the figure
# fig = matplotlib.figure.Figure(figsize=(7, 4), dpi=200)
# wx = fig.add_subplot(111)
# canvas = FigureCanvasTkAgg(fig, master=label)
# canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
# canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

# # Set the visibility of the Canvas figure
# wx.get_xaxis().set_visible(False)
# wx.get_yaxis().set_visible(False)

# entry.insert(0, r"\sin(x) = \sum_{n=0}^\infty (-1)^n\cdot  \frac{x^{2n+1} } {(2n+1)!}")
# graph(None)

# win.bind('<Return>', graph)
# win.mainloop()




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



root = Tk()

sw = root.winfo_screenwidth()		#1680
sh = root.winfo_screenheight()		#1050

root.geometry(f"{sw}x{sh}")
root.title("WolframBeta")

title = Label(root, text="WolframBeta   " + r"$\pi = 3$")
title.pack()










"""
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
"""

root.mainloop()
