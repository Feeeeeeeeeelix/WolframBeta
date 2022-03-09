from functions import *
import analysis


"""TODO:
- definitonsmenge checken neu
- latex 2*x -> 2x
- aCb -> C(a,b) ? (auch mit P?)

- Vereinfachen
- 1/x*x -> 1
- sin(x) - sin(x) -> 0            }
- sin(x) + 2sin(x) -> 3*sin(x)    } kompliziert!
- sin²(x) * sin³(x) -> sin⁵(x)    }
lol
"""

"""was gewollt nicht erkannt wird:
 nein:               sollte sein:
"x2"                 "x^2" oder "x*2"  
"2!2"                "2!*2"   
"(x+1)2"            "(x+1)^2" oder "(x+1)*2"

"""

FUNCTIONS = ['C', 'PGCD', 'PPCM', 'arccos', 'arccosh', 'arcsin', 'arcsinh', 'arctanh', 'cos', 'cosh', 'sin', 'sinh',
             'eratosthenes', 'exp', 'fact', 'ggT', 'isprime', 'kgV', 'log', 'ln', 'partition', 'pow', 'root',
             'sqrt', 'tan', 'tanh', 'Int']
ALPHABET = "qwertzuiopasdfghjklyxcvbnmQWERTZUIOPASDFGHJKLYXCVBNMπ"
NUMBERS = "0123456789"

PRINT = ""

dim = "riemann"


def isfloat(n: str or int or float) -> bool:
    try:
        float(n)
    except ValueError:
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
    constants, functions = [], []
    for arg in f:
        if test(arg):
            constants.append(arg)
        else:
            functions.append(arg)
    return constants, functions


def _extract_args(f):
    # f = "3(x+4)(x+6^x)ln(x)^2" -->  f = "3@@ln@^2", args = ['3', 'x+4', 'x+6^x', 'x']
    
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
        f = f.replace(f"({arg})", "@")
    
    return f, args


def _insert_args(f, innerargs):
    # f = "3@@ln@^2", innerargs = ['3', 'x+4', 'x+6^x', 'x'] -->   f = "3(x+4)(x+6^x)ln(x)^2"
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


def check_ensemble_de_definition(funcname, arg):
    if not isfloat(arg[0]):
        return True
    else:
        arg = [flint(arg) for arg in arg]
    if funcname in ["ln", "log"] and flint(arg[0]) <= 0:
        return False
    if funcname == "sqrt" and int(arg[0]) < 0:
        return False
    if funcname == "root" and int(arg[0]) < 0 and not flint(arg[1]) % 2:
        return False
    if funcname in ["arccos", "arcsin"] and not -1 <= flint(arg[0]) <= 1:
        return False
    if funcname == "fact" and not flint(arg[0]) == int(arg[0]):
        return False
    else:
        return True


def parse(f: str, ableiten=False):
    global PRINT
    PRINT += f"\nparse:{f}"
    
    # Leerzeichen entfernen
    f = f.replace(" ", "")
    
    if isfloat(f):
        return flint(f)
    if f in ALPHABET:
        return f
    
    f0 = f
    f, innerargs = _extract_args(f)  # klammern und ihr inneres ersetzen
    
    if f == "@":
        # unnötige klammern
        return parse(innerargs[0], ableiten)
    
    # implizierte Multiplikationen
    i = 0
    while i < len(f) - 1:
        # 2@ / 2x / @@ / @x / ax(keine funktion) --> implizierte multiplikation
        if f[i] in NUMBERS + "@" and f[i + 1] in "@" + ALPHABET or (
                f[i] in ALPHABET and f[i + 1] in ALPHABET and "@" not in f and f[i] != "d"):
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
            f = f[:i] + "+" + f[i:]
    
    def find_repeated_args(args: list, operation) -> list:
        arg_list = []
        factors = []
        # arg_and_factor = []
        # for arg in args:
        #     if arg not in arg_and_factor[::2]:
        #         arg_and_factor.append(arg)
        #         arg_and_factor.append(1)
        #     elif arg in arg_and_factor[::2]:
        #         arg_and_factor[arg_and_factor.index(arg) + 1] += 1
        #     elif type(arg) == list and arg[0] == "+":
        #         for eventual_factor in arg_and_factor[::2]:
        #             if eventual_factor in arg[1]:
        #                 arg_and_factor[arg_and_factor.index(eventual_factor) + 1] +=  WTF ich gebe auf
        
        for arg in args:
            if arg in factors:
                continue
            count = args.count(arg)
            if count > 1:
                arg_list.append(["^", [arg, count]]) if operation == "mult" else arg_list.append(["*", [count, arg]])
                factors.append(arg)
            else:
                arg_list.append(arg)
                factors.append(arg)
        return arg_list
    
    if "+" in f:
        summands = _insert_args(f.split("+"), innerargs)
        
        consts, funcs = _split_consts(summands, isfloat)
        consts = sum([flint(s) for s in consts])
        consts = [str(flint(consts))] if consts else []
        
        summands = [parse(s, ableiten) for s in consts + funcs]
        summands = find_repeated_args(summands, "sum")
        if not summands:
            summands = [0]
        PRINT += f"\n{summands=}, {consts = }, {funcs = }"
        return ["+", summands] if len(summands) > 1 else summands[0]
    
    if "*" in f:
        factors = _insert_args(f.split("*"), innerargs)
        PRINT += f"\n{factors = }"
        
        consts, funcs = _split_consts(factors, isfloat)
        PRINT += f"\n{consts = }, {funcs = }"
        consts = [str(prod(consts))] if consts else []
        
        PRINT += f"\n{consts = }"
        factors = [parse(f, ableiten) for f in consts + funcs]
        factors = find_repeated_args(factors, "mult") if len(factors) >= 2 else factors
        
        PRINT += f"\n{factors=}, {consts = }, {funcs = }"
        return ["*", factors] if len(factors) > 1 else factors[0] if 0 not in factors else 0
    
    if f[0] == "-":
        # keine substraktion
        return ["*", [-1, parse(f0[1:], ableiten)]]
    
    # Ableitung
    if f[0:3] == "d/d" and f[4] == "@" and len(f) == 5:
        var = f[3]
        assert type(var) == str
        if ableiten:
            PRINT += f"\nparse: diff: {f = }"
            return diff(parse(innerargs[0]), var)
        else:
            PRINT += f"\nparse: not diff: {f = }"
            return ["diff", parse(innerargs[0], ableiten), var]
    
    if "/" in f:
        div = _insert_args(f.split("/", 1), innerargs)
        PRINT += f"\n{div = }"
        
        num, denom = parse(div[0], ableiten), parse(div[1], ableiten)
        if not denom: raise ZeroDivisionError
        return ["/", [num, denom]] if num != denom else 1
    
    if "^" in f:
        base, exp = _insert_args(f.split("^", 1), innerargs)
        PRINT += f"\n{base=}, {exp=}"
        return ["^", [parse(base, ableiten), parse(exp, ableiten)]]
    
    # Funktion
    if f[0] in ALPHABET and f[-1] == "@":
        funcname = f[:-1]
        if funcname in FUNCTIONS:
            args = innerargs[0].split(",")
            if funcname == "Int":
                return ["Int", flint(args[0]), flint(args[1]), parse(args[2]), *args[3:]]
            if not check_ensemble_de_definition(funcname, args):
                raise TypeError(*tuple(f"{args[0]} {text} {funcname}" for text in
                                       ["gehört nicht in den Definitionsbeeich von",
                                        "n'est pas dans l'ensemble de definition de",
                                        "is not included in the domain of"]))
            if funcname == "root" and len(args) == 1:
                return ["root", args[0], 2]
            return [funcname, *[parse(a, ableiten) for a in args]]
        
        else:
            raise SyntaxError(*tuple(f"{text}: {funcname}" for text in
                                     ["Unbekannte funktion",
                                      "Fonction inconnue",
                                      "Unknown function"]))

    if f.endswith("!"):
        if f == "@!":
            return parse(f"fact({innerargs[0]})")
        else:
            return parse(f"fact({f[:-1]})")

    raise Exception(f"The parser doesn't know how to parse: {f}")


def parse_ws(f):
    # without simplifying
    global PRINT
    PRINT += f"\nparse_ws:{f}"

    # Leerzeichen entfernen
    f = f.replace(" ", "")

    if isfloat(f):
        return flint(f)
    if f in ALPHABET:
        return f

    f0 = f
    f, innerargs = _extract_args(f)  # klammern und ihr inneres ersetzen

    if f == "@":
        # unnötige klammern
        return parse_ws(innerargs[0])

    # implizierte Multiplikationen
    i = 0
    while i < len(f) - 1:
        # 2@ / 2x / @@ / @x / ax(keine funktion) --> implizierte multiplikation
        if f[i] in NUMBERS + "@" and f[i + 1] in "@" + ALPHABET or (
                f[i] in ALPHABET and f[i + 1] in ALPHABET and "@" not in f and f[i] != "d"):
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
            f = f[:i] + "+" + f[i:]

    if "+" in f:
        summands = _insert_args(f.split("+"), innerargs)
        PRINT += f"\n{summands=}"
        return ["+", [parse_ws(s) for s in summands]]

    if "*" in f:
        factors = _insert_args(f.split("*"), innerargs)
        PRINT += f"\n{factors = }"
        return ["*", [parse_ws(factor) for factor in factors]]

    if f[0] == "-":
        # keine substraktion
        return ["*", [-1, parse_ws(f[1:])]]

    # Ableitung
    if f[0:3] == "d/d" and f[4] == "@" and len(f) == 5:
        var = f[3]
        assert not isfloat(var)
        return ["diff", parse_ws(innerargs[0]), var]

    if "/" in f:
        div = _insert_args(f.split("/", 1), innerargs)
        PRINT += f"\n{div = }"

        num, denom = parse_ws(div[0]), parse_ws(div[1])
        if not denom: raise ZeroDivisionError
        return ["/", [num, denom]]

    if "^" in f:
        base, exp = _insert_args(f.split("^", 1), innerargs)
        PRINT += f"\n{base=}, {exp=}"
        return ["^", [parse_ws(base), parse_ws(exp)]]

    # Funktion
    if f[0] in ALPHABET and f[-1] == "@":
        funcname = f[:-1]
        if funcname in FUNCTIONS:
            args = innerargs[0].split(",")
            # if len(args) > 2:
            #     raise TypeError(*tuple(f"{funcname}  {text}" for text in
            #                            ["", "", "takes at most 2 arguments"]))
            if funcname == "Int":
                return ["Int", flint(args[0]), flint(args[1]), parse_ws(args[2]), *args[3:]]
            if not check_ensemble_de_definition(funcname, args):
                raise TypeError(*tuple(f"{args[0]} {text} {funcname}" for text in
                                       ["gehört nicht in den Definitionsbereich von",
                                        "n'est pas dans l'ensemble de definition de",
                                        "is not included in the domain of"]))
            if funcname == "root" and len(args) == 1:
                return ["root", args[0], 2]

            return [funcname, *[parse_ws(a) for a in args]]

        else:
            raise SyntaxError(*tuple(f"{text}: {funcname}" for text in
                                     ["Unbekannte funktion",
                                      "Fonction inconnue",
                                      "Unknown function"]))

    if f.endswith("!"):
        if f == "@!":
            return parse_ws(f"fact({innerargs[0]})")
        else:
            return parse_ws(f"fact({f[:-1]})")

    raise Exception(f"The parser doesn't know how to parse: {f}")


def write(f: list) -> str or int:
    global PRINT
    PRINT += f"\nwrite: {f=}"
    
    if type(f) != list:
        return f
    
    if f[0] == "+":
        args = [write(i) for i in f[1] if str(i) != "0"]
        
        PRINT += f"\nsumargs: {args}"
        if not args:
            return 0
        
        consts, funcs = _split_consts(args, isfloat)
        PRINT += f"\n{consts=}, {funcs=}"
        
        consts = [str(sum(flint(c) for c in consts))] if consts else []
        summands = consts + funcs
        sum_ = summands[0]
        for s in summands[1:]:
            sum_ += f" + {s}" if s[0] != "-" else f" - {s[1:]}"
        return sum_
    
    if f[0] == "*":
        args = []
        for i in f[1]:
            factor = str(write(i))
            
            if factor == "0":
                return 0
            if type(i) == list and i[0] in "+-":
                factor = f"({factor})"
            if factor != "1" and factor != "ln(e)":
                args.append(factor)
        
        consts, funcs = _split_consts(args, isfloat)
        consts = [str(prod(consts))] if consts else []
        
        return "*".join(consts + funcs) if consts + funcs else 1
    
    if f[0] == "/":
        num = f[1][0]
        if type(num) == list:
            num = f"({write(num)})" if num[0] in "+diff" else write(num)
        
        denom = f[1][1]
        if type(denom) == list:
            denom = f"({write(denom)})" if denom[0] in "+*/diff" else write(denom)
        if not denom: raise ZeroDivisionError
        return 1 if num == denom else f"{num}/{denom}"
    
    if f[0] == "^":
        base = f"({write(f[1][0])})" if type(f[1][0]) == list and f[1][0][0] not in FUNCTIONS else write(f[1][0])
        power = f"({write(f[1][1])})" if type(f[1][1]) == list else f[1][1]
        PRINT += f"\n{base=}, {power=}"
        try:
            power = eval(power)  # if "-" in power else power
            PRINT += "\nEVAL: " + power
        except:
            pass
        return f"{base}**{power}" if power != 1 and power != "(1)" else base if int(power) != 0 else 1
    
    if f[0] in FUNCTIONS:
        if f[0] == "Int":
            return str(integrate(*f[1:]))
        args = ", ".join([str(write(arg)) for arg in f[1:]])
        return f"{f[0]}({args})"
    
    if f[0] == "diff":
        return f"d/d{f[2]}({write(f[1])})"


def write_latex(f: list):
    global PRINT
    PRINT += f"\nwrite latex: {f=}"
    
    if type(f) != list:
        return f
    
    if f[0] == "+":
        args = [write_latex(i) for i in f[1] if str(i) != "0"]
        
        PRINT += f"\nsumargs: {args}"
        if not args:
            return 0
        
        consts, funcs = _split_consts(args, isfloat)
        PRINT += f"\n{consts=}, {funcs=}"
        
        consts = [str(sum(flint(c) for c in consts))] if consts else []
        summands = consts + funcs
        sum_ = summands[0]
        for s in summands[1:]:
            sum_ += f" + {s}" if s[0] != "-" else f" - {s[1:]}"
        
        return sum_
    
    if f[0] == "*":
        args = []
        for i in f[1]:
            factor = str(write_latex(i))
            if factor == "0":
                return 0
            if type(i) == list and i[0] in "+-":
                factor = f"({factor})"
            if factor != "1" and factor != "ln(e)":
                args.append(factor)
        
        consts, funcs = _split_consts(args, isfloat)
        consts = [str(prod(consts))] if consts else []
        
        return r" \cdot ".join(consts + funcs) if consts + funcs else 1
    
    if f[0] == "/":
        num = write_latex(f[1][0])
        denom = write_latex(f[1][1])
        PRINT += f"\n{num = }, {denom = }"
        
        if not denom: raise ZeroDivisionError
        return 1 if num == denom else r"\frac{" + str(num) + "}{" + str(denom) + "}"
    
    if f[0] == "^":
        base = write_latex(f[1][0])
        power = write_latex(f[1][1])
        PRINT += f"\n{base = },{power =}"
        try:
            power = eval(power)  # if "-" in power else power
            PRINT += "\nEVAL: " + power
        except:
            pass
        
        if power == 1 or power == "(1)":
            return base
        elif str(power) == "0":
            return 1
        else:
            return "{" + str(base) + "}^{" + str(power) + "}"
    
    if f[0] in FUNCTIONS:
        # args = [str(write(arg)) for arg in f[1:]]
        if f[0] == "log":
            return "\\" + f[0] + "_" + str(write_latex(f[2])) + "(" + str(write_latex(f[1])) + ")"
        
        if f[0] == "root":
            n = write_latex(f[2])
            if isfloat(n):
                return "\\sqrt[" + str(n) + "]{" + str(write_latex(f[1])) + "}"
            else:
                return write_latex(["^", [f[1], ["/", [1, f[2]]]]])
        if f[0] == "sqrt":
            return rf"\sqrt{'{'}{write_latex(f[1])}{'}'}"
        if f[0] == "Int":
            return "\\int_{" + str(f[1]) + "}^{" + str(f[2]) + "}{" + write_latex(f[3]) + "}d" + f[4]

        return "\\" + f[0] + "(" + str(write_latex(f[1])) + ")"
    
    if f[0] == "diff":
        return rf"\frac{'{d}{d'}{f[2]}{'}'}({write_latex(f[1])})"


def write_latex_ws(f: list):
    global PRINT
    PRINT += f"\nwrite latex ws: {f=}"

    if type(f) != list:
        return f

    if f[0] == "+":
        args = [str(write_latex_ws(i)) for i in f[1]]
        PRINT += f"\nsumargs: {args}"

        sum_ = args[0]
        for s in args[1:]:
            sum_ += f" + {s}" if s[0] != "-" else f" - {s[1:]}"

        return sum_

    if f[0] == "*":
        args = []
        for i in f[1]:
            factor = str(write_latex_ws(i))
            if type(i) == list and i[0] in "+-":
                factor = f"({factor})"
            args.append(factor)

        return r" \cdot ".join(args)

    if f[0] == "/":
        num = write_latex_ws(f[1][0])
        denom = write_latex_ws(f[1][1])
        PRINT += f"\n{num = }, {denom = }"

        if not denom: raise ZeroDivisionError
        return r"\frac{" + str(num) + "}{" + str(denom) + "}"

    if f[0] == "^":
        base = write_latex_ws(f[1][0])
        power = write_latex_ws(f[1][1])
        PRINT += f"\n{base = },{power =}"

        return "{" + str(base) + "}^{" + str(power) + "}"

    if f[0] in FUNCTIONS:
        # args = [str(write(arg)) for arg in f[1:]]
        if f[0] == "log":
            return "\\log_" + str(write_latex_ws(f[2])) + "(" + str(write_latex_ws(f[1])) + ")"

        if f[0] == "root":
            n = write_latex_ws(f[2])
            if isfloat(n):
                return "\\sqrt[" + str(n) + "]{" + str(write_latex_ws(f[1])) + "}"
            else:
                return write_latex_ws(["^", [f[1], ["/", [1, f[2]]]]])
        if f[0] == "sqrt":
            return rf"\sqrt{'{'}{write_latex_ws(f[1])}{'}'}"

        if f[0] == "fact":
            if type(f[1]) == list:
                return f"({write_latex_ws(f[1])})!"
            else:
                return str(f[1]) + "!"

        if f[0] == "Int":
            return "\\int_{" + str(f[1]) + "}^{" + str(f[2]) + "}{" + write_latex_ws(f[3]) + "}d" + f[4]

        return "\\" + f[0] + "(" + str(write_latex_ws(f[1])) + ")"

    if f[0] == "diff":
        return rf"\frac{'{d}{d'}{f[2]}{'}'}({write_latex_ws(f[1])})"


def diff(f: list, VAR: str) -> list or int:
    global PRINT
    PRINT += f"\ndiff: {f}"
    
    def funcderivative(f):
        dln = lambda u: ["/", [1, u]]
        dlog = lambda u, base: ["/", [1, ["*", [u, ["ln", base]]]]]
        dexp = lambda u: ["exp", u]
        dsqrt = lambda u: ["/", [1, ["*", [2, ["sqrt", u]]]]]
        droot = lambda u, n: ["*", [n, ["^", [u, ["+", [n, -1]]]]]]
        
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
        
        second = None
        if len(f) == 3:
            second = f[2]
        elif f[0] == "log":  # falls basis nicht gegeben
            second = "e"
        elif f[0] == "root":
            second = 2
        
        if du == 0:
            return 0
        elif du == 1:
            return eval(f"d{f[0]}")(u, second) if second else eval(f"d{f[0]}")(u)
        else:
            return ["*", [du, eval("d" + f[0])(u, second)]] if second else ["*", [du, eval("d" + f[0])(u)]]
    
    def isconst(a):
        return VAR not in str(a)
    
    if isconst(f):
        return 0
    
    if type(f) != list:
        return 1 if f == VAR else 0
    
    if f[0] == "*":
        constfactors, funcfactors = _split_consts(f[1], isconst)
        
        PRINT += f"\ndiff:{constfactors=}, {funcfactors=}"
        
        if len(funcfactors) > 1:
            fpairs = [["*", [diff(funcfactors[i], VAR), *funcfactors[:i], *funcfactors[i + 1:]]] for i in
                      range(len(funcfactors))]
            funcfactors = ["+", fpairs]
        else:
            funcfactors = diff(funcfactors[0], VAR)
        
        PRINT += f"\ndiff:{constfactors=}, {funcfactors=}"
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
        return ["+", summands] if len(summands) > 1 else summands[0] if summands else 0
    
    elif f[0] == "^":
        base = f[1][0]
        exp = f[1][1]
        
        if VAR in str(base) and VAR not in str(exp):  # x^a
            if not isfloat(exp):
                return ["*", [exp, diff(base, VAR), ["^", [base, ["+", [exp, -1]]]]]]
            else:
                return ["*", [exp, diff(base, VAR), ["^", [base, exp-1]]]]
        if VAR in str(exp) and VAR not in str(base):  # a^x
            return ["*", [["ln", base], diff(exp, VAR), ["^", [base, exp]]]]
        else:  # x^x
            return ["*", [diff(["*", [exp, ["ln", base]]], VAR), ["^", [base, exp]]]]
    
    elif f[0] == "root":
        return diff(["^", [f[1], ["/", [1, f[2]]]]], VAR) if len(f) > 2 else diff(["sqrt", f[1]], VAR)
    
    elif f[0] in FUNCTIONS:
        return funcderivative(f)
    
    elif f[0] == "diff":
        return diff(f[1], f[2])
    
    else:
        PRINT += f"\nDIFF: whats {f} ?"


def set_default_integration_method(method):
    global dim
    dim = method


def integrate(a, b, f, variable, method=None):
    # method: riemann, trapez or simpson
    f = Function(f, variable)
    if not method:
        method = dim
    return getattr(analysis, method)(f, a, b)


class Function:
    def __init__(self, inputfunc: str or list, variable="x"):
        global PRINT
        if type(inputfunc) == str:
            self.str = inputfunc
            PRINT += f"\n\n{self.str = }"
            
            PRINT += "\n\nPARSING STR.."
            self.tree = parse(self.str)
            PRINT += f"\n\n{self.tree = }"
            
            PRINT += "\n\nWRITING TREE.."
            self.str_in = str(write(self.tree))
            PRINT += f"\n\n{self.str_in = }"
            
            PRINT += "\n\nWRITING LATEX.."
            self.latex_in = str(write_latex(self.tree))
            PRINT += f"\n\nself.latex = " + self.latex_in
            
            PRINT += "\n\nPARSING STR.."
            self.tree = parse(self.str_in, ableiten=True)
            PRINT += f"\n\n{self.tree = }"
            
            PRINT += "\n\nWRITING TREE.."
            self.str_out = str(write(self.tree))
            PRINT += f"\n\n{self.str_out = }"
            
            PRINT += "\n\nWRITING LATEX.."
            self.latex_out = str(write_latex(self.tree))
            PRINT += f"\n\nself.latex = " + self.latex_out
            
            self.lam = lambda value: eval(self.str_out.replace("^", "**").replace(variable, str(value)))
        else:
            self.tree = inputfunc
            PRINT += f"\n\n{self.tree = }"
            
            PRINT += "\n\nWRITING TREE.."
            self.str = str(write(self.tree))
            PRINT += f"\n\n{self.str = }"
            
            PRINT += "\n\nWRITING LATEX.."
            self.latex = str(write_latex(self.tree))
            PRINT += f"\n\nself.latex = " + self.latex
            
            self.lam = lambda x: eval(self.str.replace("^", "**"))
    
    def diff(self, var="x"):
        global PRINT
        PRINT += "\n\nDIFF FUNC.."
        f = Function(diff(self.tree, var))
        return Function(f.str, var)

    def __call__(self, x):
        return self.lam(x)


if __name__ == "__main__":
    func = "lol"

    try:
        # input = "d/dx(x^34)"
        input_latex = write_latex_ws(parse_ws(func))
        output_latex = parse(func, ableiten=True)
        try:
            output_latex = eval(write(output_latex))
        except:
            output_latex = write_latex(output_latex)
        print(input_latex," = ", output_latex)

        # a = parse_ws(func)
        # d = write_latex_ws(a)
        # b = parse(func, ableiten=True)
        # c = write(b)
        # print(a)
        # print(d)
        # print()
        # print(b)
        # print(c)
        # # print(eval(c))

    except Exception as e:
        print(PRINT)
        raise e
    
    print(PRINT)
    
