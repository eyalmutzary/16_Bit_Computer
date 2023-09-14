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
from .Parser import Parser
from .CodeWriter import CodeWriter


def translate_file(
        input_file: typing.TextIO, output_file: typing.TextIO,
        bootstrap: bool) -> None:
    """Translates a single file.

    Args:
        input_file (typing.TextIO): the file to translate.
        output_file (typing.TextIO): writes all output to this file.
        bootstrap (bool): if this is True, the current file is the 
            first file we are translating.
    """
    input_filename, input_extension = os.path.splitext(os.path.basename(
        input_file.name))
    fname = input_filename.split('\\')[-1:][0] + input_extension
    parser = Parser(input_file)
    code_writer = CodeWriter(output_file)
    if bootstrap:
        code_writer.write_init()
    code_writer.set_file_name(fname)

    while parser.has_more_commands():
        cmd = parser.get_stripped_command()
        if parser.command_type() == "C_ARITHMETIC":
            code_writer.write_arithmetic(cmd)
        elif parser.command_type() in ["C_PUSH", "C_POP"]:
            segment = parser.arg1()
            index = parser.arg2() # % 32767
            code_writer.write_push_pop(parser.command_type(), segment, index)
        elif parser.command_type() == "C_LABEL":
            code_writer.write_label(parser.arg1())
        elif parser.command_type() == "C_GOTO":
            code_writer.write_goto(parser.arg1())
        elif parser.command_type() == "C_IF":
            code_writer.write_if(parser.arg1())
        elif parser.command_type() == "C_FUNCTION":
            code_writer.write_function(parser.arg1(), parser.arg2())
        elif parser.command_type() == "C_RETURN":
            code_writer.write_return()
        elif parser.command_type() == "C_CALL":
            code_writer.write_call(parser.arg1(), parser.arg2())
        parser.advance()


def translate_all_files_in_path(path: str) -> None:
    # Parses the input path and calls translate_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    # if not len(sys.argv) == 2:
    #     sys.exit("Invalid usage, please use: VMtranslator <input path>")
    # argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(path):
        files_to_translate = [
            os.path.join(path, filename)
            for filename in os.listdir(path)]
        output_path = os.path.join(path, os.path.basename(
            path))
    else:
        files_to_translate = [path]
        output_path, extension = os.path.splitext(path)
    output_path += ".asm"
    bootstrap = True
    with open(output_path, 'w') as output_file:
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file, bootstrap)
            bootstrap = False
