#!/usr/bin/env python3
#
#
# Copyright (c) 2013-2023, Hiroyuki Ohsaki.
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

from cellx.monitor.postscript import PostScript

class EnhancedPostScript(PostScript):
    def __init__(self, *kargs, **kwargs):
        super().__init__(*kargs, **kwargs)
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

    def _render_text(self, obj):
        name = obj.name
        font = 'Helvetica'
        # Use Japanese font if any non-ascii character is contained.
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
