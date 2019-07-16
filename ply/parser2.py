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

#from perlcompat import die, warn, getopts
#import tbdump


from plyplus import Grammar
list_parser = Grammar(r"""
start : (command eol)* ; 
command : alpha_command | animate_command | color_command | 'display' | define_command | kill_command | spring_command | 'wait';

alpha_command: 'alpha' pattern number;
animate_command: 'animate' geometry;
color_command: 'color' pattern color;

define_command: box_command ;
box_command : 'define' name 'box' number number (color)? (geometry)? (option)*;
kill_command: 'kill' pattern ;

sleep_command: 'sleep' number;

spring_command: 'spring' pattern (number number number number)? (option)*;

pattern: name (name)* | regexp ;

option: '-' name;

geometry : number number | name (offset)?;
offset : '\+' number '-' number ;

color: simple_color ('\*' number)?;
simple_color: name | '\#[\da-f]{6,8}' | number ',' number ',' number (',' number)? | name '\*' number; 

name : '\w+' ;
number : '[\d\.]+' ;

regexp: 'r\'.+?\'' ;

eol : '\n' ;
SPACES : ' +' (%ignore) ;
""")

r=list_parser.parse("""\
define b1 box 100 100 cyan
""")
print(r)

