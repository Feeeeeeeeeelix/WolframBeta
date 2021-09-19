from read import *


alphabet = "sincostanarchlnexpabs"
numbers = "0123456789e"
var = x = "x"

def find_arg(f, i): 	# f = function, i = aktueller index vom ersten "("
	# print(f"find_arg: {i=} {f[i]=}")	
	i += 1
	arg = ""
	parentheses = 0
	while not(f[i] == ")" and parentheses == 0):
		
		
		if f[i] == "(":
			parentheses += 1
		elif f[i] == ")":
			parentheses -= 1
		
		# print(f"{i=} {f[i]=} {parentheses=}")	
		
		arg += f[i]
		i += 1		
	return arg, i+1
	
	
def find_number(f, i):
	# print(f"find_number: {i=} {f[i]=}")	
	number = ""
	while i < len(f) and f[i] in numbers+var:
		number += f[i]
		i += 1
	return number, i
	
def power(f, i, base):
	# print(f"power: {i=} {f[i]=} {base=}")	
	
	if f[i] == "(":
		arg, i = find_arg(f, i)
		power = parse(arg, var)
	else:
		power, i = find_number(f, i)		
	return ["pow", [parse(base, var), power]], i
	
def function(f, i):
	# print(f"function: {i=} {f[i]=}")	
	funcname = ""
	while f[i] in alphabet:
		funcname += f[i]
		i += 1
		
	arg = ""
	if f[i] == "(":
		arg, i = find_arg(f, i)
	
	return [funcname, parse(arg, var)], i

def var_found(f, i, var):
	# print(f"var_found: {i=} {f[i]=} {f=}")
	i += 1
	if i < len(f):
		baum, i = operation(f, i ,var)
	else:
		baum = var
		
	return baum, i

def const_found(f, i):
	# print(f"const_found: {i=} {f[i]=} {f=}")	
			
	const = ""
	while i < len(f) and f[i] in numbers:
		const += f[i]
		i += 1
		
	if i < len(f):
		baum, i = operation(f, i, const)
	else:
		baum = const
	return baum, i

def find_next_factor(f, i, first_arg):
	# print(f"find_next_factor: {i=} {f[i]=} {f=} {first_arg=}")	

	args = [first_arg]
	while i < len(f) and f[i] in "*( "+alphabet:		#()*args**
		# print(f"fac: {f[i]=}")
		i += 1*(f[i] in "* ")
		
		if f[i] == "(":				#()*()
			arg, i = find_arg(f, i)
			args.append(parse(arg, var))
			
		elif f[i] in numbers:		#()*a
			arg, i = const_found(f, i)
			args.append(arg)
			
		elif f[i] == var:			#()*var
			arg, i = var_found(f, i, var)
			args.append(arg)
				
		elif f[i] in alphabet:		#()*function()
			arg, i = function(f, i)
			args.append(arg)
			
	# print(f"fac2: {f[i]=} {i=}")	if i <len(f)else ""
	# print(f"args(factors): {args=}")	
	return ["mult", args], i
	
def find_denominateur(f, i, baum):
	# print(f"find_denominateur: {baum=} {i=} {f[i]=}")
	
	denominateur = ""
	i += 1
	if f[i] == "(":
		denominateur, i = find_arg(f, i)
	else:
		while i < len(f) and f[i] not in "(+-*":
			denominateur += f[i]
			i += 1
	return ["div", [baum, parse(denominateur, var)]], i
	
def find_next_summand(f, i, first):
	sign = f[i]
	op = "add" if sign == "+" else "subs"	
	# print(f"{op}: {i=} {f[i]=}")
	
	next_summand = []
	i += 1
	p = 0
	while i < len(f):
		summand = ""
		while i < len(f) and not(f[i] == sign and p == 0):
			p += 1*(f[i]=="(") - 1*(f[i]==")")
			summand += f[i]
			i += 1
		next_summand.append(summand)
		i += 1
	baum = [op, [first]+[parse(i, var) for i in next_summand]]
	# print(f"{first=}{baum=}")
	return baum, i
	
def operation(f, i, arg):
	# print(f"operation: {i=} {f[i]=} {f=} {arg=}")
	
	if f[i] == "^":
		baum, i = power(f, i+1, arg)
	elif f[i] in "*("+alphabet:
		baum, i = find_next_factor(f, i, arg)
	elif f[i] == "/":
		baum, i = find_denominateur(f, i, arg)
	elif f[i] in "+-":
		baum, i = find_next_summand(f, i, arg)
	else:
		baum = arg
		
	return baum, i


def argument(f, i):
	# print(f"argument: {i=} {f[i]=} {f=}")
	
	if f[i] == var:
		baum, i = var_found(f, i, var)
			
	elif f[i] in numbers:
		baum, i = const_found(f, i)
		
	elif f[i] in alphabet:
		baum, i = function(f, i)
		# print(f"parsedfunc: {baum=} {i=} {f[i-1]=}")
	else: 
		baum = []
	return baum, i
		



def parse(f, var):
	f = f.replace(" ", "")
	i = 0
	baum = []
	while i < len(f):
		
		# print(f"parse: {i=} {f[i]=} {f=} {baum=}")
		
		if f[i] in var+numbers+alphabet:
			baum, i = argument(f, i)
		
		if i >= len(f):
			break
		
		
		### PARENTHESE	
		if f[i] == "(":
			arg, i = find_arg(f, i)		 #(arg)
			# print(f"parentheses: {baum=} {i=} {f[i]=} {arg=}")
			
			baum, i = operation(f, i, parse(arg, var))
			# print("lol")
			
		if i < len(f) and f[i] in "+-*/^"+alphabet:
			baum, i = operation(f, i, baum)	
		
	# print(f"{baum=}")
		
	return baum

	

if __name__ == "__main__":
	
	IN = "(3x^267) * sin(8x)*e^(x+3) + ln(x^23+(4567+x)/(sin(23x)))"
	p = parse(IN, "x")	
	print("\n\n", IN, "\n\n", p, "\n\n", readable(p))




