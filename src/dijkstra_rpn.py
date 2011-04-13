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
                (r'\(',        'l'),
                (r'\)',        'l'),
                (r'\+|-',      'l'), 
                (r'\*|/',      'l'),
                (r'\^',        'r'),
                (r'(um)|(up)', 'r')
                )
    
    bin_operation = {
                     'PLUS':    '+',
                     'MINUS':   '-',
                     'MUL':     '*',
                     'DIV':     '/',
                     'POW':     '^'
                     }
    
    un_operation = {
                    'PLUS':    'up',
                    'MINUS':   'um'
                    }
    
    def __init__(self, lexer):
        self.lexer = lexer
        
    def get_priority(self, sym):
        for i, (el, a)  in enumerate(Parser.priority):
            if re.match(el, sym): return i, a
    
    def to_stack(self, sym):
        sym_pr, sym_a = self.get_priority(sym)
        while not self.stack.is_empty():
            pr, a = self.get_priority(self.stack.back())
            cmp = (sym_pr < pr) if sym_a == 'r' and a == 'r' else (sym_pr <= pr)
            if cmp:
                self.out.append(self.stack.pop())
            else:
                break
        self.stack.push(sym)
                         
    def parse_operand(self, t):
        v = Parser.un_operation.get(t.type)
        if v:
            self.to_stack(v)
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
            if self.is_next_operand:
                self.parse_operand(t)
            elif t.type == 'RBRACKET':
                while not self.stack.is_empty() and self.stack.back() != '(':
                    self.out.append(self.stack.pop())
                if self.stack.is_empty():
                    raise MyException(t.lexpos, "Invalid expression. Single closing bracket")
                self.stack.pop()
            else:
                self.parse_operation(t) 
        return self.out

class Calculator:
    'Calculation expression in RPN (Reverse Polish notation)'
    func = {
            'up':   (1, lambda a: +a),
            'um':   (1, lambda a: -a),
            '+':    (2, lambda a, b: a + b),
            '-':    (2, lambda a, b: a - b),
            '*':    (2, lambda a, b: a * b),
            '/':    (2, lambda a, b: a / b),
            '^':    (2, lambda a, b: a ** b)
            }
    
    def calc(self, lst):
        if len(lst) == 0:
            return 0
        self.stack = Stack()
        for el in lst:
            if type(el) is float:
                self.stack.push(el)
                continue
            argc, f = Calculator.func[el]
            argv = [self.stack.pop() for i in range(argc)]
            argv.reverse()
            try:
                self.stack.push(f(*argv))
            except ZeroDivisionError as err:
                raise MyException(0, "Invalid expression. " + str(err)[:1].upper() + str(err)[1:].lower())
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
            out.write(str(res) + " --> " + str(c.calc(res)) + "\n")
        except MyException as e: 
            out.write(prog_name + " " + e.msg + "\n")
            continue
except IOError as err:
    sys.stderr.write(prog_name + " : " + str(err))
    raise SystemExit(1)