from functions import *

"""TO DO:

- Vereinfachen
- Parser mit "-" kompatibel ["-",[1,2,3]]
- 1/x*x -> 1
"""

FUNCTIONS = ["sqrt", "exp", "ln", "arccos", "arcsin", "arctan", "sin", "cos", "tan", "tanh", "cosh", "sinh", "arccosh", "arcsinh", "arctanh"]
ALPHABET = "qwertzuiopasdfghjklyxcvbnm"
NUMBERS = "0123456789"
# var = x = "x"




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
	if innerargs:
		n = 0
		fstr = str(f)
		for i in fstr:
			if i == "@":
				fstr = fstr.replace("@", f"({innerargs[n]})", 1)
				n += 1
		return eval(fstr)
	else:
		return f
		



#~~~~~~~~~~~~~~~~~~~~~~~~~~~ PARSE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



def parse(f):
	f = f.replace(" ", "")
	
	print(f"parse:{f}")
	
	if isfloat(f):		# f = constante
		return flint(f)
	if f[0] in "*/^":
		raise SyntaxError (f"first character cannot be '{f[0]}'")
	if f[-1] in "+-*/^":
		raise SyntaxError (f"last character cannot be '{f[0]}'")
	# if f == "e" or f == "π":
		# return 3
	if f in ALPHABET:
		return f
		
	f0 = f
	f, innerargs = inner_args(f)	#klammern und ihr inneres ersetzen
	
	if f == "@":
		return parse(innerargs[0])


	# implizierte Multiplikationen
	i = 0
	while i < len(f)-1:
		
		# 2@ / 2x / @@ / @x / ax(keine funktion) --> implizierte multiplikation
		if f[i] in NUMBERS+"@" and f[i+1] in "@"+ALPHABET or (f[i] in ALPHABET and f[i+1] in ALPHABET and "@" not in f):
			f = f[:i+1] + "*" + f[i+1:]

		# @2 -> verboten
		elif f[i] == "@" and f[i+1] in NUMBERS:
			raise SyntaxError (f"Invalid syntax : '){f[i+1]}'")

		# x2 -> verboten
		elif f[i] in ALPHABET and f[i+1] in NUMBERS:
			raise SyntaxError (f"Invalid syntax : '{f[i]}{f[i+1]}'")
			
		i += 1
		
		# 2-x / x-x / @-x --> implizierte addition mit negativem zweiten summand
		if f[i] == "-" and f[i-1] in "@"+NUMBERS+ALPHABET:
			f = f[:i] + "+" + f[i:]
		

	
	

	if "+" in f:		
		summands = replace_arg(f.split("+"), innerargs)

		consts, funcs = split_consts(summands, isfloat)
		consts = [sum([flint(s) for s in consts])] if consts else []
		summands = consts + [parse(s) for s in funcs]

		print(f"{summands=}, {consts = }, {funcs = }")				##
		return ["+", summands] if len(summands) > 1 else summands[1]


	if "*" in f:		
		factors = replace_arg(f.split("*"), innerargs)

		consts, funcs = split_consts(factors, isfloat)
		consts = [prod(consts)] if consts else []
	
		factors_ = {}
		for f in funcs:
			if f in factors_:
				factors_[f] += 1
			else:
				factors_[f] = 1
				
		factors = consts
		for s in factors_:
			if factors_[s] > 1:
				factors.append(["^", [parse(s), factors_[s]]])
			else:
				factors.append(parse(s))
		
		# factors = consts + funcs if consts != [1] else funcs

		print(f"{factors=}")		
		return ["*", factors] if len(factors) > 1 else factors[0] if 0 not in factors else 0

	
	if "/" in f:		
		div = replace_arg(f.split("/", 1), innerargs)
		print(f"{div = }")
	
		num, denom = parse(div[0]), parse(div[1])
		if not denom: raise ZeroDivisionError
		return ["/", [num, denom]] if num != denom else 1

	
	if "^" in f:
		base, exp = replace_arg(f.split("^", 1), innerargs)
		print(f"{base=}, {exp=}")			##
		return ["^", [parse(base), parse(exp)]]

	
	if f[0] == "-":
		return ["*", [-1, parse(f0[1:])]]


	# Funktion
	if f[0] in ALPHABET and f[-1] == "@":
		funcname = f[:-1]
		if funcname in FUNCTIONS:
			return [funcname, parse(innerargs[0])]
		else:
			raise SyntaxError("Unknown function: "+funcname)









#~~~~~~~~~~~~~~~~~~~~~~~~~~~ WRITE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



def write(f):
	print(f"write: {f=}")
	
	if type(f) == list:

		if f[0] == "+":
			
			args = [write(i) for i in f[1] if str(i) != "0"]
			
			print(f"sumargs: {args}")
			if not args:
				return 0
				
			consts, funcs = split_consts(args, isfloat)
			print(f"{consts=}, {funcs=}")
			
			consts = [str(sum(int(c) for c in consts))] if consts else []
			summands = consts + funcs
			sum_ = summands[0]
			for s in summands[1:]:
				sum_ += f" + {s}" if s[0] != "-" else f" - {s[1:]}"
			return sum_

		
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
			num = f[1][0]
			if type(num) == list:
				num = f"({write(num)})" if num[0] == "+" else write(num)
				
			denom = f[1][1]
			if type(denom) == list:
				denom = f"({write(denom)})" if denom[0] in "+*/" else write(denom)
			if not denom: raise ZeroDivisionError
			return 1 if num == denom else f"{num}/{denom}"
		
		if f[0] == "^":
			base = f"({write(f[1][0])})" if type(f[1][0]) == list and f[1][0][0] not in FUNCTIONS else write(f[1][0])
			power = f"({write(f[1][1])})" if type(f[1][1]) == list else f[1][1]
			print(f"{base=}, {power=}")
			try:
				
				power = eval(power)# if "-" in power else power
				print("EVAL: ", power)
			except:
				pass
			return f"{base}^{power}" if power != 1 and power != "(1)" else base if int(power) != 0 else 1
				
		if f[0] in FUNCTIONS:
			return f"{f[0]}({write(f[1])})"
	else:
		return f
		




#~~~~~~~~~~~~~~~~~~~~~~~~~~~ DIFF ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def diff(f):
	print(f"diff: {f}")
	
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
		
		darcsin = lambda u: ["/", [1, ["^", [["+", [1, ["*", [-1, ["^",[u, "2"]]]]]], 0.5]]]]
		darccos = lambda u: ["/", [-1, ["^", [["+", [1, ["*", [-1, ["^",[u, "2"]]]]]], 0.5]]]]
		darctan = lambda u: ["/", [1, ["+", [1, ["^", [u, 2]]]]]]

		darccosh = lambda u: ["/", [1, ["sqrt", ["+", [["^", [u, 2]], -1]]]]]
		darcsinh = lambda u: ["/", [1, ["sqrt", ["+", [["^", [u, 2]], 1]]]]]
		darctanh = lambda u: ["/", [1, ["+", [1, ["*", [-1, ["^", [u, 2]]]]]]]]

		u = f[1] #innere Funktion
		du = diff(u)

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
			
			print(f"diff:{constfactors=}, {funcfactors=}")

			
			if len(funcfactors) > 1:
				fpairs = []
				for i in range(len(funcfactors)): #funktionen können gleich sein, also mit index loopen
					fpairs.append(["*", [diff(funcfactors[i]), *funcfactors[:i], *funcfactors[i+1:]]])
				funcfactors = ["+", fpairs]
			else:
				funcfactors = diff(funcfactors[0])

				
			print(funcfactors)
			return ["*", [*constfactors, funcfactors]] if constfactors else funcfactors


		elif f[0] == "/":
			if isconst(f[1][0]):			# (k/u)' = (-1*k*du)/u^2
				return ["/", [["*", [-1, diff(f[1][1]), f[1][0]]], ["^", [f[1][1], 2]]]]
			elif isconst(f[1][1]):			# (u/k)' = u'/k
				return ["/", [diff(f[1][0]), f[1][1]]]
			else:							# (u/v)' = (v*u' - v'u)/v²
				return ["/", [["+", [["*", [diff(f[1][0]), f[1][1]]], ["*", [-1, diff(f[1][1]), f[1][0]]]]], ["^", [f[1][1], 2]]]]
		
		elif f[0] == "+":
			summands = [diff(i) for i in f[1] if not isconst(i)]
			return ["+", summands] if len(summands) > 1 else summands[0] if summands else 0
			
			
		elif f[0] == "^":
			base = f[1][0]
			exp = f[1][1]
			
			if VAR in str(base) and not VAR in str(exp):	# x^a
				return ["*", [exp, diff(base), ["^", [base, ["+", [exp, -1]]]]]]
			if VAR in str(exp) and not VAR in str(base):	# a^x
				return ["*", [["ln", base], diff(exp), ["^", [base, exp]]]]
			else:	#x^x
				return ["*", [diff(["*", [exp, ["ln", base]]]), ["^", [base, exp]]]]
				
		elif f[0] in FUNCTIONS:
			return funcderivative(f)
		
	return 1 if f == VAR else 0
	







class Function:
	def __init__(self, inputfunc, var):
		global VAR
		VAR = var
		if type(inputfunc) == str:
			self.str = inputfunc
			
			print("\nPARSING STR..")
			self.tree = parse(self.str)
			
			print("\nWRITING TREE..")
			self.str = write(self.tree)
		
			self.lam = lambda x: eval(self.str.replace("^", "**"))
		else:
			self.tree = inputfunc
			
			print("\nWRITING TREE..")
			self.str = write(self.tree)
			
			self.lam = lambda x: eval(self.str.replace("^", "**"))
			
	def diff(self):
		print("\nDIFF FUNC..")
		return Function(diff(self.tree), VAR)
	
	def __str__(self):
		return str(self.str)
	def __repr__(self):
		return str(self.str)

if __name__ == "__main__":
	

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
	# func = input("func = ")
	# func = "sin(sqrt(e^x+a)/2)"
	# func = "--1"
	func = "-2cos(x)-3x+e^-3x"
	func = "2*x*sin(x)*x"


	
	f = Function(func, "x")
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
	# print(f"\n{dsts = }")
