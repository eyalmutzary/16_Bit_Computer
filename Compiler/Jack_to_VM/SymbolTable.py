"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""

        self.vars = {}  # The tables is of the form: { index: (name, type) }
        self.args = {}
        self.fields = {}
        self.statics = {}
        self.names = {}  #  used in kind_of method
                         #  the from is: { name: (index, type, kind) }
        self.curr_scope = None  # used to reach the table's current scope from outside

        # self.objects = {}

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.curr_scope = SymbolTable()  # TODO: Correct way?


    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier. can be:
            int, string, boolean, className.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if kind == "STATIC":
            id_index = len(self.statics)
            self.statics[id_index] = (name, type)
        elif kind == "FIELD":
            id_index = len(self.fields)
            self.fields[id_index] = (name, type)
        elif kind == "ARG":
            id_index = len(self.args)
            self.args[id_index] = (name, type)
        elif kind == "VAR":
            id_index = len(self.vars)
            self.vars[id_index] = (name, type)
        else:
            id_index = 0
            print("Wrong kind in define function")
        self.names[name] = (id_index, type, kind)




    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        if kind == "STATIC":
            return len(self.statics)
        elif kind == "FIELD":
            return len(self.fields)
        elif kind == "ARG":
            return len(self.args)
        elif kind == "VAR":
            return len(self.vars)
        return 0  # in case of Wrong input

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if name in self.names:
            return self.names[name][2]
        else:
            return None


    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if name in self.names:
            return self.names[name][1]
        else:
            return None


    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.names:
            return self.names[name][0]
