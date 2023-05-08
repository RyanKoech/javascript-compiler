import string

##################################################
# DIGITS
##################################################

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

##################################################
# TOKEN
##################################################

TOKEN_INT = 'TOKEN_INT'
TOKEN_FLOAT = 'TOKEN_FLOAT'
TOKEN_STRING = 'TOKEN_STRING'
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
TOKEN_NEWLINE = 'TOKEN_NEWLINE'
TOKEN_EOF = 'TOKEN_EOF'
TOKEN_COMMA = 'TOKEN_COMMA'

KEYWORDS = [
    'let',
    'if',
    'else',
    'while',
    'for',
    'func'
]