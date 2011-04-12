# -*- coding: utf-8 -*-

import ply.lex as lex
import re
import sys

prog_name = "Dijkstra_RPN"
prog_help =  '''Dijkstra_RPN v1.0. Copyright Vasiliy Tsubenko
Instruction:    python3.x dijkstra_rpn.py INPUT OUTPUT
                INPUT  - file for input
                OUTPUT - file for output. If not specified, the program outputs to console
P.S.: For the work required module PLY (http://www.dabeaz.com/ply)'''

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
              'POW',
              'LBRACKET',
              'RBRACKET'
              )
    
    t_PLUS      = r'\+'
    t_MINUS     = r'-'
    t_MUL       = r'\*'
    t_DIV       = r'/'
    t_POW       = r'\^'
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
    'Parsing expression and convert it to RPN (Reverse Polish notation)'
    priority = (
                r'\(', 
                r'\)', 
                r'\+|-', 
                r'\*|/', 
                r'\^', 
                r'(um)|(up)'
                )
    
    bin_operation = {
                     'PLUS':    '+',
                     'MINUS':   '-',
                     'MUL':     '*',
                     'DIV':     '/',
                     'POW':     '^'
                     }
    
    un_operation = {
                    'PLUS':    'um',
                    'MINUS':   'up'
                    }
    
    def __init__(self, lexer):
        self.lexer = lexer
        
    def get_priority(self, sym):
        for i, el in enumerate(Parser.priority):
            if re.match(el, sym): return i

    def is_right(self, sym):
        return re.match('(um)|(up)|(\^)', sym)
    
    def to_stack(self, sym):
        pr = self.get_priority(sym)
        while not self.stack.is_empty() and pr <= self.get_priority(self.stack.back()) and not self.is_right(sym):
            self.out.append(self.stack.pop())
        self.stack.push(sym)
                         
    def parse_operand(self, t):
        v = Parser.un_operation.get(t.type)
        if v:
            self.stack.push(v)
        elif t.type == 'NUMBER': 
            self.out.append(t.value)
            self.is_next_operand = False
            return
        elif t.type == 'LBRACKET':
            self.stack.push("(")
        else:
            raise MyException(t.lexpos, "Invalid expression. Unexpected symbol '" + t.value + "'")
        self.is_next_operand = True
        
    def parse_operation(self, t):
        v = Parser.bin_operation.get(t.type)
        if not v:
            raise MyException(t.lexpos, "Invalid expression. Unexpected symbol '" + str(t.value) + "'")
        self.to_stack(v)
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
    'Calculation expression in RPN (Reverse Polish notation)'
    def calc(self, lst):
        if len(lst) == 0:
            return 0
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
                elif el == '^':
                    self.stack.push(op1 ** op2)
        return self.stack.pop() 

if len(sys.argv) == 1 or sys.argv[1] in {"-h", "-help"}:
    sys.stdout.write(prog_help)
    raise SystemExit(0)
try:
    file_in = open(sys.argv[1], "r")
    out = open(sys.argv[2], "w") if len(sys.argv) > 2 else sys.stdout
    p = Parser(Lexer())
    c = Calculator()
    for line in file_in:
        try:
            res = p.parse(line.strip())
        except MyException as e: 
            out.write(prog_name + " " + e.msg + "\n")
            continue
        out.write(str(res) + " --> " + str(c.calc(res)) + "\n")
except IOError as err:
    sys.stderr.write(prog_name + " : " + str(err))
    raise SystemExit(1)