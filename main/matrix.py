from random import randint

def rint(x):
    if float(x) == int(x):
        return str(int(x))
    else:
        return str(round(x,1))

class Matrix():
    def __init__(self,args):
        
        #Definiere eine Class für Zeilen, um addieren zu können
        #(Es gibt keine Vector class, da sie eig. Matrizen sind)
        class matrix_row():
            #Spalten_vektor
            def __init__(self,args):
                self.vector = args
                self.rows = len(args)
                self.cols = 1
        
            def __str__(self):
                text = ""
                for element in self.vector:
                    if element == 0:
                        text += "."+" "*5
                    else:
                        if element > 0:
                            text += str(round(element,2))+" "*(6-len(str(round(element,2))))
                        else:
                            text += str(round(element,2))+" "*(6-len(str(round(element,2))))
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
        
        
            def __neg__(self):
                return -1*self
        
            def __sub__(self, val):
                return self + - val
        
            def __eq__(self, val):
                return self.vector == val.vector

        self.row = [matrix_row(vec) for vec in args]

        self.rows = len(args)
        self.cols = len(args[0])

    def __getitem__(self, i):
        return self.row[i]

    def __setitem__(self, idx, val):
        if len(val) == self.cols:
            self.row[idx] = val
        else:
            raise ValueError

    def __str__(self):
        text = ""
        for row in self.row:
            for element in row:
                if element == 0:
                    text += "."+" "*4
                else:
                    if element > 0:
                        text += str(rint(element))+" "+" "*(4-len(str(rint(element))))
                    else:
                        text += str(rint(element))+" "+" "*(4-len(str(rint(element))))
            text += "\n"
        return text


    def __add__(self,val):
        if self.rows == val.rows and self.cols == val.cols:
            return self.__class__([[self[i][j] + val[i][j] for j in range(self.cols)] for i in range(self.rows)])
        else:
            raise ValueError

    def __rmul__(self,val):
        return self.__class__([[val * self[i][j] for j in range(self.cols)] for i in range(self.rows)])

    def __neg__(self):
        return -1*self

    def __sub__(self, val):
        return self + -val

    def __eq__(self, val):
        return self.matrix == val.matrix

    def __mul__(self, val):
        if self.cols == val.rows:
            return self.__class__([[sum(self[i][k]*val[k][j] for k in range(self.cols)) for j in range(val.cols)] for i in range(self.rows)])
        else:
            raise ValueError



    @classmethod
    def Random(cls, m, n, low=0, high=10):
        row = []
        for _ in range(m):
            row.append([randint(low, high) for x in range(n)])
        return Matrix(row)

    @classmethod
    def RandomSym(cls, m, n, low=0, high=10):
        row = []
        for _ in range(m):
            row.append([randint(low, high) for x in range(n)])

        for i in range(m):
            for j in range(n):
                row[i][j] = row[j][i]

        return Matrix(row)

    @classmethod
    def Zero(cls, m, n):
        rows = [[0]*n for x in range(m)]
        return Matrix(rows)

    @classmethod
    def Id(cls, m):
        row = [[0]*m for x in range(m)]
        index = 0

        for r in row:
            r[index] = 1
            index += 1

        return Matrix(row)


    #Mathematische Funktionen


    def T(self):
        return self.__class__([[self[j][i] for j in range(self.rows)] for i in range(self.cols)])

    def s(self,i,j,lam):
        #zur i-ten Zeile das lam-Fache der j-ten Zeile hinzufügen
        self[i] += lam * self[j]

    def m(self,i,lam):
        self[i] = lam * self[i]

    def v(self,i,j):
        self[i], self[j] = self[j], self[i]

    def sq(self):
        return self*self

    def __pow__(self, n):
        return self if n == 1 else  (A ** (n/2)).sq() if n % 2 == 0 else A * (A ** (n-1))
    
    def norm(self):
        return max(sum(line) for line in self.row)  #Zeilensummen-Norm
    
    
    def lu(self):
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
    
    def lu_solve(self, b):
        def upper_triangle_solve(self, b):
            try:
                x = Matrix.Zero(A.cols, 1)
                for i in range(b.rows - 1, -1, -1):
                    summe = sum(self[i][j] * x[j][0] for j in range(i + 1, b.rows))
                    x[i][0] = ((b[i][0] - summe) / self[i][i])
                return x
            
            except:
                print("A ist nicht regulär!")
                
        def lower_triangle_solve(A, b):
            try:
                x = Matrix.Zero(b.rows, 1)
                
                for i in range(0, b.rows):
                    summe = sum(self[i][j] * x[j][0] for j in range(0, i))
                    x[i][0] = ((b[i][0] - summe) / self[i][i])
                return x
            
            except:
                print("A ist nicht regulär!")
        
        
        try:
            [L,U] = self.lu()

            y = lower_triangle_solve(L, b)
            x = upper_triangle_solve(U, y)
            
            return x
        except:
            print("LU Zerlegung nicht möglich")
    
v = Matrix([[2,3,9]]) #Zeilenvektor
w = Matrix([[2],[2]]) #Spaltenvektor

B = Matrix([[1,2],[2,3]])
A = Matrix([[0.6,.5],[0.9,.5]])

C = Matrix.Random(6,6,-4,4)
D = Matrix.RandomSym(2,2,-20,30)


print(C)

print(C.lu()[0])
print(C.lu()[1])

print("---------")
print(C.lu()[0] * C.lu()[1])







