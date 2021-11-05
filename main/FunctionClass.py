# from functions import *


"""TODO:

- Vereinfachen
- 1/x*x -> 1

"""

FUNCTIONS = ["sqrt", "root", "exp", "ln", "log", "arccos", "arcsin", "arctan", "sin", "cos", "tan", "tanh",
             "cosh", "sinh", "arccosh", "arcsinh", "arctanh"]
ALPHABET = "qwertzuiopasdfghjklyxcvbnmπ"
NUMBERS = "0123456789"
VAR = "x"


global PRINT
PRINT = ""


def isfloat(n: str or int or float) -> bool:
    try:
        float(n)
    except ValueError:
        return False
    return True


def prod(iterable: list) -> int:
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


def split_consts(f, test):
    constants, functions = [], []
    for arg in f:
        if test(arg):
            constants.append(arg)
        else:
            functions.append(arg)
    return constants, functions


def extract_args(f):
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


def insert_args(f, innerargs):
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
    if funcname in ["ln", "log"] and int(arg[0]) <= 0:
        return False
    if funcname == "sqrt" and int(arg[0]) < 0:
        return False
    if funcname == "root" and int(arg[0]) < 0 and not flint(arg[1]) % 2:
        return False
    if funcname in ["arccos", "arcsin"] and not -1 <= flint(arg[0]) <= 1:
        return False
    else:
        return True


def parse(f: str):
    global PRINT
    PRINT += f"\nparse:{f}"

    # Leerzeichen entfernen
    f = f.replace(" ", "")

    if isfloat(f):
        return flint(f)
    if f in ALPHABET:
        return f

    if f[0] in "*/^":
        raise SyntaxError(f"first character cannot be '{f[0]}'")
    if f[-1] in "+-*/^":
        raise SyntaxError(f"last character cannot be '{f[-1]}'")

    f0 = f
    f, innerargs = extract_args(f)  # klammern und ihr inneres ersetzen

    if f == "@":
        # unnötige klammer
        return parse(innerargs[0])

    # implizierte Multiplikationen
    i = 0
    while i < len(f) - 1:
        # 2@ / 2x / @@ / @x / ax(keine funktion) --> implizierte multiplikation
        if f[i] in NUMBERS + "@" and f[i + 1] in "@" + ALPHABET or (
                f[i] in ALPHABET and f[i + 1] in ALPHABET and "@" not in f):
            f = f[:i + 1] + "*" + f[i + 1:]

        # @2 -> verboten
        elif f[i] == "@" and f[i + 1] in NUMBERS:
            raise SyntaxError(f"Invalid syntax : '){f[i + 1]}'")

        # x2 -> verboten
        elif f[i] in ALPHABET and f[i + 1] in NUMBERS:
            raise SyntaxError(f"Invalid syntax : '{f[i]}{f[i + 1]}'")

        i += 1

        # 2-x / x-x / @-x --> implizierte addition mit negativem zweiten summand
        if f[i] == "-" and f[i - 1] in "@" + NUMBERS + ALPHABET:
            f = f[:i] + "+" + f[i:]

    def find_repeated_args(args: list, operation) -> list:
        arg_list = []
        for arg in args:
            count = args.count(arg)
            if count > 1:
                arg_list.append(["^", [arg, count]]) if operation == "mult" else arg_list.append(["*", [count, arg]])
                while arg in args:
                    args.remove(arg)
            else:
                arg_list.append(arg)
        return arg_list

    if "+" in f:
        summands = insert_args(f.split("+"), innerargs)

        consts, funcs = split_consts(summands, isfloat)
        consts = sum([flint(s) for s in consts])
        consts = [str(consts)] if consts else []

        summands = [parse(s) for s in consts + funcs]
        summands = find_repeated_args(summands, "sum") if len(summands) > 2 else summands

        PRINT += f"\n{summands=}, {consts = }, {funcs = }"
        return ["+", summands] if len(summands) > 1 else summands[0]

    if "*" in f:
        factors = insert_args(f.split("*"), innerargs)

        consts, funcs = split_consts(factors, isfloat)
        consts = prod(consts)
        consts = [str(consts)] if consts else []

        factors = [parse(f) for f in consts + funcs]
        factors = find_repeated_args(factors, "mult") if len(factors) > 2 else factors

        PRINT += f"\n{factors=}, {consts = }, {funcs = }"
        return ["*", factors] if len(factors) > 1 else factors[0] if 0 not in factors else 0

    if "/" in f:
        div = insert_args(f.split("/", 1), innerargs)
        PRINT += f"\n{div = }"

        num, denom = parse(div[0]), parse(div[1])
        if not denom: raise ZeroDivisionError
        return ["/", [num, denom]] if num != denom else 1

    if "^" in f:
        base, exp = insert_args(f.split("^", 1), innerargs)
        PRINT += f"\n{base=}, {exp=}"
        return ["^", [parse(base), parse(exp)]]

    if f[0] == "-":
        return ["*", [-1, parse(f0[1:])]]

    # Funktion
    if f[0] in ALPHABET and f[-1] == "@":
        funcname = f[:-1]
        if funcname in FUNCTIONS:
            args = innerargs[0].split(",")
            if len(args) > 2:
                raise TypeError(f"{funcname} takes at most 2 arguments")
            if not check_ensemble_de_definition(funcname, args):
                raise TypeError(f"{args[0]} is not inculed in the ensemble de definiton of {funcname}")
            return [funcname, *[parse(a) for a in args]]

        else:
            raise SyntaxError("Unknown function: " + funcname)

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

        consts, funcs = split_consts(args, isfloat)
        PRINT += f"\n{consts=}, {funcs=}"

        consts = [str(sum(int(c) for c in consts))] if consts else []
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

        consts, funcs = split_consts(args, isfloat)
        consts = [str(prod(consts))] if consts else []

        return "*".join(consts + funcs) if consts + funcs else 1

    if f[0] == "/":
        num = f[1][0]
        if type(num) == list:
            num = f"({write(num)})" if num[0] == "+" else write(num)

        denom = f[1][1]
        if type(denom) == list:
            denom = f"({write(denom)})" if denom[0] in "+*/" else write(denom)
        if not denom: raise ZeroDivisionError
        return 1 if num == denom else f"{num}/{denom}"

    if f[0] == "^":
        base = f"({write(f[1][0])})" if type(f[1][0]) == list and f[1][0][0] not in FUNCTIONS else write(f[1][0])
        power = f"({write(f[1][1])})" if type(f[1][1]) == list else f[1][1]
        PRINT += f"\n{base=}, {power=}"
        try:
            power = eval(power)  # if "-" in power else power
            PRINT += "\nEVAL: "+ power
        except:
            pass
        return f"{base}^{power}" if power != 1 and power != "(1)" else base if int(power) != 0 else 1

    if f[0] in FUNCTIONS:
        args = ", ".join([str(write(arg)) for arg in f[1:]])
        return f"{f[0]}({args})"


def write_latex(f):
    global PRINT
    PRINT += f"\nwrite latex: {f=}"

    if type(f) != list:
        return f

    if f[0] == "+":
        args = [write_latex(i) for i in f[1] if str(i) != "0"]

        PRINT += f"\nsumargs: {args}"
        if not args:
            return 0

        consts, funcs = split_consts(args, isfloat)
        PRINT += f"\n{consts=}, {funcs=}"

        consts = [str(sum(int(c) for c in consts))] if consts else []
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

        consts, funcs = split_consts(args, isfloat)
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
                return "\\sqrt[" + str(n) + "]{" + str(write_latex(f[0])) + "}"
            else:
                return write_latex(["^", [f[1], ["/", [1, f[2]]]]])

        return "\\" + f[0] + "(" + str(write_latex(f[1])) + ")"


def diff(f: list) -> list or int:
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
        du = diff(u)

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
        constfactors, funcfactors = split_consts(f[1], isconst)

        PRINT += f"\ndiff:{constfactors=}, {funcfactors=}"

        if len(funcfactors) > 1:
            fpairs = [["*", [diff(funcfactors[i]), *funcfactors[:i], *funcfactors[i + 1:]]] for i in
                      range(len(funcfactors))]
            funcfactors = ["+", fpairs]
        else:
            funcfactors = diff(funcfactors[0])

        PRINT += f"\ndiff:{constfactors=}, {funcfactors=}"
        return ["*", [*constfactors, funcfactors]] if constfactors else funcfactors

    elif f[0] == "/":
        if isconst(f[1][0]):  # (k/u)' = (-1*k*du)/u^2
            return ["/", [["*", [-1, diff(f[1][1]), f[1][0]]], ["^", [f[1][1], 2]]]]
        elif isconst(f[1][1]):  # (u/k)' = u'/k
            return ["/", [diff(f[1][0]), f[1][1]]]
        else:  # (u/v)' = (v*u' - v'u)/v²
            return ["/", [["+", [["*", [diff(f[1][0]), f[1][1]]], ["*", [-1, diff(f[1][1]), f[1][0]]]]],
                          ["^", [f[1][1], 2]]]]

    elif f[0] == "+":
        summands = [diff(i) for i in f[1] if not isconst(i)]
        return ["+", summands] if len(summands) > 1 else summands[0] if summands else 0

    elif f[0] == "^":
        base = f[1][0]
        exp = f[1][1]

        if VAR in str(base) and VAR not in str(exp):  # x^a
            return ["*", [exp, diff(base), ["^", [base, ["+", [exp, -1]]]]]]
        if VAR in str(exp) and VAR not in str(base):  # a^x
            return ["*", [["ln", base], diff(exp), ["^", [base, exp]]]]
        else:  # x^x
            return ["*", [diff(["*", [exp, ["ln", base]]]), ["^", [base, exp]]]]

    elif f[0] == "root":
        return diff(["^", [f[1], ["/", [1, f[2]]]]]) if len(f) > 2 else diff(["sqrt", f[1]])

    elif f[0] in FUNCTIONS:
        return funcderivative(f)


class Function:
    def __init__(self, inputfunc: str or list, var: str):
        global VAR
        global PRINT
        VAR = var
        if type(inputfunc) == str:
            self.str = inputfunc
            PRINT += f"\n\n{self.str = }"

            PRINT += "\n\nPARSING STR.."
            self.tree = parse(self.str)
            PRINT += f"\n\n{self.tree = }"

            PRINT += "\n\nWRITING TREE.."
            self.str = str(write(self.tree))
            PRINT += f"\n\n{self.str = }"

            PRINT += "\n\nWRITING LATEX.."
            self.latex = str(write_latex(self.tree))
            PRINT += f"\n\nself.latex =" + self.latex

            self.lam = lambda x: eval(self.str.replace("^", "**"))
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

    def diff(self):
        global PRINT
        PRINT += "\n\nDIFF FUNC.."
        f = Function(diff(self.tree), VAR)
        return Function(f.str, VAR)


if __name__ == "__main__":
    func = "root(x, x)"

    f = Function(func, "x")
    print(PRINT)
