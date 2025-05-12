# Python regular imports
import gmpy2
from Crypto.Util.number import getPrime
from random import randrange

# Public files (challenge specific)
from machine import Machine

def setup(bit_len):
    p = getPrime(bit_len)
    q = getPrime(bit_len)
    l = (p - 1) * (q - 1) // gmpy2.gcd(p - 1,q - 1)
    N = p*q
    return N, l

def test(code, k):
    N, l = setup(256)
    M = randrange(N)

    e = (1 << k) % l
    c = Machine(code, N = N)
    c.R5 = k
    c.R6 = M
    c.exponent = 2

    c.runCode()
    if c.error:
        return False

    if c.exponent != 2:
        return False

    if gmpy2.powmod(M, e, N) != c.R6:
        return False

    return True

def correctness(code):
    print("[+] Testing correctness")

    if not test(code, 0):
        exit()

    if not test(code, (2 ** 13) | randrange(2 ** 13)):
        exit()

    return True

if __name__ == "__main__":
    try:
        print("Enter your bytecode in hexadecimal:")
        code = input(">>> ")
        if len(code) > 28:
            exit()
        if correctness(code):
            flag = open("flag.txt").read().strip()
            print(f"[+] Congrats! Here is the flag: {flag}")
    except:
        print("Please check your inputs")
