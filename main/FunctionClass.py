from functions import *

"""TO DO:

- Vereinfachen
- Parser mit "-" kompatibel
- 0 + 0 = tete a toto = nix
-  ["-",[1,2,3]]
- a/b/c  = a*c/b

"""

FUNCTIONS = ["sqrt", "exp", "ln", "arccos", "arcsin", "arctan", "sin", "cos", "tan", "tanh", "cosh", "sinh", "arccosh", "arcsinh", "arctanh"]
ALPHABET = "qwertzuiopasdfghjklyxcvbnm"
NUMBERS = "0123456789"
var = x = "x"




def isfloat(n):
    try: 
        float(n)
    except ValueError: 
        return False
    return True
    
def prod(iterable):
	prod = 1
	for factor in iterable:
		try:
			prod *= int(factor)
		except ValueError:
			raise ValueError ("non-int factor found: "+factor)
	return prod
   
def flint(x):
	return float(x) if int(x) != float(x) else int(x)
	
def split_consts(f, test):
	constants, functions = [], []
	for arg in f:	
		if test(arg):
			constants.append(arg)
		else:
			functions.append(arg)
	return constants, functions



def inner_args(f):	# "f=3(x+4)(x+6^x)ln(x)^2" ---> args=['3', 'x+4', 'x+6^x', 'x'], f='3@@ln@^2'  

	def find_arg(f, i):
		arg, p = "", 0
		
		while i < len(f) and not(f[i] == ")" and p == 0):
			p = p + (f[i]=="(") - (f[i]==")")
			arg += f[i]	
			i += 1
		return arg, i
		
	args, i = [], 0
	while i < len(f):
		if f[i] == "(":
			arg, i = find_arg(f, i+1)
			args.append(arg)	
		i += 1

	for arg in args:
		f = f.replace(f"({arg})", "@")
		
	return f, args
	
def replace_arg(f, innerargs):
	n = 0
	fstr = str(f)
	for i in fstr:
		if i == "@":
			fstr = fstr.replace("@", f"({innerargs[n]})", 1)
			n += 1
	return eval(fstr)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~ PARSE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



def parse(f):
	f = f.replace(" ", "")	#Leerzeichen entfernen
	f = f.replace("**", "^")
	
	# print(f"parse:{f}")
	
	if f[0] in "*/^":
		raise SyntaxError (f"first character cannot be '{f[0]}'")
	if f[-1] in "+-*/^":
		raise SyntaxError (f"last character cannot be '{f[0]}'")
	if isfloat(f):		# f = constante
		return flint(f)
	if f == var:		# f = var
		return var
	if all(i in ALPHABET for i in f):
		return f
	
	
	f, innerargs = inner_args(f)	#klammern und ihr inneres ersetzen

	#2@@ln@^2+@ -> 2*@*@*ln@^2+@
	i = 0
	while i < len(f)-1:
		# print(f"{i = }, {f[i] =  }, {f[i+1]=}")
		if f[i] in NUMBERS+var+"@" and f[i+1] == "@" or f[i] in "@"+NUMBERS and f[i+1]in ALPHABET:
			f = f[:i+1] + "*" + f[i+1:]
			# print(f"mult: {f=}")
		i += 1


	
	# print(f"{f=}, {innerargs=}")
	
	# Summe
	if "+" in f:		
		summands = replace_arg(f.split("+"), innerargs)	
		# print(f"{summands=}")				##
		return ["+", [parse(s) for s in summands]]
		
	# Substraktion
	if "-" in f:
		subs = replace_arg(f.split("-"), innerargs)	
		# print(f"{subs=}")
		
		if len(subs) == 2 and subs[0] == "":
			# print("minus")
			return ["*", [-1, parse(subs[1])]]
			
		return ["-", [parse(s) for s in subs]]


	if "*" in f:		
		factors = replace_arg(f.split("*"), innerargs)
		
		# zwischen konstanten und funktionen unterscheiden, dann konstanten zsmmultiplizieren
		
		consts, funcs = split_consts(factors, isfloat)
		consts = [prod(consts)] if consts else []
		factors = consts + [parse(s) for s in funcs]

		# print(f"{factors=}")		
		return ["*", factors] if len(factors) > 1 else factors[0] #if factors else 1

	

	if "/" in f:		
		div = replace_arg(f.split("/"), innerargs)
		# print(f"{div=}")			##
		
		if len(div) == 2:
			return ["/", [parse(s) for s in div]]
		else:
			return ["/", [div[0], ["*", [parse(s) for s in div[1:]]]]]

		
		return ["/", [parse(s) for s in div]]
				
	if "^" in f:
		base, exp = replace_arg(f.split("^", 1), innerargs)
		# print(f"{base=}, {exp=}")			##
		return ["^", [parse(base), parse(exp)]]

	# Funktion
	if f[0] in "sctela":
		funcname = f[:-1]
		if funcname in FUNCTIONS:
			return [funcname, parse(innerargs[0])]
		else:
			raise Exception("Unknown function: "+funcname)
		
		
	
	if f == "@":
		return parse(innerargs[0])




#~~~~~~~~~~~~~~~~~~~~~~~~~~~ WRITE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



def write(f):
	# print(f"write: {f=}")
	
	if type(f) == list:

		if f[0] in "+-":
			
			args = [write(i) for i in f[1] if str(i) != "0"]
			
			# print(f"sumargs: {args}")
			if not args:
				return 0
				
			consts, funcs = split_consts(args, isfloat)
			
			# print(f"{consts=}, {funcs=}")
			
			consts = eval(f[0].join([str(i) for i in consts])) if consts else 0
			
			if consts:
				return {"+":" + ", "-":" - "}[f[0]].join([str(consts)]+funcs) if funcs else consts
			else:
				return  {"+":" + ", "-":" - "}[f[0]].join(funcs) if funcs else 0

		
		if f[0] == "*":
			
			args = []
			for i in f[1]:
				factor = str(write(i))

				if factor == "0":
					return 0
				if type(i) == list and i[0] in "+-":
					factor = f"({factor})"
				if factor != "1" and factor != "ln(e)":
					args.append(factor)
					
			consts, funcs = split_consts(args, isfloat)
			consts = [str(prod(consts))] if consts else []
			# funcs = "*".join(funcs) if funcs else ""
			
			return "*".join(consts+funcs) if consts+funcs else 1
	
		if f[0] == "/":
			num = f"({write(f[1][0])})" if type(f[1][0]) == list else f[1][0]
			denom = f"({write(f[1][1])})" if type(f[1][1]) == list else f[1][1]
			return f"{num}/{denom}"
		
		if f[0] == "^":
			base = f"({write(f[1][0])})" if type(f[1][0]) == list and f[1][0][0] not in FUNCTIONS else write(f[1][0])
			power = f"({write(f[1][1])})" if type(f[1][1]) == list else f[1][1]
		
			try:
				power = eval(power)# if "-" in power else power
				# print("EVAL: ", power)
			except:
				pass
			return f"{base}^{power}" if power != 1 and power != "(1)" else base if int(power) != 0 else 1
				
		if f[0] in FUNCTIONS:
			return f"{f[0]}({write(f[1])})"
	else:
		return f
		




#~~~~~~~~~~~~~~~~~~~~~~~~~~~ DIFF ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def diff(f, VAR = "x"):
	print(f"diff: {f} {VAR=}")
	
	def funcderivative(f):
	
		dln = lambda u: ["/", [1, u]]
		dlog = lambda u: ["/", [1, u]]
		dexp = lambda u: ["exp", u]
		dsqrt = lambda u: ["/", [1, ["*", [2, ["sqrt", u]]]]]
		
		dsin = lambda u: ["cos", u]
		dcos = lambda u: ["*", [-1, ["sin", u]]]
		dtan = lambda u: ["/", [1, ["^", [["cos", u], 2]]]]
		
		dsinh = lambda u: ["cosh", u]
		dcosh = lambda u: ["sinh", u]
		dtanh = lambda u: ["/", [1, ["^", [["cosh", u], 2]]]]
		
		darcsin = lambda u: ["/", [1, ["^", [["-",[1,  ["^",[u, "2"]]]], 0.5]]]]
		darccos = lambda u: ["/", [-1, ["^", [["-",[1,  ["^",[u, "2"]]]], 0.5]]]]
		darctan = lambda u: ["/", [1, ["+", [1, ["^", [u, 2]]]]]]

		darccosh = lambda u: ["/", [1, ["sqrt", ["-", [["^", [u, 2]], 1]]]]]
		darcsinh = lambda u: ["/", [1, ["sqrt", ["+", [["^", [u, 2]], 1]]]]]
		darctanh = lambda u: ["/", [1, ["-", [1, ["^", [u, 2]]]]]]

		u = f[1] #innere Funktion
		du = diff(u, VAR)

		if du == 0:
			return 0
		elif du == 1:
			return eval(f"d{f[0]}")(u)	
		else:
			return ["*", [du, eval("d"+f[0])(u)]]

	
	def isconst(a):
		return not VAR in str(a)

	if isconst(f):
		return 0

	if type(f) == list:
		if f[0] == "*": #2*4*sinx*x
			constfactors, funcfactors = split_consts(f[1], isconst)
			
			# print(f"diff:{constfactors=}, {funcfactors=}")

			if len(funcfactors) == 1:
				return ["*", [*constfactors, diff(funcfactors[0], VAR)]]
			else:
				if constfactors:
					return ["*", [*constfactors, ["+", [["*", [diff(f, VAR), *[g for g in funcfactors if g != f]]] for f in funcfactors]]]]
				else:
					return ["+", [["*", [diff(f, VAR), *[g for g in funcfactors if g != f]]] for f in funcfactors]]


		elif f[0] == "/":
			if isconst(f[1][0]):							#case (k/u)' = k*(u^-1)'
				return ["*", [f[1][0], diff(["^", [f[1][1], -1]], VAR)]]
			else:		# (u/v)' = (v*u' - v'u)/v²
				return ["/", [["-", [["*", [f[1][0], diff(f[1][1], VAR)]], ["*", [f[1][1], diff(f[1][0], VAR)]]]], ["^", [f[1][1], 2]]]]
		
		elif f[0] == "+":
			summands = [diff(i, VAR) for i in f[1] if not isconst(i)]
			return ["+", summands] if len(summands) > 1 else summands[0] if summands else 0
			
		elif f[0] == "-":
			return ["-", [diff(i, VAR) for i in f[1] if not isconst(i)]]			#(u-v)' = u' - v'
			
		elif f[0] == "^":
			base = f[1][0]
			exp = f[1][1]
			
			if VAR in str(base) and not VAR in str(exp):	# x^a
				return ["*", [exp, diff(base, VAR), ["^", [base, ["-", [exp, 1]]]]]]
			if VAR in str(exp) and not VAR in str(base):	# a^x
				return ["*", [["ln", base], diff(exp, VAR), ["^", [base, exp]]]]
			else:	#x^x
				return ["*", [diff(["*", [exp, ["ln", base]]], VAR), ["^", [base, exp]]]]
				
		elif f[0] in FUNCTIONS:
			return funcderivative(f)
		
	return 1 if f == VAR else 0
	







class Function:
	def __init__(self, inputfunc):
		if type(inputfunc) == str:
			self.str = inputfunc
			# print("\nPARSING STR..")
			self.tree = parse(self.str)
			# print("\nWRITING TREE..")
			self.str = write(self.tree)
			self.lam = lambda x: eval(self.str.replace("^", "**"))
		else:
			self.tree = inputfunc
			# print("\nWRITING TREE..")
			self.str = write(self.tree)
			self.lam = lambda x: eval(self.str.replace("^", "**"))
			
	def diff(self, var = "x"):
		# print("\nDIFF FUNC..")
		return Function(diff(self.tree, var))
	
	# def lam(self, var = "x"):
		# return lambda var: eval(self.str.replace("^", "**"))
	def __str__(self):
		return self.str
	def __repr__(self):
		return self.str

if __name__ == "__main__":
	
	# f = Function("cosh(x)")
	# print(f.lam(2))

	func = "(x+4)(x+6^x)ln(x)^2"
	func = "as*x^3+x^a*bc"
	func = "-sqrt(3*x)+3"
	func = "-tan(x)*x^3"
	func = "3*4*x"
	func = "x+sin(x)"
	# func = "sihn(x)"
	# func = "x^abc+ass"
	# func = "arctanh(x)"
	# func = "1/7/x"
	# func = "x^x^x"
	# func = "2*x+3*x+34"
	
	f = Function(func)
	baum = f.tree
	
	print()
	print(f"{func = }\n")
	print(f"{baum = }\n")
	print(f"{f.str = }\n")
	
	diffed = f.diff()
	print(f"\n\n{diffed.tree = }\n")
	print(f"{diffed = }\n")
	
	
	# dst = parse(diffed.str)
	# print(f"\n{dst = }\n")
	# dsts = write(dst)
	# print(f"{dsts = }")
