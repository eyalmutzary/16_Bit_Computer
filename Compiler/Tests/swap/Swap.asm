// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// Put your code here.

  @16384 // Set R1 to max value
  D=-A
  @R1
  M=D
  @1 // Set R2 to address of max value
  D=-A
  @R2
  M=D
  @16384 // Set R3 to min value
  D=A
  @R3
  M=D
  @1 // Set R4 to address of min value
  D=-A
  @R4
  M=D
  @R14 // Set R5 to be the current address of the array
  D=M
  @R5
  M=D
  @R15 // Set R6 to be the amount of cells left to scan
  D=M
  @R6
  M=D

  // Start the program:
(LOOP)
  @R6 // check if any more cells left
  D=M
  @END_LOOP
  D;JEQ
  @R5
  A=M
  D=M  // now D contains array[i]
  @R1
  D=D-M
  @NOT_MAX
  D;JLT // jumps if not new max
  @R5 // else, set R1 to the current value and R2 to current address
  A=M
  D=M
  @R1
  M=D
  @R5
  D=M
  @R2
  M=D
  //@LOOP
  //0;JMP

(NOT_MAX) // Now check if array[i] is the minimum
  @R5
  A=M
  D=M  // now D contains array[i]
  @R3
  D=D-M
  @NOT_MIN
  D;JGT // jumps if not new max
  @R5 // else, set R1 to the current value and R2 to current address
  A=M
  D=M
  @R3
  M=D
  @R5
  D=M
  @R4
  M=D
(NOT_MIN)

  @R5 // Increase index and go to start of the loop
  M=M+1
  @R6
  M=M-1
  @LOOP
  0;JMP

(END_LOOP) // Swap the values
  @R1
  D=M  // Now D contains the max value
  @R4
  A=M
  M=D  // setting the max value on the min value
  @R3
  D=M  // Now D contains the max value
  @R2
  A=M
  M=D  // setting the max value on the min value

(END)
  @END
  0;JMP
