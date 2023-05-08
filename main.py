from string_with_arrows import *
from error import *
from position import *
from constants import *
from lexer import *
from ourjs_parser import *

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

    return ast.node, ast.error