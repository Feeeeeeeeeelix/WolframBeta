


functions = ["sin", "cos", "tan", "exp", "ln", "arccos", "arcsin", "arctan"]
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
		print(f"{subs=}")				##
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
			
			return f[0].join(args)
				
		if f[0] == "/":
			num = f"({write(f[1][0])})" if type(f[1][0]) == list else f[1][0]
			denom = f"({wrtie(f[1][1])})" if type(f[1][1]) == list else f[1][1]
			return f"{num}/{denom}"
		
		if f[0] == "^":
			base = f"({write(f[1][0])})" if type(f[1][0]) == list and f[1][0][0] not in functions else write(f[1][0])
			power = f"({write(f[1][1])})" if type(f[1][1]) == list else f[1][1]
			return f"{base}^{power}"
				
		if f[0] in functions:
			return f[0] + "(" + write(f[1]) + ")"
			
	else:
		return f
		

dsin = lambda u: [mult, [diff(u), ["cos", u]]]
dcos = lambda u: [mult, [-1, diff(u), ["sin", u]]]
dtan = lambda u: [div, [diff(u), ["pow", [["cos", u], 2]]]]
dln = lambda u: [div, [diff(u), u]]
dexp = lambda u: [mult, [diff(u), ["exp", u]]]
dpow = lambda u: [mult, [u[1], diff(u[0]),["pow", [u[0], int(u[1])-1]]]]



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
	
		
		
func = "(x+4+0)*(x+6^x)*ln(x)^2"

baum = parse(func)
diffed = diff(baum)
print()
print(func, "\n")
print(baum,"\n")
print(write(baum),"\n")
print(write(diffed),"\n")
