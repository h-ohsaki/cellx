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
command : alpha_command | animate_command | color_command | 'display' | define_command ;

alpha_command: 'alpha' pattern number;
animate_command: 'animate' geometry;
color_command: 'color' pattern color;

define_command: box_command ;
box_command : 'define' name 'box' number number (color)? (geometry)?;

pattern: name | regexp ;

geometry : number number | name (offset)?;
offset : '\+' number '-' number ;

color: name | '\#[\da-f]{6,8}'; 

name : '\w+' ;
number : '[\d\.]+' ;

regexp: 'r\'.+?\'' ;

eol : '\n' ;
SPACES : ' +' (%ignore) ;
""")

r=list_parser.parse("""\
color b4 red
color b4 #123456
color b4 #12345678
alpha r'^b' .4
display
define foo box 100 .4 white b1
define foo box 100 .4 white b1+4-20
define foo box 100 .4 white 124 333
""")
print(r)

