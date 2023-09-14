"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads an assembly language 
    command, parses it, and provides convenient access to the commands 
    components (fields and symbols). In addition, removes all white space and 
    comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is:
        self.__input_lines = input_file.read().splitlines()
        self.index = 0  # initially there shouldn't be a current instruction


    def get_stripped_command(self) -> str:
        command = self.__input_lines[self.index]
        if command.__contains__("//"):
            command = command[:command.index("/")]
        return "".join(command.split())


    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return len(self.__input_lines) > self.index


    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        if self.has_more_commands():
            self.index += 1

    def reset_parser(self):
        self.index = 0

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        command = self.get_stripped_command()
        if command != "":
            if command[0] == '@':
                return "A_COMMAND"
            elif command[0] == '(' and not command.__contains__("//"):
                return "L_COMMAND"
            elif (command.__contains__(';') or command.__contains__('=')) and not command.__contains__("//"):
                return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        command = self.get_stripped_command()
        if self.command_type() == "A_COMMAND":
            return command[1:]
        elif self.command_type() == "L_COMMAND":
            return command[1:-1]



    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        command = self.get_stripped_command()
        if self.command_type() == "C_COMMAND" and command.__contains__('='):
            index_of_sign = command.index('=')
            return command[0:index_of_sign]


    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        command = self.get_stripped_command()
        if self.command_type() == "C_COMMAND":
            if command.__contains__('='):
                if command.__contains__(';'):
                    return command[command.index('=')+1: command.index(';')]
                else:
                    return command[command.index('=')+1:]
            else:
                if command.__contains__(';'):
                    return command[: command.index(';')]

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        command = self.get_stripped_command()
        if self.command_type() == "C_COMMAND" and command.__contains__(';'):
            return command[command.index(';')+1:]
