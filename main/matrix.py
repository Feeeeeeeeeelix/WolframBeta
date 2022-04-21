from random import randint
from functions import sqrt
from time import time


def rint(x): #bessere Rundung für klarere Darstellung der Matrix Einträge
    if round(x, 4) == round(x):
        return round(x)
    else:
        return round(x, 2)


class Matrix:
    def __init__(self, args):
        
        # Definiere eine Class für Zeilen, um addieren zu können
        # (Es gibt keine Vector class, da sie eig. Matrizen sind)
        class matrix_row:
            # Spalten_vektor
            def __init__(self, args):
                self.vector = args
                self.rows = len(args)
                self.cols = 1
            
            def __str__(self):
                text = ""
                for element in self.vector:
                    if element == 0:
                        text += "." + " " * 5
                    else:
                        text += str(round(element, 2)) + " " * (6 - len(str(round(element, 2))))
                    text += "\n"
                return text
            
            def __getitem__(self, i):
                return self.vector[i]
            
            def __setitem__(self, idx, val):
                self.vector[idx] = val
            
            def __len__(self):
                return self.rows
            
            def __add__(self, val):
                if len(self) == len(val):
                    return self.__class__([self.vector[i] + val.vector[i] for i in range(len(self))])
                else:
                    raise ValueError
            
            def __rmul__(self, val):
                return self.__class__([val * self.vector[i] for i in range(len(self))])
            
            def __mul__(self, val):
                return self.__class__([val * self.vector[i] for i in range(len(self))])
            
            def __neg__(self):
                return -1 * self
            
            def __sub__(self, val):
                return self + - val
            
            def __eq__(self, val):
                return self.vector == val.vector
        
        self.row = [matrix_row(vec) for vec in args]
        
        self.rows = len(args)
        self.cols = len(args[0])
    
    def __getitem__(self, i):
        try:
            return self.row[i]
        except:
            print("Der gegebene Index ist falsch")
    
    def __setitem__(self, idx, val):
        try:
            if len(val) == self.cols:
                self.row[idx] = val
            else:
                raise ValueError
        except:
            print("Der gegebene Index ist falsch, oder die gegebene Zeile nicht korrekt formatiert")
    
    def __str__(self):
        #Die Matrix soll als Tabelle dargestellt werden und die Einträge sollen sinnvoll gerundet werden
        text = ""
        for row in self.row:
            for element in row:
                if abs(element) <= 0.00001:
                    text += "." + " " * 5    # ein "." steht für eine Null. Dies macht dünnbesetzte Matrizen lessbarer
                else:
                    text += str(rint(element)) + " " + " " * (5 - len(str(rint(element))))
            text += "\n"
        return text
    
    def __add__(self, val):
        try:
            if self.rows == val.rows and self.cols == val.cols:
                return self.__class__([[self[i][j] + val[i][j] for j in range(self.cols)] for i in range(self.rows)])
            else:
                raise ValueError
        except:
            print("Die gegebenen Matrizen können nicht addiert werden")
    
    def __rmul__(self, val): #skalare Vielfache
        return self.__class__([[val * self[i][j] for j in range(self.cols)] for i in range(self.rows)])
    
    def __neg__(self):
        return -1 * self
    
    def __sub__(self, val):
        return self + -val
    
    def __eq__(self, val):
        return self.row == val.row
    
    def __mul__(self, val):
        try:
            if type(val) == float or type(val) == int:
                return self.__class__([[val * self[i][j] for j in range(self.cols)] for i in range(self.rows)])
            
            elif self.cols == val.rows:
                return self.__class__(
                    [[sum(self[i][k] * val[k][j] for k in range(self.cols)) for j in range(val.cols)] for i in
                     range(self.rows)])
            
            else:
                raise ValueError
        except:
            print("Die Matrizen sind nicht kompatibel")
    
    @classmethod
    def Random(cls, m, n, low=0, high=10):   #Zufällige m,n Matrix mit Integer Werten zwischen low und high
        row = []
        for _ in range(m):
            row.append([randint(low, high) for _ in range(n)])
        return Matrix(row)
    
    @classmethod
    def RandomSym(cls, m, low=0, high=10): #Zufällige m,n SYMMETRISCHE Matrix mit Integer Werten zwischen low und high
        row = []
        for _ in range(m):
            row.append([randint(low, high) for _ in range(m)])
        
        for i in range(m):
            for j in range(m):
                row[i][j] = row[j][i]
        
        return Matrix(row)
    
    @classmethod
    def Zero(cls, m, n): #Null Matrix
        rows = [[0] * n for _ in range(m)]
        return Matrix(rows)
    
    @classmethod
    def Id(cls, m): #Identiätsmatrix
        row = [[0] * m for _ in range(m)]
        index = 0
        
        for r in row:
            r[index] = 1
            index += 1
        
        return Matrix(row)
    
    # Mathematische Funktionen
    
    def T(self): #Transposition
        return self.__class__([[self[j][i] for j in range(self.rows)] for i in range(self.cols)])
    
    def s(self, i, j, lam):  # zur i-ten Zeile das lam-fache der j-ten Zeile hinzufügen
        self[i] += lam * self[j]
    
    def m(self, i, lam): #i-te Zeile mit lam multiplizieren
        self[i] = lam * self[i]
    
    def v(self, i, j): #i-te und j-te Zeile vertauschen
        self[i], self[j] = self[j], self[i]
    
    def sq(self): #Quadrat
        return self * self
    
    def __pow__(self, n): #effizientere höhere Potenzen als Operator auf die Instanzen der Class
        return self if n == 1 else (self ** (n / 2)).sq() if n % 2 == 0 else self * (self ** (n - 1))
    
    def normZ(self):  # Zeilensummen-Norm
        return max(sum(line) for line in self.row) 
    
    def normS(self): # Spaltensummen-Norm
        return max(sum(line) for line in self.T().row)
    
    def lu(self): #Input: Matrix mit regulären Hauptminoren. Output: Zerlegung self = L*U mit L normierte lower-triangular Matrix und U upper-triangulear Matrix
        if self.rows == self.cols:
            try:
                n = self.rows
                
                L = Matrix.Id(n)
                U = Matrix.Zero(n, n)
                
                for i in range(0, n):
                    for k in range(i, n):
                        U[i][k] = self[i][k] - sum(L[i][j] * U[j][k] for j in range(0, i))
                    
                    for k in range(i + 1, n):
                        L[k][i] = (self[k][i] - sum(L[k][j] * U[j][i] for j in range(0, i))) / U[i][i]
                return [L, U]
            except:
                print("Die Untermatrizen der Matrix sind nicht alle regulär, also ist die LU-Zerlegung unmöglich!")
        else:
            print("Die Matrix muss quadratisch sein!")
    
    def lu_solve(self, b):#Input: Matrix A, vektor b. Output: Lösung x von Ax=b unter den Bedingungen der LU-Zerlegung
        def upper_triangle_solve(A, b):
            try:
                x = Matrix.Zero(b.rows, 1)
                for i in range(b.rows - 1, -1, -1):
                    summe = sum(A[i][j] * x[j][0] for j in range(i + 1, b.rows))
                    x[i][0] = ((b[i][0] - summe) / A[i][i])
                return x
            
            except:
                print("A ist nicht regulär!")
        
        def lower_triangle_solve(A, b):
            try:
                x = Matrix.Zero(b.rows, 1)
                
                for i in range(0, b.rows):
                    summe = sum(A[i][j] * x[j][0] for j in range(0, i))
                    x[i][0] = ((b[i][0] - summe) / A[i][i])
                return x
            
            except:
                print("A ist nicht regulär!")
        
        try:
            [L, U] = self.lu()
            
            y = lower_triangle_solve(L, b)
            x = upper_triangle_solve(U, y)
            
            return x
        except:
            print("LU Zerlegung nicht möglich")
    
    def cholesky(self):# Input: symmetrische positiv definite Matrix A. Output: Zerlegung A = L* L^T, also eine stabilee Version von LU-Zerlegung, mit halbem Aufwand.
        
        if self.rows == self.cols:
            if self == self.T():
                try:
                    n = self.rows
                    L = Matrix.Zero(n, n)
                    for k in range(0, n):
                        L[k][k] = sqrt(self[k][k] - sum(L[k][j] * L[k][j] for j in range(0, k)))  # 0der range(0,k-1)?
                        for i in range(k, n):
                            L[i][k] = (self[i][k] - sum(L[i][j] * L[k][j] for j in range(0, k))) / L[k][k]
                    return L
                
                
                except:
                    print("Die Matrix ist nicht positiv definit, also funktioniert die Cholesky-Zerlegung nicht.")
            
            else:
                print(
                    "Die Matrix ist nicht symmetrisch. Cholesky-Zerlegung funktioniert nur für positiv definite SYMMETRISCHE Matrizen")
        else:
            print("Die Matrix muss quadratisch sein! Cholesky nicht anwendbar.")
    
    def cholesky_solve(self, b):#Input: Matrix A und vektor b, A positiv definit und symmetrisch. Output: Lösung x von Ax=b. (doppelt so effizient wie LU, aber mehr bedingungen)
        def upper_triangle_solve(A, b):
            try:
                x = Matrix.Zero(b.rows, 1)
                for i in range(b.rows - 1, -1, -1):
                    summe = sum(A[i][j] * x[j][0] for j in range(i + 1, b.rows))
                    x[i][0] = ((b[i][0] - summe) / A[i][i])
                return x
            
            except:
                print("A ist nicht regulär!")
        
        def lower_triangle_solve(A, b):
            try:
                x = Matrix.Zero(b.rows, 1)
                
                for i in range(0, b.rows):
                    summe = sum(A[i][j] * x[j][0] for j in range(0, i))
                    x[i][0] = ((b[i][0] - summe) / A[i][i])
                return x
            
            except:
                print("A ist nicht regulär!")
        
        try:
            L = self.cholesky()
            
            y = lower_triangle_solve(L, b)
            x = upper_triangle_solve(L.T(), y)
            
            return x
        except:
            print("LU Zerlegung nicht möglich")
    
    def sub_matrix(self, ymin, ymax, xmin, xmax): #berechnet eine Teilmatrix mit gegebenen x und y Werten.
        coeffs = []
        for y in range(ymin, ymax):
            coeffs += [self[y][xmin:xmax]]
        
        return Matrix(coeffs)
    
    def gauss_explained(self, b_in): #Erklärt die Berechnung von x hinter dem Gauss-Algorithmus um Ax=b zu lösen, für reguläres A. 
        def Mprint(self, b): # Schreibt die Erweiterte Matrix (A,b) schön auf
            text = ""
            for i in range(self.rows):
                for element in self[i]:
                    if element == 0:
                        text += "." + " " * 4
                    else:
                        if element > 0:
                            text += str(rint(element)) + " " + " " * (4 - len(str(rint(element))))
                        else:
                            text += str(rint(element)) + " " + " " * (4 - len(str(rint(element))))
                text += "   |    "
                
                element = b[i][0]
                
                if element == 0:
                    text += "." + " " * 4
                else:
                    if element > 0:
                        text += str(rint(element)) + " " + " " * (4 - len(str(rint(element))))
                    else:
                        text += str(rint(element)) + " " + " " * (4 - len(str(rint(element))))
                
                text += "\n"
            print(text)
        
        n = self.rows
        V = 0
        M = self.T().T()  # Damit der eigentliche Wert von self nicht verändert wird (sonst wird der selbe SPeicherort verwendet und es kommt zu Fehlern)
        b = b_in.T().T()  # "
        
        L = Matrix.Zero(n, n)
        transpositions = []
        Operationen = []
        
        for k in range(0, n - 1):
            print("°~" * 50)
            print("NEUE ITERATION")
            Mprint(M, b)
            # maximal pivot
            index = k
            for l in range(k, n):
                if abs(M[l][k]) > abs(M[index][k]):
                    index = l
            
            # transpose
            if index != k:
                print("Maximal Pivot-Wert:", M[index][k])
                V += 1
                M[k], M[index] = M[index], M[k]
                b[k], b[index] = b[index], b[k]
                transpositions.append([k, index])
                Operationen.append(["V", k, index])
                print("Vertauschung:")
                Mprint(M, b)
            
            print("---" * 20)
            print("Rechnung:")
            Mprint(M, b)
            # Operate
            if M[k][k] != 0:
                for i in range(k + 1, n):
                    L[i][k] = M[i][k] / M[k][k]
                    
                    b.s(i, k, -L[i][k])
                    M.s(i, k, -L[i][k])
                    Operationen.append(["S", i, k, - L[i][k]])
                    print("S(", i, ",", k, ",", - L[i][k], ")")
                    
                    Mprint(M, b)
        
        # Triangle Zu identität
        print("=-=|" * 60)
        print("Nächste Phase:")
        print("Normierung:")
        
        for i in range(n - 1, -1, -1):
            Operationen.append(["M", i, 1 / M[i][i]])
            b.m(i, 1 / M[i][i])
            M.m(i, 1 / M[i][i])
        
        Mprint(M, b)
        print("Kürzung:")
        for i in range(n - 1, -1, -1):
            Mprint(M, b)
            for k in range(i):
                Operationen.append(["S", k, i, - M[k][i]])
                b.s(k, i, -M[k][i])
                M.s(k, i, -M[k][i])
        
        pi = transpositions[::-1]
        return [M, b, V, pi, Operationen]  #gibt die Finale Matrix M an (sollte die Id-Matrix sein), die umgeformte rechte Seite b, welche nun die Lösung x ist. V gibt die Anzahl an Zeilenvertauschungen an. pi gibt die Transpositionen der Zeilenvertauschungen an
    
    def gauss(self, b_in): #führt Gauss Algorithmus aus. Output: gibt die Finale Matrix M an (sollte die Id-Matrix sein), die umgeformte rechte Seite b, welche nun die Lösung x ist. V gibt die Anzahl an Zeilenvertauschungen an. pi gibt die Transpositionen der Zeilenvertauschungen an. Operationen gibt die Operationen an, welche verwendet wurden 
    
        n = self.rows
        V = 0
        M = self.T().T()  # Damit der eigentliche Wert von self nicht verändert wird
        b = b_in.T().T()  # "
        
        L = Matrix.Zero(n, n)
        transpositions = []
        Operationen = []
        
        for k in range(0, n - 1):
            
            # maximal pivot
            index = k
            for l in range(k, n):
                if abs(M[l][k]) > abs(M[index][k]):
                    index = l
            
            # transpose
            if index != k:
                V += 1
                M[k], M[index] = M[index], M[k]
                b[k], b[index] = b[index], b[k]
                transpositions.append([k, index])
                Operationen.append(["V", k, index])
            
            # Operate
            if M[k][k] != 0:
                for i in range(k + 1, n):
                    L[i][k] = M[i][k] / M[k][k]
                    
                    b.s(i, k, -L[i][k])
                    M.s(i, k, -L[i][k])
                    Operationen.append(["S", i, k, - L[i][k]])
        
        # Triangle Zu identität
        for i in range(n - 1, -1, -1):
            Operationen.append(["M", i, 1 / M[i][i]])
            b.m(i, 1 / M[i][i])
            M.m(i, 1 / M[i][i])
        
        for i in range(n - 1, -1, -1):
            for k in range(i):
                Operationen.append(["S", k, i, - M[k][i]])
                b.s(k, i, -M[k][i])
                M.s(k, i, -M[k][i])
        
        pi = transpositions[::-1]
        return [M, b, V, pi, Operationen]
    
    def gauss_solve(self, b): #Berechnet die Lösung von Ax=b mittels Gauss.
        def permutate(b, T):
            for i in range(len(T)):
                b[T[i][0]], b[T[i][1]] = b[T[i][1]], b[T[i][0]]
        
        List = self.gauss(b)
        x = List[1]
        
        return x
    
    def inverse(self):#gibt mittels den Operationen vom Gauss-Verfahren an, was die Inverse Matrix ist.
        try:
            def apply_operations(operations, n):
                I = Matrix.Id(n)
                for op in operations:
                    if op[0] == 'V':
                        I[op[1]], I[op[2]] = I[op[2]], I[op[1]]
                    elif op[0] == 'M':
                        I.m(op[1], op[2])
                    else:
                        I.s(op[1], op[2], op[3])
                return I
            
            op = self.gauss(Matrix.Zero(self.rows, 1))[4]
            return apply_operations(op, self.rows)
        except:
            print("Matrix nicht invertierbar.")
    
    def det(self):#mittels den Operationen vom Gauss-Verfahren bestimmt diese Funktion die Determinante
        try:
            op = self.gauss(Matrix.Zero(self.rows, 1))[4]
            determinant = 1
            for operation in op:
                if operation[0] == "M":
                    determinant /= operation[2]
                if operation[0] == "V":
                    determinant *= -1
            return determinant
        except:
            return 0
    
    def QR(self): #Jede Matrix (nicht unbedingt quadratisch) kann als A=QR mit Q orthogonale Matrix und R erweiterte trianguläre Matrix zerlegt werden.
        def sign(x):
            return 1 if x >= 0 else -1
        
        def norm(a):
            return sqrt(sum(a[i][0] ** 2 for i in range(a.rows)))
        
        R = self.T().T()
        n, m = R.rows, R.cols
        Q = Matrix.Id(n)
        
        for i in range(0, m):
            a = Matrix([[R[k][i]] for k in range(i, n)])  # Spaltenvektor
            if norm(a) != 0:
                sigma = -sign(a[0][0])
                a[0][0] -= sigma * norm(a)
                v1 = 1 / norm(a) * a
                v = Matrix.Zero(n, 1)
                for k in range(i, n):    v[k] = v1[k - i]
                
                R -= (2 * v) * (v.T() * R)
                Q -= v * (2 * v.T()) * Q
        
        return [Q.T(), R]
    
    # Überbestimmte Aufgabe lösen
    
    def ausgleichs_problem(self, b): # gegeben ein überbestimmtes und unlösbares Problem Ax=b, findet diese Methode eine Lösung, die die Gleichungen am besten löst (es minimiert die quadrate der Fehler). Nützlich für Interpolation und Physik.
        def upper_triangle_solve(A, b):
            try:
                x = Matrix.Zero(b.rows, 1)
                for i in range(b.rows - 1, -1, -1):
                    summe = sum(A[i][j] * x[j][0] for j in range(i + 1, b.rows))
                    x[i][0] = ((b[i][0] - summe) / A[i][i])
                return x
            
            except:
                print("A ist nicht regulär!")
        
        [Q, R] = self.QR()
        v = Q.T() * b
        c = v.sub_matrix(0, 0, 0, self.cols - 1)
        R_hat = R.sub_matrix(0, R.rows - 1, 0, R.rows - 1)
        return upper_triangle_solve(R_hat, c) #Output: bestes x
    

    
    def power_method(self):     # Reel Diagonalisierbare MAtrix (große Einschränkung): Mit Potenzmethode wird größter Eigenwert bestimmt
        def norm(a):
            return sqrt(sum(a[i][0] ** 2 for i in range(a.rows)))
        
        x = Matrix([[1] for _ in range(self.rows)])
        mu = 1
        for i in range(100):
            print(mu)
            mu_old = mu
            x = A * x
            mu = norm(x)
            x = 1 / mu * x
            if abs(mu_old - mu) < 0.0000000001:
                break
        if abs(mu_old - mu) < 0.0000000001:
            return mu
        else:
            print("Potenz-Methode geht nicht, da A nicht reell diagonalisierbar ist.")
    
    def hesseberg(self): # gibt für gegebene Matrix A die MAtrix H in der Zerlegung A=Q^T*H*Q mit Q orthogonal und H in Hessebergform.
        def sign(x):
            return 1 if x >= 0 else -1
        
        def norm(a):
            return sqrt(sum(a[i][0] ** 2 for i in range(a.rows)))
        
        R = self.T().T()
        n = R.rows
        
        for i in range(0, n - 1):
            a = Matrix([[R[k][i]] for k in range(i + 1, n)])  # Spaltenvektor
            sigma = -sign(a[0][0])
            a[0][0] -= sigma * norm(a)
            v1 = 1 / norm(a) * a
            v = Matrix.Zero(n, 1)
            for k in range(i + 1, n):    v[k] = v1[k - i - 1]
            
            R -= (2 * v) * (v.T() * R)
            R -= 2 * (R * v) * v.T()
        
        return R
    
    def jacobi(self):  #gibt mittels 32*n^2 Schritten alle Eigenwerte, solange die Matrix symmetrisch ist
        if self.T() == self:
            
            def givens_quick_calculation(A, i, j):
                def sign(x):
                    return 1 if x >= 0 else -1
                
                def sqrt(x):
                    if x < 0 and round(x, 10) == 0.0:
                        x = 0
                    if x > 0:
                        a = x
                        for i in range(25):
                            a = 1 / 2 * (a + x / a)
                        return a
                    elif x == 0:
                        return 0
                    else:
                        print("NEGATIV!")
                
                D = (A[i][i] - A[j][j]) / sqrt((A[i][i] - A[j][j]) ** 2 + 4 * A[i][j] ** 2)
                c = sqrt((1 + D) / 2)
                s = -sign(A[i][j]) * sqrt((1 - D) / 2)
                
                ci = []
                cj = []
                for k in range(A.rows):
                    ci.append(A[i][k] * c - A[j][k] * s)
                    cj.append(A[i][k] * s + A[j][k] * c)
                A[i][:] = ci
                A[j][:] = cj
                
                ri = []
                rj = []
                for k in range(A.rows):
                    ri.append(A[k][i] * c - A[k][j] * s)
                    rj.append(A[k][i] * s + A[k][j] * c)
                for k in range(A.rows):
                    A[k][i] = ri[k]
                    A[k][j] = rj[k]
                return A
            
            def N(A):
                return sum([sum([float(i != j) * A[i][j] ** 2 for i in range(A.rows)]) for j in range(A.rows)])
            
            A = self.T().T()
            n = self.rows
            i, j = 1, 0
            # zyklisch schneller als maximierend
            for r in range(10000000):
                if i < n - 1:
                    i += 1
                elif i == n - 1 and j < n - 2:
                    j += 1
                    i = j + 1
                else:
                    i, j = 1, 0
                
                A = givens_quick_calculation(A, i, j)  # imax,jmax
                
                if r % 100 == 0:
                    delta = N(A)
                    print(delta)
                    if delta < 0.0000001:
                        return [A[i][i] for i in range(n)]
        else:
            print("Matrix ist nicht symmetrisch. Jacobi-Vefahren nicht anwendbar.")
    
    def RQ_hesseberg(self): #berechnet Eigenwerte durch Hesseberg-Zerlegung und effizienten QR-Zerlegungen für Hessebergmatrizen, für eine schnelle QR-Methode.
        # A [=QR] in hessberg form |-> RQ
        def givensrotation(a, b):
            if b == 0:
                c = 1
                s = 0
            else:
                if abs(b) > abs(a):
                    r = a / b
                    s = 1 / sqrt(1 + r ** 2)
                    c = -s * r
                
                else:
                    r = b / a
                    c = 1 / sqrt(1 + r ** 2)
                    s = -c * r
            return [c, s]
        
        R = self.T().T()
        n = R.rows
        
        C = []
        S = []
        
        for k in range(n - 1):
            [c, s] = givensrotation(R[k][k], R[k + 1][k])
            
            C += [c]
            S += [s]
            
            A = R.sub_matrix(k, k + 2, k, n)
            
            j = 0
            for l in range(k, n):
                R[k][l] = c * A[0][j] - s * A[1][j]
                R[k + 1][l] = s * A[0][j] + c * A[1][j]
                j += 1
        
        for k in range(n - 1):
            c, s = C[k], S[k]
            
            A = R.sub_matrix(0, k + 2, k, k + 2)
            
            j = 0
            for l in range(k + 2):
                R[l][k] = c * A[j][0] - s * A[j][1]
                R[l][k + 1] = s * A[j][0] + c * A[j][1]
                j += 1
        return R
    
    def eigenvalues(self, iter=-1):#berechnet Eigenwerte mit den früheren MEthoden, und entscheidet welche die beste ist.
        if iter == -1:
            iter = 40 * self.rows
        
        def QR_verfahren(self):
            
            M = self.hesseberg()
            n = M.rows
            
            for i in range(iter):
                if i % 20 == 0:
                    # print(M)
                    print(100 * i / iter, "%")
                kappa = M[n - 1][n - 1]
                M = (M - kappa * Matrix.Id(n)).RQ_hesseberg() + kappa * Matrix.Id(n) # ein shift im RQ-Schritt verbessert die Konvergenz
            
            return M
        
        def block(B): # Die Matrix ist in Diagonalgestalt mit blöcken. Diese Blöcke werden nun erarbeitet
            block_matrizen = []
            n = B.rows
            
            if round(B[1][0], 2) == 0.0:
                block_matrizen.append(B[0][0])
            else:
                block_matrizen.append([[B[0][0], B[0][1]], [B[1][0], B[1][1]]])
            
            for k in range(1, n - 1):
                if round(B[k + 1][k], 2) != 0.0:
                    block_matrizen.append([[B[k][k], B[k][k + 1]], [B[k + 1][k], B[k + 1][k + 1]]])
                elif round(B[k][k - 1], 2) == 0.0:
                    block_matrizen.append(B[k][k])
            
            if round(B[n - 1][n - 2], 2) == 0.0:
                block_matrizen.append(B[n - 1][n - 1])
            
            return block_matrizen
        
        if self == self.T(): #falls symmetrisch, verwende Jacobi-Verfahren.
            return [[B, 0] for B in self.jacobi()]
        
        B = QR_verfahren(self)
        
        blocks = block(B)
        eigenwerte = []
        for M in blocks:
            if type(M) == int or type(M) == float: #falls es kein 2x2-Block ist, ist es ein reeller Eigenwert.
                eigenwerte.append([M, 0.0])
            else:
                C_1 = -M[0][0] - M[1][1]
                C_2 = -M[1][0] * M[0][1] + M[0][0] * M[1][1]
                
                eigenwerte.append([-C_1 / 2, 1 / 2 * sqrt(abs(C_1 * C_1 - 4 * C_2))]) #berechnet komplexe Eigenwerte für jeden Block
                eigenwerte.append([-C_1 / 2, -1 / 2 * sqrt(abs(C_1 * C_1 - 4 * C_2))])
        return eigenwerte


if __name__ == "__main__":
    A = Matrix.Random(20, 20, -10, 10)
    print(A)
    
    t = time()
    print(A.eigenvalues())
    print(time() - t)
