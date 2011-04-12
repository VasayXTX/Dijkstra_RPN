import ply.lex as lex

prog_name = "Dijkstra_RPN"

class LexerException(Exception):
    def __init__(self, pos, text):
        self.text = text
        self.pos = pos
    
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
        raise LexerException(t.lexpos, "Illegal character")
    
    def __init__(self):
        self.lexer = lex.lex(module=self)
        
    def set_input(self, str):
        self.lexer.input(str)
        
    def next(self):
        return self.lexer.token()

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        
    def parse(self, str):
        self.lexer.set_input(str)
        arr = []
        while True:
            t = self.lexer.next()
            if not t: break
            arr.append(t.value)
        return arr
            
p = Parser(Lexer())
print(p.parse("1  +2 "))