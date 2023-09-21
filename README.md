# 16 Bit Computer

Welcome to the 16 Bit Computer project! This is a complete computer system designed and built from scratch, featuring a custom programming language, a compiler, hardware components, an operating system, and a user-friendly UI. Dive into the world of computer architecture and explore the unique aspects of this project.

![16 Bit Computer](https://github.com/eyalmutzary/16_Bit_Computer/blob/master/Figma_UI_Design.png)


## Table of Contents
- [Introduction](#introduction)
- [Compiler](#compiler)
- [Hardware](#hardware)
- [Operating System](#operating-system)
- [User Interface](#user-interface)
- [Getting Started](#getting-started)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The 16 Bit Computer project is a labor of love for computer enthusiasts who want to explore the inner workings of a computer system. This project is unique in that it not only simulates a 16-bit computer but also introduces a custom programming language called "Jack" for software development.

## Features

### Compiler
- A complete [compiler](https://github.com/eyalmutzary/16_Bit_Computer/tree/master/Compiler) that translates high-level Jack code into virtual machine code, assembly, and binary code (Hack).
- Jack is a custom-made programming language, providing a unique experience for developers.

### Hardware
- A [hardware](https://github.com/eyalmutzary/16_Bit_Computer/tree/master/Hardware) simulation written in Python, meticulously crafted from basic logic gates (e.g., NAND, AND, OR, XOR etc) to complex components like ALU, CPU, and Memory.
- The hardware closely mimics real-world logic, offering a deep understanding of computer architecture.
- Note: most of the HW logic could be written easily with python, but I tried to keep the HW logic as much as possible.

### Operating System
- A fully functional [operating system](https://github.com/eyalmutzary/16_Bit_Computer/tree/master/OperationSystem) designed to run on the 16 Bit Computer.
- Includes features like memory management, mathematical operations, visual screen management, and basic data structures like arrays.
- All written in Jack language, tailored to the compiler and HW.

### User Interface (WIP)
- A user-friendly UI designed to interact with the computer system.
- Users can write and execute Jack scripts by using a backend server that runs the machine, providing a seamless experience for creating and running code.
- Main features are creating multiple files and classes, and streaming the computer's screen live.
- The UI design is available in [Figma](https://www.figma.com/file/NSU8BFW8Woc2U61dIa3U67/16Bit-Computer?type=design&node-id=0%3A1&mode=design&t=nSaanXRMDfqbVCq0-1) for preview and customization.

## Getting Started

To get started with the 16 Bit Computer project, follow these steps:

1. Clone the repository to your local machine
2. Create and code Main.jack file in the OperationSystem folder (temporary solution). You could use VSCode Jack extentions for word marking.
3. Run main.py
Note: currently, since the UI is still under development, you will be able just to see the memory screenshot after the script runs.

## Contributing
The whole design of the HW, compiler and OS was inspired from the course nand2tetris made by Noam Nisan and Shimon Schocken. 

## Contact
Feel free to reach out to us with any questions or suggestions.
