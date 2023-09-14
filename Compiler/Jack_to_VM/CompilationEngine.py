"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from .JackTokenizer import JackTokenizer
from .SymbolTable import SymbolTable
from .VMWriter import VMWriter


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    kind_mapper_dict = {
        "FIELD": "THIS",  # for objects
        "VAR": "LOCAL",
        "STATIC": "STATIC",
        "ARG": "ARG",
    }

    unary_op_dict = {
        '^': 'SHIFTLEFT',
        '#': 'SHIFTRIGHT',
        '-': 'NEG',
        '~': 'NOT'
    }

    binary_op_dict = {
        '-': 'SUB',
        '+': 'ADD',
        '=': 'EQ',
        '|': 'OR',
        '>': 'GT',
        '<': 'LT',
        '&': 'AND',
        '&gt;': 'GT',
        '&lt;': 'LT',
        '&amp;': 'AND',
    }

    class_var_dec_list = ["static", "field"]
    subroutine_dec_list = ["constructor", "function", "method"]


    def __init__(self, input_stream: typing.TextIO, output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokens = JackTokenizer(input_stream)
        self.my_output = output_stream
        self.vm_writer = VMWriter(self.my_output)
        self.symbol_table = SymbolTable()

        self.fields_to_alloc = 0
        self.function_caller_name = ""

        self.subroutine_info = {
            "class": "",  # the name of the class that contains the subroutine
            "name": "",  # the name of the subroutine
            "kind": "",  # Could be: constructor, method, function, field or static.
            "type": "",  # could be void, int, char, boolean, className
            "args_counter": 0,  # how many args the subroutine has
            "var_counter": 0  # how many local variables in the subroutine
        }

        self.function_calls_stack = []  # used for situations like: a = func1(5, func2());

        # for generating unique labels:
        self.while_counter = 0
        self.if_counter = 0


        if self.tokens.token_type() == "KEYWORD" and self.tokens.keyword() == "CLASS":
            self.compile_class()


    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.fields_to_alloc = 0

        self.tokens.advance()  # 'class'
        self.subroutine_info["class"] = self.tokens.curr_token
        self.tokens.advance()  # className
        self.tokens.advance()  # '{'

        # Now could be either static and fields, or function and methods
        while self.tokens.curr_token != "}":
            self.subroutine_info["kind"] = self.tokens.curr_token
            if self.tokens.curr_token in CompilationEngine.class_var_dec_list:
                #  Case 1: "static", "field"
                self.compile_class_var_dec()
            elif self.tokens.curr_token in CompilationEngine.subroutine_dec_list:
                #  Case 2: "constructor", "function", "method"
                self.compile_subroutine()

        self.tokens.advance()  # '}'
        self.subroutine_info["kind"] = ""
        self.subroutine_info["class"] = ""


    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # ('static'|'field') type varName (',' varName)* ';'
        kind = self.tokens.curr_token  # could be static or field
        self.tokens.advance()
        type_of_var = self.tokens.curr_token  # could be int, char, boolean or className
        self.tokens.advance()

        while self.tokens.curr_token != ';':
            name = self.tokens.curr_token
            if self.symbol_table.curr_scope == None:  # No subroutine yet, means it's global variable
                self.symbol_table.define(name, type_of_var, kind.upper())
            else:
                self.symbol_table.curr_scope.define(name, type_of_var, kind.upper())
            if kind == "field":
                self.fields_to_alloc += 1
            self.tokens.advance()  # varName or ','
            if self.tokens.curr_token == ',':  # -> there are many variables
                self.tokens.advance()  # ','

        if self.tokens.curr_token == ';':
            self.tokens.advance()


    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # ('constructor' | 'function' | 'method') ('void' | type)
        # subroutineName '(' parameterList ')' subroutineBody
        self.symbol_table.start_subroutine()

        self.tokens.advance()  # 'constructor' | 'function' | 'method'
        self.tokens.advance()  # 'void' | type
        self.subroutine_info["name"] = self.tokens.curr_token
        self.tokens.advance()  # subroutineName

        self.subroutine_info["args_counter"] = 0
        if self.subroutine_info["kind"] == "method":
            self.symbol_table.curr_scope.define("this", self.subroutine_info["class"], "ARG")
            self.subroutine_info["args_counter"] += 1

        self.tokens.advance()  # '('
        self.subroutine_info["args_counter"] += self.compile_parameter_list()
        self.tokens.advance()  # ')'
        self.tokens.advance()  # '{'

        self.compile_subroutine_body()
        self.subroutine_info["name"] = ""
        self.subroutine_info["var_counter"] = 0



    def compile_parameter_list(self) -> int:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        args_counter = 0
        while self.tokens.curr_token != ')':
            type = self.tokens.curr_token
            self.tokens.advance()  # type
            name = self.tokens.curr_token
            self.tokens.advance()  # argName
            self.symbol_table.curr_scope.define(name, type, "ARG")
            args_counter += 1
            if self.tokens.curr_token == ',':  # => there are more params
                self.tokens.advance()  # argName

        return args_counter
        # finishes with ')' as the current token


    def compile_subroutine_body(self) -> None:
        while self.tokens.curr_token == "var":
            self.compile_var_dec()
        self.vm_writer.write_function(self.subroutine_info["class"] + "." + self.subroutine_info["name"], self.subroutine_info["var_counter"])

        if self.subroutine_info["kind"] == "constructor":  # from the video 11.6 15:30
            self.vm_writer.write_push("CONST", self.fields_to_alloc)
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("POINTER", 0)  # anchor "this" (segment) at thebase address
        elif self.subroutine_info["kind"] == "method":
            self.vm_writer.write_push("ARG", 0)
            self.vm_writer.write_pop("POINTER", 0)

        self.compile_statements()


    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # 'var' type varName (',' varName)* ';'
        self.tokens.advance()  # 'var'
        type_of_var = self.tokens.curr_token
        self.tokens.advance()  # type

        while self.tokens.curr_token != ';':
            self.subroutine_info["var_counter"] += 1
            var_name = self.tokens.curr_token
            self.symbol_table.curr_scope.define(var_name, type_of_var, "VAR")
            self.tokens.advance()  # varName
            if self.tokens.curr_token == ",":
                self.tokens.advance() # ','

        self.tokens.advance()  # ';'


    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        while self.tokens.curr_token != "}":
            token = self.tokens.curr_token
            if token == "do":
                self.compile_do()
            elif token == "let":
                self.compile_let()
            elif token == "while":
                self.compile_while()
            elif token == "return":
                self.compile_return()
            elif token == "if":
                self.compile_if()

        self.tokens.advance()  # '}'


    def compile_subroutine_call(self) -> None:
        # subroutineCall template:
        # Case 1: subroutineName '('expressionList')'
        # Case 2: (className|varName)'.'subroutineName '(' expressionList ')'

        # Case 1:
        next_token = self.tokens.tokens_list[self.tokens.curr_token_index + 1]
        args_counter = 0

        if next_token == '(': # '('expressionList')'
            subroutine_name = self.tokens.curr_token
            self.function_caller_name = self.subroutine_info["class"] + '.' + subroutine_name
            args_counter += 1
            self.vm_writer.write_push("POINTER", 0)
            self.tokens.advance()  # subroutineName

        # Case 2:
        else:  # (className|varName) '.' subroutineName '(' expressionList ')'
            var_name = self.tokens.curr_token
            # Case: Check if the caller is an object, which means the callee is a method
            if var_name in self.symbol_table.curr_scope.names \
                    and self.symbol_table.curr_scope.names[var_name][1] not in ['int', 'boolean', 'char']:
                # in case it is a call to method, needs an extra arg for this.
                args_counter += 1
                self.vm_writer.write_push("LOCAL", self.symbol_table.curr_scope.names[var_name][0])

            # while self.tokens.tokens_list[self.tokens.curr_token_index+1] == ".":
            if var_name in self.symbol_table.curr_scope.names:
                self.function_caller_name += self.symbol_table.curr_scope.names[var_name][1] + "."
            else:
                var_type = self.symbol_table.type_of(var_name)
                if var_type != None:  # the variable is an object
                    self.vm_writer.write_push("THIS", self.symbol_table.names[var_name][0])
                    args_counter += 1
                    self.function_caller_name += var_type + "."
                else:
                    self.function_caller_name += var_name + "."
            self.tokens.advance()  # (className|varName)
            self.tokens.advance()  # '.'

            subroutine_name = self.tokens.curr_token
            self.tokens.advance()
            self.function_caller_name += subroutine_name

        self.tokens.advance() #  '('
        self.function_calls_stack.append(self.function_caller_name)
        self.function_caller_name = ""
        args_counter += self.compile_expression_list()
        self.tokens.advance() #  ')'

        self.vm_writer.write_call(self.function_calls_stack[-1], args_counter)

        self.function_calls_stack = self.function_calls_stack[:-1]
        self.function_caller_name = ""  # resets the subroutine call


    def compile_do(self) -> None:
        """Compiles a do statement."""
        # 'do' subroutineCall ';'

        self.tokens.advance()  # 'do'
        self.compile_subroutine_call()
        # do is a void function, so we need to get rid of the last stack value
        # by "pop temp 0"
        self.vm_writer.write_pop("TEMP", 0)
        self.tokens.advance()  # ';'


    def compile_let(self) -> None:
        """Compiles a let statement."""
        # 'let' varName ('[' expression ']')? '=' expression ';'
        var_info = {"name": "",
                    "kind": "",
                    "index": ""}
        self.tokens.advance()  # 'let'
        var_info["name"] = self.tokens.curr_token
        self.tokens.advance()  # 'varName'

        # now the variable could be inside the scope or outside.
        if self.symbol_table.curr_scope.kind_of(var_info["name"]) != None: # => in current scope
            var_info["kind"] = self.symbol_table.curr_scope.names[var_info["name"]][2]
            var_info["index"] = self.symbol_table.curr_scope.names[var_info["name"]][0]
        else:
            var_info["kind"] = self.symbol_table.names[var_info["name"]][2]
            var_info["index"] = self.symbol_table.names[var_info["name"]][0]

        var_info["kind"] = CompilationEngine.kind_mapper_dict[var_info["kind"]]
        # Case: Dealing with an array
        # TODO: it's a little different from the template, make sure it's right
        if self.tokens.curr_token == '[':
            self.tokens.advance()  # '['
            self.compile_expression()  # expression1
            self.tokens.advance()  # ']'
            # now, from the video 11.8 , 21:30
            self.vm_writer.write_push(var_info["kind"], var_info["index"])  # push arr
            self.vm_writer.write_arithmetic('ADD')
            self.tokens.advance()  # '='
            self.compile_expression()  # expression2
            self.tokens.advance()  # get to new line
            self.vm_writer.write_pop('TEMP', 0)
            self.vm_writer.write_pop('POINTER', 1)
            self.vm_writer.write_push('TEMP', 0)
            self.vm_writer.write_pop('THAT', 0)
            return

        self.tokens.advance()  # '='

        self.compile_expression()

        self.vm_writer.write_pop(var_info["kind"], var_info["index"])
        self.tokens.advance() # ';'


    def compile_while(self) -> None:
        """Compiles a while statement."""
        # 'while' '(' expression ') '{' statements '}'
        self.while_counter += 1
        start_label = self.subroutine_info["class"] + "." + self.subroutine_info["name"] + ".START_WHILE" + str(self.while_counter)
        end_label = self.subroutine_info["class"] + "." + self.subroutine_info["name"] + ".END_WHILE" + str(self.while_counter)

        self.tokens.advance()  # 'while'
        self.tokens.advance()  # '('

        # follow the template from the video
        self.vm_writer.write_label(start_label)
        self.compile_expression()
        self.vm_writer.write_arithmetic("NOT")
        self.vm_writer.write_if(end_label)  # if while statement is false, leave loop

        # else, enter loop:
        self.tokens.advance()  # ')'
        self.tokens.advance()  # '{'

        self.compile_statements()

        self.vm_writer.write_goto(start_label)  # after finish loop, go back to start
        self.vm_writer.write_label(end_label)



    def compile_return(self) -> None:
        """Compiles a return statement."""
        # 'return' expression? ';'
        self.tokens.advance()  # 'return'

        if self.tokens.curr_token != ';':
            self.compile_expression()
        else: # -> no expression, there is no return value -> return default 0
            self.vm_writer.write_push("CONST", 0)  # needed because void

        self.vm_writer.write_return()
        self.tokens.advance()  # ';'


    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        self.if_counter += 1
        # L2 is if_label , L1 is else_label  (according to the video)
        choose_if_label = self.subroutine_info["class"] + "." + self.subroutine_info["name"] + ".CHOSE_IF" + str(self.if_counter)
        choose_else_label = self.subroutine_info["class"] + "." + self.subroutine_info["name"] + ".CHOSE_ELSE" + str(self.if_counter)

        self.tokens.advance()  # 'if'
        self.tokens.advance()  # '('

        # follow the template in the video:
        self.compile_expression()
        self.vm_writer.write_arithmetic("NOT")
        self.vm_writer.write_if(choose_else_label)  # L1

        self.tokens.advance()  # ')'
        self.tokens.advance()  # '{'

        self.compile_statements()
        self.vm_writer.write_goto(choose_if_label)  # L2
        self.vm_writer.write_label(choose_else_label)  # L1


        if self.tokens.curr_token == "else":
            self.tokens.advance()  # 'else'
            self.tokens.advance()  # '{'
            self.compile_statements()

        self.vm_writer.write_label(choose_if_label)  # L2


    def compile_expression(self) -> None:
        """Compiles an expression."""
        # template: term (op temp)*
        # all expressions comes after: '(', '[', '=', ','
        # all expressions ends with: ')', ']', ';', ','

        # Case 1: expression is empty
        if self.tokens.curr_token in [')', ']', ';', ',']:
            return

        self.compile_term()

        # now could be op or: ')', ']', ';', ','
        # Case 2: expression has one or many ops
        possible_binary_ops = ['-', '+', '=', '|', '>', '<', '&', '&gt;', '&lt;', '&amp;', '*', '/']
        while self.tokens.curr_token in possible_binary_ops:
            current_op = self.tokens.curr_token
            self.tokens.advance()
            self.compile_term()
            if current_op in CompilationEngine.binary_op_dict:
                self.vm_writer.write_arithmetic(CompilationEngine.binary_op_dict[current_op])
            elif current_op == '*':
                self.vm_writer.write_call("Math.multiply", 2)
            elif current_op == '/':
                self.vm_writer.write_call("Math.divide", 2)


    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Note: In case where exp is of the form: exp1 op exp2, we handle outside
        #       in the method compile_expression
        if self.tokens.curr_token == '(':
            self.tokens.advance()
            self.compile_expression()
            self.tokens.advance()
            return

        next_token = self.tokens.tokens_list[self.tokens.curr_token_index+1]
        if self.tokens.curr_token != ')':
            # Case 1: exp is "func(exp1, exp2...)"
            if self.tokens.curr_token[0].isalpha() and next_token == '(':
                func_name = self.tokens.curr_token
                self.tokens.advance()  # funcName
                self.tokens.advance()  # '('
                args_counter = 0
                while self.tokens.curr_token != ')':
                    args_counter += 1
                    self.compile_expression()
                self.tokens.advance()  # ')'
                self.vm_writer.write_call(self.function_caller_name + func_name, args_counter)

            # Case 2: exp is "op exp"
            elif self.tokens.curr_token in CompilationEngine.unary_op_dict:
                unary_op = self.tokens.curr_token
                self.tokens.advance()  # unaryOp
                self.compile_term()
                self.vm_writer.write_arithmetic(CompilationEngine.unary_op_dict[unary_op])

            # Case 3: exp is number
            elif self.tokens.curr_token.isnumeric():
                num = int(self.tokens.curr_token)
                self.vm_writer.write_push("CONST", num)
                self.tokens.advance()
            # Case 4: exp is a true or false
            elif self.tokens.curr_token in ["true", "false", "null"]:
                self.vm_writer.write_push("CONST", 0)
                if self.tokens.curr_token == "true":
                    self.vm_writer.write_arithmetic("NOT")
                # else - set default as 0
                self.tokens.advance()
            # Case 6: exp is a const string
            elif self.tokens.token_type() == 'STRING_CONST':
                string = self.tokens.curr_token[1:-1]
                self.vm_writer.write_push('CONST', len(string))
                self.vm_writer.write_call('String.new', 1)
                for char in string:
                    self.vm_writer.write_push('CONST', ord(char))
                    self.vm_writer.write_call('String.appendChar', 2)
                self.tokens.advance()
            # Case 7: exp is an array - arrName[i]
            elif next_token == '[':
                # Now follow the slide in video 9
                if self.tokens.curr_token in self.symbol_table.curr_scope.names:  # arr instance is in current scope
                    arr_kind = self.symbol_table.curr_scope.names[self.tokens.curr_token][2]
                    arr_index = self.symbol_table.curr_scope.names[self.tokens.curr_token][0]
                else:  # arr instance is in outer scope
                    arr_kind = self.symbol_table.names[self.tokens.curr_token][2]
                    arr_index = self.symbol_table.names[self.tokens.curr_token][0]
                arr_kind = CompilationEngine.kind_mapper_dict[arr_kind]
                self.tokens.advance()  # arrName
                self.tokens.advance()  # '['
                self.compile_expression()  # push i (i is the value in a[i])
                self.tokens.advance()  # ']'
                self.vm_writer.write_push(arr_kind, arr_index)  # push arr
                self.vm_writer.write_arithmetic('ADD')  # adding the addresses to be on the right index
                self.vm_writer.write_pop('POINTER', 1)  # now pointer 1 is an entry to (arr + i)
                self.vm_writer.write_push('THAT', 0)  # THAT because it is an array. TODO: The video says it should be this, what is right?

            # Case 5: exp is variable
            elif self.tokens.curr_token[0].isalpha() or self.tokens.curr_token.startswith('_'):
                if next_token == ".":  # Case 5.1: the var is a caller - caller.subroutine(...
                    self.compile_subroutine_call()

                else:  # just a simple variable
                    if self.tokens.curr_token == "this":
                        self.vm_writer.write_push("POINTER", 0)
                        self.tokens.advance()  # 'this'
                    else:
                        if self.tokens.curr_token in self.symbol_table.curr_scope.names:  # var in current scope
                            var_kind = self.symbol_table.curr_scope.names[self.tokens.curr_token][2]
                            self.vm_writer.write_push(CompilationEngine.kind_mapper_dict[var_kind], self.symbol_table.curr_scope.names[self.tokens.curr_token][0])
                        else:  # var in outer scope
                            var_kind = self.symbol_table.names[self.tokens.curr_token][2]
                            self.vm_writer.write_push(CompilationEngine.kind_mapper_dict[var_kind], self.symbol_table.names[self.tokens.curr_token][0])
                        self.tokens.advance()


    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        args_counter = 0
        if self.tokens.curr_token in [')', ']']:  # => list is empty
            return 0

        self.compile_expression()  # has at least one expression
        args_counter += 1

        while self.tokens.curr_token not in [')',']']:
            self.tokens.advance()  # ','
            args_counter += 1
            self.compile_expression()
        return args_counter
