
def readable(f):
	operations = {"add":" + ", "subs":" - ", "mult":"*"}
	functions = ["sin", "cos", "tan", "exp", "ln"]
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



if __name__ == "__main__":
	print("f(x) = " + readable(d2))
	
