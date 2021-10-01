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

def maximum(f,a,b):
    n=3000
    x = a
    max_fx = f.lam(x)
    while x < b:
        if f.lam(x) > max_fx:
            max_fx = f.lam(x)
            max_x = x
        else:
            x+= (b-a)/n
    
    return max_fx
"""
def maximum(f,a,b):
    
    #MAN MÜSSTE lokal um UNSTETIGKEITSSTELLEN ANALYSISEREN!
    extremstellen = [a,b]
    extremstellen += nullstellen(f.diff(),a,b)
    
    max_x=a
    max_fx=f.lam(a)
    for x in extremstellen:
        if f.lam(x) > max_fx:
            max_fx = f.lam(x)
            max_x = x

    return max_fx
"""
def minimum(f,a,b):
    #MAN MÜSSTE lokal um UNSTETIGKEITSSTELLEN ANALYSISEREN!
    extremstellen = [a,b]
    extremstellen += nullstellen(f.diff(),a,b)
    
    min_x=a
    min_fx=f.lam(a)
    for x in extremstellen:
        if f.lam(x) < min_fx:
            min_fx = f.lam(x)
            min_x = x
    
    return min_fx

def riemann(f,a,b):
    n = 5000
    Int = 0
    x = a
    schrittweite = (b-a)/n
    
    for i in range(n):
        Int += f.lam(a + i*schrittweite)
        
    Int *= schrittweite
    
    return Int

def trapez(f,a,b):
    n = 5000
    Int = 0
    x = a
    schrittweite = (b-a)/n
    
    Int += 1/2*f.lam(a)
    Int += sum( f.lam(a + i * schrittweite) for i in range(n))
    Int += 1/2*f.lam(b)    
    
    Int *= schrittweite
    
    return Int

def simpson(f,a,b):
    n = 5000
    Int = 0
    schrittweite = (b-a)/n
    
    Int += 1/2*f.lam(a)
    Int += sum( (1 + i % 2) * f.lam(a + i*schrittweite) for i in range(1,n))
    Int += 1/2*f.lam(b)
    
    Int *= 2/3*schrittweite
    return Int

def trapez_fehler(f,a,b):
    h = (b-a)/5000
    return abs(1/12*(b-a)*h**2*maximum(f.diff().diff(),a,b))

def simpson_fehler(f,a,b):
    h = (b-a)/5000
    g = f.diff().diff().diff().diff()
    print(g.str)
    return abs(1/180*(b-a)*h**4*maximum(g,a,b))


f = function("x^9*cos(x^2)^3")

#print("trapez",trapez(f,0,10))
#print("riemann",riemann(f,0,10))
print("simpson",simpson(f,0,10))

#print("t Fehler-abschätzung:",trapez_fehler(f,0,10))
print("s Fehler-abschätzung:",simpson_fehler(f,0,10))
