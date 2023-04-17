from string_with_arrows import *

import string

##################################################
# DIGITS
##################################################

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

##################################################
# ERRORS
##################################################

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result = f'{self.error_name} : {self.details}'
        result += f' File {self.pos_start.file_name}, line {self.pos_start.line + 1}'
        result += '\n\n' + string_with_arrows(self.pos_start.file_txt, self.pos_start, self.pos_end)
        return result
    

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class ExpectedCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Expected Character', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)
##################################################
# POSITION
##################################################

class Position:
    def __init__(self, index, line, col, file_name, file_txt):
        self.index = index
        self.line = line
        self.col = col
        self.file_name= file_name
        self.file_txt = file_txt

    def advance(self, current_char=None):
        self.index += 1
        self.col += 1

        if current_char == '\n':
            self.line += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.index, self.line, self.col, self.file_name, self.file_txt)

##################################################
# TOKEN
##################################################

TOKEN_INT = 'TOKEN_INT'
TOKEN_FLOAT = 'TOKEN_FLOAT'
TOKEN_IDENTIFIER = 'TOKEN_IDENTIFIER'
TOKEN_KEYWORD = 'TOKEN_KEYWORD'
TOKEN_PLUS = 'TOKEN_PLUS'
TOKEN_MINUS = 'TOKEN_MINUS'
TOKEN_MUL = 'TOKEN_MUL'
TOKEN_DIV = 'TOKEN_DIV'
TOKEN_EQ = 'TOKEN_EQ'
TOKEN_LPAREN = 'TOKEN_LPAREN'
TOKEN_RPAREN = 'TOKEN_RPAREN'
TOKEN_EE = 'TOKEN_EE'
TOKEN_NE = 'TOKEN_NE'
TOKEN_LT = 'TOKEN_LT'
TOKEN_GT = 'TOKEN_GT'
TOKEN_LTE = 'TOKEN_LTE'
TOKEN_GTE = 'TOKEN_GTE'
TOKEN_LCURL = 'TOKEN_LCURL'
TOKEN_RCURL = 'TOKEN_RCURL'
TOKEN_NOT = 'TOKEN_NOT'
TOKEN_AND = 'TOKEN_AND'
TOKEN_OR = 'TOKEN_OR'
TOKEN_EOF = 'TOKEN_EOF'

KEYWORDS = [
    'let',
    '&&',
    '||',
    '!'
    'if',
    'else'
]

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        
        if pos_end:
            self.pos_end = pos_end
    
    def matches(self, type_, value):
        return self.type == type_ and self.value == value
		
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return self.type

##################################################
# LEXER
##################################################

class Lexer:
    def __init__(self, file_name, text):
        self.text = text
        self.pos = Position(-1, 0, -1, file_name, text)
        self.current_char = None
        self.advance()
      
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char == '+':
                tokens.append(Token(TOKEN_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TOKEN_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TOKEN_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TOKEN_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TOKEN_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TOKEN_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(TOKEN_LCURL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(TOKEN_RCURL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '!':
                token, error = self.make_not_equals()
                if error: return [], error
                tokens.append(token)
            elif self.current_char == '&':
                token, error = self.make_and()
                if error: return [], error
                tokens.append(token)
            elif self.current_char == '|':
                token, error = self.make_or()
                if error: return [], error
                tokens.append(token)
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return[], IllegalCharError(pos_start, self.pos, "'" + char + "'")
            
        tokens.append(Token(TOKEN_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0
        post_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TOKEN_INT, int(num_str), post_start, self.pos)
        else:
            return Token(TOKEN_FLOAT, float(num_str), post_start, self.pos)
    
    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()

        token_type = TOKEN_KEYWORD if id_str in KEYWORDS else TOKEN_IDENTIFIER
        return Token(token_type, id_str, pos_start, self.pos)

    def make_or(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '|':
            self.advance()
            return Token(TOKEN_OR, pos_start=pos_start, pos_end=self.pos), None

        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'|' (after '|')")
    
    def make_and(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '&':
            self.advance()
            return Token(TOKEN_AND, pos_start=pos_start, pos_end=self.pos), None

        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'&' (after '&')")
        
    
    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TOKEN_NE, pos_start=pos_start, pos_end=self.pos), None

        return Token(TOKEN_NOT, pos_start=pos_start, pos_end=self.pos), None
        
    def make_equals(self):
        token_type = TOKEN_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TOKEN_EE

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_less_than(self):
        token_type = TOKEN_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TOKEN_EE

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_less_than(self):
        token_type = TOKEN_LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TOKEN_LTE

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_greater_than(self):
        token_type = TOKEN_GT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TOKEN_GTE

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

##################################################
# NODES
##################################################

class NumberNode:
    def __init__(self, token):
        self.token = token
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end
    
    def __repr__(self):
        return f'{self.token}'
    
class VarAccessNode:
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.var_name_token.pos_end

    def __repr__(self):
        return f'{self.var_name_token}'

class VarAssignNode:
    def __init__(self, var_name_token, value_node):
        self.var_name_token = var_name_token
        self.value_node = value_node

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.var_name_token.pos_end
    
    def __repr__(self):
        return f'({self.var_name_token} {Token(TOKEN_EQ)} {self.value_node})'
    
class BinOpNode:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node 
        self.op_token = op_token 
        self.right_node = right_node 
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end
    
    def __repr__(self):
        return f'({self.left_node}, {self.op_token}, {self.right_node})'

class UnaryOpNode:
    def __init__(self, op_token, node):    
        self.op_token = op_token
        self.node = node
        self.pos_start = self.op_token.pos_start
        self.pos_end = self.node.pos_end
    
    def __repr__(self):
        return f'({self.op_token}, {self.node})'
    
class IfNode:
	def __init__(self, cases, else_case):
		self.cases = cases
		self.else_case = else_case

		self.pos_start = self.cases[0][0].pos_start
		self.pos_end = (self.else_case or self.cases[len(self.cases) - 1][0]).pos_end

#######################################
# PARSE RESULT
#######################################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0
                
    def register_advancement(self):
        self.advance_count += 1
    
    def register(self, res):
            self.advance_count += res.advance_count
            if res.error: self.error = res.error
            return res.node
    
    def success(self, node):
            self.node = node
            return self
    
    def failure(self, error):
            if not self.error or self.advance_count == 0:
                self.error = error
            return self

##################################################
# PARSER
##################################################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.advance()

    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token
    
    def parse(self):
        res = self.expression()
        if not res.error and self.current_token.type is not TOKEN_EOF:
            return res.failure(
                InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '+' , '-', '*' or '/'"
                )
            )
    
        return res
    
    ###################################

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_token.matches(TOKEN_KEYWORD, 'if'):
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'if'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if self.current_token.matches(TOKEN_KEYWORD, 'else'):
            res.register_advancement()
            self.advance()

        else_case = res.register(self.expr())
        if res.error: return res

        return res.success(IfNode(cases, else_case))
        
    def factor(self):
            res = ParseResult()
            token = self.current_token

            if token.type in  (TOKEN_PLUS, TOKEN_MINUS):
                res.register_advancement
                self.advance()
                factor = res.register(self.factor())
                if res.error: return res
                return res.success(UnaryOpNode(token, factor))
            
            elif token.type == TOKEN_IDENTIFIER:
                res.register_advancement
                self.advance()
                return res.success(VarAccessNode(token))

            elif  token.type in (TOKEN_INT, TOKEN_FLOAT):
                res.register_advancement
                self.advance()
                return res.success(NumberNode(token))
            
            elif token.type == TOKEN_LPAREN:
                res.register_advancement
                self.advance()
                expr = res.register(self.expression())
                if res.error : return res
                if self.current_token.type == TOKEN_RPAREN:
                        res.register_advancement
                        self.advance()
                        return res.success(expr)
                else:
                    return res.failure(
                        InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end,
                            "Expected ')"
                        )
                    )
            
            elif token.matches(TOKEN_KEYWORD, 'if'):
                if_expr = res.register(self.if_expr())
                if res.error: return res
                return res.success(if_expr)
            
            return res.failure(
                InvalidSyntaxError(token.pos_start, token.pos_end, "Expected number or identifier.")
            )

    def term(self):
            return self.binary_op(self.factor, (TOKEN_MUL, TOKEN_DIV))
    
    def arith_expression(self):
        return self.binary_op(self.term, (TOKEN_PLUS, TOKEN_MINUS))
    
    def comp_expression(self):
        res = ParseResult()

        if self.current_token.type == TOKEN_NOT:
            op_token = self.current_token
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expression())
            if res.error: return res
            return res.success(UnaryOpNode(op_token,node))
        
        node = res.register(self.binary_op(self.arith_expression, (TOKEN_EE, TOKEN_NE, TOKEN_LT, TOKEN_GT, TOKEN_LTE, TOKEN_GTE)))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected int, float, identifier, '+', '-', '(' or '!'"
            ))
        
        return res.success(node)


    def expression(self):
            res = ParseResult()

            if self.current_token.matches(TOKEN_KEYWORD, 'let'):
                res.register_advancement
                self.advance()

                if self.current_token.type != TOKEN_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected identifier"
                    ))
                
                var_name = self.current_token
                res.register_advancement
                self.advance()

                if self.current_token.type != TOKEN_EQ:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected '='"
                    ))
                
                res.register_advancement
                self.advance()
                expression = res.register(self.expression())
                if res.error: return res
                return res.success(VarAssignNode(var_name, expression))

            node = res.register(self.binary_op(
                self.comp_expression, 
                ((TOKEN_AND), (TOKEN_OR))
                ))

            if res.error: 
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected let, number or identifier"
                ))

            return res.success(node)

    def binary_op(self, func_a, ops, func_b=None):

        if func_b == None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res
        while self.current_token.type in ops:
            op_token = self.current_token
            res.register_advancement
            self.advance()
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_token, right)
        return res.success(left)

##################################################
# SYMBOL TABLE
##################################################

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value
    
    def set(self, name,value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]

##################################################
# RUN
##################################################

global_symbol_table = SymbolTable()

def run(file_name, text):
    # Generate Tokens
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()

    if error : return None , error

    print(tokens)
    # Generate AST
    parser  = Parser(tokens)
    ast = parser.parse()

    return ast.node, ast.error
