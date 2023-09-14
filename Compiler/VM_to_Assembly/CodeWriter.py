"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from typing import List
import os



class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Ex 7
        self.output_stream = output_stream
        self.jmp_counter = 0
        self.skip_counter = 0
        self.if_else_signs = 0
        # Ex 8
        self.functions_dict = {} # used to track all functions from different files
        self.current_func_name = "" # used for labels and other stuff
        self.counter_per_func = {} # used for recursive cases
        self.current_file_name = "" # used for labels and other stuff

    def write_init(self) -> None:
        lines = ["@256\n", "D=A\n", "@SP\n", "M=D\n"]
        self.output_stream.writelines(lines)
        self.write_call("Sys.init", 0)

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        output_name, output_extension = os.path.splitext(
            os.path.basename(self.output_stream.name))
        output_file_name = output_name.split('\\')[-1:][0] + output_extension
        print(f"translating {filename} to {output_file_name} \n")
        self.current_file_name = filename

    def store_last_signs_for_jump(self, element_pos: int) -> List[str]:
        # stores the sign of the last 2 elements in the stack
        last_or_one_before = [[["@SP // Store sht1\n", "A=M-1\n", "A=A-1\n"], ["@R14\n", "M=D\n"]],
                              [["@SP // Store sht2\n", "A=M-1\n"], ["@R15\n", "M=D\n"]]]
        lines = last_or_one_before[element_pos][0]
        lines += ["D=M\n",
                  "@YES"+str(self.if_else_signs)+"\n",
                  "D;JGE\n",
                  "@NO"+str(self.if_else_signs)+"\n",
                  "0;JMP\n",
                  "(YES"+str(self.if_else_signs)+")\n",
                  "D=1\n",
                  "@ANYWAY" + str(self.if_else_signs) + "\n",
                  "0;JMP\n",
                  "(NO"+str(self.if_else_signs)+")\n",
                  "D=-1\n",
                  "@ANYWAY" + str(self.if_else_signs) + "\n",
                  "0;JMP\n",
                  "(ANYWAY"+str(self.if_else_signs)+")\n"] + last_or_one_before[element_pos][1]
        self.if_else_signs += 1
        return lines

    def check_last_signs_for_jump(self):
        lines = ["@R14\n",
                 "D=M\n",
                 "@R15\n",
                 "D=D-M\n",
                 "@SKIP" + str(self.skip_counter) + "\n",
                 "D;JEQ\n",
                 "@SP\n",
                 "A=M-1\n",

                 "@R15\n",
                 "D=M\n",
                 "@SP\n",
                 "A=M-1\n",
                 "M=M>>\n",
                 "M=M+D\n",
                 "M=M>>\n",
                 "M=M+D\n",

                 "A=A-1\n",
                 # "M=M>>\n",

                 "@R14\n",
                 "D=M\n",
                 "@SP\n",
                 "A=M-1\n",
                 "A=A-1\n",
                 "M=M+D\n",
                 "M=M>>\n",
                 "M=M+D\n",
                 "M=M>>\n",

                 # "M=-M\n",
                 "(SKIP" + str(self.skip_counter) + ")\n"]
        self.skip_counter += 1
        return lines

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        arith_commands = {
            "add": "D=D+M",
            "sub": "D=D-M",
            "and": "D=D&M",
            "or": "D=D|M",
        }
        jump_commands = {
            "eq": "D;JEQ",
            "gt": "D;JGT",
            "lt": "D;JLT",
        }
        single_params = {
            "neg": "M=-M",
            "not": "M=!M",
            "shiftleft": "M=M<<",
            "shiftright": "M=M>>"
        }
        lines = []
        if command in arith_commands:
            lines = ["@SP //" + command + " \n",
                     "A=M-1\n",
                     "A=A-1\n",
                     "D=M\n",
                     "A=A+1\n",
                     arith_commands[command] +"\n",
                     "A=A-1\n",
                     "M=D\n",
                     "@SP\n",
                     "M=M-1\n"]
        elif command in single_params:
            lines = ["@SP //" + command + "\n", "A=M-1\n", single_params[command]+"\n"]
        elif command in jump_commands:
            lines = self.store_last_signs_for_jump(0) # solves the overflow case
            lines += self.store_last_signs_for_jump(1)
            lines += self.check_last_signs_for_jump()
            lines += ["@SP //" + command + "\n",
                     "A=M-1\n",
                     "D=M\n",
                     "A=A-1\n",
                     "D=M-D\n", # D contains range of last two elements
                     "@TRUE" + str(self.jmp_counter) + "\n", # if... else...
                     jump_commands[command] + "\n",
                     "(FALSE" + str(self.jmp_counter) +")\n",
                     "D=0\n",
                     "@ADDJMPCMD" + str(self.jmp_counter) + "\n",
                     "0;JMP\n",
                     "(TRUE" + str(self.jmp_counter) +")\n",
                     "D=-1\n",
                     "(ADDJMPCMD" + str(self.jmp_counter) + ")\n",
                     "@SP\n", # M--
                     "M=M-1\n",
                     "A=M-1\n", # update stack
                     "M=D\n"]
            self.jmp_counter += 1
        self.output_stream.writelines(lines)


    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Commands are in the form:
        pop <segment> <i>

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.
        segment_dictionary = {"local": "LCL",
                              "argument": "ARG",
                              "this": "THIS",
                              "that": "THAT",
                              "temp": "5",
                              "static": 16}
        lines = []
        if command == "C_PUSH":
            if segment == "static":
                lines = ["@" + self.current_file_name + "." + str(index) + " // push static " + str(index) + "\n",
                # lines = ["@" + str(segment_dictionary["static"] + index) + " // push static " + str(index) + "\n",
                         "D=M\n",
                         "@SP\n",
                         "A=M\n",
                         "M=D\n",
                         "@SP\n",
                         "M=M+1\n"]
            elif segment == "constant": # Works
                lines = ["@"+str(index) + " // push constant " + str(index) + "\n",
                         "D=A\n",
                         "@SP\n",
                         "A=M\n",
                         "M=D\n",
                         "@SP\n",
                         "M=M+1\n"]
            elif segment == "pointer":
                this_or_that = {0: "THIS\n", 1: "THAT\n"}
                lines = ["@"+this_or_that[index] + " // push pointer " + str(index) + "\n",
                         "D=M\n",
                         "@SP\n",
                         "A=M\n",
                         "M=D\n",
                         "@SP\n",
                         "M=M+1\n"]
            elif segment == "temp":
                lines = ["@"+ segment_dictionary[segment]+" // push temp " + str(index) + "\n",
                         "D=A\n", # notice the difference of temp
                         "@"+str(index)+"\n",
                         "A=A+D\n",
                         "D=M\n",
                         "@SP\n",
                         "A=M\n",
                         "M=D\n",
                         "@SP\n",
                         "M=M+1\n"]
            else:
                lines = ["@"+segment_dictionary[segment]+" // push "+segment+" " + str(index) + "\n",
                         "D=M\n", "@"+str(index)+"\n",
                         "A=A+D\n",
                         "D=M\n",
                         "@SP\n",
                         "A=M\n",
                         "M=D\n",
                         "@SP\n",
                         "M=M+1\n"]
        elif command == "C_POP":
            if segment == "static":
                lines = ["@SP // pop static " + str(index) + "\n", "A=M\n", "A=A-1\n", "D=M\n"]
                lines += ["@" + self.current_file_name + "." + (str(index)) + "\n", "M=D\n"]
                # lines += ["@" + str(segment_dictionary["static"] + index) + "\n", "M=D\n"]
                lines += ["@SP\n", "M=M-1\n"]
            elif segment == "pointer": # THIS and THAT
                this_or_that = {0: "@THIS\n", 1: "@THAT\n"}
                lines = ["@SP // pop pointer " + str(index) + "\n", "A=M\n", "A=A-1\n", "D=M\n"]
                lines += [this_or_that[index], "M=D\n"]
                lines += ["@SP\n", "M=M-1\n"]
            elif segment == "temp":
                lines = ["@"+segment_dictionary[segment]+" // pop temp " + str(index) + "\n",
                                         "D=A\n",
                                         "@" + str(index) + "\n",
                                         "D=D+A\n",
                                         "@R15\n",
                                         "M=D\n",
                                         "@SP\n",
                                         "A=M-1\n",
                                         "D=M\n",
                                         "@SP\n",
                                         "M=M-1\n",
                                         "@R15\n",
                                         "A=M\n",
                                         "M=D\n"]
            else:
                store_seg_ind_address = ["@"+segment_dictionary[segment]+" // pop " + segment + " " + str(index) + "\n",
                                         "D=M\n",
                                         "@" + str(index) + "\n",
                                         "D=D+A\n",
                                         "@R15\n",
                                         "M=D\n"]
                store_popped_val_to_D = ["@SP\n",
                                         "A=M-1\n",
                                         "D=M\n"]
                SPminus1 =              ["@SP\n",
                                         "M=M-1\n"]
                set_value =             ["@R15\n",
                                         "A=M\n",
                                         "M=D\n"]
                lines = store_seg_ind_address + store_popped_val_to_D +\
                        SPminus1 + set_value
        self.output_stream.writelines(lines)





    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        full_label = self.current_func_name + "$" + label
        self.output_stream.writelines(["(" + full_label + ") // label " +label+ "\n"])
    
    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        full_label = self.current_func_name + "$" + label
        lines = ["@" + full_label + "// goto " + label + "\n",
                 "0;JMP\n"]
        self.output_stream.writelines(lines)


    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        full_label = self.current_func_name + "$" + label
        lines = ["@SP // if-goto " +label+ "\n",
                 "AM=M-1\n",
                 "D=M\n",
                 "@" + full_label + "\n",
                 "D;JNE\n"]
        self.output_stream.writelines(lines)
    
    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0

        if function_name not in self.counter_per_func:
            self.counter_per_func[function_name] = 0
        full_func_name = function_name + str(self.counter_per_func[function_name])
        self.output_stream.writelines(["(" + function_name + ") // function "+full_func_name+" " +str(n_vars)+ "\n"])
        for _ in range(n_vars):
            self.write_push_pop("C_PUSH", "constant", 0)
        self.current_func_name = full_func_name
        self.functions_dict[function_name] = full_func_name


    def push_formatter_for_pointer_and_static(self,segment: str) -> List[str]:
        lines = [f"{segment}\n", "D=M\n", "@SP\n", "A=M\n", "M=D\n", "@SP\n", "M=M+1\n"]
        return lines

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "foo" be a function within the file Xxx.vm.
        The handling of each "call" command within foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        if function_name not in self.counter_per_func:
            self.counter_per_func[function_name] = 0
        self.counter_per_func[function_name] += 1

        if function_name in self.functions_dict:
            self.current_func_name = self.functions_dict[function_name]
        else:
            full_func_name = function_name + str(self.counter_per_func[function_name])
            self.functions_dict[function_name] = full_func_name
            self.current_func_name = full_func_name

        self.output_stream.writelines([f"@{self.current_func_name}$RET{self.counter_per_func[function_name]} // call "+function_name+" " +str(n_args)+ "\n",
                                       "D=A\n",
                                       "@SP\n",
                                       "A=M\n",
                                       "M=D\n",
                                       "@SP\n",
                                       "M=M+1\n"])
        lines = ["@LCL\n", "D=M\n", "@SP\n", "A=M\n", "M=D\n", "@SP\n", "M=M+1\n"]
        lines += ["@ARG\n", "D=M\n", "@SP\n", "A=M\n", "M=D\n", "@SP\n", "M=M+1\n"]
        lines += ["@THIS\n", "D=M\n", "@SP\n", "A=M\n", "M=D\n", "@SP\n", "M=M+1\n"]
        lines += ["@THAT\n", "D=M\n", "@SP\n", "A=M\n", "M=D\n", "@SP\n", "M=M+1\n"]
        lines += ["@SP\n", "D=M\n", "@5\n", "D=D-A\n", f"@{n_args}\n", "D=D-A\n",
                  "@R2\n", "M=D\n", "@SP\n", "D=M\n", "@R1\n", "M=D\n"]
        lines += [f"@{function_name}\n", "0;JMP\n",
                  f"({self.current_func_name}$RET{self.counter_per_func[function_name]})\n"]
        self.output_stream.writelines(lines)



    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        lines = ["@LCL\n", "D=M\n", "@R13\n", "M=D\n", "@5\n", "A=D-A\n",
                 "D=M\n", "@R14\n", "M=D\n"]
        lines += ["@ARG\n", "D=M\n", "@SP\n", "D=D+A\n", "@R15\n", "M=D\n",
                  "@SP\n", "AM=M-1\n", "D=M\n", "@R15\n", "A=M\n", "M=D\n"]
        lines += ["@ARG\n", "D=M\n", "@SP\n", "M=D+1\n"] # SP = ARG + 1
        lines += ["@R13\n", "M=M-1\n", "A=M\n", "D=M\n", "@THAT\n", "M=D\n"]
        lines += ["@R13\n", "M=M-1\n", "A=M\n", "D=M\n", "@THIS\n", "M=D\n"]
        lines += ["@R13\n", "M=M-1\n", "A=M\n", "D=M\n", "@ARG\n", "M=D\n"]
        lines += ["@R13\n", "M=M-1\n", "A=M\n", "D=M\n", "@LCL\n", "M=D\n"]
        lines += ["@R14\n", "A=M\n", "0;JMP\n"]
        self.output_stream.writelines(lines)





