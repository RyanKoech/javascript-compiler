from string_with_arrows import *
from error import *
from position import *
from constants import *
from lexer import *
from ourjs_parser import *

class IntermediateCodeGenerator:
    def __init__(self, ast):
        self.temp_counter = 0
        self.ast = ast

    def get_next_temp(self):
        self.temp_counter = self.temp_counter + 1
        return self.temp_counter - 1

    def get_current_temp(self):
        return self.temp_counter - 1

    def generate_intermediate_code(self):
        if self.ast == None: return ''
        return self.ast.get_ic(self.get_next_temp, self.get_current_temp)
        

##################################################
# RUN
##################################################

def run(file_name, text):
    # Generate Tokens
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()

    if error : return None , error

    # print(tokens)
    # Generate AST
    parser  = Parser(tokens)
    ast = parser.parse()

    if ast.error:
        return None, ast.error
    
    print('_______ABSTRACT SYNTAX TREE____________\n')
    
    print(ast.node)

    print('\n_______INTERMEDIATE CODE____________\n')

    # Intermediate Code Generator
    intermediateCodeGenerator = IntermediateCodeGenerator(ast.node)

    return intermediateCodeGenerator.generate_intermediate_code(), ast.error