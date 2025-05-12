import random

class Fp_machine:
    def __init__(self, p, minWorkingSize, RR=0, logWordSize=6):
        self.logWordSize = logWordSize
        self.wordSize = 1<<logWordSize
        self.workingSize = ((minWorkingSize+3+((1<<logWordSize)-1))>>logWordSize)<<logWordSize
        self.module = p
        self.v = NegInvertModuloPower2(p,self.wordSize)
        if RR:
            self.RR = RR
        else:
            self.RR = self.computeRR()
        self.R = self.MM(self.RR,1)

    def display(self):
        print(f"word size:  {self.wordSize}")
        print(f"workingSize:{self.workingSize}")
        print(f"module:     {hex(self.module)}")
        print(f"RR:         {hex(self.RR)}")
        print(f"v:          {hex(self.v)}")

    def check(self):
        if (not self.v) or self.v == 0:
            print("error v")
            return False
        if (not self.module) or self.module == 0:
            print("error module")
            return False
        if (self.module&1) == 0:
            print("module not odd")
            return False
        return True

    #Montgomery Multiplication : a*b/R mod module
    def MM(self, a, b):
        if b==1:
            return self.multByOne(a)
        if not self.check():
            return False
        res = 0
        wordMask = (1<<self.wordSize)-1
        for _ in range(self.workingSize>>self.logWordSize):
            currentWord = b&wordMask
            b >>= self.wordSize
            res += currentWord*a
            u = ((res&wordMask)*self.v)&wordMask
            res += u*self.module
            res >>= self.wordSize
        return res

    def multByOne(self,a):
        if not self.check():
            return False
        res = a
        wordMask = (1<<self.wordSize)-1
        for _ in range(self.workingSize>>self.logWordSize):
            u = ((res&wordMask)*self.v)&wordMask
            res += u*self.module
            res >>= self.wordSize
        return res

    #Compute R*R mod module
    def computeRR(self):
        if not self.check():
            return False
        wordCount = 0
        lastWord = 0
        tmp = self.module
        while tmp > 0:
            lastWord = tmp
            tmp >>= self.wordSize
            wordCount += 1
        clz = CountLeadingZeroes(lastWord,self.wordSize)
        R = (1<<self.workingSize)-1
        R ^= self.module
        R ^= 1
        RR = R
        align = self.module<<(clz+self.workingSize-(wordCount<<self.logWordSize))
        tradeoff = 5
        if self.logWordSize < tradeoff:
            tradeoff = self.logWordSize
        shift = self.workingSize>>tradeoff
        if RR > align:
            RR -= align
        for _ in range(shift):
            RR += RR
            if RR > align:
                RR -= align

        for _ in range(tradeoff):
            RR = self.MM(RR,RR)
        RR = self.MM(RR,RR)
        RR = self.MM(RR,1)
        return RR

    def MPow(self,m,e):
        if (1==e):
            return m
        res = self.R
        a = m
        while e > 0:
            if (e&1==1):
                res = self.MM(res,a)
            a = self.MM(a,a)
            e >>= 1
        return res

def RemoveTrailingZeroes(a):
    ctz = 0
    while a&1==0:
        a>>=1
        ctz+=1
    return ctz,a

#count leading zeroes for one word, according to the bitsize of a word
def CountLeadingZeroes(a,wordsize):
    if a==0:
        return wordsize

    a &= (1<<wordsize)-1
    res = 0
    for i in range(wordsize-1,-1,-1):
        if a&(1<<i) != 0:
            return res
        res += 1
    return res

# return -1/a mod 2**n
def NegInvertModuloPower2(a,n):
    if a&1==0:
        return False
    a &=((1<<n)-1)
    res = 1
    i = 1
    while i<n :
        res = res*(2+a*res)
        i<<=1
    return res&((1<<n)-1)

def InvertModuloPower2(a,n):
    return NegInvertModuloPower2((1<<n)-a,n)

def ExactDivision(a,b,bitsize=32):
    while a&1 == b&1 and a&1==0:
        a >>= 1
        b >>= 1
    res = 0
    k = 0
    i = InvertModuloPower2(b,bitsize)
    while a > 0:
        r = (i*a)&((1<<bitsize)-1)
        res += r<<(k*bitsize)
        a -= r*b
        a >>= bitsize
        k+=1
    return res

def MillerRabin_round(a,machine):
    p = machine.module
    ctz, e = RemoveTrailingZeroes(p-1)
    a = machine.MPow(a,e)
    t = machine.MM(a,1)
    if (1 == t) or (p-1 == t):
        return True
    for _ in range(ctz-1):
        y = machine.MM(a,a)
        t = machine.MM(y,1)
        if (1 == t):
            return False
        if (p-1 == t):
            return True
        a = y
    if not (p-1 == t):
        return False
    return True

def MillerRabin(p):
    if p < 2:
        return False
    if (p&1)==0:
        return False
    if p < 9:
        return True
    machine = Fp_machine(p, p.bit_length())
    if not MillerRabin_round(2,machine):
        return False
    nb_test = 49
    if p.bit_length() >= 100:
        nb_test = 37
    if p.bit_length() >= 140:
        nb_test = 31
    if p.bit_length() >= 170:
        nb_test = 26
    if p.bit_length() >= 1024:
        nb_test = 3
    if p.bit_length() >= 2048:
        nb_test = 2
    for _ in range(nb_test):
        a = random.randrange(3,p-1)
        if not MillerRabin_round(a,machine):
            return False
    return True

