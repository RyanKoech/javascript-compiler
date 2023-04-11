from string_with_arrows import *

##################################################
# DIGITS
##################################################

DIGITS = '0123456789'

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
TOKEN_PLUS = 'TOKEN_PLUS'
TOKEN_MINUS = 'TOKEN_MINUS'
TOKEN_MUL = 'TOKEN_MUL'
TOKEN_DIV = 'TOKEN_DIV'
TOKEN_LPAREN = 'TOKEN_LPAREN'
TOKEN_RPAREN = 'TOKEN_RPAREN'
TOKEN_LCURL = 'TOKEN_LCURL'
TOKEN_RCURL = 'TOKEN_RCURL'
TOKEN_EOF = 'TOKEN_EOF'

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

#######################################
# PARSE RESULT
#######################################

class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None

	def register(self, res):
		if isinstance(res, ParseResult):
			if res.error: self.error = res.error
			return res.node

		return res

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
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
            print(res.node)
            return res.failure(
                InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '+' , '-', '*' or '/'"
                )
            )
    
        return res
    
    def factor(self):
        res = ParseResult()
        token = self.current_token

        if token.type in  (TOKEN_PLUS, TOKEN_MINUS):
            res.register(self.advance())
            factor = res.register(self.advance())
            if res.error: return res
            return res.success(UnaryOpNode(token, factor))

        elif  token.type in (TOKEN_INT, TOKEN_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(token))
        
        elif token.type == TOKEN_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expression())
            if res.error : return res
            if self.current_token.type == TOKEN_RPAREN:
                    res.register(self.advance())
                    return res.success(expr)
            else:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected ')"
                    )
                )
        
        return res.failure(
            InvalidSyntaxError(token.pos_start, token.pos_end, "Expected number.")
        )

    def term(self):
        return self.binary_op(self.factor, (TOKEN_MUL, TOKEN_DIV))

    def expression(self):
        return self.binary_op(self.term, (TOKEN_PLUS, TOKEN_MINUS))

    def binary_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res
        while self.current_token.type in ops:
            op_token = self.current_token
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left, op_token, right)
        return res.success(left)

##################################################
# RUN
##################################################

def run(file_name, text):
    # Generate Tokens
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()

    if error : return None , error

    # Generate AST
    parser  = Parser(tokens)
    ast = parser.parse()

    return ast.node, ast.error
