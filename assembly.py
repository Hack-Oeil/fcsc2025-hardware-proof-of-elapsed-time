import re
import sys

def assembly(asm):
    res = ''
    labels = {}
    refs = []
    for line in asm:
        if not re.search(r'\w', line):
            continue

        if re.search(r'^\s*$', line):
            continue

        if re.search(r'^\s*;', line):
            continue

        if re.search(r'\W*([A-Za-z]\w*):', line):
            b = re.findall(r'\W*([A-Za-z]\w*):',line)
            labels[b[0]] = len(res) >> 2
            continue

        if re.search(r'\.word\b', line):
            b = re.split(r'\.word\b', line)[1]
            b = re.split(r',', b)
            for i in range(len(b)):
                if re.search(r'=[A-Za-z]\w*', b[i]):
                    refs.append(re.split(r'=', b[i])[1])
                    res += '(XX)'
                    continue
                if re.search(r'0x', b[i]):
                    t = int(b[i], 16)
                else:
                    t = int(b[i])
                if t < (1<<16):
                    res += f"{t:04x}"
                else:
                    print(f"{t} is not a word")
            continue

        opcode = 'FFFF'
        if re.search(r'\bMOV\b', line):
            b = re.findall(r'\bMOV\W*R([0-9A-Fa-f]),\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0  < len(b):
                opcode = '00' + b[0][1] + b[0][0]

            b = re.findall(r'\bMOV\W*R([0-9A-Fa-f]),\s*#([0-9]+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][1])
                if t < (1 << 16):
                    opcode = '800' + b[0][0] + f"{t:04x}"

            b = re.findall(r'\bMOV\W*R([0-9A-Fa-f]),\s*#0x([0-9A-Fa-f]+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][1], 16)
                if t < (1 << 16):
                    opcode = '800' + b[0][0] + f"{t:04x}"

            b = re.findall(r'\bMOV\W*R([0-9A-Fa-f]),\s*=([A-Za-z]\w*)\s*($|;)',line)
            if 0 < len(b):
                refs.append(b[0][1])
                opcode = '800' + b[0][0] + "(XX)"

        if re.search(r'\bAND\b', line):
            b = re.findall(r'\bAND\W*R([0-7]),\W*R([0-7]),\W*R([0-7])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 3) + (int(b[0][2], 16) << 6)
                t += 0x4000
                opcode = f"{t:04x}"

        if re.search(r'\bOR\b', line):
            b = re.findall(r'\bOR\W*R([0-7]),\W*R([0-7]),\W*R([0-7])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 3) + (int(b[0][2], 16) << 6)
                t += 0x4200
                opcode = f"{t:04x}"

        if re.search(r'\bXOR\b', line):
            b = re.findall(r'\bXOR\W*R([0-7]),\W*R([0-7]),\W*R([0-7])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 3) + (int(b[0][2], 16) << 6)
                t += 0x4400
                opcode = f"{t:04x}"

        if re.search(r'\bSRL\b', line):
            b = re.findall(r'\bSRL\W*R([0-7]),\W*R([0-7]),\W*R([0-7])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 3) + (int(b[0][2], 16) << 6)
                t += 0x4800
                opcode = f"{t:04x}"

        if re.search(r'\bSLL\b', line):
            b = re.findall(r'\bSLL\W*R([0-7]),\W*R([0-7]),\W*R([0-7])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 3) + (int(b[0][2], 16) << 6)
                t += 0x4600
                opcode = f"{t:04x}"

        if re.search(r'\bBTL\b', line):
            b = re.findall(r'\bBTL\W*R([0-9A-Fa-f]),\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 4)
                t += 0x0100
                opcode = f"{t:04x}"

        if re.search(r'\bADD\b', line):
            b = re.findall(r'\bADD\W*R([0-7]),\W*R([0-7]),\W*R([0-7])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 3) + (int(b[0][2], 16) << 6)
                t += 0x4A00
                opcode = f"{t:04x}"

        if re.search(r'\bSUB\b', line):
            b = re.findall(r'\bSUB\W*R([0-7]),\W*R([0-7]),\W*R([0-7])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 3) + (int(b[0][2], 16) << 6)
                t += 0x4C00
                opcode = f"{t:04x}"

        if re.search(r'\bMUL\b', line):
            b = re.findall(r'\bMUL\W*R([0-7]),\W*R([0-7]),\W*R([0-7])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 3) + (int(b[0][2], 16) << 6)
                t += 0x4E00
                opcode = f"{t:04x}"

        if re.search(r'\bDIV\b', line):
            b = re.findall(r'\bDIV\W*R([0-7]),\W*R([0-7]),\W*R([0-7])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 3) + (int(b[0][2], 16) << 6)
                t += 0x5000
                opcode = f"{t:04x}"

        if re.search(r'\bMOD\b', line):
            b = re.findall(r'\bMOD\W*R([0-9A-Fa-f]),\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 4)
                t += 0x0200
                opcode = f"{t:04x}"

        if re.search(r'\bPOW\b', line):
            b = re.findall(r'\bPOW\W*R([0-9A-Fa-f]),\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 4)
                t += 0x0300
                opcode = f"{t:04x}"

        if re.search(r'\bGCD\b', line):
            b = re.findall(r'\bGCD\W*R([0-7]),\W*R([0-7]),\W*R([0-7])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 3) + (int(b[0][2], 16) << 6)
                t += 0x5200
                opcode = f"{t:04x}"

        if re.search(r'\bINV\b', line):
            b = re.findall(r'\bINV\W*R([0-9A-Fa-f]),\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 4)
                t += 0x0400
                opcode = f"{t:04x}"

        if re.search(r'\bRND\b', line):
            b = re.findall(r'\bRND\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16)
                t += 0x0500
                opcode = f"{t:04x}"

        if re.search(r'\bCMP\b', line):
            b = re.findall(r'\bCMP\W*R([0-9A-Fa-f]),\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 4)
                t += 0x0600
                opcode = f"{t:04x}"

        if re.search(r'\bMOVC\b', line):
            b = re.findall(r'\bMOVC\W*R([0-9A-Fa-f]),\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 4)
                t += (21) << 8
                opcode = f"{t:04x}"

        if re.search(r'\bMOVCW\b', line):
            b = re.findall(r'\bMOVCW\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16)
                t += (23) << 8
                opcode = f"{t:04x}"

        if re.search(r'\bJZR\b', line):
            b = re.findall(r'\bJZR\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = (int(b[0][0], 16) << 4)
                t += 0x0700
                opcode = f"{t:04x}"
            c = re.findall(r'\bJZR\s*([A-Za-z]\w*)\s*($|;)',line)   #Use a second variable so that `Ri` is not considered as a label
            if 0 == len(b) and 0 < len(c):
                refs.append(c[0][0])
                opcode = 'C7()'

            b = re.findall(r'\bJZR\s*\+(\d+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t < (1 << 7):
                    t += 0xC700
                    opcode = f"{t:04x}"

            b = re.findall(r'\bJZR\s*-(\d+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t <= (1 << 7) and 0 < t:
                    t = 256 - t
                    t += 0xC700
                    opcode = f"{t:04x}"

        if re.search(r'\bJZA\b', line):
            b = re.findall(r'\bJZA\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = (int(b[0][0], 16) << 4)
                t += 0x0800
                opcode = f"{t:04x}"
            c = re.findall(r'\bJZA\s*([A-Za-z]\w*)\s*($|;)',line)
            if 0 == len(b) and 0 < len(c):
                refs.append(c[0][0])
                opcode = '8800(XX)'

            b = re.findall(r'\bJZA\s*#([0-9]+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t < (1 << 16):
                    opcode = '8800'+f"{t:04x}"

            b = re.findall(r'\bJZA\s*#0x([0-9A-Fa-f]+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16)
                if t < (1 << 16):
                    opcode = '8800'+f"{t:04x}"

        if re.search(r'\bJNZR\b', line):
            b = re.findall(r'\bJNZR\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = (int(b[0][0], 16) << 4)
                t += 0x0900
                opcode = f"{t:04x}"
            c = re.findall(r'\bJNZR\s*([A-Za-z]\w*)\s*($|;)',line)
            if 0 == len(b) and 0 < len(c):
                refs.append(c[0][0])
                opcode = 'C9()'

            b = re.findall(r'\bJNZR\s*\+(\d+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t < (1 << 7):
                    t += 0xC900
                    opcode = f"{t:04x}"

            b = re.findall(r'\bJNZR\s*-(\d+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t <= (1 << 7) and 0 < t:
                    t = 256 - t
                    t += 0xC900
                    opcode = f"{t:04x}"

        if re.search(r'\bJNZA\b', line):
            b = re.findall(r'\bJNZA\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = (int(b[0][0], 16) << 4)
                t += 0x0A00
                opcode = f"{t:04x}"
            c = re.findall(r'\bJNZA\s*([A-Za-z]\w*)\s*($|;)',line)
            if 0 == len(b) and 0 < len(c):
                refs.append(c[0][0])
                opcode = '8A00(XX)'

            b = re.findall(r'\bJNZA\s*#([0-9]+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t < (1 << 16):
                    opcode = '8A00'+f"{t:04x}"

            b = re.findall(r'\bJNZA\s*#0x([0-9A-Fa-f]+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16)
                if t < (1 << 16):
                    opcode = '8A00'+f"{t:04x}"

        if re.search(r'\bJCR\b', line):
            b = re.findall(r'\bJCR\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = (int(b[0][0], 16) << 4)
                t += 0x0B00
                opcode = f"{t:04x}"
            c = re.findall(r'\bJCR\s*([A-Za-z]\w*)\s*($|;)',line)
            if 0 == len(b) and 0 < len(c):
                refs.append(c[0][0])
                opcode = 'CB()'

            b = re.findall(r'\bJCR\s*\+(\d+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t < (1 << 7):
                    t += 0xCB00
                    opcode = f"{t:04x}"

            b = re.findall(r'\bJCR\s*-(\d+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t <= (1 << 7) and 0 < t:
                    t = 256 - t
                    t += 0xCB00
                    opcode = f"{t:04x}"

        if re.search(r'\bJCA\b', line):
            b = re.findall(r'\bJCA\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = (int(b[0][0], 16) << 4)
                t += 0x0C00
                opcode = f"{t:04x}"
            c = re.findall(r'\bJCA\s*([A-Za-z]\w*)\s*($|;)',line)
            if 0 == len(b) and 0 < len(c):
                refs.append(c[0][0])
                opcode = '8C00(XX)'

            b = re.findall(r'\bJCA\s*#([0-9]+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t < (1 << 16):
                    opcode = '8C00'+f"{t:04x}"

            b = re.findall(r'\bJCA\s*#0x([0-9A-Fa-f]+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16)
                if t < (1 << 16):
                    opcode = '8C00'+f"{t:04x}"

        if re.search(r'\bJNCR\b', line):
            b = re.findall(r'\bJNCR\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = (int(b[0][0], 16) << 4)
                t += 0x0D00
                opcode = f"{t:04x}"
            c = re.findall(r'\bJNCR\s*([A-Za-z]\w*)\s*($|;)',line)
            if 0 == len(b) and 0 < len(c):
                refs.append(c[0][0])
                opcode = 'CD()'

            b = re.findall(r'\bJNCR\s*\+(\d+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t < (1 << 7):
                    t += 0xCD00
                    opcode = f"{t:04x}"

            b = re.findall(r'\bJNCR\s*-(\d+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t <= (1 << 7) and 0 < t:
                    t = 256 - t
                    t += 0xCD00
                    opcode = f"{t:04x}"

        if re.search(r'\bJNCA\b', line):
            b = re.findall(r'\bJNCA\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = (int(b[0][0], 16) << 4)
                t += 0x0E00
                opcode = f"{t:04x}"
            c = re.findall(r'\bJNCA\s*([A-Za-z]\w*)\s*($|;)',line)
            if 0 == len(b) and 0 < len(c):
                refs.append(c[0][0])
                opcode = '8E00(XX)'

            b = re.findall(r'\bJNCA\s*#([0-9]+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t < (1 << 16):
                    opcode = '8E00' + f"{t:04x}"

            b = re.findall(r'\bJNCA\s*#0x([0-9A-Fa-f]+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16)
                if t < (1 << 16):
                    opcode = '8E00' + f"{t:04x}"

        if re.search(r'\bJR\b', line):
            b = re.findall(r'\bJR\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = (int(b[0][0], 16) << 4)
                t += 0x0F00
                opcode = f"{t:04x}"
            c = re.findall(r'\bJR\s*([A-Za-z]\w*)\s*($|;)',line)
            if 0 == len(b) and 0 < len(c):
                refs.append(c[0][0])
                opcode = 'CF()'

            b = re.findall(r'\bJR\s*\+(\d+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t < (1 << 7):
                    t += 0xCF00
                    opcode = f"{t:04x}"

            b = re.findall(r'\bJR\s*-(\d+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t <= (1 << 7) and 0 < t:
                    t = 256 - t
                    t += 0xCF00
                    opcode = f"{t:04x}"

        if re.search(r'\bJA\b', line):
            b = re.findall(r'\bJA\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = (int(b[0][0], 16) << 4)
                t += 0x1000
                opcode = f"{t:04x}"
            c = re.findall(r'\bJA\s*([A-Za-z]\w*)\s*($|;)',line)
            if 0 == len(b) and 0 < len(c):
                refs.append(c[0][0])
                opcode = '9000(XX)'

            b = re.findall(r'\bJA\s*#([0-9]+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t < (1 << 16):
                    opcode = '9000' + f"{t:04x}"

            b = re.findall(r'\bJA\s*#0x([0-9A-Fa-f]+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16)
                if t < (1 << 16):
                    opcode = '9000' + f"{t:04x}"

        if re.search(r'\bCR\b', line):
            b = re.findall(r'\bCR\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = (int(b[0][0], 16) << 4)
                t += 0x1100
                opcode = f"{t:04x}"
            c = re.findall(r'\bCR\s*([A-Za-z]\w*)\s*($|;)',line)
            if 0 == len(b) and 0 < len(c):
                refs.append(c[0][0])
                opcode = 'D1()'

            b = re.findall(r'\bCR\s*\+(\d+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t < (1 << 7):
                    t += 0xD100
                    opcode = f"{t:04x}"

            b = re.findall(r'\bCR\s*-(\d+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t <= (1 << 7) and 0 < t:
                    t = 256 - t
                    t += 0xD100
                    opcode = f"{t:04x}"

        if re.search(r'\bCA\b', line):
            b = re.findall(r'\bCA\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = (int(b[0][0], 16) << 4)
                t += 0x1200
                opcode = f"{t:04x}"
            c = re.findall(r'\bCA\s*([A-Za-z]\w*)\s*($|;)',line)
            if 0 == len(b) and 0 < len(c):
                refs.append(c[0][0])
                opcode = '9200(XX)'

            b = re.findall(r'\bCA\s*#([0-9]+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0])
                if t < (1 << 16):
                    opcode = '9200' + f"{t:04x}"

            b = re.findall(r'\bCA\s*#0x([0-9A-Fa-f]+)\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16)
                if t < (1 << 16):
                    opcode = '9200' + f"{t:04x}"

        if re.search(r'\bRET\b\s*($|;)', line):
            opcode = '1300'

        if re.search(r'\bSTP\b\s*($|;)', line):
            opcode = '1400'

        if re.search(r'\bFP\b', line):
            b = re.findall(r'\bFP\W*R([0-9A-Fa-f]),\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 4)
                t += 24<<8
                opcode = f"{t:04x}"

        if re.search(r'\bFPRR\b', line):
            b = re.findall(r'\bFPRR\W*R([0-7]),\W*R([0-7]),\W*R([0-7])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 3) + (int(b[0][2], 16) << 6)
                t += 0x4000 | (24<<8)
                opcode = f"{t:04x}"

        if re.search(r'\bMM1\b', line):
            b = re.findall(r'\bMM1\W*R([0-9A-Fa-f]),\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 4)
                t += 26<<8
                opcode = f"{t:04x}"

        if re.search(r'\bMM\b', line):
            b = re.findall(r'\bMM\W*R([0-7]),\W*R([0-7]),\W*R([0-7])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 3) + (int(b[0][2], 16) << 6)
                t += 0x4000 | (26<<8)
                opcode = f"{t:04x}"

        if re.search(r'\bEDIV\b', line):
            b = re.findall(r'\bEDIV\W*R([0-7]),\W*R([0-7]),\W*R([0-7])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 3) + (int(b[0][2], 16) << 6)
                t += 0x4000 | (28<<8)
                opcode = f"{t:04x}"

        if re.search(r'\bMPOW\b', line):
            b = re.findall(r'\bMPOW\W*R([0-9A-Fa-f]),\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16) + (int(b[0][1], 16) << 4)
                t += 25<<8
                opcode = f"{t:04x}"

        if re.search(r'\bMOVRR\b', line):
            b = re.findall(r'\bMOVRR\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16)
                t += 28<<8
                opcode = f"{t:04x}"

        if re.search(r'\bMR\b', line):
            b = re.findall(r'\bMR\W*R([0-9A-Fa-f])\s*($|;)',line)
            if 0 < len(b):
                t = int(b[0][0], 16)
                t += 27<<8
                opcode = f"{t:04x}"

        if 'FFFF' == opcode:
            print(f'invalid instruction {line}')

        res += opcode

    # Handle labels
    b = re.split(r"\(",res)
    res = b[0]
    for i in range(1, len(b)):
        s = len(res)
        PC = s >> 2
        b2 = re.split(r"\)",b[i])
        label = refs[i-1]
        if label in labels:
            t = labels[label]
            # is jump relative?
            if (s >> 1) & 1:
                PC += 1
                t = t - PC
                if t < 128 and t >= -128:
                    if t < 0:
                        t += (1 << 8)
                    res += f"{t:02X}"
                else:
                    print(f"label {label} out of reach")
            else:
                if t < (1<<16):
                    res += f"{t:04x}"
                else:
                    print(f"label {label} out of reach")
        else:
            print(f"missing label {label}")

        res += b2[1]

    return res

if __name__ == "__main__":
    code = open(sys.argv[1], "r").read().splitlines()
    code = assembly(code)
    print(code)
