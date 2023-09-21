// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// Multiplies R0 and R1 and stores the result in R2.
//
// Assumptions:
// - R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.
// - You can assume that you will only receive arguments that satisfy:
//   R0 >= 0, R1 >= 0, and R0*R1 < 32768.
// - Your program does not need to test these conditions.
//
// Requirements:
// - Your program should not change the values stored in R0 and R1.
// - You can implement any multiplication algorithm you want.

// Put your code here.

  @5
  D=A
  @R0
  M=D // R0 = 5
  @3
  D=A
  @R1
  M=D // R1 = 3
  @R2 // R2 = 0
  M=0
  @i // int i = 0
  M=0
(LOOP)
  @R1 // while(i < R1)
  D=M
  @i
  D=D-M
  @END
  D;JLE
  @R0 // R2 = R2 + R0
  D=M
  @R2
  M=M+D
  @i
  M=M+1
  @LOOP // restart loop
  0;JMP
(END)
  @END
  0;JMP