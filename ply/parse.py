#!/usr/bin/env python3
#
#
# Copyright (c) 2019, Hiroyuki Ohsaki.
# All rights reserved.
#
# $Id: $
#

import fileinput
import os
import os.path
import re
import subprocess
import sys

from perlcompat import die, warn, getopts
#import tbdump

import ply.lex as lex

# display
# wait
# define name box [-f color] [width height color (x y|name[(+|-)dx(+|-)dy])]

keywords = ('DISPLAY', 'DEFINE', 'BOX')

tokens = keywords + (
   'PLUS',
   'MINUS',
   'ID',
   'INTEGER',
   'STRING',
   'NEWLINE',
)

t_ignore  = ' \t'

t_PLUS = r'\+'
t_MINUS = r'\-'
t_INTEGER = r'\d+'
t_STRING = r'\".*?\"'

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
"""
define foo box (32 + 45) 16 


statements := single_statement*

single_statement := define_statement
                  | wait_statement

define_statement := 'define' name boxspec

boxspec := 'box' size_spec_opt color_spec_opt pos_spec_opt

"""

def p_statement_display(p):
    "statement : DISPLAY NEWLINE"
    pass

def p_statement_define(p):
    "statement : DEFINE ID BOX box_spec NEWLINE"
    pass

def p_box_spec(p):
    "box_spec : dimension dimension"
    pass

def p_dimension(p):
    "dimension : INTEGER"
    pass

import ply.yacc as yacc
yacc.yacc()

s = """display
define foo box 100 100
"""

# lexer.input(s)
# for tok in lexer:
#     print(tok)
yacc.parse(s)
