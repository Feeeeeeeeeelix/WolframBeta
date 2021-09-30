


functions = ["exp", "ln", "arccos", "arcsin", "arctan", "sin", "cos", "tan", "sqrt"]
alphabet = "qwertzuiopasdfghjklyxcvbnm"

def isfloat(n):
    try: 
        float(n)
    except ValueError: 
        return False
    return True
    
numbers = "0123456789"
var = x = "x"

def inner_args(f):	# "f=3(x+4)(x+6^x)ln(x)^2" ---> args=['3', 'x+4', 'x+6^x', 'x'], f='@@ln@^2'  

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
	

def parse(f):
	f = f.replace(" ", "")	#Leerzeichen entfernen
	
	print(f"parse:{f}")
	
	if isfloat(f):		# f = constante
		return float(f) if int(f) != float(f) else int(f)
	if f == var:		# f = var
		return var
	
	
	f, innerargs = inner_args(f)	#klammern und ihr inneres ersetzen

	#2@@ln@^2+@ -> 2*@*@*ln@^2+@
	i = 0
	while i < len(f)-1:
		# print(f"{i = }, {f[i] =  }, {f[i+1]=}")
		if f[i] in numbers+var+"@" and f[i+1] == "@" or f[i]=="@" and f[i+1]in alphabet:
			f = f[:i+1] + "*" + f[i+1:]
			# print(f"mult: {f=}")
		i += 1

	
	# for i, j in enumerate(f):
		# print(f"{i=}, {j=}")
		# if i<len(f)-1 and j in numbers+alphabet+"@" and f[i+1] == "@":
			
			
		
	


	
	print(f"{f=}, {innerargs=}")
	
	# Summe
	if "+" in f:		
		summands = replace_arg(f.split("+"), innerargs)	
		print(f"{summands=}")				##
		return ["+", [parse(s) for s in summands]]
		
	# Substraktion
	if "-" in f:
		subs = replace_arg(f.split("-"), innerargs)	
		print(f"{subs=}")
		
		if len(subs) == 2 and subs[0] == "":
			print("minus")
			return ["*", [-1, parse(subs[1])]]
			
		return ["-", [parse(s) for s in subs]]

	if "*" in f:		
		factors = replace_arg(f.split("*"), innerargs)
		print(f"{factors=}")			##
		return ["*", [parse(s) for s in factors]]
	

	if "/" in f:		
		div = replace_arg(f.split("/"), innerargs)
		print(f"{div=}")			##
		return ["/", [parse(s) for s in div]]
				
	if "^" in f:
		base, exp = replace_arg(f.split("^"), innerargs)
		print(f"{base=}, {exp=}")			##
		return ["^", [parse(base), parse(exp)]]

	# Funktion
	if f[0] in "sctela":
		funcname = f[:-1]
		if funcname in functions:
			return [funcname, parse(innerargs[0])]
		if f[-1] != "@":	#konstante
			return f
		else:
			raise Exception("Unknown function: "+funcname)
		
		
	
	if f == "@":
		return parse(innerargs[0])
		





def write(f):
	
	if type(f) == list:
		if f[0] in "+-*":		
			args = [str(write(i)) for i in f[1]]
			args = [i for i in args if i != "0"] if f[0] in "+-" else args

			if f[0] == "*":
				if "0" in args:
					return "0"
					
				# for fac in f[1]:
					# print(f"{fac=}")
					# if type(fac) == list and fac[0] in "+-":
						# print("yey")
						# args[f[1].index(fac)] = f"({fac})"
						
				for fac in args:
					if "+" in fac or "-" in fac:
						args[args.index(fac)] = f"({fac})"
						
				while "1" in args:
					args.remove("1")
			
			return {"+":" + ", "-":" - ", "*":"*"}[f[0]].join(args)
				
		if f[0] == "/":
			num = f"({write(f[1][0])})" if type(f[1][0]) == list else f[1][0]
			denom = f"({write(f[1][1])})" if type(f[1][1]) == list else f[1][1]
			return f"{num}/{denom}"
		
		if f[0] == "^":
			base = f"({write(f[1][0])})" if type(f[1][0]) == list and f[1][0][0] not in functions else write(f[1][0])
			power = f"({write(f[1][1])})" if type(f[1][1]) == list else f[1][1]
		
			try:
				power = eval(power)
			except:
				pass
			return f"{base}^{power}" if power != 1 else base if power != 0 else 1
				
		if f[0] in functions:
			return f"{f[0]}({write(f[1])})"
	else:
		return f
		







def diff(f, var = "x"):

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
		
		u = f[1] #innere Funktion
		du = diff(u)

		if du == 0:
			return 0
		elif du == 1:
			return eval(f"d{f[0]}")(u)	
		else:
			return ["*", [du, eval("d"+f[0])(u)]]

	
	def isconst(a):
		return not var in str(a)
	
	if type(f) == list:
		if f[0] == "*": #2*4*sinx*x
			constfactors = [factor for factor in f[1] if isconst(factor)]
			funcfactors = [factor for factor in f[1] if factor not in constfactors]
			
			# ~ print(f"{constfactors=}, {funcfactors=}")

			if len(funcfactors) == 1:
				return ["*", [*constfactors, diff(funcfactors[0])]]
			else:
				return ["*", [*constfactors, ["+", [["*", [diff(f), *[g for g in funcfactors if g != f]]] for f in funcfactors]]]]
	
		elif f[0] == "/":
			if isconst(f[1][0]):							#case (k/u)' = k*(u^-1)'
				return ["*", [f[1][0], diff(["^", [f[1][1], -1]])]]
			else:		# (u/v)' = (v*u' - v'u)/v²
				return ["/", [["-", [["*", [f[1][0], diff(f[1][1])]], ["*", [f[1][1], diff(f[1][0])]]]], ["^", [f[1][1], 2]]]]
		
		elif f[0] == "+":
			return ["+", [diff(i) for i in f[1] if not isconst(i)]]			#(u+v)' = u' + v'
			
		elif f[0] == "-":
			return ["-", [diff(i) for i in f[1] if not isconst(i)]]			#(u-v)' = u' - v'
			
		elif f[0] == "^":
			base = f[1][0]
			exp = f[1][1]
			
			if var in str(base) and not var in str(exp):	# x^a
				return ["*", [exp, diff(base), ["^", [base, ["-", [exp, 1]]]]]]
			if var in str(exp) and not var in str(base):	# a^x
				return ["*", [["ln", base], diff(exp), ["^", [base, exp]]]]
			else:	#x^x
				return ["*", [diff(["*", [exp, ["ln", base]]]), ["^", [base, exp]]]]
				
		elif f[0] in functions:
			return funcderivative(f)
		
	return 1 if f == var else 0
	



class Function:
	def __init__(self, inputfunc):
		if type(inputfunc) == str:
			self.str = inputfunc
			self.tree = parse(self.str)
			self.str = write(self.tree)
		else:
			self.tree = inputfunc
			self.str = write(self.tree)
			
	def diff(self, var = "x"):
		return Function(diff(self.tree, var))
	
	def lam(self, var = "x"):
		return lambda var: eval(self.str.replace("^", "**"))





if __name__ == "__main__":
		
	func = "(x+4)(x+6^x)ln(x)^2"
	# func = "as*x^3+x^abc"
	# func = "-sqrt(3*x)+3"
	# func = "-tan(x)*x^3"
	
	print("PARSE\n\n")
	f = Function(func)
	
	baum = f.tree
	
	# ~ print(f"\nf(x) = {func}\n\nTree: {baum}\n\nwrite: {f.str}\n\nf'(x): {diffed.tree}\n\nf'(x) = {diffed.str}")
	
	print()
	print(f"{func = }\n")
	print(f"{baum = }\n")
	print(f"{f.str = }\n")
	
	diffed = f.diff()
	print(f"{diffed.tree = }\n")
	print(f"{diffed.str = }\n")
	
	
	dst = parse(diffed.str)
	print(f"\n{dst = }\n")
	dsts = write(dst)
	print(f"{dsts = }")
