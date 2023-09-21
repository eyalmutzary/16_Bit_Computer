import os
from BasicGates import binary_to_decimal
from Computer import Computer
from Compiler.Compiler import main as compile_jack_to_hack
def process_instructions(instructions: list) -> list:
    processed_instructions = []
    for i in range(len(instructions)):
        processed_instructions.append(binary_to_decimal(instructions[i].replace('\n', '')))
    return processed_instructions


def load_instructions(path: str) -> list:
    with open(path, 'r') as file:
        instructions = file.readlines()
    return instructions


if __name__ == '__main__':
    jack_dir_path = os.path.abspath("../OperationSystem")
    compile_jack_to_hack(jack_dir_path)
    hack_code_path = os.path.abspath("../OperationSystem/OperationSystem.hack")
    # # hack_code_path = os.path.abspath("../Compiler/Tests/Pong/Pong.hack")
    instructions = load_instructions(hack_code_path)
    computer = Computer()
    computer.load_instructions(process_instructions(instructions))
    computer.run()
    print(computer.get_screen())
