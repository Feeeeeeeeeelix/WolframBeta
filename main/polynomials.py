def flint(x):
    if float(x) == int(float(x)):
        return int(float(x))
    else:
        return float(x)  



class Polynomial():
    def __init__(self,args):
        
        def str_to_polynomial(p):
            p = p.replace(" ","")
            
            i = 0
            while i < len(p):
                if p[i] == "-":
                    p = p[:i] + "+" + p[i:]
                    i += 1
                i += 1
        
            p = p.split("+")
            powers = []
            factors =[]
            
            for term in p:
                if "x" in term:
                    x_index = term.find("x")
                    if x_index != len(term)-1:
                        powers.append(int(term[x_index+2:]))
                    else:
                        powers.append(1)
                    
                    if term[:x_index] != "":
                        factors.append(float(term[:x_index]))
                    else:
                        factors.append(1)
                else:
                    powers.append(0)
                    factors.append(term)
            
            degree = max(powers)
            polynomial = [0] * (degree + 1)
            
            for i in range(len(factors)):
                polynomial[powers[i]] = flint(factors[i])
            
            return polynomial 

        if type(args) == str:
            self.coeffs = str_to_polynomial(args)

        elif type(args) == list:
            self.coeffs = args
        
        else:
            self.coeffs = [args]

    def __add__(self, val):
        if isinstance(val, Polynomial):
            if len(self.coeffs) > len(val.coeffs):
                res = self.coeffs
                for i in range(len(val.coeffs)):
                    res[i] += val.coeffs[i]
            if len(self.coeffs) < len(val.coeffs):
                res = val.coeffs
                for i in range(len(self.coeffs)):
                    res[i] += self.coeffs[i]
        else:
            res = self.coeffs
            res[0] += val

        return self.__class__(res)

    def __mul__(self,val):
        
        if isinstance(val, Polynomial):
            res = [0]  * (len(self.coeffs)+len(val.coeffs)-1)
            for o1,i1 in enumerate(self.coeffs):
                for o2,i2 in enumerate(val.coeffs):
                    res[o1+o2] += i1*i2
                
        else:
            res = [co*val for co in self.coeffs]
            
        return self.__class__(res)

    def __neg__(self):
        return self.__class__([-term for term in self.coeffs])
    
    def __pow__(self, val):
        if type(val) == int:
            val_bin = bin(val)[2:]
            teiler = [self]
            b = self
            x = Polynomial(1)
            
            for i in range(len(val_bin)-1):
                b = b*b
                teiler.append(b)
            
            for i in range(len(val_bin)):
                if int(val_bin[::-1][i]):
                    x = x * teiler[i]
            return x
    
    def __str__(self):
            res = []
            for po,co in enumerate(self.coeffs):
                if co:
                    if po==0:
                        po = ''
                    elif po==1:
                        po = 'x'
                    else:
                        po = 'x^'+str(po)
                    if po != '':
                        if flint(co) == 1:
                            res.append(po)
                        elif flint(co) == -1:
                            res.append("-"+po)
                        else:
                            res.append(str(flint(co))+po)
                    else:
                        res.append(str(flint(co)))
            if res:
                res.reverse()
                return ' + '.join(res).replace("+ -","- ")
            else:
                return "0"

    def __call__(self, x):
        res = 0
        power = 1
        for co in self.coeffs:
            res += co*power
            power *= x
        return res
    
    def __sub__(self, val):
        return self.__add__(-val)

    def _radd__(self, val):
        return self+val

    def __rmul__(self, val):
        return self*val

    def __rsub__(self, val):
        return -self + val
    
    def __eq__(self, val):
        return self.coeffs == val.coeffs

        
    def derivative(self):
        return self.__class__([self.coeffs[i]*i     for i in range(1,len(self.coeffs))])
    
    
p = Polynomial("x^2+3x-2")
q = Polynomial("1")

print(((p*q + 2*p) - q^4) + 4)  #leider ist a+b+c nicht definiert, da python nicht weiß, ob mein __add__ assoziativ ist.
