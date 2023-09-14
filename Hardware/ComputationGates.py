from BasicGates import And, Or, Not, Xor, Mux, DMux, Mux16, Not16, Or16Way, And16, Or16, numTo16Bit, binary_to_decimal

"""
description:
    This file contains the implementation of the following gates:
        - HalfAdder
        - FullAdder
        - Add16
        
    Note: Most of the gates could be use with python's built-in operators, but I wanted to act as if I was using a 
    hardware description language.
"""

def HalfAdder(a, b):
    carry = And(a, b)
    sum = Xor(a, b)
    return sum, carry

def FullAdder(a, b, c):
    sum1, carry1 = HalfAdder(a, b)
    sum2, carry2 = HalfAdder(sum1, c)
    return sum2, Or(carry1, carry2)


def Add16(a, b):
    bin_a, bin_b = numTo16Bit(a), numTo16Bit(b)
    result = ''
    carry = 0
    for i in range(15, -1, -1):
        sum, carry = FullAdder(int(bin_a[i]), int(bin_b[i]), carry)
        result += str(sum)
    return binary_to_decimal(result[::-1])

def Inc16(a):
    return Add16(a, 1)

def ShiftLeft16(a):
    return Add16(a, a)

def ShiftRight16(a):
    bin_a = numTo16Bit(a)
    result = ''
    for i in range(14, 0, -1):
        result += str(Or(int(bin_a[i]), 0))
    result += str(And(int(bin_a[0]), 1))
    return binary_to_decimal(result[::-1])

def ALU(x, y, zx, nx, zy, ny, f, no):
    # // -----
    #
    # Mux16(a=x, b=false, sel=zx, out=XafterZX); // if (zx == 1) set x = 0
    if zx == 1:
        zx = -1
    XafterZX = Mux16(x, 0, zx)
    # // -----

    # Not16( in = XafterZX, out = Notx); // flips x = > Notx
    Notx = Not16(XafterZX)
    # Mux16(a=XafterZX, b=Notx, sel=nx, out=XafterNX); // if (zx == 1) set x = !x
    if nx == 1:
        nx = -1
    XafterNX = Mux16(XafterZX, Notx, nx)
    # // -----
    #
    # Mux16(a=y, b=false, sel=zy, out=YafterZY); // if (zy == 1) set y = 0
    if zy == 1:
        zy = -1
    YafterZY = Mux16(y, 0, zy)

    # // -----
    #
    # Not16( in = YafterZY, out = Noty); // flips y = > Noty
    Noty = Not16(YafterZY)
    # Mux16(a=YafterZY, b=Noty, sel=ny, out=YafterNY); // if (ny == 1) set y = !y
    if ny == 1:
        ny = -1
    YafterNY = Mux16(YafterZY, Noty, ny)

    #
    # // -----
    #
    # Add16(a=XafterNX, b=YafterNY, out=xPlusy);
    xPlusy = Add16(XafterNX, YafterNY)
    # And16(a=XafterNX, b=YafterNY, out=xAndy);
    xAndy = And16(XafterNX, YafterNY)
    # Mux16(a=xAndy, b=xPlusy, sel=f, out=OutAfterF); // Handle with f
    if f == 1:
        f = -1
    OutAfterF = Mux16(xAndy, xPlusy, f)

    # // -----
    #
    # Not16( in = OutAfterF, out = NotOut);
    NotOut = Not16(OutAfterF)
    # Mux16(a=OutAfterF, b=NotOut, sel=no, out=OutAfterNot); // Handle no
    if no == 1:
        no = -1
    OutAfterNot = Mux16(OutAfterF, NotOut, no)
    #
    # // -----
    #
    # Or16Way( in = OutAfterNot, out = o); // Handle zr
    o = Or16Way(OutAfterNot)
    # Not( in = o, out = zr);
    zr = Not(o)
    #
    # // -----
    #
    # And16(a[0..15]=true, b = OutAfterNot, out[15] = ng, out[0..14]=drop); // ng
    ng = And16(32768, OutAfterNot)
    # Or16(a=OutAfterNot, b[0..15]=false, out = out);
    out = Or16(OutAfterNot, 0)

    return out, zr, 0 if ng == 0 else 1



def test_ALU():
    # values, as follows:
    # // if (zx == 1) set x = 0 // 16-bit constant
    # // if (nx == 1) set x = !x // bitwise not
    # // if (zy == 1) set y = 0 // 16-bit constant
    # // if (ny == 1) set y = !y // bitwise not
    # // if (f == 1)  set out = x + y // integer 2's complement addition
    # // if (f == 0)  set out = x & y // bitwise and
    # // if (no == 1) set out = !out // bitwise not
    # // if (out == 0) set zr = 1
    # // if (out < 0) set ng = 1
    input_lst = ['101010', # 0
                 '111111', # 1
                 '111010', # -1
                 '001100', # x
                 '110000', # y
                 '001101', # !x
                 '110001', # !y
                 '001111', # -x
                 '110011', # -y
                 '011111', # x+1
                 '110111', # y+1
                 '001110', # x-1
                 '110010', # y-1
                 '000010', # x+y
                 '010011', # x-y
                 '000111', # y-x
                 '000000', # x&y,
                 '010101'] # x|y
    for item in input_lst:
        out, zero, neg = ALU(x=5, y=2, zx=int(item[0]), nx=int(item[1]), zy=int(item[2]), ny=int(item[3]), f=int(item[4]), no=int(item[5]))
        print(f'out: {out}, zero: {zero}, neg: {neg}')
