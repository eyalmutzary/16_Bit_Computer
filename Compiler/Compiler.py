import os
import sys
from .Jack_to_VM.JackCompiler import compile_all_files_in_path as compile_jack_to_vm
# from .Else11.JackCompiler import compile_all_files_in_path as compile_jack_to_vm
# from .Else8.VMTranslator import translate_all_files_in_path as translate_vm_to_asm
# from .Else6.Assembler import assemble_all_files_in_path as assemble_asm_to_hack
from .VM_to_Assembly.VMTranslator import translate_all_files_in_path as translate_vm_to_asm
from .Assembly_to_Hack.Assembler import assemble_all_files_in_path as assemble_asm_to_hack
def main(path: str) -> None:
    argument_path = os.path.abspath(path)
    compile_jack_to_vm(argument_path)
    translate_vm_to_asm(argument_path)
    assemble_asm_to_hack(argument_path)
    print("Compilation completed successfully!")
