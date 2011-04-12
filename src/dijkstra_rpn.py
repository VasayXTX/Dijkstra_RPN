import ply.lex as lex
import re

prog_name = "Dijkstra_RPN"

class MyException(Exception):
    def __init__(self, pos, text):
        self.text = text
        self.pos = pos + 1
    
    @property     
    def msg(self):
        return "(" + str(self.pos) + "): " + self.text

class Lexer:
    'Lexical analysis of expression'
    tokens = (
              'NUMBER', 
              'PLUS', 
              'MINUS', 
              'MUL',
              'DIV',
              'LBRACKET',
              'RBRACKET'
              )
    
    t_PLUS      = r'\+'
    t_MINUS     = r'-'
    t_MUL       = r'\*'
    t_DIV       = r'/'
    t_LBRACKET  = r'\('
    t_RBRACKET  = r'\)'
    
    t_ignore = ' \t'
    
    def t_NUMBER(self, t):
        r'\d+(\.?\d+)?'
        t.value = float(t.value)
        return t
    
    def t_error(self, t):
        raise MyException(t.lexpos, "Illegal character")
    
    def __init__(self):
        self.lexer = lex.lex(module=self)
        
    def set_input(self, str):
        self.lexer.input(str)
        
    def next(self):
        return self.lexer.token()
    
class Stack:    
    def __init__(self):
        self.s = []
        
    def is_empty(self):
        return not len(self.s)
    
    def push(self, el):
        self.s.append(el)
    
    def pop(self):
        return self.s.pop()
    
    def back(self):
        return self.s[len(self.s)-1]
        
class Parser:
    def __init__(self, lexer):
        self.priority = [r'\(', r'\)', r'\+|-', r'\*|/', r'(um)|(up)']
        self.lexer = lexer
        
    def get_priority(self, sym):
        for i, el in enumerate(self.priority):
            if re.search(el, sym): return i

    def to_stack(self, sym):
        pr = self.get_priority(sym)
        while not self.stack.is_empty() and pr <= self.get_priority(self.stack.back()):
            self.out.append(self.stack.pop())
        self.stack.push(sym)
                         
    def parse_operand(self, t):
        if t.type == 'NUMBER': 
            self.out.append(t.value)
            self.is_next_operand = False
            return
        elif t.type == 'LBRACKET':
            self.stack.push(t.value)
        elif t.type == 'MINUS':
            self.to_stack('um')
        elif t.type == 'PLUS':
            self.to_stack('up')
        else:
            raise MyException(t.lexpos, "Invalid expression. Unexpected symbol '" + t.value + "'")
        self.is_next_operand = True
        
    def parse_operation(self, t):
        if t.type == 'PLUS':
            self.to_stack('+')
        elif t.type == 'MINUS':
            self.to_stack('-')
        elif t.type == 'MUL':
            self.to_stack('*')
        elif t.type == 'DIV':
            self.to_stack('/')
        else:
            raise MyException(t.lexpos, "Invalid expression. Unexpected symbol '" + str(t.value) + "'")
        self.is_next_operand = True
            
    def parse(self, str):
        self.lexer.set_input(str)
        self.stack = Stack()
        self.out = []
        self.is_next_operand = True
        while True:
            t = self.lexer.next()
            if not t:
                while not self.stack.is_empty():
                    if self.stack.back() == '(':
                        raise MyException(0, "Invalid expression. Single opening bracket")
                    self.out.append(self.stack.pop())
                break
            if t.type == 'RBRACKET':
                while not self.stack.is_empty() and self.stack.back() != '(':
                    self.out.append(self.stack.pop())
                if self.stack.is_empty():
                    raise MyException(t.lexpos, "Invalid expression. Single closing bracket")
                self.stack.pop()
            elif self.is_next_operand:
                self.parse_operand(t)
            else:
                self.parse_operation(t) 
        return self.out

class Calculator:
    def calc(self, lst):
        self.stack = Stack()
        for el in lst:
            if type(el) is float:
                self.stack.push(el)
            elif el == 'up':
                pass
            elif el == 'um':
                self.stack.push(-self.stack.pop())
            else:
                op2 = self.stack.pop()
                op1 = self.stack.pop()
                if el == '+': 
                    self.stack.push(op1 + op2)
                elif el == '-':
                    self.stack.push(op1 - op2)
                elif el == '*':
                    self.stack.push(op1 * op2)
                elif el == '/':
                    self.stack.push(op1 / op2)
        return self.stack.pop() 
    
p = Parser(Lexer())
c = Calculator()
for line in open("input.in", "r"):
    line = line.strip()
    if not len(line): continue
    try:
        res = p.parse(line)
    except MyException as e: 
        print(prog_name + " " + e.msg)
        continue
    print(str(res) + " --> " + str(c.calc(res)))