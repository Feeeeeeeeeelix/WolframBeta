from random import randint


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
                    text += "."+" "*5
                else:
                    if element > 0:
                        text += str(round(element,2))+" "*(6-len(str(round(element,2))))
                    else:
                        text += str(round(element,2))+" "*(6-len(str(round(element,2))))
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
    def makeRandom(cls, m, n, low=0, high=10):
        row = []
        for _ in range(m):
            row.append([randint(low, high) for x in range(n)])
        return Matrix(row)

    @classmethod
    def makeRandomSym(cls, m, n, low=0, high=10):
        row = []
        for _ in range(m):
            row.append([randint(low, high) for x in range(n)])

        for i in range(m):
            for j in range(n):
                row[i][j] = row[j][i]

        return Matrix(row)

    @classmethod
    def makeZero(cls, m, n):
        rows = [[0]*n for x in range(m)]
        return Matrix(rows)

    @classmethod
    def makeId(cls, m):
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

v = Matrix([[2,3,9]]) #Zeilenvektor
w = Matrix([[1],[2],[-1]]) #Spaltenvektor

B = Matrix([[1,2],[2,3]])
A = Matrix([[1,4],[2,1]])

C = Matrix.makeRandom(3,3,-2,3)
D = Matrix.makeRandomSym(2,2,-20,30)

print(C)
print(C[1]+C[2])

print("----")

print(v)
print(v.T())
print(C)

print("----"*3)

print(v*v.T())  # = (Norm von v)^2

