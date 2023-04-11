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
        return result
    

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

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

    def advance(self, current_char):
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

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

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
                tokens.append(Token(TOKEN_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TOKEN_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TOKEN_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TOKEN_DIV))
                self.advance()
            elif self.current_char == '()':
                tokens.append(Token(TOKEN_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TOKEN_RPAREN))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(TOKEN_LCURL))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(TOKEN_RCURL))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return[], IllegalCharError(pos_start, self.pos, "'" + char + "'")
            
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TOKEN_INT, int(num_str))
        else:
            return Token(TOKEN_FLOAT, float(num_str))


##################################################
# RUN
##################################################

def run(file_name, text):
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()

    return tokens, error
