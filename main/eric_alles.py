from function_class import *
from functions import *

def sekanten_verfahren(f, x1, x2):
    eps_stop = 10 ** -15

    y1 = f.lam(x1)
    y2 = f.lam(x2)

    if y1 == 0:
        return x1

    elif y2 == 0:
        return x2

    elif y1 * y2 > 0:
        print("Kein Vorzeichenwechsel")

    else:
        x_old = x1
        x_old_old = x2
        while abs(x_old - x_old_old) > eps_stop:
            if f.lam(x_old) != f.lam(x_old_old):
                # Schnittstelle von Gerade durch (x_old, f(x_old) und  (x_old_old, f(x_old_old)) mit x-Achse
                x_new = x_old - (x_old - x_old_old) / (f.lam(x_old) - f.lam(x_old_old)) * f.lam(x_old)

                x_old_old = x_old
                x_old = x_new
            else:
                return x_old
        return x_new

def sign(x):
    return 1 if x > 0 else 0 if x == 0 else -1

def nullstellen(f, a, b):
    number_of_test_values = 1000

    Values = []
    x = a
    schrittweite = (b - a) / number_of_test_values

    # Values bestimmen auf allen Test-Punkten
    while True:
        Values.append([x, sign(f.lam(x))])
        x += schrittweite

        if x > b:
            break

    Nulls = []
    Vorzeichen_wechsel = []

    # Vorzeichen wechselnde Werte bestimmen
    for i in range(len(Values) - 1):

        if Values[i][1] == 0:
            Nulls.append(Values[i][0])

        elif Values[i][1] * Values[i + 1][1] < 0:
            Vorzeichen_wechsel.append([Values[i][0], Values[i + 1][0]])

    # Sekantenverfahren für alle Vorzeichenwechsel verwenden
    for elements in Vorzeichen_wechsel:
        Nulls.append(sekanten_verfahren(f, elements[0], elements[1]))

    # Überprüfen, ob kein Fehler enstanden ist
    for element in Nulls:
        if f.lam(element) > 10 ** -10:
            Nulls.remove(element)

    return Nulls

def fact(n):
    return n * fact(n - 1) if n >= 1 else 1

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
    for i in range(2, int(sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def factor(n):
    factors = []
    temp = n

    for i in range(2, temp):

        while temp % i == 0:
            temp = temp / i
            factors.append(i)

    return factors

#Namen wie arcatnh falsch nämlich eig. artanh

pi = nullstellen(function("sin(x)"),3, 4)[0]

