#!/usr/bin/env python3
#
#
# Copyright (c) 2018-2023, Hiroyuki Ohsaki.
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

import cellx.monitor.color

class Null:
    def __init__(self,
                 width=800,
                 height=600,
                 color_scheme=0,
                 alpha=1,
                 outfile=None,
                 *kargs,
                 **kwargs):
        self.width = width
        self.height = height
        self.alpha = alpha
        self.outfile = outfile

        self.palette = cellx.monitor.color.Palette(color_scheme=color_scheme)
        self.palette.reset()

    def draw_line(self, sx, sy, dx, dy, width, color, alpha):
        pass

    def _render_bitmap(self, obj):
        pass

    def _render_box(self, obj):
        pass

    def _render_ellipse(self, obj):
        pass

    def _render_line(self, obj):
        """Render a line segment with specified attributes.  This method
        renders a line segment with the specified starting and ending
        coordinates, line width, color, and alpha transparency. It utilizes
        the 'draw_line' method to perform the rendering."""
        self.draw_line(obj.x, obj.y, obj.x2, obj.y2, obj.width, obj.color,
                       obj.alpha)

    def _render_link(self, obj):
        src, dst = obj.src, obj.dst
        self.draw_line(src.x, src.y, dst.x, dst.y, obj.width, obj.color,
                       obj.alpha)

    def _render_spline(self, obj):
        pass

    def _render_polygon(self, obj):
        pass

    def _render_text(self, obj):
        pass

    def _render_wire(self, obj):
        """Render a wire or line with specified attributes.  This method
        renders a wire or line with the specified starting and ending
        coordinates, line width, color, and alpha transparency. It extends the
        line slightly to draw smooth corners by splitting it into
        segments. Each segment is rendered using the 'draw_line' method."""
        x, y = obj.x, obj.y
        x2, y2 = obj.x2, obj.y2
        # Slightly extend the line length to draw smooth corners.
        xsign = cellx.cmp(x2 - x, 0)
        ysign = cellx.cmp(y2 - y, 0)
        delta = obj.width / 2
        xmid = (x + x2) / 2
        segments = [[x, y, xmid + xsign * delta, y], \
            [xmid, y - ysign * delta, xmid, y2 + ysign * delta], \
            [xmid - xsign * delta, y2, x2, y2]]
        for segment in segments:
            self.draw_line(*segment, obj.width, obj.color, obj.alpha)

    def render(self, obj):
        """Render an object with its specified type-specific rendering method.
        This method renders an object using its specified rendering method
        based on its 'type_' attribute. The 'type_' attribute determines the
        type of object to be rendered, such as 'bitmap', 'box', 'ellipse',
        'line', 'link', 'polygon', 'spline', 'text', or 'wire'. The
        appropriate rendering method is called for the given object."""
        type = obj.type_
        if type == 'bitmap':
            self._render_bitmap(obj)
        elif type == 'box':
            self._render_box(obj)
        elif type == 'ellipse':
            self._render_ellipse(obj)
        elif type == 'line':
            self._render_line(obj)
        elif type == 'link':
            self._render_link(obj)
        elif type == 'polygon':
            self._render_polygon(obj)
        elif type == 'spline':
            self._render_spline(obj)
        elif type == 'text':
            self._render_text(obj)
        elif type == 'wire':
            self._render_wire(obj)

    def render_objects(self, objs):
        for obj in objs:
            self.render(obj)

    def display(self):
        pass

    def clear(self):
        pass

    def wait(self):
        pass

    def play(self, file):
        pass
