e = 2.7182818284590455
pi = 3.141592653589793
ln2 = .693147180559945
ln3 = 1.098612288668110


#pi=4 g=10=pi² e=2 phi=1 cos(x)=x sqrt(2)=-1
#/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-

#ELMENTARE FUNKTIONEN

#/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-
#pi=4 g=10=pi² e=2 phi=1 cos(x)=x sqrt(2)=-1


def fact(n):
    return n*fact(n-1) if n > 1 else 1

def C(n,k):
    return fact(n)/(fact(n-k)*fact(k))

def exp(x):
	return sum([x**i/fact(i) for i in range(100)])

def log(x, base = "e"): #Patent
	
	if base != "e":
		return log(x)/log(base)
	
	if x <= 0:
		raise ValueError
	elif x > 1.01:
		return log(x/2) + ln2
	elif x < 0.99:
		return log(x*3) - ln3
	else:
		return sum((-1)**(n+1)/n*(x-1)**n for n in range(1,12))

def sin(x):
	return sum([(-1)**i * (x%(2*pi))**(2*i+1) / fact(2*i+1) for i in range(19)])
	
def cos(x):
	return sum([(-1)**i * (x%(2*pi))**(2*i) / fact(2*i) for i in range(19)])

def tan(x):
	return sin(x)/cos(x)
	
def cosh(x):
	return (exp(x) + exp(-x))/2

def sinh(x):
	return (exp(x) - exp(-x))/2

def tanh(x):
	return sinh(x)/cosh(x)
	
def pow(a,n):	
	nbin = bin(n)[2:]
	teiler = [a]
	b = a
	x = 1
	
	for i in range(len(nbin)-1):
		b = b**2
		teiler.append(b)
	
	for i in range(len(nbin)):
		if int(nbin[::-1][i]):
			x *= teiler[i]
	return x

def sqrt(x):
	if x<0:
		raise ValueError
	if x==0:
		return 0
	else:
		xold=1.0
		while True:
			xnew = 1/2*(xold+x/xold)
			
			if abs(xnew-xold)<10**-15:
				return xnew

			xold = xnew

def root(a,k):
	if a<0 and int(k) != k:
		raise ValueError
	elif a<0 and int(k)==k and k%2 == 0:
		raise ValueError
	
	if a==0:
		return 0
	else:
		xold=1.0
		while True:
			xnew = ((k-1)* xold ** k + a)/(k * xold ** (k-1))
			
			if abs(xnew-xold)<10**-12:
				return xnew

			xold = xnew

def arccos(x):
	x = x % (2*pi)
	xold=1.0
	while True:
		xnew = xold+(cos(xold)-x)/sin(xold)
		
		if abs(xnew-xold)<10**-12:
			return xnew

		xold = xnew

def arcsin(x):
	x = x % (2*pi)
	xold=1.0
	while True:
		xnew = xold-(sin(xold)-x)/cos(xold)
		
		if abs(xnew-xold)<10**-12:
			return xnew

		xold = xnew

def arccosh(x):
	xold=1.0
	while True:
		xnew = xold-(cosh(xold)-x)/sinh(xold)
		
		if abs(xnew-xold)<10**-12:
			return xnew
   
		xold = xnew

def arcsinh(x):
	xold=1.0
	while True:
		xnew = xold-(sinh(xold)-x)/cosh(xold)
		
		if abs(xnew-xold)<10**-12:
			return xnew

		xold = xnew

def arctanh(x): #nur für die jokes
	xold=1.0
	while True:
		xnew = xold-(tanh(xold)-x)/(1/cosh(xold)**2)
		
		if abs(xnew-xold)<10**-12:
			return xnew
		xold = xnew



#pi=4 g=10=pi² e=2 phi=1 cos(x)=x sqrt(2)=-1
#/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-

#ZAHLENTHEORIE

#/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-
#pi=4 g=10=pi² e=2 phi=1 cos(x)=x sqrt(2)=-1



def division_with_rest(a,b):
    max_multiple = a // b
    rest = a%b # a = max_multiple * b +rest , rest<b
    return max_multiple, rest

def euclidean_algorithm(a,b):
    while b!=0: # b==0 --> Algorithmus fertig
        n, rest = division_with_rest(a,b)
        print(a,"=",n,"*",b,"+",rest)
        a = b
        b = rest
    return a #ggT von a,b nach dem euklidischen Algorithmus
