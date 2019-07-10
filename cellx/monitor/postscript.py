#!/usr/bin/env python3
#
#
# Copyright (c) 2013-2019, Hiroyuki Ohsaki.
# All rights reserved.
#
# $Id: PostScript.pm,v 1.16 2016/12/08 03:30:10 ohsaki Exp ohsaki $
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

import io
import sys

from cellx.monitor.null import Null

A4_WIDTH_IN_PIXELS = 21.0 / 2.54 * 72
LEFT_MARGIN = A4_WIDTH_IN_PIXELS * 0.01
RIGHT_MARGIN = A4_WIDTH_IN_PIXELS * 0.01

def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

class PostScript(Null):
    def __init__(self, *kargs, **kwargs):
        super().__init__(*kargs, **kwargs)
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='euc-jp')
        print("""\
%!
gsave
""")

    def normalize_position(self, x, y):
        factor = (A4_WIDTH_IN_PIXELS - LEFT_MARGIN - RIGHT_MARGIN) / self.width
        return (LEFT_MARGIN + x * factor,
                LEFT_MARGIN + (self.height - y) * factor)

    def normalize_size(self, l):
        factor = (A4_WIDTH_IN_PIXELS - LEFT_MARGIN - RIGHT_MARGIN) / self.width
        return l * factor

    def gray(self, color, alpha):
        r, g, b, a = self.palette.rgba(color, alpha)
        level = (r + g + b) / 3 / 0xff
        return level

    def _render_fill(self, obj):
        if obj.color is None:
            return
        gray = self.gray(obj.color, obj.alpha)
        print("""\
gsave	
  {} setgray
  fill
grestore""".format(gray))

    def _render_stroke(self, obj):
        if obj.frame_color is None:
            return
        gray = self.gray(obj.frame_color, obj.alpha)
        print("""\
gsave	
  {} setgray
  1 setlinewidth stroke
grestore""".format(gray))

    def _render_box(self, obj):
        name = obj.name
        x, y = self.normalize_position(obj.x, obj.y)
        w = self.normalize_size(obj.width)
        h = self.normalize_size(obj.height)
        x1, y1 = (x - w / 2, y - h / 2)
        x2, y2 = (x + w / 2, y + h / 2)
        print("""\
% box: {}
newpath
  {} {} moveto
  {} {} lineto
  {} {} lineto
  {} {} lineto
closepath""".format(name, x1, y1, x2, y1, x2, y2, x1, y2))
        self._render_fill(obj)
        self._render_stroke(obj)

    def _render_ellipse(self, obj):
        name = obj.name
        x, y = self.normalize_position(obj.x, obj.y)
        rx = self.normalize_size(obj.width / 2)
        ry = self.normalize_size(obj.height / 2)
        print("""\
% ellipse: {}
matrix currentmatrix	% push CTM
  newpath
    {} {} translate
    {} {} scale
    0 0 1 0 360 arc
  closepath
setmatrix		% pop CTM""".format(name, x, y, rx, ry))
        self._render_fill(obj)
        self._render_stroke(obj)

    def draw_line(self, sx, sy, dx, dy, width, color, alpha):
        sx, sy = self.normalize_position(sx, sy)
        dx, dy = self.normalize_position(dx, dy)
        gray = self.gray(color, alpha)
        print("""\
% line
newpath
  {} {} moveto
  {} {} lineto
gsave
  {} setgray
  {} setlinewidth stroke
grestore
""".format(sx, sy, dx, dy, gray, width))

    # taken from Monitro::SDL
    def _render_line(self, obj):
        self.draw_line(obj.x, obj.y, obj.x2, obj.y2, obj.width, obj.color,
                       obj.alpha)

    # taken from Monitro::SDL
    def _render_link(self, obj):
        src, dst = obj.src, obj.dst
        self.draw_line(src.x, src.y, dst.x, dst.y, obj.width, obj.color,
                       obj.alpha)

    def _render_polygon(self, obj):
        name = obj.name
        vertices = obj.vertices()
        print("""\
% polygon: {}
newpath""".format(name))
        v = vertices[0]
        vertices = vertices[1:]
        print("{} {} moveto".format(*self.normalize_position(*v)))
        for x, y in vertices:
            print("{} {} lineto".format(*self.normalize_position(x, y)))

        print("closepath")
        self._render_fill(obj)
        self._render_stroke(obj)

    def _render_string(self, str, x, y, size, gray, align):
        align_ops = ''
        if align == 'center':
            align_ops = """\
/w ({}) stringwidth pop def
w 2 div neg 0 rmoveto""".format(str)
        if align == 'right':
            align_ops = """\
/w ({}) stringwidth pop def
w neg 0 rmoveto""".format(str)
        print("""\
{} {} moveto
{}
gsave
  {} setgray
  ({}) show
grestore""".format(x, y, align_ops, gray, str))

    def _render_spline(self, obj):
        x, y = self.normalize_position(obj.x, obj.y)
        x2, y2 = self.normalize_position(obj.x2, obj.y2)
        x3, y3 = self.normalize_position(obj.x3, obj.y3)
        width = self.normalize_size(obj.width)
        gray = self.gray(obj.color, obj.alpha)
        print("""\
% spline
newpath
  {} {} moveto
  {} {}
  {} {}
  {} {} curveto
gsave
  {} setgray
  {} setlinewidth stroke
grestore""".format(x, y, x, y, x2, y2, x3, y3, gray, width))

    def _render_text(self, obj):
        name = obj.name
        font = 'Helvetica'
        # use Japanese font if any non-ascii character is contained
        if not obj.text.isascii():
            font = 'GothicBBB-Medium-EUC-H'
        x, y = self.normalize_position(obj.x, obj.y)
        size = self.normalize_size(obj.size)
        align = obj.align
        gray = 1 - self.gray(obj.color, obj.alpha)
        print("""\
% text: {}
/{} findfont {} scalefont setfont""".format(name, font, size))
        for str in obj.text.split('\\\\'):
            self._render_string(str, x, y - size / 3.5, size, gray, align)
            y -= size

    # taken from Monitro::SDL
    def _render_wire(self, obj):
        x, y = (obj.x, obj.y)
        x2, y2 = (obj.x2, obj.y2)
        # slightly extend the line length to draw smooth corners
        xsign = sign(x2 - x)
        ysign = sign(y2 - y)
        delta = obj.width / 2
        xmid = (x + x2) / 2
        segments = [[x, y, xmid + xsign * delta, y],
                    [xmid, y - ysign * delta, xmid, y2 + ysign * delta],
                    [xmid - xsign * delta, y2, x2, y2]]
        for l in segments:
            self.draw_line(*l, obj.width, obj.color, obj.alpha)

    def render(self, obj):
        if obj.type_ == 'bitmap':
            self._render_bitmap(obj)
        elif obj.type_ == 'box':
            self._render_box(obj)
        elif obj.type_ == 'ellipse':
            self._render_ellipse(obj)
        elif obj.type_ == 'line':
            self._render_line(obj)
        elif obj.type_ == 'link':
            self._render_link(obj)
        elif obj.type_ == 'polygon':
            self._render_polygon(obj)
        elif obj.type_ == 'spline':
            self._render_spline(obj)
        elif obj.type_ == 'text':
            self._render_text(obj)
        elif obj.type_ == 'wire':
            self._render_wire(obj)

    def display(self):
        print("""\
% display
showpage""")

    def DESTROY(self):
        print("grestore")
