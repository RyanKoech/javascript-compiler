from lexer import *

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
    
class StringNode:
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
		self.if_token = Token(TOKEN_KEYWORD, 'if')
		self.else_token = Token(TOKEN_KEYWORD, 'else')
		self.else_case = else_case
			
		self.pos_start = self.cases[0][0].pos_start
		self.pos_end = (self.else_case or self.cases[len(self.cases) - 1][0]).pos_end
    
	def __repr__(self):
		if self.else_case: 
			return f'({self.if_token} {TOKEN_LCURL} {self.cases[0]} {TOKEN_RCURL} {self.else_token}  {TOKEN_LCURL} {self.else_case} {TOKEN_RCURL})'
		return f'({self.if_token} {TOKEN_LCURL} {self.cases[0]} {TOKEN_RCURL})'

class ForNode:
    def __init__(self, expr_node, comp_expr_node, arith_expr_node, body_node):
        self.for_token = Token(TOKEN_KEYWORD, 'for')
        self.expr_node = expr_node
        self.comp_expr_node = comp_expr_node
        self.arith_expr_node = arith_expr_node
        self.body_node = body_node
        
        self.pos_start = self.expr_node.pos_start
        self.pos_end = self.body_node.pos_end
        
    def __repr__(self):
        return f'({self.for_token} {TOKEN_LPAREN} {self.expr_node} {TOKEN_COMMA} {self.comp_expr_node} {TOKEN_COMMA} {self.arith_expr_node} {TOKEN_RPAREN} {TOKEN_LCURL} {self.body_node} {TOKEN_RCURL})'     
        
class WhileNode:
    def __init__(self, condition_node, body_node):
        self.while_token = Token(TOKEN_KEYWORD, 'while')
        self.condition_node = condition_node
        self.body_node = body_node
        
        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f'({self.while_token} {TOKEN_LPAREN} {self.condition_node} {TOKEN_RPAREN} {TOKEN_LCURL} {self.body_node} {TOKEN_RCURL})'     
    
class FuncDefNode:
    def __init__(self, var_name_token, arg_name_tokens, body_node):
        self.func_token = Token(TOKEN_KEYWORD, 'func')
        self.var_name_token = var_name_token
        self.arg_name_tokens = arg_name_tokens
        self.body_node = body_node

        if len(self.arg_name_tokens) > 0:
            self.pos_start = self.arg_name_tokens[0].pos_start
        else:
            self.pos_start = self.body_node.pos_end

    def __repr__(self):
        return f'({self.func_token} {self.var_name_token} {TOKEN_LPAREN} {self.arg_name_tokens} {TOKEN_RPAREN} {TOKEN_LCURL} {self.body_node} {TOKEN_RCURL})'

class CallNode:
    def __init__(self, node_to_call,arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = self.node_to_call.pos_start

        if len(self.arg_nodes) > 0:
            self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end

    def __repr__(self):
        arg_name_string = ""
        for arg_node in self.arg_nodes:
            if arg_name_string == "":
                arg_name_string += f'{arg_node}'
            else:
                arg_name_string += f'{TOKEN_COMMA} {arg_node}'
        return f'({self.node_to_call} {TOKEN_LPAREN} {arg_name_string} {TOKEN_RPAREN})'

class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end
    
    def to_string(self, nodes_list):
        size = len(nodes_list)
        if size <= 0:
            return ""
        elif size == 1:
            return f'{nodes_list[0]}'
        else:
            node = nodes_list[0]
            nodes_list.pop(0)
            return f'({node} {self.to_string(nodes_list)})'

    def __repr__(self):
        return self.to_string(self.element_nodes.copy())

