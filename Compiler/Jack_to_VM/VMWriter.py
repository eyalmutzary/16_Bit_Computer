"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class VMWriter:
    """
    Writes VM commands into a file. Encapsulates the VM command syntax.
    """
    segments_dict = {
        "CONST": "constant",
        "ARG": "argument",
        "LOCAL": "local",
        "STATIC": "static",
        "THIS": "this",
        "THAT": "that",
        "POINTER": "pointer",
        "TEMP": "temp"
    }

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Creates a new file and prepares it for writing VM commands."""
        self.output = output_stream
        #  TODO: need a close function? I don't think so.


    def write_push(self, segment: str, index: int) -> None:
        """Writes a VM push command.

        Args:
            segment (str): the segment to push to, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP"
            index (int): the index to push to.
        """
        text = "push " + VMWriter.segments_dict[segment] + " " + str(index) + "\n"
        if segment in ["CONST", "ARG",
                       "LOCAL", "STATIC", "THIS",
                       "THAT", "POINTER", "TEMP"]:
            self.output.write(text)
        else:
            print("Error write_push, got " + segment)


    def write_pop(self, segment: str, index: int) -> None:
        """Writes a VM pop command.

        Args:
            segment (str): the segment to pop from, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP".
            index (int): the index to pop from.
        """
        text = "pop " + VMWriter.segments_dict[segment] + " " + str(index) + "\n"
        if segment in ["CONST", "ARG",
                       "LOCAL", "STATIC", "THIS",
                       "THAT", "POINTER", "TEMP"]:
            self.output.write(text)
        else:
            print("Error write_pop, got " + segment)


    def write_arithmetic(self, command: str) -> None:
        """Writes a VM arithmetic command.

        Args:
            command (str): the command to write, can be "ADD", "SUB", "NEG", 
            "EQ", "GT", "LT", "AND", "OR", "NOT", "SHIFTLEFT", "SHIFTRIGHT".
        """
        if command in ["ADD", "SUB", "NEG",
                       "EQ", "GT", "LT", "AND", "OR",
                       "NOT", "SHIFTLEFT", "SHIFTRIGHT"]:
            self.output.write(command.lower() + "\n")
        else:
            print("Error write_arithmetic, got " + command)

    def write_label(self, label: str) -> None:
        """Writes a VM label command.

        Args:
            label (str): the label to write.
        """
        self.output.write("label " + label + "\n")


    def write_goto(self, label: str) -> None:
        """Writes a VM goto command.

        Args:
            label (str): the label to go to.
        """
        self.output.write("goto " + label + "\n")


    def write_if(self, label: str) -> None:
        """Writes a VM if-goto command.

        Args:
            label (str): the label to go to.
        """
        self.output.write("if-goto " + label + "\n")


    def write_call(self, name: str, n_args: int) -> None:
        """Writes a VM call command.

        Args:
            name (str): the name of the function to call.
            n_args (int): the number of arguments the function receives.
        """
        self.output.write("call " + name + " " + str(n_args) + "\n")


    def write_function(self, name: str, n_locals: int) -> None:
        """Writes a VM function command.

        Args:
            name (str): the name of the function.
            n_locals (int): the number of local variables the function uses.
        """
        self.output.write("function " + name + " " + str(n_locals) + "\n")



    def write_return(self) -> None:
        """Writes a VM return command."""
        self.output.write("return\n")

