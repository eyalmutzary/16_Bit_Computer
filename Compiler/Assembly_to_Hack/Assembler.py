"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from .SymbolTable import SymbolTable
from .Parser import Parser
from .Code import Code

SYMBOL_BASE_INDEX = 16

def number_to_binary(num):
    binary_code = ""
    for i in range(15,-1,-1):
        if 2**i <= num:
            binary_code += "1"
            num -= 2**i
        else:
            binary_code += "0"
    return binary_code


def print_lst(lst):
    for code in lst:
        print(code)


def get_binary_from_A_cmd(parser: Parser, symbol_table: SymbolTable, curr_symbol_index) -> str:
    symbol = parser.symbol()
    if symbol.isnumeric():
        return number_to_binary(int(symbol))
    elif not symbol_table.contains(symbol):
        symbol_table.add_entry(symbol, curr_symbol_index[0])
        binary_num = number_to_binary(curr_symbol_index[0])
        curr_symbol_index[0] += 1
        return binary_num
    else:
        address = symbol_table.get_address(symbol)
        return number_to_binary(address)


def first_pass(parser: Parser, symbol_table: SymbolTable, curr_symbol_index) -> None:
    row_counter = 0
    while parser.has_more_commands():
        if parser.command_type() == "L_COMMAND" \
                and not symbol_table.contains(parser.symbol()):
            # symbol_table.add_entry(parser.symbol(), curr_symbol_index[0])
            symbol_table.add_entry(parser.symbol(), row_counter)
            # curr_symbol_index[0] += 1
        elif parser.command_type() != None:
            row_counter += 1
        parser.advance()



def second_pass(parser: Parser, symbol_table: SymbolTable, curr_symbol_index, output_lst) -> None:
    while parser.has_more_commands():
        binary_st = ""
        if parser.command_type() == "A_COMMAND":
            binary_st = get_binary_from_A_cmd(parser, symbol_table, curr_symbol_index)
        elif parser.command_type() == "C_COMMAND":
            dest, comp, jump = parser.dest(), parser.comp(), parser.jump()
            if comp.__contains__("<<") or comp.__contains__(">>"):
                start = "101"
            else:
                start = "111"
            binary_st = start + Code.comp(comp) + Code.dest(dest) + Code.jump(jump)
        if binary_st != "":
            output_lst.append(binary_st)
        parser.advance()




def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    parser = Parser(input_file)
    symbol_table = SymbolTable()
    curr_symbol_index = [SYMBOL_BASE_INDEX]

    first_pass(parser, symbol_table, curr_symbol_index)
    parser.reset_parser()

    output_lst = []
    second_pass(parser, symbol_table, curr_symbol_index, output_lst)

    for line in output_lst:
        output_file.write(line + "\n") # output_file.writelines(output_file_lines)
    # print_lst(output_lst)





def assemble_all_files_in_path(path: str) -> None:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if os.path.isdir(path):
        files_to_assemble = [
            os.path.join(path, filename)
            for filename in os.listdir(path)]
    else:
        files_to_assemble = [path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
