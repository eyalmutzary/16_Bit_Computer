def numTo16Bit(num):
    if num < 0:
        num = 65536 + num
        bin_num = '{0:016b}'.format(num)
        # bin_num = '1' + bin_num[1:]
    else:
        bin_num = '{0:016b}'.format(num)
    return bin_num

def binary_to_decimal(binary):
    # 000000000000..01 == 1
    # 100000000000..00 = -32768
    # 111111111111..11 = -1

    if binary[0] == '1':
        return -32768 + int(binary[1:], 2)
    return int(binary, 2)


def numTo8Bit(num):
    return '{0:08b}'.format(num)

def And(a, b):
    return a & b

def And16(a, b):
    bin_a, bin_b = numTo16Bit(a), numTo16Bit(b)
    result = ''
    for i in range(16):
        result += str(And(int(bin_a[i]), int(bin_b[i])))
    return binary_to_decimal(result)



def Not(a):
    if a == 0:
        return 1
    return 0

def Not16(a):
    return ~a

def Or(a, b):
    return a | b

def Or16(a, b):
    return a | b

def Or8Way(a):
    return a != 0

def Or16Way(a):
    return a != 0

def Xor(a, b):
    return a ^ b

def Mux(a, b, sel):
    if sel == 0:
        return a
    return b

def Mux16(a, b, sel):
    bin_a = numTo16Bit(a)
    bin_b = numTo16Bit(b)
    bin_sel = numTo16Bit(sel)
    result = ''
    for i in range(16):
        result += str(Mux(int(bin_a[i]), int(bin_b[i]), int(bin_sel[i])))
    return binary_to_decimal(result)

# # test Mux16
# print(Mux16(0, -1, 0))
# print(Mux16(15, 0, 5))
# print(Mux16(1, 0, 0))
# print(Mux16(1, 0, 1))
# print(Mux16(1, 1, 0))
# print(Mux16(1, 1, 1))


def Mux4Way16(a, b, c, d, sel):
    if sel == 0:
        return a
    if sel == 1:
        return b
    if sel == 2:
        return c
    return d

def Mux8Way16(a, b, c, d, e, f, g, h, sel):
    if sel == 0:
        return a
    if sel == 1:
        return b
    if sel == 2:
        return c
    if sel == 3:
        return d
    if sel == 4:
        return e
    if sel == 5:
        return f
    if sel == 6:
        return g
    return h

def DMux(input, sel):
    if sel == 0:
        return input, 0
    return 0, input

def DMux4Way(input, sel):
    if sel == 0:
        return input, 0, 0, 0
    if sel == 1:
        return 0, input, 0, 0
    if sel == 2:
        return 0, 0, input, 0
    return 0, 0, 0, input

def DMux8Way(input, sel):
    if sel == 0:
        return input, 0, 0, 0, 0, 0, 0, 0
    if sel == 1:
        return 0, input, 0, 0, 0, 0, 0, 0
    if sel == 2:
        return 0, 0, input, 0, 0, 0, 0, 0
    if sel == 3:
        return 0, 0, 0, input, 0, 0, 0, 0
    if sel == 4:
        return 0, 0, 0, 0, input, 0, 0, 0
    if sel == 5:
        return 0, 0, 0, 0, 0, input, 0, 0
    if sel == 6:
        return 0, 0, 0, 0, 0, 0, input, 0
    return 0, 0, 0, 0, 0, 0, 0, input

