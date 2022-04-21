"""
functions.py module:

- essential constants (π, e) (3)
- all trigonometric functions
- logarithmic, exponential and root functions
- zahlentheorie baaic functions
- n! and aCb

"""

#  KONSTANTEN


e = 2.7182818284590455
pi = 3.141592653589793
ln2 = .693147180559945
ln3 = 1.098612288668110
π = pi


#  ELEMENTARE FUNKTIONEN

def is_pos_int(n):
    if int(n) != float(n) or float(n) < 0:
        return False
    return True


def is_int(n):
    if int(n) != float(n):
        return False
    return True


def fact(n):
    if not is_pos_int(n):
        raise ValueError(f"fact argument must be a positive integer")
    return n * fact(n - 1) if n > 1 else 1


def C(n, k):
    if not is_pos_int(n) or not is_pos_int(k):
        raise ValueError(f"C arguments must be positive intergers")
    if n < k:
        raise ValueError(f"n must be greater than k")
    return fact(n) / (fact(n - k) * fact(k))


def exp(x):  # Taylor Reihe (ohne x**i jedes mal neu zu berechnen)
    sum = 0
    term = 1
    for i in range(1, 20 + 3 * abs(x)):
        sum += term
        term *= x / i
    return sum


def log(x, base="e"):  # Patent
    # Da die Taylor Reihe nur sehr langsam konvergiert, verwenden wir die multiplikative Eigenschaft des
    # Logarithmus um x in eine enge Umgebung von 1 zu verschieben, damit die Reihe sehr schnell konvergiert
    
    if base != "e":
        return log(x) / log(base)
    
    if x <= 0:
        raise ValueError("log argument must be positive")
    elif x > 1.01:
        return log(x / 2) + ln2
    elif x < 0.99:
        return log(x * 3) - ln3
    else:
        return sum((-1) ** (n + 1) / n * (x - 1) ** n for n in range(1, 12))


def ln(x):
    return log(x)


def pow(a, n):
    nbin = bin(n)[2:]
    teiler = [a]
    b = a
    x = 1
    
    for i in range(len(nbin) - 1):
        b = b ** 2
        teiler.append(b)
    
    for i in range(len(nbin)):
        if int(nbin[::-1][i]):
            x *= teiler[i]
    return x


def sqrt(x):
    if x < 0:
        raise ValueError(f"sqrt argument must be positive")
    if x == 0:
        return 0
    else:
        xold = 1.0
    while True:
        xnew = 1 / 2 * (xold + x / xold)
        
        if abs(xnew - xold) < 10 ** -15:
            return xnew
        
        xold = xnew


def root(a, k):
    if a < 0 and not k % 2:
        raise ValueError
    if not is_pos_int(k):
        raise TypeError("k must be a positive integer")
    
    if a == 0:
        return 0
    else:
        if a > 0:
            xold = 1.0
        else:
            xold = -1.0
        while True:
            xnew = ((k - 1) * xold ** k + a) / (k * xold ** (k - 1))
            
            if abs(xnew - xold) < 10 ** -12:
                return xnew
            
            xold = xnew


def sin(x):
    # x wird in das gute Konvergenz-Bereich verschoben
    vorzeichen = 1
    x = x % (2 * pi)
    if x > pi:  # Verschiebung in [0,pi]
        x = x - pi
        vorzeichen = -1
    
    if x > pi / 2:  # Verschiebung in [0,pi/2]
        x = pi - x  # sin(pi-x) = sin(x)
    
    sum = 0
    term = x
    for i in range(1, 10):
        sum += term
        term *= -x * x / (2 * i * (2 * i + 1))
    return sum * vorzeichen


def cos(x):
    # x wird in das gute Konvergenz-Bereich verschoben (Eigenschaften von cosinus)
    vorzeichen = 1
    x = x % (2 * pi)
    if x > pi:  # Verschiebung in [0,pi]
        x = 2 * pi - x  # Spiegelung in pi
    
    if x > pi / 2:  # Verschiebung in [0,pi/2]
        x = pi - x  # Spiegelung in pi/2
        vorzeichen = -1

    # Taylor-Reihe mit gespeicherten Koeffizienten:
    sum = 1
    term = -x ** 2 / 2
    for i in range(1, 10):
        sum += term
        term *= -x * x / ((2 * i + 1) * (2 * i + 2))
    
    return sum * vorzeichen


def tan(x):
    if not x % 2*pi:
        raise ValueError
    return sin(x) / cos(x)


def cosh(x):
    return (exp(x) + exp(-x)) / 2


def sinh(x):
    return (exp(x) - exp(-x)) / 2


def tanh(x):
    return sinh(x) / cosh(x)


def arcsin(x):
    if x <= -1 or x >= 1:
        raise ValueError(f"arcsin argument must be between -1 and 1")
    
    # arcsin(x) = arctan( x/sqrt(1-x^2) ) und arctan ist durch rationales polynom gut approximiert
    return arctan(x / sqrt(1 - x ** 2))


def arccos(x):
    if x <= -1 or x >= 1:
        raise ValueError(f"arccos argument must be between -1 and 1")
    return pi / 2 - arcsin(x)


def arctan(x):
    # Approximation mit 0.005 Fehler
    if x > 1:
        approx = pi / 2 - x / (x ** 2 + 0.28)
    elif x > -1:
        approx = x / (1 + 0.28 * x ** 2)
    else:
        approx = -pi / 2 - x / (x ** 2 + 0.28)
    
    # verbesserte Approximation durch Newton-Verfahren
    for k in range(3):
        approx -= (tan(approx) - x) * cos(approx) ** 2
    
    return approx


def arccosh(x):
    if x <= 1:
        raise ValueError(f"arccosh argument must be greater than 1")
    return ln(x + sqrt(x ** 2 - 1))


def arcsinh(x):
    return ln(x + sqrt(x ** 2 + 1))


def arctanh(x):
    if x <= -1 or x >= 1:
        raise ValueError(f"arctanh argument must be between -1 and 1")
    return 0.5 * ln((1 + x) / (1 - x))


#  ZAHLENTHEORIE


def division_with_rest(a, b):
    max_multiple = a // b
    rest = a % b  # a = max_multiple * b +rest , rest<b
    return max_multiple, rest


def euclidean_algorithm(a, b):
    while b != 0:  # b==0 --> Algorithmus fertig
        n, rest = division_with_rest(a, b)
        print(a, "=", n, "*", b, "+", rest)
        a = b
        b = rest
    return a  # ggT von a,b nach dem euklidischen Algorithmus


def kgV(a, b):
    return a * b / euclidean_algorithm(a, b)


ggT = euclidean_algorithm
PGCD = ggT
PPCM = kgV


def eratosthenes(n):
    x = [True] * (n + 3)
    prime_list = []
    
    for i in range(2, n + 1):
        
        if x[i]:
            prime_list.append(i)
            a = 2 * i
            
            while a <= n:
                x[a] = False
                a += i
    
    return prime_list


def isprime(n):
    if n <= 1:
        return False
    for i in range(2, int(sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def prim_factors(n):
    factors = []
    temp = n
    
    for i in range(2, sqrt(temp) + 1):
        
        while temp % i == 0:
            temp = temp / i
            factors.append(i)
    
    return factors


def partition(n):
    part = [[1 if i == j or j == 0 else 0 for j in range(i + 1)] for i in range(n + 1)]
    
    for i in range(1, n + 1):
        for j in range(1, i):
            if i - j >= 0 and i - j >= j:
                part[i][j] += part[i - j][j]
            if i - 1 > 0 and j - 1 > 0:
                part[i][j] += part[i - 1][j - 1]
    
    return sum(part[n][k] for k in range(1, n + 1))


if __name__ == '__main__':
    print(root(-4,5))

