#!/usr/bin/env python3
#
#
# Copyright (c) 2019, Hiroyuki Ohsaki.
# All rights reserved.
#
# $Id: $
#

from perlcompat import die, warn, getopts
#import tbdump

import ply.lex as lex

keywords = ('DISPLAY', 'DEFINE', 'BOX')

tokens = keywords + (
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'ID',
    'LPAREN',
    'RPAREN',
    'NUMBER',
    'STRING',
    'AT',
    'NEWLINE',
)

t_ignore = ' \t'

t_PLUS = r'\+'
t_MINUS = r'\-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_NUMBER = r'(\d+(\.\d+)?|\.\d+)'
t_STRING = r'\".*?\"'
t_AT = r'@'

def t_ID(t):
    r'[A-Za-z_.][A-Za-z0-9_.]*'
    if t.value.upper() in keywords:
        t.type = t.value.upper()
    return t

def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno += 1
    return t

def t_error(t):
    print("illegal character '{}'".format(t.value[0]))
    t.lexer.skip(1)

lexer = lex.lex()

# ----------------------------------------------------------------
def p_statements(p):
    """statements : empty
    | statements statement"""
    pass

def p_statement_define(p):
    """statement : DEFINE ID BOX box_specs_with_location NEWLINE"""
    pass

def p_statement_display(p):
    """statement : DISPLAY NEWLINE"""
    pass

def p_box_specs_with_location(p):
    """box_specs_with_location : box_specs
    | box_specs location"""
    pass

def p_box_specs(p):
    """box_specs | dimension dimension
    | dimension dimension color"""
    pass

def p_geometry_sepc(p):
    """geometry_spec : number number"""
    pass

def p_dimension(p):
    """dimension : number"""
    p[0] = p[1]

def p_expression(p):
    """expression : number
    | variable
    | expression binary_op expression
    | LPAREN expression RPAREN"""
    pass

def p_binary_op(p):
    """binary_op : PLUS
    | MINUS
    | TIMES
    | DIVIDE"""
    pass

def p_variable(p):
    """variable : ID"""
    pass

def p_number(p):
    """number : NUMBER
    | PLUS NUMBER
    | MINUS NUMBER"""
    pass

def p_color(p):
    """color : ID"""
    p[0] = p[1]

def p_empty_sepc(p):
    """empty :"""
    pass

# def p_error(p):
#     raise

import ply.yacc as yacc
yacc.yacc()

s = """define foo box 100 100
display
define foo box 12 (-34 * 1.2 + foo)
"""

# lexer.input(s)
# for tok in lexer:
#     print(tok)
yacc.parse(s)
"""

x = 124
y = 24
define box 124,34 @ 64,39
define box x,y @ 64,39

"""
