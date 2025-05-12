from Crypto.Random.random import randrange
from crypto_accelerator import Fp_machine, ExactDivision, MillerRabin
import gmpy2

invalidOpCode = -1
#Limits of the machine
maxNbInstruction    = 1 << 16
maxBitSize          = 1 << 13
maxCodeSize         = 1 << 20

class Machine:
    def __init__(self, code, e = 0, N = 0):
        #Null machine
        self.code_size = 0
        self.code = []
        self.end = True
        #Limit the code size
        if (len(code) >> 1) > maxCodeSize:
            return self

        #Initialize registers
        self.a  = 0
        self.b  = 0
        self.dst = 0
        self.R0 = 0
        self.R1 = 0
        self.R2 = 0
        self.R3 = 0
        self.R4 = 0
        self.R5 = 0
        self.R6 = 0       # p
        self.R7 = 0       # q
        self.R8 = 0       # iq
        self.R9 = 0       # dp
        self.RA = 0       # dq
        self.RB = e       # e
        self.exponent = 0 # d
        self.module = N   # n

        #Initialize code
        self.tokenizeCode(code)
        self.code_size = len(self.code)
        self.reset()

    def reset(self):
        self.pc = 0
        self.end = not (self.code_size > 0)
        self.error = False
        self.nbInstruction = 0
        self.FP_accelerator = None
        self.lr = -1
        self.instructionString = ""

    def tokenizeCode(self,s):
        self.code = []

        for i in range(len(s) >> 2):
            self.code.append(s[4*i:4*i+4])

        if (len(s) % 4) != 0:
            self.code.append(invalidOpCode)

    def fetchInstruction(self):
        self.instructionString = ""
        c = self.code[self.pc]
        if c == invalidOpCode :
            self.error = True
            return self
        opcode = int(c[:2], 16)
        operand1 = 0
        operand2 = 0
        sop1 = ""
        sop2 = ""
        sdst = ""
        self.instructionString += c[:4]

        # Case where the second byte contains only two operands
        if (0 << 6) == opcode & (3 << 6) or (2 << 6) == opcode & (3 << 6):
            operand1 = int(c[3], 16)
            operand2 = int(c[2], 16)
            self.dst = operand1

        # Case where b15 b14 b13 b12 b11 b10 b9 b8 b7 b6 b5 b4 b3 b2 b1 b0 => b13 b12 b11 b10 b9 is the instruction, b8 b7 b6 is the op2, b5 b4 b3 is the op1, b2 b1 b0 is the dst
        if (1 << 6) == opcode & (3 << 6):
            t        = int(c[1:4], 16)
            self.dst, t = 7 & t, t >> 3
            operand1, t = 7 & t, t >> 3
            operand2 = 7 & t
            opcode &= ((1 << 7) - 1) << 1

        if  0 == operand1: self.a = self.R0
        if  1 == operand1: self.a = self.R1
        if  2 == operand1: self.a = self.R2
        if  3 == operand1: self.a = self.R3
        if  4 == operand1: self.a = self.R4
        if  5 == operand1: self.a = self.R5
        if  6 == operand1: self.a = self.R6
        if  7 == operand1: self.a = self.R7
        if  8 == operand1: self.a = self.R8
        if  9 == operand1: self.a = self.R9
        if 10 == operand1: self.a = self.RA
        if 11 == operand1: self.a = self.RB
        if 12 == operand1: self.a = self.exponent
        if 13 == operand1: self.a = self.module
        if 14 == operand1: self.a = self.lr
        if 15 == operand1: self.a = self.pc

        if  0 == operand2: self.b = self.R0
        if  1 == operand2: self.b = self.R1
        if  2 == operand2: self.b = self.R2
        if  3 == operand2: self.b = self.R3
        if  4 == operand2: self.b = self.R4
        if  5 == operand2: self.b = self.R5
        if  6 == operand2: self.b = self.R6
        if  7 == operand2: self.b = self.R7
        if  8 == operand2: self.b = self.R8
        if  9 == operand2: self.b = self.R9
        if 10 == operand2: self.b = self.RA
        if 11 == operand2: self.b = self.RB
        if 12 == operand2: self.b = self.exponent
        if 13 == operand2: self.b = self.module
        if 14 == operand2: self.b = self.lr
        if 15 == operand2: self.b = self.pc

        sop1 = "R" + f"{operand1:01X}"
        sop2 = "R" + f"{operand2:01X}"
        sdst = "R" + f"{self.dst:01X}"

        # Case where the instruction is on 4 bytes
        if (2 << 6) == opcode & (3 << 6) :
            self.pc += 1
            self.b = int(self.code[self.pc], 16)
            opcode = opcode & ((1 << 7)-1)
            sop2 = f"{hex(self.b)}"
            self.instructionString += " "
            self.instructionString += self.code[self.pc][:4]

        # Case where the second byte represents an 8-bit value
        if (3 << 6) == opcode & (3 << 6):
            self.b = int(c[2] + c[3], 16)
            sop2 = f"{hex(self.b)}"

        self.instructionString += "\n"
        self.instruction = False

        if 0               == opcode: self.instruction = self.move                          ; self.instructionString += "MOV    " + ", ".join([sdst, sop2])
        if (0 + (2 << 6))  == opcode: self.instruction = self.move                          ; self.instructionString += "MOV    " + ", ".join([sdst, sop2])
        if (0 + (1 << 6))  == opcode: self.instruction = self.log_and                       ; self.instructionString += "AND    " + ", ".join([sdst, sop1, sop2])
        if (2 + (1 << 6))  == opcode: self.instruction = self.log_or                        ; self.instructionString += "OR     " + ", ".join([sdst, sop1, sop2])
        if (4 + (1 << 6))  == opcode: self.instruction = self.log_xor                       ; self.instructionString += "XOR    " + ", ".join([sdst, sop1, sop2])
        if (6 + (1 << 6))  == opcode: self.instruction = self.shiftL                        ; self.instructionString += "SLL    " + ", ".join([sdst, sop1, sop2])
        if (8 + (1 << 6))  == opcode: self.instruction = self.shiftR                        ; self.instructionString += "SRL    " + ", ".join([sdst, sop1, sop2])
        if 1               == opcode: self.instruction = self.bit_len                       ; self.instructionString += "BTL    " + ", ".join([sdst, sop2])
        if (10 + (1 << 6)) == opcode: self.instruction = self.add                           ; self.instructionString += "ADD    " + ", ".join([sdst, sop1, sop2])
        if (12 + (1 << 6)) == opcode: self.instruction = self.sub                           ; self.instructionString += "SUB    " + ", ".join([sdst, sop1, sop2])
        if (14 + (1 << 6)) == opcode: self.instruction = self.mul                           ; self.instructionString += "MUL    " + ", ".join([sdst, sop1, sop2])
        if (16 + (1 << 6)) == opcode: self.instruction = self.div                           ; self.instructionString += "DIV    " + ", ".join([sdst, sop1, sop2])
        if 2               == opcode: self.instruction = self.mod                           ; self.instructionString += "MOD    " + ", ".join([sdst, sop2])
        if 3               == opcode: self.instruction = self.pow                           ; self.instructionString += "POW    " + ", ".join([sdst, sop2])
        if (18 + (1 << 6)) == opcode: self.instruction = self.gcd                           ; self.instructionString += "GCD    " + ", ".join([sdst, sop1, sop2])
        if 4               == opcode: self.instruction = self.invert                        ; self.instructionString += "INV    " + ", ".join([sdst, sop2])
        if 5               == opcode: self.instruction = self.random                        ; self.instructionString += "RND    " + ", ".join([sdst])
        if 6               == opcode: self.instruction = self.cmp                           ; self.instructionString += "CMP    " + ", ".join([sop1, sop2])
        if 24              == opcode: self.instruction = self.init_FP_accelerator           ; self.instructionString += "FP     " + ", ".join([sop1, sop2])
        if (24 + (1 << 6)) == opcode: self.instruction = self.init_FP_accelerator_withRR    ; self.instructionString += "FPRR   " + ", ".join([sdst, sop1, sop2])
        if 26              == opcode: self.instruction = self.MM1                           ; self.instructionString += "MM1    " + ", ".join([sdst, sop2])
        if (26 + (1 << 6)) == opcode: self.instruction = self.MM                            ; self.instructionString += "MM     " + ", ".join([sdst, sop1, sop2])
        if 28              == opcode: self.instruction = self.movRR                         ; self.instructionString += "MOVRR  " + ", ".join([sdst])
        if (28 + (1 << 6)) == opcode: self.instruction = self.ExactDiv                      ; self.instructionString += "EDIV   " + ", ".join([sdst, sop1, sop2])
        if 25              == opcode: self.instruction = self.MontgomeryPow                 ; self.instructionString += "MPOW   " + ", ".join([sdst, sop2])
        if 27              == opcode: self.instruction = self.MillerRabin                   ; self.instructionString += "MR     " + ", ".join([sop1])

        # relative jumps have an odd opcode
        if  7 == opcode or ((3 << 6) + 7) == opcode:  self.instruction = self.jz_rel        ; self.instructionString += "JZR    " + sop2
        if  8 == opcode or ((2 << 6) + 8) == opcode:  self.instruction = self.jz_abs        ; self.instructionString += "JZA    " + sop2
        if  9 == opcode or ((3 << 6) + 9) == opcode:  self.instruction = self.jnz_rel       ; self.instructionString += "JNZR   " + sop2
        if 10 == opcode or ((2 << 6) + 10) == opcode: self.instruction = self.jnz_abs       ; self.instructionString += "JNZA   " + sop2
        if 11 == opcode or ((3 << 6) + 11) == opcode: self.instruction = self.jc_rel        ; self.instructionString += "JCR    " + sop2
        if 12 == opcode or ((2 << 6) + 12) == opcode: self.instruction = self.jc_abs        ; self.instructionString += "JCA    " + sop2
        if 13 == opcode or ((3 << 6) + 13) == opcode: self.instruction = self.jnc_rel       ; self.instructionString += "JNCR   " + sop2
        if 14 == opcode or ((2 << 6) + 14) == opcode: self.instruction = self.jnc_abs       ; self.instructionString += "JNCA   " + sop2
        if 15 == opcode or ((3 << 6) + 15) == opcode: self.instruction = self.j_rel         ; self.instructionString += "JR     " + sop2
        if 16 == opcode or ((2 << 6) + 16) == opcode: self.instruction = self.j_abs         ; self.instructionString += "JA     " + sop2
        if 17 == opcode or ((3 << 6) + 17) == opcode: self.instruction = self.call_rel      ; self.instructionString += "CR     " + sop2
        if 18 == opcode or ((2 << 6) + 18) == opcode: self.instruction = self.call_abs      ; self.instructionString += "CA     " + sop2
        if 19 == opcode:                              self.instruction = self.ret           ; self.instructionString += "RET"
        if 20 == opcode:                              self.instruction = self.stop          ; self.instructionString += "STP"
        if 21 == opcode:                              self.instruction = self.movc          ; self.instructionString += "MOVC   " + ",".join([sop1, sop2])
        if 22 == opcode:                              self.instruction = self.movcb         ; self.instructionString += "MOVCB  " + sop1
        if 23 == opcode:                              self.instruction = self.movcw         ; self.instructionString += "MOVCW  " + sop1

        self.pc += 1
        if not self.instruction:
            self.error = True

    def executeInstruction(self):
        if not self.error:
            self.instruction()
            self.nbInstruction += 1

    def runCode(self, debug=False):
        if debug:
            print("entering debug")

        while True:
            if self.end or self.error:
                return self

            if self.pc >= self.code_size or self.pc < 0 or self.nbInstruction > (maxNbInstruction):
                self.end = True
                self.error = True
                return self

            self.fetchInstruction()
            self.executeInstruction()
            if debug:
                self.printState()

    def printState(self):
        print("=" * 80)
        print("")
        print(self.instructionString)
        print("")
        print(f"a =        {self.a}")
        print(f"b =        {self.b}")
        print(f"R0 =       {self.R0}")
        print(f"R1 =       {self.R1}")
        print(f"R2 =       {self.R2}")
        print(f"R3 =       {self.R3}")
        print(f"R4 =       {self.R4}")
        print(f"R5 =       {self.R5}")
        print(f"R6 =       {self.R6}")
        print(f"R7 =       {self.R7}")
        print(f"R8 =       {self.R8}")
        print(f"R9 =       {self.R9}")
        print(f"RA =       {self.RA}")
        print(f"RB =       {self.RB}")
        print(f"exponent = {self.exponent}")
        print(f"module =   {self.module}")
        print(f"lr =       {self.lr}")
        print(f"pc =       {self.pc}")
        print(f"error =    {self.error}")
        print(f"counter =  {self.nbInstruction}")
        if self.FP_accelerator:
            self.FP_accelerator.display()

    def debugCode(self):
        self.runCode(True)

    def finalize_move(self):
        if (self.a).bit_length() < maxBitSize:
            if 0 == self.dst:  self.R0 = self.a
            if 1 == self.dst:  self.R1 = self.a
            if 2 == self.dst:  self.R2 = self.a
            if 3 == self.dst:  self.R3 = self.a
            if 4 == self.dst:  self.R4 = self.a
            if 5 == self.dst:  self.R5 = self.a
            if 6 == self.dst:  self.R6 = self.a
            if 7 == self.dst:  self.R7 = self.a
            if 8 == self.dst:  self.R8 = self.a
            if 9 == self.dst:  self.R9 = self.a
            if 10 == self.dst: self.RA = self.a
            if 11 == self.dst: self.RB = self.a
            if 12 == self.dst: self.exponent = self.a
            if 13 == self.dst: self.module = self.a
            if 14 == self.dst: self.lr = self.a
            if 15 == self.dst: self.pc = self.a
        else:
            self.error = True

    def move(self):
        self.a = self.b
        self.finalize_move()

    def log_and(self):
        if self.a >= 0 and self.b >= 0:
            self.a = self.a & self.b
            self.finalize_move()
        else:
            self.error = True

    def log_or(self):
        if self.a >= 0 and self.b >= 0:
            self.a = self.a | self.b
            self.finalize_move()
        else:
            self.error = True

    def log_xor(self):
        if self.a >= 0 and self.b >= 0:
            self.a = self.a ^ self.b
            self.finalize_move()
        else:
            self.error = True

    def shiftL(self):
        if self.b > 0:
            self.a = self.a  <<  self.b
            self.finalize_move()
        else:
            self.error = True

    def shiftR(self):
        if self.b > 0:
            self.a = self.a >> self.b
            self.finalize_move()
        else:
            self.error = True

    def bit_len(self):
        self.a = self.b.bit_length()
        self.finalize_move()

    def add(self):
        self.a = self.a + self.b
        self.finalize_move()

    def sub(self):
        self.C = (self.a >= self.b)
        self.Z = (self.a == self.b)
        self.a = self.a - self.b
        self.finalize_move()

    def mul(self):
        self.a = self.a * self.b
        self.Z = (self.a == 0)
        self.finalize_move()

    def div(self):
        if self.b != 0:
            self.a = self.a // self.b
            self.finalize_move()
        else:
            self.error = True

    def mod(self):
        if self.module > 0:
            self.a = self.b % self.module
            self.finalize_move()
        else:
            self.error = True

    def pow(self):
        if self.module > 0 and self.exponent >= 0:
            self.a = int(gmpy2.powmod(self.b, self.exponent, self.module))
            self.Z = (self.a == 0)
            self.finalize_move()
        else:
            self.error = True

    def gcd(self):
        self.a = int(gmpy2.gcd(self.a, self.b))
        self.finalize_move()

    def invert(self):
        if 1 == gmpy2.gcd(self.b, self.module) and (self.module > 0):
            self.a = int(gmpy2.invert(self.b, self.module))
            self.finalize_move()
        else:
            self.error = True

    def random(self):
        if self.a <= 0:
            self.error = True
        else:
            self.a = randrange(1 << self.a)
            self.finalize_move()

    def cmp(self):
        self.C = (self.a >= self.b)
        self.Z = (self.a == self.b)

    def jz_rel(self):
        if self.Z:
            if self.b < (1 << 7):
                self.pc += self.b
            else:
                self.pc -= (1 << 8) - self.b

    def jnz_rel(self):
        if not self.Z:
            if self.b < (1 << 7):
                self.pc += self.b
            else:
                self.pc -= (1 << 8) - self.b

    def jc_rel(self):
        if self.C:
            if self.b < (1 << 7):
                self.pc += self.b
            else:
                self.pc -= (1 << 8) - self.b

    def jnc_rel(self):
        if not self.C:
            if self.b < (1 << 7):
                self.pc += self.b
            else:
                self.pc -= (1 << 8) - self.b

    def jz_abs(self):
        if self.Z:
            self.pc = self.b

    def jnz_abs(self):
        if not self.Z:
            self.pc = self.b

    def jc_abs(self):
        if self.C:
            self.pc = self.b

    def jnc_abs(self):
        if not self.C:
            self.pc = self.b

    def j_rel(self):
        if self.b < (1 << 7):
            self.pc += self.b
        else:
            self.pc -= (1 << 8) - self.b

    def j_abs(self):
        self.pc = self.b

    def call_rel(self):
        self.lr = self.pc
        if self.b < (1 << 7):
            self.pc += self.b
        else:
            self.pc -= (1 << 8) - self.b

    def call_abs(self):
        self.lr = self.pc
        self.pc = self.b

    def ret(self):
        self.pc = self.lr

    def stop(self):
        self.end = True

    def movcw(self):
        if 0 <= self.a and self.a < self.code_size:
            c = self.code[self.a]
            self.a = int(c[0:4],16)
            self.finalize_move()
        else:
            self.error = True

    def movc(self):
        if 0 <= self.a and self.a + self.b < self.code_size and self.b > 0:
            t = 0
            for i in range(self.b):
                c = self.code[self.a+i]
                t <<= 16
                t ^= int(c[0:4], 16)
            self.a = t
            self.finalize_move()
        else:
            self.error = True

    def init_FP_accelerator(self):
        if (0 < self.b) and (0 != self.a & 1) and (self.a > 0):
            self.FP_accelerator = Fp_machine(self.a, self.b)
        else:
            self.error = True

    def init_FP_accelerator_withRR(self):
        if (0 < self.b) and (0 != self.a & 1) and (self.a > 0):
            if 0 == self.dst:  t = self.R0
            if 1 == self.dst:  t = self.R1
            if 2 == self.dst:  t = self.R2
            if 3 == self.dst:  t = self.R3
            if 4 == self.dst:  t = self.R4
            if 5 == self.dst:  t = self.R5
            if 6 == self.dst:  t = self.R6
            if 7 == self.dst:  t = self.R7
            self.FP_accelerator = Fp_machine(self.a, self.b, t)
        else:
            self.error = True

    def movRR(self):
        if self.FP_accelerator:
            self.a = self.FP_accelerator.RR
            self.finalize_move()
        else:
            self.error = True

    def MM1(self):
        if not self.FP_accelerator or self.a < 0 or self.b < 0:
            self.error = True
        else:
            self.a = self.FP_accelerator.MM(self.a, 1)
            self.finalize_move()

    def MM(self):
        if not self.FP_accelerator or self.a < 0 or self.b < 0:
            self.error = True
        else:
            self.a = self.FP_accelerator.MM(self.a, self.b)
            self.finalize_move()

    def MontgomeryPow(self):
        if self.FP_accelerator and self.exponent >= 0:
            self.a = self.FP_accelerator.MPow(self.b, self.exponent)
            self.finalize_move()
        else:
            self.error = True

    def ExactDiv(self):
        if self.b > 0 and self.a >= 0 and 0 == (self.a%self.b):
            self.a = ExactDivision(self.a, self.b)
            self.finalize_move()
        else:
            self.error = True

    def MillerRabin(self):
        if self.a <= 0:
            self.Z = False
        else:
            self.Z = MillerRabin(self.a)
