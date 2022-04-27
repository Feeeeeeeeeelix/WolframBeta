"""
FunctionClass.py module:

- parse mathematical expression into a syntax tree
- write expressions as LaTeX code
- differentiate expressions
- simplify expressions

"""

from analysis import trapez, riemann, simpson, der, trapez_fehler, simpson_fehler
from functions import *


FUNCTIONS = ['C', 'PGCD', 'PPCM', 'arccos', 'arccosh', 'arcsin', 'arcsinh', 'arctan', 'arctanh', 'cos', 'cosh', 'sin',
             'sinh', 'eratosthenes', 'exp', 'fact', 'ggT', 'isprime', 'kgV', 'log', 'ln', 'partition', 'pow', 'root',
             'sqrt', 'tan', 'tanh', 'Int', 'min', 'max', 'primfactors', 'nullstellen', "T", "s", "m", "v", "sq","normZ",
             "normS", "lu", "cholesky", "inverse", "det", "QR", "ausgleichs_problem", "power_method", "eigenvalues"]

SIMPLE_FUNCTIONS = ['cos', 'cosh', 'arccos', 'arccosh', 'sin', 'sinh', 'arcsin', 'arcsinh', 'tan', 'tanh', 'arctan',
                    'arctanh', 'exp', 'log', 'ln', 'sqrt']

DEFINED_FUNCTIONS = {}
DEFINED_MATRICES = []

ALPHABET = "qwertzuiopasdfghjklyxcvbnmQWERTZUIOPASDFGHJKLYXCVBNMπ"
NUMBERS = "0123456789"


dim = "riemann"
# für WolframBeta, wenn man von dort ein integral berechnet wird hier der fehler gespeichert damit wolframbeta den wert
# hier sehen und im interface zeigen kann:
int_fehler = 0


def isfloat(n: str or int or float) -> bool:
    if type(n) is bool or type(n) is list:
        return False
    try:
        float(n)
    except Exception:
        return False
    return True


def prod(iterable: list) -> int or list:
    if not iterable: return iterable
    
    prod = 1
    for factor in iterable:
        try:
            prod *= flint(factor)
        except ValueError as ve:
            raise ve  # ValueError ("non-float factor found: "+factor)
    return prod


def flint(x: int or float) -> int if int else float:
    x = float(x)
    return x if int(x) != x else int(x)


def _split_consts(f, test):
    # splittet Terme in f je nach test, zb mit test=isfloat
    constants, functions = [], []
    for arg in f:
        if test(arg):
            constants.append(arg)
        else:
            functions.append(arg)
    return constants, functions


def _extract_args(f):
    # f = "3(x+4)(x+6^x)ln(x)^2" -->  f = "3@@ln@^2", args = ['3', 'x+4', 'x+6^x', 'x']
    # nützlich für den parser, um klammerregelungen zu beachten
    
    def find_arg(f, i):
        arg, p = "", 0
        
        while i < len(f) and not (f[i] == ")" and p == 0):
            p = p + (f[i] == "(") - (f[i] == ")")
            arg += f[i]
            i += 1
        return arg, i
    
    args, i = [], 0
    while i < len(f):
        if f[i] == "(":
            arg, i = find_arg(f, i + 1)
            args.append(arg)
        i += 1
    
    for arg in args:
        f = f.replace(f"({arg})", "@", 1)
    
    return f, args


def _insert_args(f, innerargs):
    # f = "3@@ln@^2", innerargs = ['3', 'x+4', 'x+6^x', 'x'] -->   f = "3(x+4)(x+6^x)ln(x)^2"
    # Gegenteil von _extract_args
    
    if innerargs:
        n = 0
        fstr = str(f)
        for i in fstr:
            if i == "@":
                fstr = fstr.replace("@", f"({innerargs[n]})", 1)
                n += 1
        return eval(fstr)
    else:
        return f


def check_ensemble_de_definition(funcname, arg, n):
    df_error = lambda funcname, args: TypeError(*tuple(f"{args[0]} {text} {funcname}" for text in
                                                       ["gehört nicht in den Definitionsbeeich von",
                                                        "n'est pas dans l'ensemble de definition de",
                                                        "is not included in the domain of"]))
    n_error = lambda funcname, n: TypeError(*tuple(f"{funcname} {text} " for text in
                                                   [f"braucht nur {n} Argument",
                                                    f"ne prend que {n} argmuents",
                                                    f"only takes {n} arguments"]))
    
    if funcname in ['arccosh', 'arcsin', 'arcsinh', 'arctanh', 'cos', 'cosh', 'sin', 'sinh', 'eratosthenes',
                      'exp', 'fact', 'isprime', 'ln', 'partition', 'sqrt', 'tan', 'tanh'] and n > 1:
        raise n_error(funcname, 1)
    elif funcname in ['C', 'PGCD', 'PPCM', 'ggT', 'kgV', 'pow', 'root', 'log'] and n > 2:
        raise n_error(funcname, 2)
    
    if not isfloat(arg[0]):
        # bei variable
        return True
    else:
        arg = [flint(arg) for arg in arg]
    if funcname in ["ln", "log"] and arg[0] <= 0:
        raise df_error(funcname, arg)
    elif funcname == "sqrt" and arg[0] < 0:
        raise df_error(funcname, arg)
    elif funcname == "root" and int(arg[0]) < 0 and not arg[1] % 2:
        raise df_error(funcname, arg)
    elif funcname in ["arccos", "arcsin"] and not -1 <= arg[0] <= 1:
        raise df_error(funcname, arg)
    elif funcname in ['PGCD', 'PPCM', 'ggT', 'kgV'] and not arg[0] == int(arg[0]):
        raise df_error(funcname, arg)
    elif funcname in ['C', 'eratosthenes', 'fact', 'isprime', 'partition'] and not arg[0] == abs(int(arg[0])):
        raise df_error(funcname, arg)


def find_repeated_args(args: list, operation) -> list:
    dict = {}
    for arg in args:
        if arg in dict:
            dict[arg] += 1
        elif operation == "+" and arg[0] == "-" and arg[1:] in dict:
            dict[arg[1:]] -= 1
        elif operation == "+" and "-" + arg in dict:
            dict["-" + arg] -= 1
        else:
            dict[arg] = 1

    s = []
    for string, count in dict.items():
        if count == 1:
            s.append(string)
        elif count == 0:
            pass  # eh nur bei addition
        elif operation == "+" and string[0] == "-":
            s.append(f"{-count}*{string[1:]}")
        elif operation == "+":
            s.append(f"{count}*{string}")
        elif operation == "*":
            s.append(f"({string})^{count}")

    return s


def parse(f: str, simp=False) -> list or str:
    """Konvertiert einen mathematischen Ausdruck zu einem Syntaxtree die reihenfolge von operationen zu verstehen.
    Dabei werden Klammern und ihr inneres durch ein '@' (Da dies einer der charaktere ist, die der user nicht braucht/
    nicht eingeben darf) ersetzt und später wieder eingefügt. Falls simp=True, wird immer versucht de Ausdruck
    zu vereinfachen."""
    
    # Leerzeichen entfernen
    f = f.replace(" ", "").replace("**", "^")
    if not f:
        return ""
    
    if f[0] == "+":
        # positives vorzeichen wird ignoriert
        return parse(f[1:], simp)
    if isfloat(f):
        #Zahl
        return str(flint(f))
    if f[:-1] in SIMPLE_FUNCTIONS and f[-1] in ALPHABET + NUMBERS:
        # ex: sinx, sin2 -> sin(x), sin(2)
        return parse(f"{f[:-1]}({f[-1]})", simp)
    if f in SIMPLE_FUNCTIONS or f in DEFINED_MATRICES:
        # kommt nicht weiter, sonst wird ein name als factor von buchtstaben erkannt
        return f
    if len(f) >= 3 and "C" in f and isfloat(f[:f.index("C")]) and isfloat(f[f.index("C") + 1:]):
        # 2C3 -> C(2,3)
        return parse(f"C({f[:f.index('C')]},{f[f.index('C') + 1:]})", simp)
    if f in DEFINED_FUNCTIONS and simp:
        # Funktionsname einer im AnalysisFrame von WolframBeta definierten Funktion wird durch ihren term ersetzt
        return parse(DEFINED_FUNCTIONS[f], simp)
    # for matrix in DEFINED_MATRICES:
    #     if matrix in f and f"({matrix})" not in f:
    #         n0 = f.index(matrix)
    #         n1 = n0 + len(matrix)
    #         f = f[:n0] + "(" + f[n0:n1] + ")" + f[n1:]
    if f in ALPHABET and len(f) == 1:
        # varible/konstante
        return f
    if "@" in f:
        raise SyntaxError(f"Invalid character: '@'")
    
    f0 = f
    f, innerargs = _extract_args(f)  # klammern und ihr inneres ersetzen
    
    if ")" in f or "(" in f:
        raise SyntaxError
    
    if f == "@":
        # unnötige klammern
        return parse(innerargs[0], simp)
    
    # Ableitung:
    if f[0:3] == "d/d" and f[4] == "@" and len(f) == 5:
        # bsp: d/dx(e^x)
        var = f[3]
        assert type(var) == str
        if simp:
            return diff(parse(innerargs[0], simp), var)
        else:
            return ["diff", parse(innerargs[0]), var]
    
    # höhere approximative Ableitung:
    if len(f) == 10 and f[:2] == "d^" and f[3:5] == "/d" and f[6] == "^" and f[8:10] == "@@":
        # höhere Ableitung: f = "d^n/dx^n(f)(x_0) (n'te ableitung von f(x) nach x in x_0)
        
        if (n := f[2]) != f[7] or not isfloat(f[2]) or not isfloat(f[7]):
            raise ValueError("invalid n while taking the n'th derivative")
        if not isfloat(x_0 := innerargs[1]):
            raise TypeError("n'th derivative must be evaluated at a float value")
        
        if simp:
            return str(der(lambda x: eval(innerargs[0]), var=f[5], n=int(n))(flint(x_0)))
        else:
            return ["diff", parse(innerargs[0]), f[5], n, x_0]
    
    # höhere exakte ableitung
    if len(f) == 9 and f[:2] == "d^" and f[3:5] == "/d" and f[6] == "^" and f[8] == "@":
        # höhere Ableitung: f = "d^n/dx^n(f) (n'te ableitung von f(x) nach x)
        
        if (n := f[2]) != f[7] or not isfloat(f[2]) or not isfloat(f[7]):
            raise ValueError("invalid n while taking the n'th derivative")
        if simp:
            func = parse(innerargs[0], True)
            for i in range(int(n)):
                func = diff(func, f[5])
            return str(func)
        else:
            return ["diff", parse(innerargs[0]), f[5], n]
    
    # implizierte Multiplikationen:
    i = 0
    while i < len(f) - 1:
        """was gewollt nicht erkannt wird:
         nein:               sollte sein:
        "x2"                 "x^2" oder "x*2"
        "2!2"                "2!*2"
        "(x+1)2"            "(x+1)^2" oder "(x+1)*2"

        """
        # 2@ / 2x / @@ / @x / ax(keine funktion) --> implizierte multiplikation
        if f[i] in NUMBERS + "@" and f[i + 1] in "@" + ALPHABET \
                or (f[i] in ALPHABET and f[i + 1] in ALPHABET and "@" not in f and f[i] != "d"
                and not any([f.find(func) + len(func) < len(f) and func in f for func in FUNCTIONS])) \
                and not any(mat in f for mat in DEFINED_MATRICES):
            f = f[:i + 1] + "*" + f[i + 1:]
        
        # @2 -> verboten
        elif f[i] == "@" and f[i + 1] in NUMBERS:
            raise SyntaxError(*tuple(f"{text} : '){f[i + 1]}'" for text in
                                     ["Ungültiger Ausdruck", "Syntaxe invalide", "Invalid syntax"]))
        
        # x2 -> verboten
        elif f[i] in ALPHABET and f[i + 1] in NUMBERS:
            raise SyntaxError(*tuple(f"{text} : '{f[i]}{f[i + 1]}'" for text in
                                     ["Ungültiger Ausdruck", "Syntaxe invalide", "Invalid syntax"]))
        
        i += 1
        
        # 2-x / x-x / @-x --> implizierte addition mit negativem zweiten summand
        if f[i] == "-" and f[i - 1] in "@" + NUMBERS + ALPHABET:
            # Von 5-3 wird intern mit 5+-3 weitergerechnet
            f = f[:i] + "+" + f[i:]
    
    if "+" in f:
        summands = _insert_args(f.split("+"), innerargs)
        
        if not all(summands):
            raise SyntaxError(f"Invalid syntax: '{f}'")
        
        if simp:
            # bei zb "2+sin(x)+3+x" wird 2,3 von sinx, x getrennt
            # 2 und 3 werden addiert -> consts
            # wenn const = 0, dann soll consts = [] sein, damit am ende nicht 0+sinx+x steht
            consts, funcs = _split_consts(summands, isfloat)
            consts = sum([flint(s) for s in consts])
            consts = [str(consts)] if consts else []
            
            summands = find_repeated_args(consts + funcs, "+")
            if not summands:
                summands = ["0"]
        
        return ["+", [parse(s, simp) for s in summands]] if len(summands) > 1 else parse(summands[0], simp)
    
    if "*" in f:
        factors = _insert_args(f.split("*"), innerargs)
        
        if not all(factors):
            raise SyntaxError(f"Invalid syntax: '{f}'")
        
        if simp:
            consts, funcs = _split_consts(factors, isfloat)
            consts = [str(prod(consts))] if consts else []
            factors = find_repeated_args(consts + funcs, "*")
            if "0" in factors:
                return "0"
        
        return ["*", [parse(f, simp) for f in factors]] if len(factors) > 1 else parse(factors[0], simp)
    
    if f[0] == "-":
        # keine substraktion
        if len(f) == 2 and f[1] in ALPHABET+NUMBERS and f[1] not in DEFINED_FUNCTIONS:
            return f"-{f[1]}"
        else:
            return ["*", [-1, parse(f0[1:], simp)]]
    
    if "/" in f:
        div = _insert_args(f.split("/", 1), innerargs)
        
        if not all(div):
            raise SyntaxError(f"Invalid syntax: '{f}'")
        
        num, denom = parse(div[0], simp), parse(div[1], simp)
        
        if not denom:
            raise ZeroDivisionError
        
        return ["/", [num, denom]] if not(num == denom and simp) else 1
    
    if "^" in f:
        base, exp = _insert_args(f.split("^", 1), innerargs)
        
        if not base or not exp:
            raise SyntaxError(f"Invalid syntax: '{f}'")
        
        return ["^", [parse(base, simp), parse(exp, simp)]]
    
    # Funktion
    if f[0] in ALPHABET and f[-1] == "@":
        funcname = f[:-1]
        
        if funcname in FUNCTIONS:
            args = innerargs[0].split(",")
            n = len(args)
            
            if funcname == "Int":
                return ["Int", flint(args[0]), flint(args[1]), parse(args[2], simp), *args[3:]]
            
            check_ensemble_de_definition(funcname, args, n)
            
            if funcname == "root" and len(args) == 1:
                return ["sqrt", parse(args[0], simp)]
            
            if funcname == "log" and len(args) == 1:
                return ["ln", parse(args[0], simp)]
            
            if funcname == "pow":
                return parse(f"{args[0]}**{args[1]}")
            
            return [funcname, *[parse(a, simp) for a in args]]
        
        elif funcname in DEFINED_FUNCTIONS:
            if simp:
                return (lambda x: eval(DEFINED_FUNCTIONS[funcname]))(float(innerargs[0]))
            else:
                return [funcname, parse(innerargs[0], simp)]
        else:
            raise SyntaxError(*tuple(f"{text}: {funcname}" for text in
                                     ["Unbekannte funktion",
                                      "Fonction inconnue",
                                      "Unknown function"]))
    
    if f.endswith("!"):
        if f == "@!":
            return parse(f"fact({innerargs[0]})", simp)
        
        elif (isfloat(f[:-1]) or f[:-1] in ALPHABET) and f[:-1]:
            return parse(f"fact({f[:-1]})", simp)
        
        else:
            raise SyntaxError("usage of '!' not clear")
    
    raise SyntaxError(f"Invalid syntax: '{f}'")  # Falls keine der Fälle oben eingetreten ist, ist was falsch geschriebn


def write(f: list) -> str:
    """Schreibt den Syntaxtree wieder als lesbaren Ausdruck, und vereinfacht ihn ,wenn möglich"""
    
    if type(f) != list:
        return str(f)
    
    if f[0] == "+":
        args = [write(i) for i in f[1] if str(i) != "0"]
        
        if not args:
            return 0
        
        consts, funcs = _split_consts(args, isfloat)
        consts = [str(sum(flint(c) for c in consts))] if consts else []
        summands = consts + funcs
        
        sum_ = summands[0]
        for s in summands[1:]:
            sum_ += f" + {s}" if s[0] != "-" else f" - {s[1:]}"
            
        return sum_
    
    if f[0] == "*":
        args = [str(write(arg)) for arg in f[1]]
        factors = []
        for arg in args:
            if str(arg) == "0":
                return "0"
            # try:
            #     factors.append(str(eval(str(arg))))
            # except:
            #     pass
            
            if "+" in arg or "-" in arg:
                factors.append(f"({arg})")
            
            elif arg != "1" and arg != ["ln", "e"]:
                factors.append(arg)
                
        consts, funcs = _split_consts(factors, isfloat)
        consts = [str(prod(consts))] if consts else []
        
        return "*".join(consts + funcs) if consts + funcs else 1
    
    if f[0] == "/":
        num = f[1][0]
        if type(num) == list:
            num = f"({write(num)})" if num[0] in "+diff" else write(num)
        
        denom = f[1][1]
        if type(denom) == list:
            denom = f"({write(denom)})" if denom[0] in "+*/diff" else write(denom)
            
        if not denom:
            raise ZeroDivisionError
        
        return 1 if num == denom else f"{num}/{denom}"
    
    if f[0] == "^":
        base = f"({write(f[1][0])})" if type(f[1][0]) == list and f[1][0][0] not in FUNCTIONS else write(f[1][0])
        power = f"({write(f[1][1])})" if type(f[1][1]) == list else f[1][1]
        
        try:
            # Versuch, den exponenten zu vereinfachen
            power = str(eval(power))
        except:
            pass
        
        return f"{base}**{power}" if power not in "(1)" else base if power == "0" else "1"
    
    if f[0] in FUNCTIONS+list(DEFINED_FUNCTIONS.keys()):
        if f[0] == "Int":
            return str(integrate(*f[1:]))
        
        args = ", ".join([str(write(arg)) for arg in f[1:]])
        try:
            # es wird versucht, die funktion gleich mit args zu evaluieren
            return eval(f"{f[0]}({args})")
        except Exception:
            return f"{f[0]}({args})"
    
    if f[0] == "diff":
        # erste Ableitung
        return f"d/d{f[2]}({write(f[1])})"


def write_latex(f: list, simp=False) -> str:
    """Schreibt den Syntaxtree als LaTeX code auf. Wenn simp=True wird versucht, den Ausdruck zu vereinfachen"""
    
    if type(f) != list:
        return str(f)
    
    if f[0] == "+":
        sum_ = [write_latex(i, simp) for i in f[1] if not(str(i) == "0" and simp)]
        
        if simp:
            if not sum_:
                return 0
            consts, funcs = _split_consts(sum_, isfloat)
            consts = [str(sum(flint(c) for c in consts))] if consts else []
            sum_ = find_repeated_args(consts + funcs, "+")
            
        summands = []
        for summand in sum_:
            if summand.startswith("(-1) \\cdot "):
                summands.append("-"+summand[11:])
                
            elif summand.startswith("(-") and ") \\cdot " in summand and isfloat(fac := summand[2:summand.index(") \\cdot ")]):
                summands.append(f"-{fac} \\cdot  " + summand[summand.index(") \\cdot ")+8:])
                
            else:
                summands.append(summand)
                
        sum_ = summands[0]
        for s in summands[1:]:
            sum_ += f" + {s}" if s[0] != "-" else f" - {s[1:]}"
        
        return sum_
    
    if f[0] == "*":
        factors = f[1]
        
        if simp:
            
            for fac in factors[::-1]:
                if type(fac) == list and fac[0] == "*":
                    # Ein Faktor der ganzen Multiplikation ist auch selber eine Multiplikation
                    # Hier werden die Terme zusammengetan, damit keine unnötigen Klammern entstehen
                    factors.remove(fac)
                    factors.extend(fac[1])
            
            factors = [str(write_latex(fact, simp)) for fact in factors]
            consts, funcs = _split_consts(factors, isfloat)
            consts = [str(prod(consts))] if consts else []
            
            if consts == ["0"]:
                return "0"
            if consts == ["1"]:
                consts = []
                
            factors = find_repeated_args(consts + funcs, "*")
            
        else:
            factors = [str(write_latex(fact, simp)) for fact in factors]

        factors = [f"({fact})" if "+" in fact or "-" in fact else fact for fact in factors]
        if factors[0] == "(-1)":
            factors = ["-"+factors[1], *factors[2:]]
        
        return r" \cdot ".join(factors) if factors else 1
    
    if f[0] == "/":
        num = write_latex(f[1][0], simp)
        denom = write_latex(f[1][1], simp)
        
        if not denom:
            raise ZeroDivisionError
        
        return 1 if num == denom and simp else r"\frac{" + str(num) + "}{" + str(denom) + "}"
    
    if f[0] == "^":
        base = write_latex(f[1][0], simp)
        power = write_latex(f[1][1], simp)
        
        if simp:
            try:
                power = eval(power)
            except:
                pass
            
            if power == "1":
                return base
            elif power == "0":
                return "1"
        
        if isfloat(base) or base in ALPHABET:
            # man braucht keine Klammern
            return "{" + str(base) + "}^{" + str(power) + "}"
        else:
            return "{(" + str(base) + ")}^{" + str(power) + "}"
    
    if f[0] in FUNCTIONS+list(DEFINED_FUNCTIONS.keys()):
        
        if f[0] == "log":
            return "\\" + f[0] + "_{" + str(write_latex(f[2], simp)) + "}(" + str(write_latex(f[1], simp)) + ")"
        
        if f[0] == "root":
            n = write_latex(f[2], simp)
            if isfloat(n):
                return "\\sqrt[" + str(n) + "]{" + str(write_latex(f[1], simp)) + "}"
            
            else:
                return write_latex(["^", [f[1], ["/", ["1", n]]]], simp)
            
        if f[0] == "sqrt":
            return rf"\sqrt{'{'}{write_latex(f[1], simp)}{'}'}"
        
        if f[0] == "Int":
            return "\\int_{" + str(f[1]) + "}^{" + str(f[2]) + "}{" + write_latex(f[3], simp) + "}d" + f[4]
        
        if f[0] in SIMPLE_FUNCTIONS:
            return "\\" + f[0] + "(" + str(write_latex(f[1], simp)) + ")"
        
        else:
            args = ", ".join(str(write_latex(arg, simp)) for arg in f[1:])
            return f"{f[0]}({args})"
    
    if f[0] == "diff":
        if len(f) == 3:
            # Erste Ableitung
            return rf"\frac{'{d}{d'}{f[2]}{'}'}({write_latex(f[1], simp)})"
        elif len(f) == 4:
            # n'te Exakte Ableitung
            return rf"\frac{'{'}d^{f[3]}{'}{'}d{f[2]}^{f[3]}{'}'}({write_latex(f[1], simp)})"
        elif len(f) == 5:
            # n'te Approximative Ableitung in f[4]
            return rf"\frac{'{'}d^{f[3]}{'}{'}d{f[2]}^{f[3]}{'}'}({write_latex(f[1], simp)})\vert_{'{'}x={f[4]}{'}'}"


def diff(f: list, VAR: str) -> list or int:

    def funcderivative(f):
        dln = lambda u: ["/", [1, u]]
        dexp = lambda u: ["exp", u]
        dsqrt = lambda u: ["/", [1, ["*", [2, ["sqrt", u]]]]]
        
        dsin = lambda u: ["cos", u]
        dcos = lambda u: ["*", [-1, ["sin", u]]]
        dtan = lambda u: ["/", [1, ["^", [["cos", u], 2]]]]
        
        dsinh = lambda u: ["cosh", u]
        dcosh = lambda u: ["sinh", u]
        dtanh = lambda u: ["/", [1, ["^", [["cosh", u], 2]]]]
        
        darcsin = lambda u: ["/", [1, ["^", [["+", [1, ["*", [-1, ["^", [u, "2"]]]]]], 0.5]]]]
        darccos = lambda u: ["/", [-1, ["^", [["+", [1, ["*", [-1, ["^", [u, "2"]]]]]], 0.5]]]]
        darctan = lambda u: ["/", [1, ["+", [1, ["^", [u, 2]]]]]]
        
        darccosh = lambda u: ["/", [1, ["sqrt", ["+", [["^", [u, 2]], -1]]]]]
        darcsinh = lambda u: ["/", [1, ["sqrt", ["+", [["^", [u, 2]], 1]]]]]
        darctanh = lambda u: ["/", [1, ["+", [1, ["*", [-1, ["^", [u, 2]]]]]]]]
        
        u = f[1]  # innere Funktion
        du = diff(u, VAR)
        
        if f[0] == "log":
            if len(f) == 3:
                return ["/", [du, ["*", [u, ["ln", f[2]]]]]]
            else:
                return ["/", [du, u]]
    
        if du == 0:
            return 0
        elif du == 1:
            return eval(f"d{f[0]}")(u)
        else:
            return ["*", [du, eval("d" + f[0])(u)]]
    
    def isconst(a):
        return VAR not in str(a)
    
    if isconst(f):
        return 0
    
    if type(f) != list:
        return 1 if f == VAR else 0
    
    if f[0] == "*":
        constfactors, funcfactors = _split_consts(f[1], isconst)
        
        if len(funcfactors) > 1:
            fpairs = [["*", [diff(funcfactors[i], VAR), *funcfactors[:i], *funcfactors[i + 1:]]] for i in
                      range(len(funcfactors))]
            funcfactors = ["+", fpairs]
        else:
            funcfactors = diff(funcfactors[0], VAR)
        
        return ["*", [*constfactors, funcfactors]] if constfactors else funcfactors
    
    elif f[0] == "/":
        if isconst(f[1][0]):  # (k/u)' = (-1*k*du)/u^2
            return ["/", [["*", [-1, diff(f[1][1], VAR), f[1][0]]], ["^", [f[1][1], 2]]]]
        elif isconst(f[1][1]):  # (u/k)' = u'/k
            return ["/", [diff(f[1][0], VAR), f[1][1]]]
        else:  # (u/v)' = (v*u' - v'u)/v²
            return ["/", [["+", [["*", [diff(f[1][0], VAR), f[1][1]]], ["*", [-1, diff(f[1][1], VAR), f[1][0]]]]],
                          ["^", [f[1][1], 2]]]]
    
    elif f[0] == "+":
        summands = [diff(i, VAR) for i in f[1] if not isconst(i)]
        
        return ["+", summands] if len(summands) > 1 else summands[0] if summands else "0"
    
    elif f[0] == "^":
        base = f[1][0]
        exp = f[1][1]
        
        if VAR in str(base) and VAR not in str(exp):
            # x^a
            if not isfloat(exp):
                return ["*", [exp, diff(base, VAR), ["^", [base, ["+", [exp, -1]]]]]]
            else:
                return ["*", [exp, diff(base, VAR), ["^", [base, exp - 1]]]]
            
        if VAR in str(exp) and VAR not in str(base):
            # a^x
            return ["*", [["ln", base], diff(exp, VAR), ["^", [base, exp]]]]
        
        else:
            # x^x
            return ["*", [diff(["*", [exp, ["ln", base]]], VAR), ["^", [base, exp]]]]
    
    elif f[0] == "root":
        return diff(["^", [f[1], ["/", [1, f[2]]]]], VAR) if len(f) > 2 else diff(["sqrt", f[1]], VAR)
    
    elif f[0] in SIMPLE_FUNCTIONS:
        return funcderivative(f)
    
    elif f[0] == "diff":
        return diff(f[1], f[2])
    
    else:
        raise Exception(f"Couldn't differentiate {write(f)}")


def set_default_integration_method(method):
    global dim
    dim = method


def integrate(a, b, f, variable, method=None):
    global int_fehler
    # method: riemann, trapez or simpson
    f = Function(f, variable)
    if not method:
        method = dim
    if method in ("trapez", "simpson"):
        int_fehler = {"trapez": trapez_fehler, "simpson": simpson_fehler}[method](f, a, b)
    return {"riemann": riemann, "trapez": trapez, "simpson": simpson}[method](f, a, b)


def get_int_fehler():
    return int_fehler


def set_int_fehler(fel=0):
    global int_fehler
    int_fehler = fel


class Function:
    def __init__(self, inputfunc: str or list, variable="x"):
        self.var = variable
        
        if type(inputfunc) == str:
            self.str = inputfunc
            
            self.tree = parse(self.str, simp=False)
            self.latex_in = str(write_latex(self.tree, simp=False))
            
            self.tree = parse(self.str, simp=True)
            self.str_out = str(write(self.tree))
            self.latex_out = str(write_latex(self.tree, simp=True))
            
        else:
            assert type(inputfunc) == list
            self.tree = inputfunc
            
            self.str_out = str(write(self.tree))
            self.latex_out = str(write_latex(self.tree, simp=True))
            
        self.lam = lambda x: eval(self.str_out.replace("^", "**"))
    
    def diff(self, var="x"):
        d = diff(self.tree, var)
        print(d)
        return Function(d)
    
    def __call__(self, x):
        return self.lam(x)
    
    def __add__(self, other):
        if isinstance(other, Function):
            return Function(self.str_out + "+" + other.str_out)
        else:
            return Function(self.str_out + "+" + str(other))
    
    def __sub__(self, other):
        if isinstance(other, Function):
            return Function(self.str_out + "-" + other.str_out)
        else:
            return Function(self.str_out + "-" + str(other))
    
    def __mul__(self, other):
        if isinstance(other, Function):
            return Function(self.str_out + "*" + other.str_out)
        else:
            return Function(self.str_out + "*" + str(other))
        
    def __rmul__(self, other):
        return self*other
    
    def __pow__(self, power):
        return Function(["^", [self.tree, str(power)]])
    
    def __str__(self):
        return self.str_out


if __name__ == "__main__":
    func = "d/dx(root(x, 3))"
    
    try:
        s = Function(func)
        print(s.tree)
        print(s.str)
        print(s.latex_in)
        print(s.str_out)
        print(s.latex_out)
        print("diff:")
        print(s.diff())
        
    except Exception as e:
        raise e
    
