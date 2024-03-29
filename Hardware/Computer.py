from BasicGates import And, Or, Not, Xor, Mux, DMux, Mux16, Not16, Or16Way, And16, Or16, numTo16Bit, binary_to_decimal
from ComputationGates import HalfAdder, FullAdder, Add16, Inc16, ShiftLeft16, ShiftRight16, ALU, Extended_ALU

KEYBOARD = 24576
SCREEN = 16384
SCREEN_SIZE = 8191
class Computer:
    def __init__(self):
        self.RAM = [0 for _ in range(24577)]
        self.ROM = [0 for _ in range(32768)]
        self.ARegister = 0
        self.DRegister = 0
        self.last_ALU_output = 0
        self.PC = 0
        self.clock = 0

    def load_instructions(self, program):
        self.ROM = program

    def run(self):
        while self.clock < 60000 and self.PC < len(self.ROM):
            self.tick()


    def tick(self):
        if 0 <= self.ARegister < len(self.RAM):
            self.CPU2(inM=self.RAM[self.ARegister], instruction=self.ROM[self.PC], reset=0)
        else:
            self.CPU2(inM=0, instruction=self.ROM[self.PC], reset=0)
        self.clock += 1

        print(f"A = {self.ARegister}")
        print(f"D = {self.DRegister}")
        print(f"PC: " + str(self.PC))
        print("RAM[0:20]: " + str(self.RAM[0:20]))
        print("RAM[256:266]: " + str(self.RAM[256:266]))


    def reset_computer(self):
        self.PC = 0
        self.ARegister = 0
        self.DRegister = 0

    def get_screen(self):
        return self.RAM[0:270]

    def CPU1(self, inM, instruction, reset):
        """
        :param inM: 16 bit input from RAM
        :param instruction: 16 bit instruction
        :param reset: 1 bit reset
        :return:

        """
        old_ARegister = self.ARegister
        old_DRegister = self.DRegister

        bin_instruction = numTo16Bit(instruction)
        isAFunction = bin_instruction[0] == '0'
        if isAFunction:
            self.ARegister = instruction
            self.PC += 1
            return

        isNormalC = bin_instruction[0:3] == '111'

        result = None
        if isNormalC:
            x, y = self.DRegister, self.ARegister if bin_instruction[3] == '0' else inM
            relevant_bits = bin_instruction[4:10]
            zx, nx, zy, ny, f, no = relevant_bits[0], relevant_bits[1], relevant_bits[2], relevant_bits[3], relevant_bits[4], relevant_bits[5]
            if zx == '1':
                x = 0
            if nx == '1':
                x = Not16(x)
            if zy == '1':
                y = 0
            if ny == '1':
                y = Not16(y)
            if f == '1':
                result = x + y
            else:
                result = And16(x, y)
            if no == '1':
                result = Not16(result)
        else:
            ext_bits = bin_instruction[2:5]
            if ext_bits == '010':
                result = self.ARegister * 2
            elif ext_bits == '011':
                result = self.DRegister * 2
            elif ext_bits == '110':
                result = inM * 2
            elif ext_bits == '000':
                result = self.ARegister // 2
            elif ext_bits == '001':
                result = self.DRegister // 2
            elif ext_bits == '100':
                result = inM // 2

        dest_bits = bin_instruction[10:13]
        dest_to_A, dest_to_D, dest_to_M = dest_bits[0], dest_bits[1], dest_bits[2]
        if dest_to_M == '1':
            self.RAM[self.ARegister] = result
        if dest_to_A == '1':
            self.ARegister = result
        if dest_to_D == '1':
            self.DRegister = result

        jump_bits = bin_instruction[13:16]
        is_jump = False
        if jump_bits[0] == '1' and result < 0:
            is_jump = True
        elif jump_bits[1] == '1' and result == 0:
            is_jump = True
        elif jump_bits[2] == '1' and result > 0:
            is_jump = True
        if is_jump:
            print("JUMPING from " + str(self.PC) + " to " + str(self.ARegister))
            self.PC = self.ARegister
        else:
            self.PC += 1

        if reset == 1:
            self.reset_computer()


    def CPU2(self, inM, instruction, reset):
        bin_instruction = numTo16Bit(instruction)
        # Mux16(a=instruction, b=ALUoutput, sel=instruction[15], out=OutToARegister);
        selector = 0
        print("-----------")
        print(f"bin_instruction: {bin_instruction}")
        if int(bin_instruction[0]) == 0: # => A function
            selector = 0
        OutToARegister = Mux16(a=instruction, b=self.ARegister, sel=selector)
    #     Not(in=instruction[15],out=ni);
    #     Or(a=ni,b=instruction[5],out=loadA);
    #     ARegister(in=OutToARegister, load=loadA, out=ARegOutput, out[0..14]=addressM);
        isAFunction = Not(int(bin_instruction[0]))
        if isAFunction == 1:
            self.ARegister = OutToARegister

        ARegOutput = self.ARegister
        addressM = numTo16Bit(self.ARegister)[1:]

        # And(a=instruction[15], b=instruction[12], out=AorM); // checks if it is a C function (and not @<=>A function)
        # Mux16(a=ARegOutput, b=inM, sel=AorM, out=MuxOutToALU);
        AorM = And(int(bin_instruction[0]), int(bin_instruction[3]))
        selector = 0
        if AorM == 1:
            selector = -1
        MuxOutToALU = Mux16(a=ARegOutput, b=inM, sel=selector)
        # ALU(x=DRegOutput, y=MuxOutToALU, zx=instruction[11], nx=instruction[10], zy=instruction[9], ny=instruction[8],f=instruction[7], no=instruction[6], out=RegALUoutput, out=RegOutM, zr=RegZr, ng=RegNg);
        # ExtendAlu(x=DRegOutput, y=MuxOutToALU, instruction[0..6]=instruction[6..12], instruction[7] = true, instruction[8] = false, out = ExALUoutput, out = ExOutM, zr = ExZr, ng = ExNg);
        RegALUoutput, RegZr, RegNg = ALU(x=self.DRegister, y=MuxOutToALU, zx=int(bin_instruction[4]), nx=int(bin_instruction[5]), zy=int(bin_instruction[6]), ny=int(bin_instruction[7]),f=int(bin_instruction[8]), no=int(bin_instruction[9]))
        ext_bin_instruction = '0000000' + bin_instruction[1:10]
        ExtALUoutput, ExtZr, ExtNg = Extended_ALU(x=self.DRegister, y=MuxOutToALU, instruction=binary_to_decimal(ext_bin_instruction))
        # TODO: Ext not working
        # Xor(a=instruction[15], b=false, out=firstCondition); // Determine if should use regular ALU or extended ALU
        firstCondition = Xor(int(bin_instruction[0]), 0)
        # Xor(a=instruction[14], b=true, out=secondCondition);
        secondCondition = Xor(int(bin_instruction[1]), 1)
        # And(a=firstCondition, b=secondCondition, out=isExtended);
        isExtended = And(firstCondition, secondCondition) # Check if the correct way for is extended
        # Mux16(a=RegALUoutput, b=ExALUoutput, sel=isExtended, out=ALUoutput);
        if isExtended == 1:
            isExtended = -1
        ALUoutput = Mux16(RegALUoutput, ExtALUoutput, isExtended)
        # Mux16(a=RegOutM, b=ExOutM, sel=isExtended, out=outM);
        outM = Mux16(ALUoutput, ALUoutput, isExtended)
        # Mux(a=RegZr, b=ExZr, sel=isExtended, out=zr);
        zr = Mux(RegZr, RegZr, isExtended)
        # Mux(a=RegNg, b=ExNg, sel=isExtended, out=ng);
        ng = Mux(RegNg, RegNg, isExtended)

        # // Continue to the normal CPU process
        # And(a=instruction[15], b=instruction[4], out=loadD);
        loadD = And(int(bin_instruction[0]), int(bin_instruction[11]))
        # DRegister( in = ALUoutput, load = loadD, out = DRegOutput);
        if loadD == 1:
            self.DRegister = ALUoutput

        # And(a=instruction[15],b=instruction[3],out=writeM);
        writeM = And(int(bin_instruction[0]), int(bin_instruction[12]))

        writeA = And(a=int(bin_instruction[0]), b=int(bin_instruction[10]))
        if writeA == 1:
            writeA = -1
        self.ARegister = Mux16(a=self.ARegister, b=ALUoutput, sel=writeA)
        # // Now calculate g function, to check if there is a jump, reset or continue to next line
        # Not( in = ng, out = pos); // prefix for positive
        pos = Not(ng)
        # Not( in = zr, out = nzr); // prefix for not -zero
        nzr = Not(zr)

        # And(a=instruction[15], b=instruction[0], out=jgt); // checks if greater than
        jgt = And(int(bin_instruction[0]), int(bin_instruction[15]))
        # And(a=pos, b=nzr, out=posnzr); // and not equal
        posnzr = And(pos, nzr)
        # And(a=jgt, b=posnzr, out=load1);
        load1 = And(jgt, posnzr)
        #
        # And(a=instruction[15], b=instruction[1], out=jeq); // checks if equal
        jeq = And(int(bin_instruction[0]), int(bin_instruction[14]))
        # And(a=jeq, b=zr, out=load2);
        load2 = And(jeq, zr)
        #
        # And(a=instruction[15], b=instruction[2], out=jlt); // checks lower than
        jlt = And(int(bin_instruction[0]), int(bin_instruction[13]))
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
            print(f"Jump from {self.PC} to address: {str(ARegOutput)}")
            print("RAM[0:25]: " + str(self.RAM[0:25]))
            self.PC = ARegOutput
        else:
            self.PC += 1

        addressM = binary_to_decimal('0' + addressM)
        if writeM == 1:
            self.RAM[addressM] = outM
        return outM, writeM, addressM

