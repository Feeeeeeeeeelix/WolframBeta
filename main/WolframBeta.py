from tkinter import *

from functions import *
from FunctionClass import *
from analysis import *
	







def calculate(userinput):
	
	for i, j in enumerate(userinput):
		if j not in "+-*/()^"+numbers+var+alphabet:
			return f"Invalid input: '{userinput[i]}'"
			
	if userinput:

		F = Function(userinput)
		parsed = F.tree
		diffed = F.diff()
		difftree = diffed.tree
		diffstr = diffed.str

	
		print(f"{userinput    = }")
		print(f"\n{parsed       = }")
		print(f"\n{difftree     = }")
		print(f"\n{diffstr      = }")
		print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		
		return diffstr
	else:
		return ""
	
	




def show_answer(event = None):
	userinput = entryspace.get()
	answer = calculate(userinput)	
	userout_label["text"] = answer




def Create_Screen():
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
	
Create_Screen()







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
