#!/usr/bin/env python3
#
#
# Copyright (c) 2019, Hiroyuki Ohsaki.
# All rights reserved.
#

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from cellx.parser import Parser
from perlcompat import die
import plyplus

GRAMMAR = r"""
@start : (NEWLINE | cmd)+ ; 

@cmd : (   
          animate_cmd
        | attach_cmd 
        | color_cmd 
        | define_cmd
        | display_cmd 
        | fade_cmd 
        | move_cmd 
        | palette_cmd 
        | play_cmd 
        | priority_cmd 
        | resize_cmd 
        | shift_cmd 
        | spring_cmd 
        | wait_cmd 
      ) (NEWLINE | EOF) ;

animate_cmd: ANIMATE pattern geometry ;
attach_cmd: ATTACH name name geometry? ;
color_cmd: COLOR pattern color ;
display_cmd: DISPLAY ;
fade_cmd: FADE pattern ;
move_cmd: MOVE pattern geometry ;
palette_cmd: PALETTE name color ;
play_cmd: PLAY string ;
priority_cmd: PRIORITY pattern number ;
resize_cmd: RESIZE pattern geometry ;
shift_cmd: SHIFT pattern geometry ;
spring_cmd: SPRING pattern (geometry geometry)? ;
wait_cmd: WAIT ;

define_cmd: bitmap_cmd
    | box_cmd
    | ellipse_cmd
    | line_cmd
    | link_cmd
    | polygon_cmd
    | spline_cmd
    | text_cmd
    | wire_cmd 
    ;

bitmap_cmd: DEFINE name BITMAP (option)* string geometry? ;
box_cmd: DEFINE name BOX (option)* (number number (color geometry?)?)? ;
ellipse_cmd: DEFINE name ELLIPSE (option)* (number number (color geometry?)?)? ;
line_cmd: DEFINE name LINE (option)* geometry geometry (number color?)? ;
link_cmd: DEFINE name LINK (option)* name name (number color?)? ;
polygon_cmd: DEFINE name POLYGON (option)* number number (color geometry?)? ;
spline_cmd: DEFINE name SPLINE (option)* geometry geometry geometry (number color)? ;
text_cmd: DEFINE name TEXT (option)* string (number (color geometry?)?)? ;
wire_cmd: DEFINE name WIRE (option)* geometry geometry (number color?)? ;

pattern : name | regexp ;

name: NAME | minus | minus minus ;

color: name
    | number number number number?
    | hexcolor
    | color number
    ;

geometry: number number
    | name (sign number sign number)?
    ;

sign: plus | minus ;

number: '[+-]?[\d.]+' ;

string: '".+?"' | '\'.+?\'';

regexp: '/.+?/';

option: minus name;

WS: ' +' (%ignore);

hexcolor: '#[\da-f]{6,8}';

plus: '\+';
minus: '-';

NAME: '[A-Za-z_][0-9A-Za-z_]*'
        (%unless
    ANIMATE: 'animate';
    ATTACH: 'attach';
    BITMAP: 'bitmap';
    BOX: 'box';
    COLOR: 'color';
    DEFINE: 'define';
    DISPLAY: 'display';
    ELLIPSE: 'ellipse';
    FADE: 'fade';
    LINE: 'line';
    LINK: 'link';
    MOVE: 'move';
    PALETTE: 'palette';
    PLAY: 'play';
    POLYGON: 'polygon';
    PRIORITY: 'priority';
    RESIZE: 'resize';
    SHIFT: 'shift';
    SPLINE: 'spline';
    SPRING: 'spring';
    TEXT: 'text';
    WAIT: 'wait';
    WIRE: 'wire';
        );

NEWLINE: '\n+' (%newline) ;
EOF: '<EOF>' ;
"""

import re


import tbdump

class FullParser(Parser):
    def __init__(self, *kargs, **kwargs):
        super().__init__(*kargs, **kwargs)
        self.parser = plyplus.Grammar(GRAMMAR)

    def parse_line(self, line):
        self.line = line
        if line == '':
            return

        line = re.sub(r'^define +(\S+) +bitmap (\S+)', r'define \1 bitmap "\2"', line)
        line = re.sub(r'^define +(\S+) +text (\S+)', r'define \1 text "\2"', line)


        ast = self.parser.parse(line + '\n')
        print(ast)
        cmd = ast.head
        if cmd == 'color_cmd':
            pattern, color = [str(x) for x in ast.select('*:is-leaf')]
            self.validate_color(color)
            for n in self.expand_name(pattern):
                self.cell.object(n).color = color
        elif cmd == 'define_cmd':
            tree = ast.tail[0]
            atype = tree.head

            # insert dash before option char 
            for x in tree.select('option > name'):
                print(type(x.tail[0]))
                x.tail[0] = plyplus.common.TokValue('-' + x.tail[0])

            name, *args = [str(x) for x in tree.select('*:is-leaf')]
            print('>', name, args)
            if atype == 'bitmap_cmd':
                opts = self.parse_options('bi', args)
                args[0] = args[0].replace('\"', '')
                self.define_bitmap(name, args, opts)
            elif atype == 'box_cmd':
                opts = self.parse_options('f:', args)
                self.define_box(name, args, opts)
            elif atype == 'ellipse_cmd':
                opts = self.parse_options('f:', args)
                self.define_ellipse(name, args, opts)
            elif atype == 'line_cmd':
                opts = self.parse_options('ht', args)
                self.define_line(name, args, opts)
            elif atype == 'link_cmd':
                self.define_link(name, args)
            elif atype == 'text_cmd':
                opts = self.parse_options('lcr', args)
                self.define_text(name, args, opts)
            else:
                die("unknown define command '{}'".format(atype))
        elif cmd == 'display_cmd':
            self.cell.display()
        elif cmd == 'palette_cmd':
            args = [str(x) for x in ast.select('*:is-leaf')]
            self._parse_palette(args)
        elif cmd == 'resize_cmd':
            args = [str(x) for x in ast.select('*:is-leaf')]
            name = args.pop(0)
            w, h = self.expand_position(*args)
            for n in self.expand_name(name):
                self.cell.object(n).resize(w, h)
        elif cmd == 'wait_cmd':
            self.cell.wait()
        else:
            die("unknown command '{}'".format(cmd))
