import os
from BasicGates import binary_to_decimal
from Computer import Computer
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
    path = os.path.abspath("../Compiler/Tests/Square/Square.hack")
    instructions = load_instructions(path)
    computer = Computer()
    computer.load_instructions(process_instructions(instructions))
    computer.run()
