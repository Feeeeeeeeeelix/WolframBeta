from functions import *

operators = ["sin", "cos", "exp", "log", "cosh", "sinh", "tan", "tanh", "arccos", "arcsin", "arctan", "arccosh",
             "arcsinh", "arctanh"]

def is_number(s):
    #checks if string represents a number
    try:
        float(s)
        return True
    except:
        return False
def inner_and_outer_operation(f):
    #Gibt zu f(x) = cos(x^2+1)*(2*x+1) den String cos{} * {} aus und die place_holders [x^2+1, 2*x+1].

    outer_text = ""
    place_holders = []

    left_brakets = 0
    right_brakets = 0

    for letter in f:
        if letter == "(":
            if left_brakets == right_brakets:
                #dann ist es eine nicht umklammerte klammer
                outer_text += "{}"
                place_holders += [""]

            else:
                place_holders[-1] += letter

            left_brakets += 1

        elif letter == ")":

            if left_brakets != right_brakets:
                place_holders[-1] += letter

            right_brakets += 1

            if right_brakets == left_brakets:
                place_holders[-1] = place_holders[-1][:-1]  # Letzte Klammer entfernen, da sonst "3*(x+1)^2)"

        elif left_brakets == right_brakets:
            outer_text += letter

        else:
            place_holders[-1] += letter

    return [outer_text, place_holders]
def tree(f):
    # - durch +- ersetzen, damit dies als "Summand" erkannt wird
    for letter_index in range(1, len(f)):
        if f[letter_index] == "-" and f[letter_index - 1] != "+":
            f = f[:letter_index] + '+' + f[letter_index:]
            #FALSCH!!!!
            # cos(x)*-sin(x) wird zu einer addition! dies ist aber falsch!!!
                        #FALSCH!!!!
            # cos(x)*-sin(x) wird zu einer addition! dies ist aber falsch!!!
                        #FALSCH!!!!
            # cos(x)*-sin(x) wird zu einer addition! dies ist aber falsch!!!
            
    # störende Leerzeichen entfernen:
    f = f.replace(" ", "")

    # Das innere von klammern wird ersetzt durch {} und wird in place_holders gespeichert.
    [simplified, place_holders] = inner_and_outer_operation(f)

    is_sum_or_prod = False

    if "+" in simplified:
        #Neu, vllt falsch:
        if simplified[:2] == "+-" and simplified.count("+") == 1: #falls nur ein +- am anfang ist, dann ist es keine summe sondern nur ein minus

            factorized = ["-", simplified[2:]]

            # Die {} durch deren Inhalt ersetzen
            holder_counter = 0

            while "{}" in factorized[1]:
                factorized[1] = factorized[1].replace("{}", "(" + place_holders[holder_counter] + ")", 1)
                holder_counter += 1

            # Tree auf inneres anwenden

            return ["-", tree(factorized[1])]
        else:
            factorized = ["+", simplified.split("+")]
            is_sum_or_prod = True

    elif "*" in simplified:
        factorized = ["*", simplified.split("*")]  #Nachteil: Es werden mehrere Faktoren erlaubt, weshalb die Produktregel schwieriger ist
        is_sum_or_prod = True

    elif "-" in simplified:
        factorized = ["-", simplified[1:]]

        # Die {} durch deren Inhalt ersetzen
        holder_counter = 0

        while "{}" in factorized[1]:
            factorized[1] = factorized[1].replace("{}", "(" + place_holders[holder_counter] + ")", 1)
            holder_counter += 1

        # Tree auf inneres anwenden
        return ["-", tree(factorized[1])]

    if is_sum_or_prod == True:
        # Die {} durch deren Inhalt ersetzen

        holder_counter = 0

        for factor_index in range(len(factorized[1])):
            while "{}" in factorized[1][factor_index]:
                factorized[1][factor_index] = factorized[1][factor_index].replace("{}", "(" + place_holders[
                    holder_counter] + ")", 1)
                holder_counter += 1

        # Tree auf alle Summanden/Faktoren anwenden
        return [factorized[0], [tree(factorized[1][i]) for i in range(len(factorized[1]))]]


    if is_sum_or_prod == False:
        # Nun kein Faktor / Summand und es gibt kein Minus.
        if "/" in simplified:
            if simplified.count("/") == 1:
                # Ersetzt "/" durch "@" damit man es von "/" in inneren klammern unterscheiden kann:
                simplified = simplified.replace("/", "@")

                holder_counter = 0
                while "{}" in simplified:
                    simplified = simplified.replace("{}", "(" + place_holders[holder_counter] + ")", 1)
                    holder_counter += 1

                # Nenner und Zähler mit Tree vereinfachen:
                return ["/", tree(simplified[:simplified.index("@")]), tree(simplified[simplified.index("@") + 1:])]

            else:
                # falls es mehrere "/" ohne klammern gibt es uneindeutig (z.B. 2/3/5 kommt auf klammerung an)
                print("Divisionen müssen eindeutig geschrieben werden!")



        # Die Reihenfolge ist wichtig, denn cos(x)/x^2 soll cos(x) / (x^2) sein !!
        elif "^" in simplified:
            if simplified.count("^") == 1:
                # Ersetzt "^" durch "@" damit man es von "^" in inneren klammern unterscheiden kann:
                simplified = simplified.replace("^", "@")
                holder_counter = 0

                while "{}" in simplified:
                    simplified = simplified.replace("{}", "(" + place_holders[holder_counter] + ")", 1)
                    holder_counter += 1

                # Basis und Exponent mit Tree vereinfachen:
                return ["^", tree(simplified[:simplified.index("@")]), tree(simplified[simplified.index("@") + 1:])]

            else:
                # falls es mehrere "^" ohne klammern gibt, ist es uneindeutig
                print("Potenzen müssen eindeutig geschrieben werden!")

        else:
            # Nun gibt es weder +, noch -,/,^,* im zu vereinfachenden Term.
            # {} wird durch inneres wieder ersetzt

            holder_counter = 0
            while "{}" in simplified:
                simplified = simplified.replace("{}", "(" + place_holders[holder_counter] + ")", 1)
                holder_counter += 1

            # Falls "(" im String, dann wirkt eine Funktion von links (denn Potenzierungen und so sind ja bereits behandelt)
            if "(" in simplified:

                # Vllt falsch: (unnötige Klammern entfernen)
                if simplified.index("(") == 0 and simplified.rindex(")") == len(simplified) - 1:
                    simplified = simplified[1: len(simplified) - 1]

                    return tree(simplified)

                    # Falls es vor der_hilfs_funktion ersten Klammer text gibt, so ist es eine Operation:
                if simplified.index("(") != 0:
                    operation = simplified[:simplified.index("(")]
                    inner_operations = simplified[simplified.index("(") + 1:simplified.rindex(")")]

                    if operation in operators:
                        return [operation, tree(inner_operations)]

                    else:
                        print("Input Fehler")


            # kein +,-,*,/,^ und keine Klammer (also keine Operation)
            # --> entweder ungültige eingabe oder "x" oder einfach eine Zahl
            else:
                if simplified == "x":
                    return "x"
                elif is_number(simplified) == True:
                    return simplified
                # Einzige fehlende möglichkeit die noch hinzugegefügt werden könnte: 2x statt 2*x
                else:
                    print("Input nicht verstanden")
def w(f):
    if f[0] == "+":
        text = ""
        for i in range(len(f[1])):

            if f[1][i][0] != "-":
                text += "+" + w(f[1][i])
            else:
                text += w(f[1][i])
                # 2  - cos(x) anstatt 2 + -cos(x)

        return text[1:] #das erste + entfernen

    elif f[0] == "*":

        text = ""
        for i in range(len(f[1])):
            # Faktoren sind nur in klammern, falls sie aus einer summe bestehen:
            if f[1][i][0] == "+":
                text += "(" + w(f[1][i]) + ")" + "*"
            else:
                text += w(f[1][i]) + "*"

        return text[:-1] #letztes "*" entfernen

    elif f[0] == "-":
        # Term ist nur in klammern, falls es eine Summe ist:
        if f[1][0][0] == "+":
            return "-" + "(" + w(f[1]) + ")"
        else:
            return "-" + w(f[1])

    elif f[0] == "^":
        # Es wird geschaut, welche Klammern nötig sind z.B.:
        # cos(x)^sin(x) or (1+x)^x or cos(x)^(1+x) or (cos(x)+1)^(sin(x)+2)

        klammer_eins = False
        klammer_zwei = False
        # Klammer nur nötig, falls es eine Summe/Produkt/Division/Potenz ist
        if f[1][0] == "+" or f[1][0] == "*" or f[1][0] == "/" or f[1][0] == "^" or f[1][0] == "-":
            klammer_eins = True
        if f[2][0] == "+" or f[2][0] == "*" or f[2][0] == "/" or f[2][0] == "^" or f[2][0] == "-":
            klammer_zwei = True
        if klammer_eins and klammer_zwei:
            return "(" + w(f[1]) + ")" + "^" + "(" + w(f[2]) + ")"
        elif klammer_eins and not klammer_zwei:
            return "(" + w(f[1]) + ")" + "^" + w(f[2])
        elif not klammer_eins and klammer_zwei:
            return w(f[1]) + "^" + "(" + w(f[2]) + ")"
        else:
            return w(f[1]) + "^" + w(f[2])

    elif f[0] == "/":
        # Es wird geschaut, welche Klammern nötig sind z.B.:
        # cos(x)/sin(x) or (1+x)/x or cos(x)/(1+x) or (cos(x)+1)/(sin(x)+2)
        klammer_eins = False
        klammer_zwei = False
        # Klammer nur nötig, falls es eine Summe/Produkt/Division/Potenz ist
        if f[1][0] == "+" or f[1][0] == "*" or f[1][0] == "/" or f[1][0] == "^":
            klammer_eins = True
        if f[2][0] == "+" or f[2][0] == "*" or f[2][0] == "/" or f[2][0] == "^":
            klammer_zwei = True
        if klammer_eins and klammer_zwei:
            return "(" + w(f[1]) + ")" + "/" + "(" + w(f[2]) + ")"
        elif klammer_eins and not klammer_zwei:
            return "(" + w(f[1]) + ")" + "/" + w(f[2])
        elif not klammer_eins and klammer_zwei:
            return w(f[1]) + "/" + "(" + w(f[2]) + ")"
        else:
            return w(f[1]) + "/" + w(f[2])
    else:
        # Keine elementare Operation +,-,*,/,^:
        if f == "x":
            return "x"

        # Operationen:
        elif type(f) == list:
            #nachtrag: nötig??
            if f[0][0] != "^":
                return f[0] + "(" + w(f[1]) + ")"
            else:
                return "(" + w(f[1]) + ")" + f[0]

        # Sonst nur noch Zahlen möglich
        elif is_number(f) == True:
            if float(f) == int(float(f)):
                return str(int(float(f)))  #schreibe 2 statt 2.0
            else:
                return f
        else:
            print("Fehler in der_hilfs_funktion Funktion!")
def write(f):
    # Es werden Leerzeichen für besseres Lesen hinzugefügt:
    phrase = w(f)
    phrase = phrase.replace("*", " * ")
    phrase = phrase.replace("+", " + ")
    # phrase = phrase.replace("^"," ^ ")
    # phrase = phrase.replace("-", " - ")
    phrase = phrase.replace("/", " / ")
    return phrase

##
def elementare_ableitung_hilfs_funktion(operator, innen):
    # operators=["sin","cos","exp","lnlog"cosh","sinh","tan","tanh","arccos","arcsin","arctan","arccosh","arcsinh","arctanh"]

    #Müsste getestet werden!

    if operator == "sin":
        return ["cos", innen]

    if operator == "cos":
        return ["-", ["sin", innen]]

    if operator == "exp":
        return ["exp", innen]

    if operator == "log":
        return ["/", "1", innen]

    if operator == "cosh":
        return ["sinh", innen]

    if operator == "sinh":
        return ["cosh", innen]

    if operator == "tan":
        return ["/", "1", ["^", ["cos", innen], 2]]

    if operator == "tanh":
        return ["/", "1", ["^", ["cosh", innen], 2]]

    if operator == "arccos":
        # -1/sqrt(1-x^2)
        return ["-", ["/", "1", ["^", ["+", ["1", ["-", ["^", innen, "2"]]]], "0.5"]]]

    if operator == "arcsin":
        # 1/sqrt(1-x^2)
        return ["/", "1", ["^", ["+", ["1", ["-", ["^", innen, "2"]]]], "0.5"]]

    if operator == "arctan":
        # 1/(1+x^2)
        return ["/", "1", ["+", ["1", ["^", innen, "2"]]]]

    if operator == "arccos":
        # 1/sqrt(x^2-1)
        return ["/", "1", ["^", ["+", ["-1", ["^", innen, "2"]]], "0.5"]]

    if operator == "arcsin":
        # 1/sqrt(x^2+1)
        return ["/", "1", ["^", ["+", ["1", ["^", innen, "2"]]], "0.5"]]

    if operator == "arctanh":
        # 1/(1+x^2)
        return ["/", "1", ["+", ["1", ["-", ["^", innen, "2"]]]]]

    else:
        print("Operator nicht erkannt")
def der_hilfs_funktion(f):
    if f[0] == "+":
        return ["+", [der_hilfs_funktion(summand) for summand in f[1]]]

    elif f[0] == "*":
        if len(f[1]) > 2:
            return ["+", [["*", [der_hilfs_funktion(f[1][index])] + [f[1][i] for i in range(len(f[1])) if i != index]] for index in range(len(f[1]))]]
        else:
            return ["+", [["*", [der_hilfs_funktion(f[1][0]), f[1][1]]], ["*", [der_hilfs_funktion(f[1][1]), f[1][0]]]]]


    elif f[0] == "/":
        return ["/", ["+", [["*", [f[2], der_hilfs_funktion(f[1])]], ["-", ["*", [der_hilfs_funktion(f[2]), f[1]]]]]], ["^", f[2], "2"]]

    elif f[0] == "^":
        if is_number(f[2]) == True:

            # Trennung um kein unnötiges Komma zu haben
            if float(f[2]) == int(float(f[2])):
                if f[1]=="x":
                    return ["*",[f[2], ["^", f[1], str(int(f[2]) - 1)]]]
                return ["*", [der_hilfs_funktion(f[1]), f[2], ["^", f[1], str(int(f[2]) - 1)]]]
            else:
                return ["*", [der_hilfs_funktion(f[1]), f[2], ["^", f[1], str(float(f[2]) - 1)]]]

        else:
            return ["*", [["+", ["/", f[2], f[1]], ["*", ["log", f[1]], der_hilfs_funktion(f[2])]], f]]  # (a^b)' =(b/a+ln(a)b')*a^b



    elif f[0] == "-":
        return ["-", der_hilfs_funktion(f[1])]

    elif f == "x":
        return "1"

    elif is_number(f) == True:
        return "0"

    # sonst operator

    else:
        #Nun ist es z.B. cos(...)

        #Falls ... = x, mache keine unnötige Kettenregel.
        if f[1] == "x":
            return elementare_ableitung_hilfs_funktion(f[0], f[1])

        #analog für ... = const
        elif is_number(f[1]) == True:
            return "0"

        else:
            # Für jeden elementaren operator explizit schreiben (z.B. (arctan(f))' = f' * 1/(1+f^2)
            return ["*", [der_hilfs_funktion(f[1]), elementare_ableitung_hilfs_funktion(f[0], f[1])]]
#work in progress:
def kuerze_listen(f):

    if f[0]=="+":
        S=0
        non_sumands = []
        list = f[1]
        i=0
        while i < len(list):
            list[i] = kuerze_listen(list[i])
            if is_number(list[i]) == True:
                S += float(list[i])
            else:
                non_sumands += [list[i]]
            i+=1

        if S != 0:
            if len(non_sumands) >= 1:
                return ["+",[str(S)] + non_sumands]
            elif len(non_sumands) == 0:
                return str(S)
        else:
            if len(non_sumands) > 1:
                return ["+",non_sumands]
            elif len(non_sumands) == 1:
                return non_sumands[0]
            elif len(non_sumands) == 0:
                return "0"

    if f[0]=="*":
        list = f[1]
        i=0
        non_factors = []
        M = 1 
        while i < len(list):
            list[i] = kuerze_listen(list[i])
            if is_number(list[i]) == True:
                M *= float(list[i])
            else:
                non_factors += [list[i]]
            i+=1

        if M == 0:
            return "0"
        elif M == 1:
            if len(non_factors)>1:
                return ["*",non_factors]
            if len(non_factors) == 1:
                return non_factors[0]
            else:
                return "1"
        else:
            if len(non_factors) >= 1:
                return ["*",[str(M)] + non_factors]
            else:
                return str(M)

    elif f[0]=="/":
        f[1] = kuerze_listen(f[1])
        f[2] = kuerze_listen(f[2])

        if f[1] == "0":
            return "0"
        else:
            return ["/",f[1],f[2]]

    elif f[0]=="^":
        f[1] = kuerze_listen(f[1])
        f[2] = kuerze_listen(f[2])

        if f[2] == "0":
            return "1"
        elif f[1] == "0":
            return "0"
        else:
            return ["^",f[1],f[2]]
    elif f[0] == "-":
        f[1] = kuerze_listen(f[1])
        if f[1] == "0":
            return "0"
        else:
            return ["-",f[1]]
    else:
        # zahl, variabeln und operatoren
        if is_number(f) == True or f == "x":
            return f
        elif f[0] in operators:
            return [f[0],kuerze_listen(f[1])]
        else:
            print("INPUT FEHLER")

class function():

    def __init__(self,str_or_list): #entweder string "x^2-1" oder Liste als definition einer Funktion
        if type(str_or_list) == str:
            self.str = str_or_list
            self.lam = lambda x: eval(self.str.replace("^", "**"))
            self.list = tree(self.str)
        else: #Liste
            self.list = str_or_list
            self.str = write(self.list)
            self.lam = lambda x: eval(self.str.replace("^", "**"))

    def diff(self):
        list_of_derivative = der_hilfs_funktion(self.list)
        list_of_derivative = kuerze_listen(list_of_derivative)
        return function(list_of_derivative)

def add(f,g):
    return function(f.str+"+"+g.str)
def mult(f,g):
    return function("("+f.str+")*("+g.str+")")
def div(f,g):
    return function("("+f.str+")/("+g.str+")")
def power(f,g):
    return function("("+f.str+")^("+g.str+")")
def minus(f):
    return function("-"+f.str)
def verkettet(f,g):
    return function(f.str.replace("x","("+g.str+")"))

#f = function("(cos(x) - sin(x) * x) * -sin(x * cos(x))")
