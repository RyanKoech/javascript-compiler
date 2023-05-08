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

    def get_ic(self, get_next_temp, get_current_temp):
      return f't{get_next_temp()} = {self.token.value}\n'
    
class StringNode:
    def __init__(self, token):
        self.token = token
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end
    
    def __repr__(self):
        return f'{self.token}'

    def get_ic(self, get_next_temp, get_current_temp):
      return f't{get_next_temp()} = "{self.token.value}"\n'
    
class VarAccessNode:
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.var_name_token.pos_end

    def __repr__(self):
        return f'{self.var_name_token}'

    def get_ic(self, get_next_temp, get_current_temp):
      return f't{get_next_temp()} = {self.var_name_token.value}\n'

class VarAssignNode:
    def __init__(self, var_name_token, value_node):
        self.var_name_token = var_name_token
        self.value_node = value_node

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.var_name_token.pos_end
    
    def __repr__(self):
        return f'({self.var_name_token} {Token(TOKEN_EQ)} {self.value_node})'

    def get_ic(self, get_next_temp, get_current_temp):
      return f'{self.value_node.get_ic(get_next_temp, get_current_temp)}{self.var_name_token.value} = t{get_current_temp()}\n'
    
class BinOpNode:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node 
        self.op_token = op_token 
        self.right_node = right_node 
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end
    
    def __repr__(self):
        return f'({self.left_node}, {self.op_token}, {self.right_node})'

    def get_ic(self, get_next_temp, get_current_temp):
      left_ic = self.left_node.get_ic(get_next_temp, get_current_temp)
      left_ic_temp = get_current_temp()
      right_ic = self.right_node.get_ic(get_next_temp, get_current_temp)
      right_ic_temp = get_current_temp()
      op = self.get_op_symbol()
      return f'{left_ic}{right_ic}t{get_next_temp()} = t{left_ic_temp} {op} t{right_ic_temp}\n'

    def get_op_symbol(self):
      if (self.op_token.type == TOKEN_MINUS):
        return '-'
      elif(self.op_token.type == TOKEN_PLUS):
        return '+'
      elif(self.op_token.type == TOKEN_DIV):
        return '/'
      elif(self.op_token.type == TOKEN_MUL):
        return '*'
      elif(self.op_token.type == TOKEN_EE):
        return '=='
      elif(self.op_token.type == TOKEN_GT):
        return '>'
      elif(self.op_token.type == TOKEN_GTE):
        return '>='
      elif(self.op_token.type == TOKEN_LT):
        return '<'
      elif(self.op_token.type == TOKEN_LTE):
        return '<='
      elif(self.op_token.type == TOKEN_NE):
        return '!='
      elif(self.op_token.type == TOKEN_AND):
        return '&&'
      elif(self.op_token.type == TOKEN_OR):
        return '||'
      else:
        return '%'

class UnaryOpNode:
    def __init__(self, op_token, node):    
        self.op_token = op_token
        self.node = node
        self.pos_start = self.op_token.pos_start
        self.pos_end = self.node.pos_end
    
    def __repr__(self):
        return f'({self.op_token}, {self.node})'

    def get_ic(self, get_next_temp, get_current_temp):
      node_ic = self.node.get_ic(get_next_temp, get_current_temp)
      node_ic_temp = get_current_temp()
      if self.op_token.type == TOKEN_PLUS:
        return f'{node_ic}'
      elif self.op_token.type == TOKEN_NOT:
        return f'{node_ic}t{get_next_temp()} = !t{node_ic_temp}\n'
      else: 
        return f'{node_ic}t{get_next_temp()} = uminus t{node_ic_temp}\n'
    
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

    def get_ic(self, get_next_temp, get_current_temp):
      comp_ic = self.cases[0][0].get_ic(get_next_temp, get_current_temp)
      comp_ic_temp = get_current_temp()
      label1 = get_next_temp()
      body_ic = self.cases[0][1].get_ic(get_next_temp, get_current_temp)
      return f'{comp_ic}if !t{comp_ic_temp} goto L{label1}\n{body_ic}L{label1}:\n'

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
    
    def get_ic(self, get_next_temp, get_current_temp):
      var_ic = self.expr_node.get_ic(get_next_temp, get_current_temp)
      var_ic_token_name = self.expr_node.var_name_token.value
      comp_ic = self.comp_expr_node.get_ic(get_next_temp, get_current_temp)
      comp_ic_temp = get_current_temp()
      arith_ic = self.arith_expr_node.get_ic(get_next_temp, get_current_temp)
      arith_ic_temp = get_current_temp()
      label1 = get_next_temp()
      label2 = get_next_temp()
      body_ic = self.body_node.get_ic(get_next_temp, get_current_temp)

      
      return f'{var_ic}L{label1}:\n{comp_ic}if !t{comp_ic_temp} goto L{label2}\n{body_ic}{arith_ic}{var_ic_token_name} = t{arith_ic_temp}\ngoto L{label1}\nL{label2}:\n'
        
class WhileNode:
    def __init__(self, condition_node, body_node):
        self.while_token = Token(TOKEN_KEYWORD, 'while')
        self.condition_node = condition_node
        self.body_node = body_node
        
        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f'({self.while_token} {TOKEN_LPAREN} {self.condition_node} {TOKEN_RPAREN} {TOKEN_LCURL} {self.body_node} {TOKEN_RCURL})'   
    
    def get_ic(self, get_next_temp, get_current_temp):
      comp_ic = self.condition_node.get_ic(get_next_temp, get_current_temp)
      comp_ic_temp = get_current_temp()
      label1 = get_next_temp()
      body_ic = self.body_node.get_ic(get_next_temp, get_current_temp)
      return f'{comp_ic}if !t{comp_ic_temp} goto L{label1}\n{body_ic}L{label1}:\n'  
    
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

    def get_ic(self, get_next_temp, get_current_temp):
      return f'{self.var_name_token.value}:\n{self.body_node.get_ic(get_next_temp, get_current_temp)}ret\n'

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

    def get_ic(self, get_next_temp, get_current_temp):
      arg_nodes_temps = ''
      arg_nodes_ic = ''
      for arg_node in self.arg_nodes:
        arg_nodes_ic += arg_node.get_ic(get_next_temp, get_current_temp)
        arg_node_temp = get_current_temp()
        if arg_nodes_temps == '':
          arg_nodes_temps += f't{arg_node_temp}'
        else:
          arg_nodes_temps += f', t{arg_node_temp}'
      return f'{arg_nodes_ic}call {self.node_to_call.var_name_token.value} {arg_nodes_temps}\n'

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

    def get_ic(self, get_next_temp, get_current_temp):
      ic_statements = ''
      for node in self.element_nodes:
        ic_statements += node.get_ic(get_next_temp, get_current_temp)
      return ic_statements


