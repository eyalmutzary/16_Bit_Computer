"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    """

    comments = ["//", "/*", "**/", "*/"]

    keyword_dict = {'class': "CLASS", 'constructor': "CONSTRUCTOR",
                    'function': "FUNCTION", 'method': "METHOD",
                    'field': "FIELD", 'static': "STATIC", 'var': "VAR",
                    'int': "INT", 'char': "CHAR", 'boolean': "BOOLEAN", 'void': "VOID",
                    'true': "TRUE", 'false': "FALSE", 'null': "NULL", 'this': "THIS",
                    'let': "LET", 'do': "DO", 'if': "IF", 'else': "ELSE",
                    'while': "WHILE", 'return': "RETURN"}

    symbol_list = ['{', '}', '(', ')', '[', ']',
                   '.', ',', ';',
                   '+', '-', '*', '/', '^', '#',
                   '&', '|', '<', '>', '=', '~']

    special_symbol_dict = {'"': '&quot;', '<': '&lt;', '>': '&gt;', '&': '&amp;'}

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is:
        input_lines = input_stream.read().splitlines()
        self.curr_token_index = 0
        self.curr_line = 0
        self.remove_spare_whitespaces(input_lines)
        self.remove_comments(input_lines)
        self.tokens_list = []
        for line in input_lines:
            if line == '':
                continue
            curr_token = ""
            letter_index = 0
            is_open_quotation = False

            for letter in line: # scans every letter in the line
                letter_index += 1
                if letter == "\"": # Case 1: const string - "~~~"
                    is_open_quotation = not is_open_quotation
                    curr_token += letter
                    continue
                if is_open_quotation:
                    curr_token += letter
                    if letter == "\"":
                        self.tokens_list.append(curr_token)
                        curr_token = ""
                        is_open_quotation = False

                else:
                    if letter in JackTokenizer.symbol_list: # Case 2: Letter is symbol
                        if curr_token == "": # if is only symbol
                            self.tokens_list.append(letter)
                        else: # if connected to other phrase
                            self.tokens_list.append(curr_token)
                            self.tokens_list.append(letter)
                            curr_token = ""
                    else:
                        if letter == " ": # Case 3: letter is whitespace
                            if curr_token != "": # if the token is not empty
                                self.tokens_list.append(curr_token)
                            curr_token = ""
                        else:
                            curr_token += letter # Case 4: letter is just another letter
                            # if token is keyword:
                            if curr_token in JackTokenizer.keyword_dict \
                                    and (len(self.tokens_list) == 0 or self.tokens_list[-1] != '.')\
                                    and (len(self.tokens_list) > letter_index+1 or not line[letter_index+1].isnumeric()):  # specific case, if there is a variable or function that starts with keyword
                                # print(str(len(self.tokens_list)) + " AND " + str(letter_index+1))
                                if not (len(line) > letter_index and line[letter_index].isalpha()):
                                    self.tokens_list.append(curr_token) # adds and reset
                                    curr_token = ""
                    if letter_index == len(line) and curr_token != "": # Case 5: end of line
                        self.tokens_list.append(curr_token)
                        curr_token = ""
        self.curr_token = self.tokens_list[self.curr_token_index]


    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.curr_token_index < len(self.tokens_list)-1

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        # Your code goes here!
        if self.has_more_tokens():
            self.curr_token_index += 1
        self.curr_token = self.tokens_list[self.curr_token_index]

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Your code goes here!
        token = self.tokens_list[self.curr_token_index]
        if token in JackTokenizer.keyword_dict:
            return "KEYWORD"
        elif token in JackTokenizer.symbol_list:
            return "SYMBOL"
        elif token.startswith("\"") and token.endswith("\""):
            return "STRING_CONST"
        elif token.isnumeric():
            return "INT_CONST"
        else:
            return "IDENTIFIER"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        if self.token_type() == "KEYWORD":
            token = self.tokens_list[self.curr_token_index]
            return JackTokenizer.keyword_dict[token]

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        # Your code goes here!
        if self.token_type() == "SYMBOL":
            token = self.tokens_list[self.curr_token_index]
            if token in JackTokenizer.special_symbol_dict:
                return JackTokenizer.special_symbol_dict[token]
            return token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        if self.token_type() == "IDENTIFIER":
            token = self.tokens_list[self.curr_token_index]
            return token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        if self.token_type() == "INT_CONST":
            token = self.tokens_list[self.curr_token_index]
            return int(token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        if self.token_type() == "STRING_CONST":
            token = self.tokens_list[self.curr_token_index]
            return token

    def remove_comments(self, code : typing.List) -> None:
        multiline_comment = False
        for line_index in range(len(code)):
            line = code[line_index]

            const_string_indexes = []  # Private case: comment characters inside a string
            if not multiline_comment:
                is_string = False
                letter_index = 0
                for letter in line:
                    if letter == "\"":
                        is_string = not is_string
                    if is_string:
                        const_string_indexes.append(letter_index)
                    letter_index += 1

            if multiline_comment:
                if "*/" not in line:
                    line = ""
                else:
                    line = line[line.index("*/")+2:]
                    multiline_comment = False

            # private case to check if /* in a string, and there are also other /* outside string
            slash_star_indexes = []
            for letter_ind in range(len(line)-1):
                if (line[letter_ind] + line[letter_ind+1]) == '/*':
                    slash_star_indexes.append(letter_ind)

            for slash_star in slash_star_indexes:
                if slash_star not in const_string_indexes:
                    if "*/" in line:
                        line = line[:slash_star] + line[line.index('*/')+2:]
                    else:
                        multiline_comment = True
                        line = line[:line.index('/*')]

            # private case to check if // in a string, and there are also other // outside string
            slash_slash_indexes = []
            for letter_ind in range(len(line)-1):
                if (line[letter_ind] + line[letter_ind+1]) == '//':
                    slash_slash_indexes.append(letter_ind)

            for slash_slash in slash_slash_indexes:
                if slash_slash not in const_string_indexes:
                    line = line[:slash_slash]

            line = line.strip()
            code[line_index] = line

    def remove_spare_whitespaces(self, code : typing.List) -> None:
        for line_i in range(len(code)):
            code[line_i] = " ".join(code[line_i].split())
