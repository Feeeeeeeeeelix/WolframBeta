from integration import *
from function_class import *

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

def minimum(f,a,b):
    #MAN MÜSSTE lokal um UNSTETIGKEITSSTELLEN ANALYSISEREN!
    extremstellen = [a,b]
    extremstellen.append(nullstellen(f.diff(),a,b))
    
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
    return abs(1/180*(b-a)*h**4*maximum(f.diff().diff().diff().diff(),a,b))


#EIGENTLICH LAMBDA:::


#f = function("x^9")

#print("trapez",trapez(f,0,1),"Fehler-abschätzung:",trapez_fehler(f,0,1))
#print("riemann",riemann(f,0,1))
#print("simpson",simpson(f,0,1),"Fehler-abschätzung:",simpson_fehler(f,0,1))

        
    
