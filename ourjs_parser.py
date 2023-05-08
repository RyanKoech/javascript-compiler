from constants import *
from nodes import *

#######################################
# PARSE RESULT
#######################################

from error import InvalidSyntaxError


class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0
        self.to_reverse_count = 0
        self.ast = None
                
    def register_advancement(self):
        self.advance_count += 1
    
    def register(self, res):
            self.advance_count += res.advance_count
            if res.error: self.error = res.error
            return res.node

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)
    
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
        self.update_current_token()
        return self.current_token
    
    def reverse(self, amount=1):
        self.token_index -= amount
        self.update_current_token()
        return self.current_token
    
    def update_current_token(self):
        if self.token_index < len(self.tokens):
                    self.current_token = self.tokens[self.token_index]
    
    def parse(self):
        res = self.statements()
        if not res.error and self.current_token.type is not TOKEN_EOF:
            return res.failure(
                InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '+' , '-', '*' or '/'"
                )
            )
    
        return res

    def intermediate_code(self):
        if self.ast == None:
            self.parse()
        
        return self.ast.get_ic()
        
    
    ###################################

    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_token.pos_start.copy()

        while self.current_token.type == TOKEN_NEWLINE:
            res.register_advancement()
            self.advance()

        statement = res.register(self.expression())
        if res.error: return res
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.current_token.type == TOKEN_NEWLINE:
                res.register_advancement()
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False
            
            if not more_statements: break
            statement = res.try_register(self.expression())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)

        return res.success(ListNode(
        statements,
        pos_start,
        self.current_token.pos_end.copy()
        ))

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

        if self.current_token.type != TOKEN_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected opening {'('}"
            ))
		        
        res.register_advancement()
        self.advance()

        condition = res.register(self.expression())
        if res.error: return res
        

        if self.current_token.type != TOKEN_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected opening ')'"
            ))
                
        res.register_advancement()
        self.advance()

        
        if self.current_token.type != TOKEN_LCURL:
            return res.failure(InvalidSyntaxError(
				self.current_token.pos_start, self.current_token.pos_end,
				f"Expected opening {'{'}"
			))
        
        res.register_advancement()
        self.advance()
        
        statements = res.register(self.statements())
        if res.error: return res
        cases.append((condition, statements))
        
        if self.current_token.type != TOKEN_RCURL:
            return res.failure(InvalidSyntaxError(
				self.current_token.pos_start, self.current_token.pos_end,
				f"Expected opening {'}'}"
			))
        
        res.register_advancement()
        self.advance()
            
        if self.current_token.matches(TOKEN_KEYWORD, 'else'):
            res.register_advancement()
            self.advance()
            
            if self.current_token.type != TOKEN_LCURL:
                return res.failure(InvalidSyntaxError(
					self.current_token.pos_start, self.current_token.pos_end,
					f"Expected opening {'{'}"
				))
            res.register_advancement()
            self.advance()

            else_case = res.register(self.statements())
            if res.error: return res
            
            if self.current_token.type != TOKEN_RCURL:
                return res.failure(InvalidSyntaxError(
					self.current_token.pos_start, self.current_token.pos_end,
					f"Expected opening {'}'}"
				))
            res.register_advancement()
            self.advance()      
        
                
        return res.success(IfNode(cases, else_case))

    def for_expr(self):
        res = ParseResult()
        
        if not self.current_token.matches(TOKEN_KEYWORD, 'for'):
            return res.failure(InvalidSyntaxError(
				self.current_token.pos_start, self.current_token.pos_end,
				f"Expected {'for'}"
			))
        
        res.register_advancement()
        self.advance()
		
        if self.current_token.type != TOKEN_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected opening {'('}"
            ))

        res.register_advancement()
        self.advance()

        expression = res.register(self.expression())
        if res.error: return res
        
        if self.current_token.type != TOKEN_COMMA:
            return res.failure(InvalidSyntaxError(
				self.current_token.pos_start, self.current_token.pos_end,
				f"Expected comma {','}"
			))
            
        res.register_advancement()
        self.advance()
        
        comparative_expression = res.register(self.comp_expression())  
        if res.error: return res

        if self.current_token.type != TOKEN_COMMA:
            return res.failure(InvalidSyntaxError(
				self.current_token.pos_start, self.current_token.pos_end,
				f"Expected character {','}"
			))
            
        res.register_advancement()
        self.advance()
                            
        arithmetic_expression = res.register(self.arith_expression())  
        if res.error: return res
        
        if self.current_token.type != TOKEN_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected closing ')'"
            ))
                
        res.register_advancement()
        self.advance()
        
        if self.current_token.type != TOKEN_LCURL:
                return res.failure(InvalidSyntaxError(
					self.current_token.pos_start, self.current_token.pos_end,
					f"Expected opening {'{'}"
				))
            
        res.register_advancement()
        self.advance()
            
        body = res.register(self.statements())
        if  res.error: return res
            
        if self.current_token.type != TOKEN_RCURL:
                return res.failure(InvalidSyntaxError(
					self.current_token.pos_start, self.current_token.pos_end,
					f"Expected closing {'}'}"
				))
        res.register_advancement()
        self.advance()
            
        return res.success(ForNode(expression, comparative_expression, arithmetic_expression, body))
        
    def while_expr(self):
        res = ParseResult()
        
        if not self.current_token.matches(TOKEN_KEYWORD, 'while'):
            return res.failure(InvalidSyntaxError(
				self.current_token.pos_start, self.current_token.pos_end,
				f"Expected {'while'}"
			))
        
        res.register_advancement()
        self.advance()
        
        if self.current_token.type != TOKEN_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected opening {'('}"
            ))
		        
        res.register_advancement()
        self.advance()
        
        condition = res.register(self.expression())
        if res.error: return res
        
        if self.current_token.type != TOKEN_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected closing {')'}"
            ))
                
        res.register_advancement()
        self.advance()
        
        if self.current_token.type != TOKEN_LCURL:
                return res.failure(InvalidSyntaxError(
					self.current_token.pos_start, self.current_token.pos_end,
					f"Expected opening {'{'}"
				))
            
        res.register_advancement()
        self.advance()
        
        body = res.register(self.statements())
        if  res.error: return res
            
        if self.current_token.type != TOKEN_RCURL:
                return res.failure(InvalidSyntaxError(
					self.current_token.pos_start, self.current_token.pos_end,
					f"Expected closing {'}'}"
				))
        res.register_advancement()
        self.advance()
        
        return res.success(WhileNode(condition, body))
        
    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error: return res

        if self.current_token.type == TOKEN_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_token.type == TOKEN_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expression()))
                if res.error:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected ')', 'let', 'if', 'for', 'while', 'func', int, float, identifier,  '+', '-', '(' or 'NOT'"
                    ))
                
                while self.current_token.type == TOKEN_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expression()))
                    if res.error: return res

                if self.current_token.type != TOKEN_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        f"Expected ',' or ')'"
                    ))
                
                res.register_advancement()
                self.advance()
            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def atom(self):
            res = ParseResult()
            token = self.current_token

            if token.type == TOKEN_IDENTIFIER:
                res.register_advancement
                self.advance()
                return res.success(VarAccessNode(token))

            elif  token.type in (TOKEN_INT, TOKEN_FLOAT):
                res.register_advancement
                self.advance()
                return res.success(NumberNode(token))
            
            elif  token.type in (TOKEN_STRING):
                res.register_advancement
                self.advance()
                return res.success(StringNode(token))
            
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
                            f"Expected {')'}"
                        )
                    )
            
            elif token.matches(TOKEN_KEYWORD, 'if'):
                if_expr = res.register(self.if_expr())
                if res.error: return res
                return res.success(if_expr)
            
            elif token.matches(TOKEN_KEYWORD, 'for'):
                 for_expr = res.register(self.for_expr())
                 if res.error: return res
                 return res.success(for_expr)
            
            elif token.matches(TOKEN_KEYWORD, 'while'):
                while_expr = res.register(self.while_expr())
                if res.error: return res
                return res.success(while_expr)
            
            elif token.matches(TOKEN_KEYWORD, 'func'):
                func_def = res.register(self.func_def())
                if res.error: return res
                return res.success(func_def)
            
            return res.failure(
                InvalidSyntaxError(token.pos_start, token.pos_end, "Expected number, identifier, 'if', 'for', 'while', 'func'")
            )
    
    def factor(self):
            res = ParseResult()
            token = self.current_token

            if token.type in  (TOKEN_PLUS, TOKEN_MINUS):
                res.register_advancement
                self.advance()
                factor = res.register(self.factor())
                if res.error: return res
                return res.success(UnaryOpNode(token, factor))
            
            return self.call()

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
                    "Expected let, if, for, while, func, number or identifier"
                ))

            return res.success(node)

    def func_def(self):
        res = ParseResult()

        if not self.current_token.matches(TOKEN_KEYWORD, 'func'):
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'func'"
            ))
        
        res.register_advancement()
        self.advance()

        if self.current_token.type == TOKEN_IDENTIFIER:
            var_name_token = self.current_token
            res.register_advancement()
            self.advance()
            if self.current_token.type != TOKEN_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected '('"
                ))
        else:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected identifier"
            ))
            
        res.register_advancement()
        self.advance()
        arg_name_tokens = []

        if self.current_token.type == TOKEN_IDENTIFIER:
            arg_name_tokens.append(self.current_token)
            res.register_advancement()
            self.advance()

            while self.current_token.type == TOKEN_COMMA:
                res.register_advancement()
                self.advance()

                if self.current_token.type != TOKEN_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        f"Expected identifier"
                    ))
                arg_name_tokens.append(self.current_token)
                res.register_advancement()
                self.advance()

            if self.current_token.type != TOKEN_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected ',' or ')'"
                ))
            
        else:
            if self.current_token.type != TOKEN_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected identifier or ')'"
                ))
            
        res.register_advancement()
        self.advance()

        if self.current_token.type != TOKEN_LCURL:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected {'{'}"
            ))
        
        res.register_advancement()
        self.advance()
        node_to_return = res.register(self.statements())
        if res.error: return res

        if self.current_token.type != TOKEN_RCURL:
            return res.failure(InvalidSyntaxError(
				self.current_token.pos_start, self.current_token.pos_end,
				f"Expected closing {'}'}"
			))
        
        res.register_advancement()
        self.advance()

        return res.success(FuncDefNode(
            var_name_token,
            arg_name_tokens,
            node_to_return
        ))
    
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
