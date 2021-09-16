def sekanten_verfahren(f,x1,x2):

    eps_stop = 10**-10

    y1=f(x1)

    y2=f(x2)

    if y1==0:

        return x1

    elif y2==0:

        return x2

    elif y1*y2>0:

        print("Keine Vorzeichenwechsel")

    else:

        x_old_old = x1

        x_old = x2

       

        while abs(x_old-x_old_old) > eps_stop:

            if f(x_old) != f(x_old_old):

                # Schnittstelle von Gerade durch (x_old, f(x_old) und  (x_old_old, f(x_old_old)) mit x-Achse

                x_new = x_old - (x_old-x_old_old)/(f(x_old)-f(x_old_old))*f(x_old)

                x_old_old = x_old

                x_old = x_new

            else:

                return x_old

        

        return x_new

   

def sign(x):

    return 1 if x>0 else 0 if x==0 else -1 

 

def Nullstellen(f,a,b,number_of_test_values): #a<b !

    Values=[]

    x=a

    schrittweite=(b-a)/number_of_test_values

   

    #Values bestimmen auf allen Test-Punkten

    while True:

        Values.append([x,sign(f(x))])

        x+=schrittweite

        if x>b:

            break

   

    Nulls=[]

    Vorzeichen_wechsel=[]   

    #Vorzeichen wechselnde Werte bestimmen

    for i in range(len(Values)-1):

        if Values[i][1]==0:

            Nulls.append(Values[i][0])

       

        elif Values[i][1]*Values[i+1][1]<0:

            Vorzeichen_wechsel.append([Values[i][0],Values[i+1][0]])

   

    #Sekantenverfahren für alle Vorzeichenwechsel verwenden

    for elements in Vorzeichen_wechsel:

        Nulls.append(sekanten_verfahren(f,elements[0],elements[1]))

       

    #Überprüfen, ob kein Fehler enstanden ist

    for element in Nulls:

        if f(element)>10**-5:

            Nulls.remove(element)

   

    return Nulls

 

 

print(Nullstellen(lambda x: x ** 5 - 20*x**3 + 4*x - 1   , -10, 10, 100))

                          # Funktion            # Intervall [-10,10] , 100 Testwerte.

