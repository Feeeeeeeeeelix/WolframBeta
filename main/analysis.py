"""
analysis.py module:

- find nullstellen of functions
- find extrema
- compute integrals with 3 methods and their precision
- evaluate higher order derivatives
- approximate first order differential equations

"""
from functions import *
DEFAULT_RANGE = [-5, 5]


def set_default_range(ran):
    global DEFAULT_RANGE
    DEFAULT_RANGE = ran


def _sekanten_verfahren(f, x1, x2):
    eps_stop = 10 ** -15
    
    y1 = f(x1)
    y2 = f(x2)
    
    if y1 == 0:
        return x1
    
    elif y2 == 0:
        return x2
    
    elif y1 * y2 > 0:
        raise Exception("Kein Vorzeichenwechsel")
    
    else:
        x_old = x1
        x_old_old = x2
        x_new = x_old_old
        while abs(x_old - x_old_old) > eps_stop:
            if f(x_old) != f(x_old_old):
                # Schnittstelle von Gerade durch (x_old, f(x_old) und  (x_old_old, f(x_old_old)) mit x-Achse
                x_new = x_old - (x_old - x_old_old) / (f(x_old) - f(x_old_old)) * f(x_old)
                
                x_old_old = x_old
                x_old = x_new
            else:
                return x_old
        return x_new


def _sign(x):
    return 1 if x > 0 else 0 if x == 0 else -1


def nullstellen(func, a=None, b=None):
    a = DEFAULT_RANGE[0] if a is None else a
    b = DEFAULT_RANGE[1] if b is None else b
    if type(func) == str:
        # funktionsterme werden in eine funktion umgewandelt
        f = lambda x: eval(func)
    else:
        f = func
        
    number_of_test_values = 1000
    
    values = []
    x = a
    schrittweite = (b - a) / number_of_test_values
    
    # Values bestimmen auf allen Test-Punkten
    while x <= b:
        x = round(x, 12)
        try:
            values.append([x, _sign(f(x))])
        except ValueError:
            # Wenn f nicht in x definiert ist
            pass
        x += schrittweite
    
    nulls = []
    Vorzeichen_wechsel = []
    
    # Vorzeichen wechselnde Werte bestimmen
    for i in range(len(values) - 1):
        
        if values[i][1] == 0:
            nulls.append(values[i][0])
        
        elif values[i][1] * values[i + 1][1] < 0:
            Vorzeichen_wechsel.append([values[i][0], values[i + 1][0]])
    
    # Sekanten verfahren für alle Vorzeichenwechsel verwenden
    for elements in Vorzeichen_wechsel:
        nulls.append(_sekanten_verfahren(f, elements[0], elements[1]))
    
    # Überprüfen, ob kein Fehler entstanden ist
    for element in nulls:
        if f(element) > 10 ** -10:
            nulls.remove(element)
    
    return nulls


def maximum(func, a=None, b=None):
    a = DEFAULT_RANGE[0] if a is None else a
    b = DEFAULT_RANGE[1] if b is None else b
    if type(func) == str:
        # funktionsterme werden in eine funktion umgewandelt
        f = lambda x: eval(func)
    else:
        f = func
        
    n = 3000
    x = a
    max_fx = f(x)
    while x < b:
        x += (b - a) / n
        if f(x) > max_fx:
            max_fx = f(x)
        # max_x = x
    return max_fx


def minimum(func, a=None, b=None):
    a = DEFAULT_RANGE[0] if a is None else a
    b = DEFAULT_RANGE[1] if b is None else b
    if type(func) == str:
        # funktionsterme werden in eine funktion umgewandelt
        f = lambda x: eval(func)
    else:
        f = func
        
    n = 3000
    x = a
    min_fx = f(x)
    while x < b:
        x += (b - a) / n
        if f(x) < min_fx:
            min_fx = f(x)
        # min_x = x
    return min_fx


min = minimum
max = maximum
racines = nullstellen


def riemann(f, a, b):
    n = 5000
    Int = 0
    schrittweite = (b - a) / n
    
    for i in range(n):
        Int += f(a + i * schrittweite)
    
    Int *= schrittweite
    
    return Int


def trapez(f, a, b):
    n = 5000
    Int = 0
    schrittweite = (b - a) / n
    
    Int += 1 / 2 * f(a)
    Int += sum(f(a + i * schrittweite) for i in range(n))
    Int += 1 / 2 * f(b)
    
    Int *= schrittweite
    
    return Int


def simpson(f, a, b):
    n = 5000
    Int = 0
    schrittweite = (b - a) / n
    
    Int += 1 / 2 * f(a)
    Int += sum((1 + i % 2) * f(a + i * schrittweite) for i in range(1, n))
    Int += 1 / 2 * f(b)
    
    Int *= 2 / 3 * schrittweite
    return Int


def trapez_fehler(f, a, b):
    h = (b - a) / 5000
    return abs(1 / 12 * (b - a) * h ** 2 * maximum(der(f, n=2), a, b))


def simpson_fehler(f, a, b):
    h = (b - a) / 5000
    return abs(1 / 180 * (b - a) * h ** 4 * maximum(der(f, n=4), a, b))


def euler_collatz(f_str, t_0, y_0, end, steps=1000):
    # Löse y' = f(t,y) mit y(t_0) = y_0 auf dem Intervall (t_0 ; end) mit insgesamt 1000 Iterationsschritte/Stützstellen
    f = lambda t, y: eval(f_str.replace("y", "( " + str(y) + ")").replace("t", "( " + str(t) + ")").replace("^", "**"))
    
    y = [0] * steps
    y[0] = y_0
    dt = (end - t_0) / steps
    t = t_0
    for i in range(1, steps):
        y[i] = y[i - 1] + dt * f(t + dt / 2, y[i - 1] + dt / 2 * f(t, y[i - 1]))
        t += dt
    x = [t_0 + i * dt for i in range(steps)]
    return x, y  # Die Menge der Funktionswerte (die dazugehörigen x-Werte sind [x_0 + i * dt for i in range(0,steps)])


def der(f, var="x", n=1, dx=10 ** (-3)):
    # approximation der n-ten Ableitung in x von f.
    # Sehr instabil bei großem n, daher sollte dx nicht zu klein gewählt werden.
    from functions import C
    
    if float(n) != int(n) or float(n) < 0:
        raise ValueError("nur positive integer erlaubt")
    if n == 0:
        return f
    if n == 1:
        return lambda x=var: (f(x + dx) - f(x - dx)) / (2 * dx)
    
    else:
        return lambda x=var: 1 / dx ** n * sum([(-1) ** (k + n) * C(n, k) * f(x + k * dx) for k in range(n + 1)])
