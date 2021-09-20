from tkinter import *

from functions import *
from oldparser import *

	

mult, div, add, subs = "mult", "div", "add", "subs"
sin , cos, tan, exp, ln, pow = "sin", "cos", "tan", "exp", "ln", "pow"
functions = ["sin", "cos", "tan", "exp", "ln", "pow"]
var = x = "x"
	
dsin = lambda u: [mult, [diff(u), ["cos", u]]]
dcos = lambda u: [mult, [-1, diff(u), ["sin", u]]]
dtan = lambda u: [div, [diff(u), ["pow", [["cos", u], 2]]]]
dln = lambda u: [div, [diff(u), u]]
dexp = lambda u: [mult, [diff(u), ["exp", u]]]
dpow = lambda u: [mult, [u[1], diff(u[0]),["pow", [u[0], int(u[1])-1]]]]



F = [div, [2, var]]



def isconst(a):
	return True if (str(a).isalnum() or (a[0] == "-" and a[1:].isalnum())) and var not in str(a) else False


def diff(f):
	# print(f"{f = }") #debug
	
	if type(f) == list:
		if f[0] == "mult":
			if isconst(f[1][0]):							#case (ku)' = k*u'
				return [mult, [f[1][0], diff(f[1][1])]]
			else:
				return [add,[[mult, [diff(f[1][0]), f[1][1]]],[mult, [f[1][0], diff(f[1][1])]]]]
				
		elif f[0] == "div":
			if isconst(f[1][0]):							#case (k/u)' = k*(u^-1)'
				return [mult, [f[1][0], diff(["pow", [f[1][1], -1]])]]
			else:
				return ["div", [["subs", [["mult", [f[1][0], diff(f[1][1])]], ["mult", [f[1][1], diff(f[1][0])]]]], ["pow", [f[1][1], 2]]]]
		
		elif f[0] == "add":
			return [add, [diff(i) for i in f[1]]]			#(u+v)' = u' + v'
		elif f[0] == "subs":
			return [subs, [diff(i) for i in f[1]]]			#(u-v)' = u' - v'
			
		elif f[0] in functions:
			return eval("d"+f[0])(f[1])						# (f(g(x)))' -> df(g)
		
	return 1 if f == var else 0
	
# [subs, [[pow, [x, 56]], [sin, [exp,[add, [x, 89]]]]]


	

def readable(f):
	operations = {"add":" + ", "subs":" - ", "mult":"*"}

	if type(f) == list:
		if f[0] in operations.keys():		
			args = [str(readable(i)) for i in f[1]]		
			args = [i for i in args if i != "0"] if f[0] in ["add", "subs"] else args
			
			return operations[f[0]].join(args) if not ("0" in args and f[0] == "mult") else "0"
				
		if f[0] == "div":
			num = f"({readable(f[1][0])})" if type(f[1][0]) == list else f[1][0]
			denom = f"({readable(f[1][1])})" if type(f[1][1]) == list else f[1][1]
			return f"{num}/{denom}"
	
		if f[0] == "pow":
			base = f"({readable(f[1][0])})" if type(f[1][0]) == list and f[0] not in functions else readable(f[1][0])
			power = f"({readable(f[1][1])})" if type(f[1][1]) == list else f[1][1]
			return f"{base}^{power}"
			
		if f[0] in functions:
			return f[0] + "(" + readable(f[1]) + ")"

	return "x" if f == "x" else f











def calculate(userinput):
	
	for i, j in enumerate(userinput):
		if j not in "+-*/()^"+numbers+var+alphabet:
			return f"Invalid input: '{userinput[i]}'"
			
	if userinput:
		print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		print(f"{userinput      = }")
		parsed = parse(userinput, "x")
		print(f"\n{parsed         = }")
		differentiated = diff(parsed)
		print(f"\n{differentiated = }")
		readablee = readable(differentiated)
		print(f"\n{readablee      = }")
		return readablee
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
	entryspace = Entry(root, justify="center", font=(50), text=F)
	entryspace.grid(row=2, column=1, sticky="news", padx=10)
	
	Label(entry_frame, text="Input", font=("Times", 20, "bold"), height=2).pack()
	
	
		#Solve Button
	solve_button = Button(root, text="=", font=("times", 24, "bold"), width=10, command=show_answer)
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
