from _collections_abc import Iterable
class Vector():
    def __init__(self,args):
        self.vector = args
        
    def __str__(self):
        return str(self.vector)
    
    def __getitem__(self, i):
        return self.vector[i]

    def __len__(self):
        return len(self.vector)
    
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
    
    
class Matrix():
    def __init__(self,args):
        self.row = [Vector(vec) for vec in args]
        self.rows = len(args)
        self.cols = len(args[0])
    
    def __str__(self):
        text = ""
        for row in self.row:
            for element in row:
                text += str(round(element,2))+" "+"  "*(3-len(str(round(element,2))))
            text += "\n"
        return text
    
    def __getitem__(self, i):
        return self.row[i]
    
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
     
       
        
        
        
v = Vector([2,3,4])
w = Vector([1,2,-1])

B = Matrix([[1,2],[2,3]])
A = Matrix([[1,4],[2,1]])

print(A)
print(B)


#Ziel noch: Zeilen von A als Vektoren manipulieren
