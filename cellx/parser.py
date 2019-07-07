#!/usr/bin/env python3
#
#
# Copyright (c) 2018, Hiroyuki Ohsaki.
# All rights reserved.
#
# $Id: parser.py,v 1.8 2019/07/06 16:10:08 ohsaki Exp ohsaki $
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

import math
import os.path
import re
import time

import cellx
from perlcompat import die

def str2number(v):
    """If V is a string, convert it to a numeric value and return the result.
    Otherwise, V is returned as-is."""
    # FIXME: shoud not check type
    if type(v) != str:
        return v
    elif v.startswith('0x'):
        return int(v, 16)
    elif re.match(r'[\d+-]+$', v):
        return int(v)
    elif re.match(r'[\d.eE+-]+$', v):
        return float(v)
    else:
        return v

def get_args(args, defaults):
    """Convert all strings in list ARGS to numeric values.  If list ARGS is
    shorter than list DEFAULTS, the list is padded with corresponding elements
    in DEFAULTS."""
    args = [str2number(x) for x in args]
    return args + defaults[len(args):]

class Parser:
    def __init__(self, cell=None):
        self.lineno = 0
        self.cell = cell

    def help(self):
        return """\
alpha (name|regexp) alpha
animate name (goal_x goal_y|name[(+|-)dx(+|-)dy])
attach name parent_name dx dy
color (name|regexp) color
define name bitmap file [(x y|name[(+|-)dx(+|-)dy])]
define name box [-f color] [width height color (x y|name[(+|-)dx(+|-)dy])]
define name ellipse [-f color] [rx ry color] [(x y|name[(+|-)dx(+|-)dy])]
define name line [-ht] sx sy dx dy [width color]
define name link src_name dst_name [width color]
define name polygon [-f color] [-r degree] n r [color (x y|name[(+|-)dx(+|-)dy])]
define name spline x1 y1 x2 y2 x3 y3 [width color]
define name text [-lcr] string [size color (x y|name[(+|-)dx(+|-)dy])]
define name wire [-ht] sx sy dx dy [width color]
display
fade (name|regexp)...
fix (name|regexp)...
hide (name|regexp)...
kill (name|regexp)...
move (name|regexp) (x y|name[(+|-)dx(+|-)dy])
palette symbol r g b [alpha]
play file
priority (name|regexp) level
resize (name|regexp) (x y|name[(+|-)dx(+|-)dy])
scale (name|regexp) ratio
shift (name|regexp) dx dy
sleep x
spring [-f filter] [-r degree] (name|regexp)... [x1 y1 x2 y2]
unhide (name|regexp)...
wait
"""

    def abort(self, msg, *args):
        """Display error message MSG with the line number and the content, and
        abort the program execution."""
        die("{}: {}\n{}\n".format(self.lineno, self.line, msg, *args))

    def validate_color(self, color):
        """Check the validity of color name COLOR.  If invalid, abort the
        program execution."""
        try:
            self.cell.monitor.palette.rgba(color)
        except KeyError:
            self.abort("undefined color '{}'".format(color))
        return color

    def expand_numeric_position(self, x, y):
        """Return the abolute geometry of (X, Y).  Namely, if the geometry (X,
        Y) is relative (i.e., specified by a fractional number), it is
        converted to the abolute one.  For instance, (0.5, 0.5) is converted
        to the center of the screen.  (-0.1, 0) is converted to (X, 0) where X
        is the 1/10-th of the screen width."""
        if -1 <= x <= 1:
            x *= self.cell.width
        if -1 <= y <= 1:
            y *= self.cell.height
        return x, y

    def expand_position(self, arg1, arg2=None):
        """Parse arguments ARG1 and ARG2 as the gometry specification, and
        return the geometry.  Types of ARG1 and ARG2 can be either float or
        str.  Arguments can be a reference, a reference with offsets, or a
        pair of numbers.

        Examples:
          term2        the geometry of object 'term2'
          term2+10+10  10 pixels away from object 'term2'
          term2+.1-.2  (+10% of screen width, -20% of screen height) from object 'term2'
          12 34        absolute geometry (12, 34)
          0.2 245      relative & absolute geometry (20% of screen width, 245)
          0.7 0.2      relative geometry (70% of screen width, 20% of screen height)"""

        # FIXME: shoud not check type
        if type(arg1) == str:
            # object name with offset?
            m = re.search(r'(\w+)([+-][\d.]+)([+-][\d.]+)', arg1)
            if m:
                name, dx, dy = m.group(1), m.group(2), m.group(3)
                dx, dy = self.expand_position(dx, dy)
                return (self.cell.object(name).x + dx,
                        self.cell.object(name).y + dy)

            # object name?
            if self.cell.object(arg1):
                return (self.cell.object(arg1).x, self.cell.object(arg1).y)

            # must be positions
            if not re.search(r'[\d.eE+-]+', arg1):
                self.abort("inlvaid positional parameter '%s'", arg1)
            if not re.search(r'[\d.eE+-]+', arg2):
                self.abort("inlvaid positional parameter '%s'", arg2)
            return self.expand_numeric_position(float(arg1), float(arg2))
        else:
            return self.expand_numeric_position(arg1, arg2)

    def expand_palette(self, args):
        """Parse color specifiers ARGS, and return (R, G, B, A) as a list.  If
        the length of ARGS is one, assume it is 32-bit color code."""
        if len(args) == 1:
            v = str2number(args[0])
            r = (v >> 24) & 0xff
            g = (v >> 16) & 0xff
            b = (v >> 8) & 0xff
            a = v & 0xff
            return r, g, b, a
        return [str2number(v) for v in args]

    def expand_name(self, name, allow_create=False, allow_nomatch=False):
        """Expand the name NAME and return the list of matching objects."""
        # magic name
        if name == '-':
            return [None]

        # reference to the last object
        if name == '--':
            return [self.last_name]

        # regular expression
        m = re.match(r'/(.*)/', name)
        if m:
            regexp = m.group(1)
            matches = [name for name in self.cell.all_object_names() \
                    if re.search(regexp, name)]
            if not matches:
                if not allow_nomatch:
                    self.abort(
                        "expand_name: non-matching regexp '{}'".format(regexp))
            return matches

        # number
        if re.match(r'[+-]?[\d.]+', name):
            return [name]

        # existing object
        if self.cell.object(name):
            return [name]

        if allow_create:
            return [name]
        else:
            self.abort("expand_name: invalid name '{}'".format(name))

    def expand_names(self, *names, allow_create=False, allow_nomatch=False):
        """Expand all names in NAMES, and return the list of all matching
        objects."""
        found = []
        for name in names:
            # FIXME: should remove duplicates?
            found.extend(
                self.expand_name(name,
                                 allow_create=allow_create,
                                 allow_nomatch=allow_nomatch))
        return found

    def parse_options(self, template, args):
        """Parse options in arguments ARGS using the UNIX-like options
        template TEMPLATE.  Parsed options with their values are return as a
        dictionary.  Arguments ARGS are shortened to be composed of remaining
        arguments."""
        # FIXME: rewrite using getopt module
        opt_type = {}
        for spec in re.findall(r'\w:?', template):
            if ':' in spec:
                opt_type[spec[0]] = 'with_arg'
            else:
                opt_type[spec[0]] = 'switch'

        opts = {}
        while args:
            m = re.match(r'-(\w)(.*)', args[0])
            if not m:
                break
            char, rest = m.group(1), m.group(2)
            if opt_type[char] == 'with_arg':
                if len(rest) > 0:
                    args.pop(0)
                    opts[char] = rest
                else:
                    args.pop(0)
                    opts[char] = args.pop(0)
            elif opt_type[char] == 'switch':
                opts[char] = True
                if len(rest) > 0:
                    args[0] = '-' + rest
                else:
                    args.pop(0)
            else:
                self.abort("unrecognized option '{}'".format(char))
        return opts

    def define_bitmap(self, name, args, opts=None):
        """Createa a bitmap object with name NAME.  Parameters (filename, x
        and y) are taken from ARGS."""
        file, x, y = get_args(args, [None, 0.5, 0.5])
        if not os.path.exists(file):
            if os.path.exists('figure/' + file):
                file = 'figure/' + file
            else:
                self.abort('define_bitmap: not found: {}'.format(file))
        x, y = self.expand_position(x, y)

        obj = cellx.Object(
            type='bitmap',
            name=name,
            file=file,
            x=x,
            y=y,
        )
        self.cell.add(obj)
        return obj

    def define_box(self, name, args, opts=None):
        """Createa a box object with name NAME.  Parameters (width, height,
        color, x, and y) are taken from ARGS.  Frame color can be specified
        with 'f' option (e.g., opts = { 'f': 'cyan'})."""
        width, height, color, x, y = get_args(args,
                                              [10, 10, 'white', 0.5, 0.5])
        width, height = self.expand_position(width, height)
        self.validate_color(color)
        x, y = self.expand_position(x, y)

        obj = cellx.Object(
            type='box',
            name=name,
            width=width,
            height=height,
            color=color,
            x=x,
            y=y,
            frame_color=opts.get('f', None),
        )
        self.cell.add(obj)
        return obj

    def define_ellipse(self, name, args, opts):
        """Createa an ellipse with name NAME.  Parameters (rx, ry, color, x,
        and y) are taken from ARGS.  Frame color can be specified with 'f'
        option (e.g., opts = { 'f': 'cyan'})."""
        rx, ry, color, x, y = get_args(args, [10, 10, 'white', 0.5, 0.5])
        rx, ry = self.expand_position(rx, ry)
        self.validate_color(color)
        x, y = self.expand_position(x, y)

        obj = cellx.Object(
            type='ellipse',
            name=name,
            width=rx * 2,
            height=ry * 2,
            color=color,
            x=x,
            y=y,
            frame_color=opts.get('f', None),
        )
        self.cell.add(obj)
        return obj

    def define_link(self, name, args):
        """Createa a link named NAME connecting two cell objects.  Parameters
        (src_name, dst_name, width, and color) are taken from ARGS."""
        src_name, dst_name, width, color = get_args(args,
                                                    [None, None, 1, 'white'])
        if not self.cell.object(src_name):
            self.abort("undefined object '{}'".format(src_name))
        if not self.cell.object(dst_name):
            self.abort("undefined object '{}'".format(dst_name))
        self.validate_color(color)

        obj = cellx.Object(
            type='link',
            name=name,
            src=self.cell.object(src_name),
            dst=self.cell.object(dst_name),
            width=width,
            color=color,
            priority=-20,
        )
        self.cell.add(obj)
        return obj

    def _define_arrowhead(self, name, sx, sy, dx, dy, size, color):
        """Create an arrowhead object named NAME for line segment connecting
        from (SX, SY) to (DX, DY) with size SIZE and color COLOR."""
        rotation = 90 + cellx.rad2deg(math.atan2(dy - sy, dx - sx))
        obj = self.define_polygon(name, [3, size, color, dx, dy],
                                  {'r': rotation})
        # FIXME: arrow head shoul be attached
        return obj

    def define_line(self, name, args, opts):
        """Createa a line object with name NAME.  Parameters (x, y, x2, y2,
        width and color) are taken from ARGS.  Arrowhead and arrowtail are
        created if 'h' option and 't' option are specified, respectively."""
        x, y, x2, y2, width, color = get_args(
            args, [0.25, 0.25, 0.75, 0.75, 1, 'white'])
        x, y = self.expand_position(x, y)
        x2, y2 = self.expand_position(x2, y2)
        self.validate_color(color)

        obj = cellx.Object(
            type='line',
            name=name,
            x=x,
            y=y,
            x2=x2,
            y2=y2,
            width=width,
            color=color,
            priority=-10,
        )
        self.cell.add(obj)

        # FIXME: head size must be configurable
        if 'h' in opts:
            self._define_arrowhead(name + '_head', x, y, x2, y2, width * 2,
                                   color)
        if 't' in opts:
            self._define_arrowhead(name + '_tail', x2, y2, x, y, width * 2,
                                   color)
        return obj

    def define_polygon(self, name, args, opts):
        """Createa a polygon with name NAME.  Parameters (n, r, color, x, y)
        are taken from ARGS.  Rotation and frame color can be specified with
        'r' option and 'f' option, respectively."""
        n, r, color, x, y = get_args(args, [3, 10, 'white', 0.5, 0.5])
        self.validate_color(color)
        x, y = self.expand_position(x, y)

        obj = cellx.Object(
            type='polygon',
            name=name,
            n=n,
            width=r * 2,
            height=r * 2,
            color=color,
            x=x,
            y=y,
            rotation=float(opts.get('r', 0)),
            frame_color=opts.get('f', None),
        )
        self.cell.add(obj)
        return obj

    def define_spline(self, name, args, opts):
        """Createa a spline curve object with name NAME.  Parameters (x, y,
        x2, y2, x3, y3, width, color) are taken from ARGS.  Arrowhead and
        arrowtail are created if 'h' option and 't' option are specified,
        respectively."""
        x, y, x2, y2, x3, y3, width, color = get_args(
            args, [0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1, 'white'])
        x, y = self.expand_position(x, y)
        x2, y2 = self.expand_position(x2, y2)
        x3, y3 = self.expand_position(x3, y3)
        self.validate_color(color)

        obj = cellx.Object(
            type='spline',
            name=name,
            x=x,
            y=y,
            x2=x2,
            y2=y2,
            x3=x3,
            y3=y3,
            width=width,
            color=color,
            priority=-10,
        )
        self.cell.add(obj)

        # FIXME: head size must be configurable
        if 'h' in opts:
            self._define_arrowhead(name + '_head', x2, y2, x3, y3, width * 2,
                                   color)
        if 't' in opts:
            self._define_arrowhead(name + '_tail', x2, y2, x, y, width * 2,
                                   color)
        return obj

    def define_text(self, name, args, opts):
        """Createa a text object with name NAME.  Parameters (text, size,
        color, x and y) are taken from ARGS.  Text alignment can be specified
        with 'l' option (left justified) and 'r' option (right justified)."""
        text, size, color, x, y = get_args(args, ['', 16, 'white', 0.5, 0.5])
        text = re.sub(r'__', ' ', text)
        self.validate_color(color)
        x, y = self.expand_position(x, y)
        align = 'center'
        if opts.get('l', None):
            align = 'left'
        if opts.get('r', None):
            align = 'right'

        obj = cellx.Object(
            type='text',
            name=name,
            text=text,
            align=align,
            size=size,
            x=x,
            y=y,
            color=color,
            priority=10,
        )
        self.cell.add(obj)
        return obj

    # FIXME: merge with define_line since these are almost identical
    # FIXME: automatically detect horizontal/vertical directions
    def define_wire(self, name, args, opts):
        """Createa a wire object with name NAME.  Parameters (x, y, x2, y2,
        width and color) are taken from ARGS.  Arrowhead and arrowtail are
        created if 'h' option and 't' option are specified,
        respectively."""
        x, y, x2, y2, width, color = get_args(
            args, [0.25, 0.25, 0.75, 0.75, 1, 'white'])
        x, y = self.expand_position(x, y)
        x2, y2 = self.expand_position(x2, y2)
        self.validate_color(color)

        obj = cellx.Object(
            type='wire',
            name=name,
            x=x,
            y=y,
            x2=x2,
            y2=y2,
            width=width,
            color=color,
            priority=-10,
        )
        self.cell.add(obj)

        # FIXME: head size must be configurable
        # force arrowhead to have a right angle
        if 'h' in opts:
            self._define_arrowhead(name + '_head', x, y2, x2, y2, width * 2,
                                   color)
        if 't' in opts:
            self._define_arrowhead(name + '_tail', x2, y, x, y, width * 2,
                                   color)
        return obj

    def parse_single_line(self, line):
        """Parse a sing line LINE, which can be either a simple statement, a
        comment, or a blank line."""

        def _parse_define(self, args):
            """Parse arguments ARGS for define command."""
            name, atype, *args = args
            name = self.expand_name(name, allow_create=True)[0]
            atype = atype.lower()
            if atype.startswith('bi'):  # bitmap
                self.define_bitmap(name, args)
            elif atype.startswith('bo'):  # box
                opts = self.parse_options('f:', args)
                self.define_box(name, args, opts)
            elif atype.startswith('e'):  # ellipse
                opts = self.parse_options('f:', args)
                self.define_ellipse(name, args, opts)
            elif atype.startswith('line'):  # line
                opts = self.parse_options('ht', args)
                self.define_line(name, args, opts)
            elif atype.startswith('link'):  # link
                self.define_link(name, args)
            elif atype.startswith('p'):  # polygon
                opts = self.parse_options('r:f:', args)
                self.define_polygon(name, args, opts)
            elif atype.startswith('s'):  # spline
                opts = self.parse_options('ht', args)
                self.define_spline(name, args, opts)
            elif atype.startswith('t'):  # text
                opts = self.parse_options('lcr', args)
                self.define_text(name, args, opts)
            elif atype.startswith('w'):  # wire
                opts = self.parse_options('ht', args)
                self.define_wire(name, args, opts)
            else:
                self.abort("unknown object type '{}' in define.".format(atype))

        def _parse_spring(self, args):
            """Parse arguments ARGS for spring command."""
            opts = self.parse_options('f:r:', args)
            x1, y1 = self.cell.width * .05, self.cell.height * .05
            x2, y2 = self.cell.width * .95, self.cell.height * .95
            args = self.expand_names(*args)
            if len(args) > 4 and re.match(r'[+-]?[\d.]+', args[-3]) \
                and re.match(r'[+-]?[\d.]+', args[-1]):
                x1, y1, x2, y2 = args[-4:]
                del args[-4:]
                x1, y1 = self.expand_position(x1, y1)
                x2, y2 = self.expand_position(x2, y2)
            self.cell.spring(x1, y1, x2, y2, args, opts)

        # remove comment
        line = re.sub(r'^#.*', '', line)
        # remove indentation
        line = re.sub(r'^\s+', '', line)
        if not line:
            return

        args = line.split()
        cmd = args.pop(0).lower()
        # record the second argument (may be object name) for later reference
        current_name = args[0] if args else None

        if cmd.startswith('al'):  # alpha
            name, alpha = args
            for n in self.expand_name(name):
                self.cell.object(n).alpha(alpha)
        elif cmd.startswith('an'):  # animate
            name = args.pop(0)
            x, y = self.expand_position(*args)
            for n in self.expand_name(name):
                self.cell.animate(n, x, y)
        elif cmd.startswith('at'):  # attach
            name, parent, dx, dy = get_args(args, [None, None, 0., 0.])
            dx, dy = self.expand_position(dx, dy)
            for n in self.expand_name(name):
                self.cell.object(n).attach(self.cell.object(parent), dx, dy)
        elif cmd.startswith('c'):  # color
            name, color = args
            self.validate_color(color)
            for n in self.expand_name(name):
                self.cell.object(n).color = color
        elif cmd.startswith('de'):  # define
            _parse_define(self, args)
        elif cmd.startswith('di'):  # display
            self.cell.display()
        elif cmd.startswith('fa'):  # fade
            for n in self.expand_names(*args):
                self.cell.object(n).fade_out = True
        elif cmd.startswith('fi'):  # fix
            for n in self.expand_names(*args):
                self.cell.object(n).fixed = True
        elif cmd.startswith('h'):  # hide
            for n in self.expand_names(*args):
                self.cell.object(n).visible = 0
        elif cmd.startswith('k'):  # kill
            for n in self.expand_names(*args, allow_nomatch=1):
                self.cell.delete(n)
        elif cmd.startswith('m'):  # move
            name = args.pop(0)
            (x, y) = self.expand_position(*args)
            for n in self.expand_name(name):
                self.cell.object(n).move(x, y)
        elif cmd.startswith('pa'):  # palette
            color = args.pop(0)
            r, g, b, a = self.expand_palette(args)
            self.cell.monitor.palette.define_color(color, r, g, b, a)
        elif cmd.startswith('pl'):  # play
            file = args.pop(0)
            if not os.path.exists(file):
                self.abort("play: '{}' not found".format(file))
            self.cell.monitor.play(file)
        elif cmd.startswith('pr'):  # priority
            name, level = args
            for n in self.expand_name(name):
                self.cell.object(n).priority = float(level)
        elif cmd.startswith('r'):  # resize
            name = args.pop(0)
            w, h = self.expand_position(*args)
            for n in self.expand_name(name):
                self.cell.object(n).resize(w, h)
        elif cmd.startswith('sc'):  # scale
            name, ratio = args
            for n in self.expand_name(name):
                self.cell.object(n).scale = ratio
        elif cmd.startswith('sh'):  # shift
            name, dx, dy = args
            dx, dy = self.expand_position(dx, dy)
            for n in self.expand_name(name):
                self.cell.object(n).shift(dx, dy)
        elif cmd.startswith('sl'):  # sleep
            secs = args.pop(0)
            time.sleep(secs)
        elif cmd.startswith('sp'):  # spring
            _parse_spring(self, args)
        elif cmd.startswith('u'):  # unhide
            for n in self.expand_names(*args):
                self.cell.object(n).visible = True
        elif cmd.startswith('w'):  # wait
            self.cell.wait()
        else:
            self.abort("illegal command '%s'", cmd)

        if self.cell.object(current_name):
            self.last_name = current_name

    def parse_line(self, line):
        """Parse a line LINE written in the cell language.  LINE can have
        multiple statements (compound statements) separated with
        semicolons. """
        self.line = line
        self.lineno += 1
        # FIXME: should ignore semicolon in string
        for l in line.split(';'):
            self.parse_single_line(l)
