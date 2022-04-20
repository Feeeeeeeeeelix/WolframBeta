
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


def fact(n):
    if int(n) != float(n) or n < 0:
        raise ValueError
    return n * fact(n - 1) if n > 1 else 1


def C(n, k):
    return fact(n) / (fact(n - k) * fact(k))


def exp(x):
    return sum([x ** i / fact(i) for i in range(100)])


def log(x, base="e"):  # Patent

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
        raise ValueError
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
    if a < 0 and int(k) != k:
        raise ValueError
    elif a < 0 and int(k) == k and k % 2 == 0:
        raise ValueError

    if a == 0:
        return 0
    else:
        xold = 1.0
        while True:
            xnew = ((k - 1) * xold ** k + a) / (k * xold ** (k - 1))

            if abs(xnew - xold) < 10 ** -12:
                return xnew

            xold = xnew


def sin(x):
    return sum([(-1) ** i * (x % (2 * pi)) ** (2 * i + 1) / fact(2 * i + 1) for i in range(19)])


def cos(x):
    return sum([(-1) ** i * (x % (2 * pi)) ** (2 * i) / fact(2 * i) for i in range(19)])


def tan(x):
    return sin(x) / cos(x)


def cosh(x):
    return (exp(x) + exp(-x)) / 2


def sinh(x):
    return (exp(x) - exp(-x)) / 2


def tanh(x):
    return sinh(x) / cosh(x)


def arccos(x):
    if x < -1 or x > 1:
        raise ValueError(f"arccos argument must be between -1 and 1")
    
    xold = x
    while True:
        xnew = xold + (cos(xold) - x) / sin(xold)

        if abs(xnew - xold) < 10 ** -12:
            return xnew

        xold = xnew


def arcsin(x):
    if x < -1 or x > 1:
        raise ValueError(f"arcsin argument must be between -1 and 1")
    
    xold = x
    while True:
        xnew = xold - (sin(xold) - x) / cos(xold)

        if abs(xnew - xold) < 10 ** -12:
            return xnew

        xold = xnew


def arctan(x):
    xold = x
    while True:
        xnew = xold - (tan(xold) - x) / (1 / cos(xold) ** 2)

        if abs(xnew - xold) < 10 ** -12:
            return xnew
        xold = xnew


def arccosh(x):
    if x <= 1:
        raise ValueError(f"arccosh argument must be greater than 1")
    return ln(x+sqrt(x**2-1))


def arcsinh(x):
    return ln(x+sqrt(x**2+1))


def arctanh(x):
    if x <= -1 or x >= 1:
        raise ValueError(f"arctanh argument must be between -1 and 1")
    
    return 0.5*ln((1+x)/(1-x))


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
    return a*b/euclidean_algorithm(a, b)


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
    print(cosh(-5))