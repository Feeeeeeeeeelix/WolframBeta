


functions = ["exp", "ln", "arccos", "arcsin", "arctan", "sin", "cos", "tan", "sqrt"]
alphabet = "qwertzuiopasdfghjklyxcvbnm"
numbers = "0123456789"
var = x = "x"

def inner_args(f):	# "f=(x+4)(x+6^x)ln(x)^2" ---> args=['x+4', 'x+6^x', 'x'], f='@@ln@^2')  

	def find_arg(f, i):
		arg = ""
		p = 0
		while i < len(f) and not(f[i] == ")" and p == 0):
			p = p +1*(f[i]=="(") -1*(f[i]==")")
			arg += f[i]	
			i += 1
		return arg, i
		
	args = []
	i = 0
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
	
"""
1. args entfernen
2. äusseren +/- splitten, einzelnt parsen
3. äusseren *,/ splitten, einzelnt parsen

EX: sin(sqrt(e^x+3)/2)
(x+4)(x+6^x)ln(x)^2
ln(cos(x^4))
-cos(x)*x^3
-sqrt(3*x)+3
"""

def parse(f):
	f = f.replace(" ", "")
	
	print(f"parse:{f}")			##
	
	if f in numbers+var:
		print(f"constfound: {f=}")
		return f
	
	f, innerargs = inner_args(f)
	
	print(f"{f=}, {innerargs=}")		##
	
	if "+" in f:
		summands = replace_arg(f.split("+"), innerargs)	
		print(f"{summands=}")				##
		return ["+", [parse(s) for s in summands]]
			
	if "-" in f:
		subs = replace_arg(f.split("-"), innerargs)	
		print(f"{subs=}")
		if len(subs) == 2 and subs[0] == "":
			return ["*", [-1, parse(subs[1])]]
			
						##
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
	
	if f[0] in "sctela":
		for func in functions:
			if func in f:
				return [func, parse(innerargs[0])]
	
	if f == "@":
		return parse(innerargs[0])
		
"""
['+', [['*', [-1, ['sqrt', ['*', ['3', 'x']]]]], '3']]  


['+',[
	['*',[
		-1, 
		['+', [
			['*', [
				['*', [
					['*', [
						'3', 
						['+', [
							['*', 
								[1]
							]
							]]
						],
						['/', [1, ['*', [2, ['sqrt', ['*', ['3', 'x']]]]]]]
						]]]]]]]]]] 


"""














def write(f):
	
	if type(f) == list:
		if f[0] in "+-*":		
			args = [str(write(i)) for i in f[1]]
			args = [i for i in args if i != "0"] if f[0] in "+-" else args

			if f[0] == "*":
				for fac in args:
					if "+" in fac or "-" in fac:
						args[args.index(fac)] = f"({fac})"
				if "0" in args:
					return "0"
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
			return f"{base}^{power}"
				
		if f[0] in functions:
			return f[0] + "(" + write(f[1]) + ")"		
	else:
		return f
		







def diff(f, var = "x"):
	# ~ print(f"diff: {f=}")
	def funcderivative(f):
		# ~ print(f"funcdiff: {f=}")

		
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
			else:
				return ["/", [["-", [["*", [f[1][0], diff(f[1][1])]], ["*", [f[1][1], diff(f[1][0])]]]], ["^", [f[1][1], 2]]]]
		
		elif f[0] == "+":
			return ["+", [diff(i) for i in f[1] if not isconst(i)]]			#(u+v)' = u' + v'
		elif f[0] == "-":
			return ["-", [diff(i) for i in f[1] if not isconst(i)]]			#(u-v)' = u' - v'
			
		elif f[0] == "^":
			base = f[1][0]
			exp = f[1][1]
			
			if var in str(base) and not var in str(exp):
				return ["*", [exp, diff(base), ["^", [base, ["-", [exp, 1]]]]]]
			if var in str(exp) and not var in str(base):
				return ["*", [[ln, base], diff(exp), ["^", [base, exp]]]]
			else:
				return ["*", [diff(["*", [exp, [ln, base]]]), ["^", [base, exp]]]]
				
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






func = "(x+4+0)*(x+6^x)*ln(x)^2"
func = "-sqrt(3*x)+3"
func = "-cos(x)*x^3"

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

# ~ p = parse(diffed.str)
# ~ print(f"{p = }")
# ~ print(f"{write(p) = }")
