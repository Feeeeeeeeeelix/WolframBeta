from functions import e, sin, cos


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
    
    # Sekanten verfahren für alle Vorzeichenwechsel verwenden
    for elements in Vorzeichen_wechsel:
        Nulls.append(sekanten_verfahren(f, elements[0], elements[1]))
    
    # Überprüfen, ob kein Fehler entstanden ist
    for element in Nulls:
        if f.lam(element) > 10 ** -10:
            Nulls.remove(element)
    
    return Nulls


def maximum(f, a, b):
    n = 3000
    x = a
    max_fx = f.lam(x)
    while x < b:
        x += (b - a) / n
        if f.lam(x) > max_fx:
            max_fx = f.lam(x)
        # max_x = x
    return max_fx


def minimum(f, a, b):
    n = 3000
    x = a
    min_fx = f.lam(x)
    while x < b:
        x += (b - a) / n
        if f.lam(x) < min_fx:
            min_fx = f.lam(x)
        # min_x = x
    return min_fx


def riemann(f, a, b):
    n = 5000
    Int = 0
    x = a
    schrittweite = (b - a) / n
    
    for i in range(n):
        Int += f.lam(a + i * schrittweite)
    
    Int *= schrittweite
    
    return Int


def trapez(f, a, b):
    n = 5000
    Int = 0
    x = a
    schrittweite = (b - a) / n
    
    Int += 1 / 2 * f.lam(a)
    Int += sum(f.lam(a + i * schrittweite) for i in range(n))
    Int += 1 / 2 * f.lam(b)
    
    Int *= schrittweite
    
    return Int


def simpson(f, a, b):
    n = 5000
    Int = 0
    schrittweite = (b - a) / n
    
    Int += 1 / 2 * f.lam(a)
    Int += sum((1 + i % 2) * f.lam(a + i * schrittweite) for i in range(1, n))
    Int += 1 / 2 * f.lam(b)
    
    Int *= 2 / 3 * schrittweite
    return Int


def trapez_fehler(f, a, b):
    h = (b - a) / 5000
    return abs(1 / 12 * (b - a) * h ** 2 * maximum(f.diff().diff(), a, b))


def simpson_fehler(f, a, b):
    h = (b - a) / 5000
    g = f.diff().diff().diff().diff()
    print(g.str)
    return abs(1 / 180 * (b - a) * h ** 4 * maximum(g, a, b))


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
    return y  # Die Menge der Funktionswerte (die dazugehörigen x-Werte sind [x_0 + i * dt for i in range(0,steps)])


def der(f, x, n=1, dx=10 ** (-5)):
    # approximation der n-ten Ableitung in x von f.
    if float(n) != int(n) or float(n) < 0:
        raise ValueError("nur positive integer erlaubt")
    if n == 0:
        return f(x)
    if n == 1:
        return (f(x + dx) - f(x - dx)) / (2 * dx)
    
    elif n % 2 == 0:
        return (der(f, x + dx, n - 1) - der(f, x - dx, n - 1)) / (2 * dx)
    
    else:
        return (der(f, x + dx, n - 2) - 2 * der(f, x, n - 2) + der(f, x - dx, n - 2)) / (dx * dx)


if __name__ == "__main__":
    """print("Beispiele:\n")
    
    y = euler_collatz("y", 0, 1, 3)  # Löse y' = y mit y(0) = 1   --> y(t) = e^t einzige Lösung
    print(y)
    print("Zum Vergleich mit dem letzten Term: ", e ** 3)
    
    print("")
    
    y = euler_collatz("y^2", 0, 1,
                      0.9)  # Löse y'(t) = y^2 mit y(0) = 1 auf Intervall (0,0.9) --> exakte Lösung y(t) = 1/(1-t)
    print(y)
    print("Zum Vergleich mit dem letzten Term: ", 1 / (1 - 0.9))
    
    print("")
    
    y = euler_collatz("y*t", 0, 1,
                      2)  # Löse y'(t) = y*t mit y(0) = 1 auf Intervall (0,2) --> exakte Lösung y(t) = e^{1/2*t^2}
    print(y)
    print("Zum Vergleich mit dem letzten Term: ", e ** (1 / 2 * 2 ** 2))"""

    f = lambda x: sin(x ** 2)
    df = lambda x: 2 * x * cos(x ** 2)
    ddf = lambda x: 2 * cos(x ** 2) - 4 * x ** 2 * sin(x ** 2)

    print(der(f, x=1, n=1))
    print(df(1))

    print(der(f, x=1, n=2))
    print(ddf(1))
