from BasicGates import And, Or, Not, Xor, Mux, DMux, Mux16, Not16, Or16Way, And16, Or16, numTo16Bit, binary_to_decimal
from ComputationGates import HalfAdder, FullAdder, Add16, Inc16, ShiftLeft16, ShiftRight16, ALU, Extended_ALU

KEYBOARD = 24576
SCREEN = 16384
class Computer:
    def __init__(self):
        self.RAM = [0 for _ in range(24577)]
        self.ROM = [0 for _ in range(32768)]
        self.ARegister = 0
        self.DRegister = 0
        self.PC = 0

    def load_program(self, program):
        self.ROM = program

    def CPU(self, inM, instruction, reset):
        bin_inM, bin_instruction = numTo16Bit(inM), numTo16Bit(instruction)

        # Mux16(a=instruction, b=ALUoutput, sel=instruction[15], out=OutToARegister);
        OutToARegister = Mux16(instruction, self.ARegister, instruction[15])


    #     Not(in=instruction[15],out=ni);
    #     Or(a=ni,b=instruction[5],out=loadA);
    #     ARegister(in=OutToARegister, load=loadA, out=ARegOutput, out[0..14]=addressM);
        ni = Not(bin_instruction[15])
        loadA = Or(ni, bin_instruction[5])
        if loadA == 1:
            self.ARegister = OutToARegister
        ARegOutput = self.ARegister
        addressM = self.ARegister[0:14] # TODO: check if this is correct

        # And(a=instruction[15], b=instruction[12], out=AorM); // checks if it is a C function (and not @<=>A function)
        # Mux16(a=ARegOutput, b=inM, sel=AorM, out=MuxOutToALU);
        AorM = And(bin_instruction[15], bin_instruction[12])
        MuxOutToALU = Mux16(a=ARegOutput, b=bin_inM, sel=AorM)

        # ALU(x=DRegOutput, y=MuxOutToALU, zx=instruction[11], nx=instruction[10], zy=instruction[9], ny=instruction[8],f=instruction[7], no=instruction[6], out=RegALUoutput, out=RegOutM, zr=RegZr, ng=RegNg);
        # ExtendAlu(x=DRegOutput, y=MuxOutToALU, instruction[0..6]=instruction[6..12], instruction[7] = true, instruction[8] = false, out = ExALUoutput, out = ExOutM, zr = ExZr, ng = ExNg);
        out, RegZr, RegNg = ALU(x=self.DRegister, y=MuxOutToALU, zx=instruction[11], nx=instruction[10], zy=instruction[9], ny=instruction[8],f=instruction[7], no=instruction[6])
        RegALUoutput, RegOutM = out

        # Xor(a=instruction[15], b=false, out=firstCondition); // Determine if should use regular ALU or extended ALU
        firstCondition = Xor(bin_instruction[15], 0)
        # Xor(a=instruction[14], b=true, out=secondCondition);
        secondCondition = Xor(bin_instruction[14], 1)
        # And(a=firstCondition, b=secondCondition, out=isExtended);
        isExtended = And(firstCondition, secondCondition)
        # Mux16(a=RegALUoutput, b=ExALUoutput, sel=isExtended, out=ALUoutput);
        ALUoutput = Mux16(RegALUoutput, RegOutM, isExtended)
        # Mux16(a=RegOutM, b=ExOutM, sel=isExtended, out=outM);
        outM = Mux16(RegOutM, RegOutM, isExtended)
        # Mux(a=RegZr, b=ExZr, sel=isExtended, out=zr);
        zr = Mux(RegZr, RegZr, isExtended)
        # Mux(a=RegNg, b=ExNg, sel=isExtended, out=ng);
        ng = Mux(RegNg, RegNg, isExtended)

        # // Continue to the normal CPU process
        # And(a=instruction[15], b=instruction[4], out=loadD);
        loadD = And(bin_instruction[15], bin_instruction[4])
        # DRegister( in = ALUoutput, load = loadD, out = DRegOutput);
        if loadD == 1:
            self.DRegister, DRegOutput = ALUoutput # TOOD: make solution for D and A registers

        # And(a=instruction[15],b=instruction[3],out=writeM);
        writeM = And(bin_instruction[15], bin_instruction[3])

        # // Now calculate g function, to check if there is a jump, reset or continue to next line
        # Not( in = ng, out = pos); // prefix for positive
        pos = Not(ng)
        # Not( in = zr, out = nzr); // prefix for not -zero
        nzr = Not(zr)

        # And(a=instruction[15], b=instruction[0], out=jgt); // checks if greater than
        jgt = And(bin_instruction[15], bin_instruction[0])
        # And(a=pos, b=nzr, out=posnzr); // and not equal
        posnzr = And(pos, nzr)
        # And(a=jgt, b=posnzr, out=load1);
        load1 = And(jgt, posnzr)
        #
        # And(a=instruction[15], b=instruction[1], out=jeq); // checks if equal
        jeq = And(bin_instruction[15], bin_instruction[1])
        # And(a=jeq, b=zr, out=load2);
        load2 = And(jeq, zr)
        #
        # And(a=instruction[15], b=instruction[2], out=jlt); // checks lower than
        jlt = And(bin_instruction[15], bin_instruction[2])
        # And(a=jlt, b=ng, out=load3);
        load3 = And(jlt, ng)
        #
        # Or(a=load1, b=load2, out=ldt); // checks if one of the conditions is 1
        ldt = Or(load1, load2)
        # Or(a=load3, b=ldt, out=pcLoad);
        pcLoad = Or(load3, ldt)
        #
        # PC( in = ARegOutput, reset = reset, load = pcLoad, inc = true, out[0..14]=pc);
        if reset == 1:
            self.PC = 0
        elif pcLoad == 1:
            self.PC = ARegOutput
        else:
            self.PC += 1

        return outM, writeM, addressM

