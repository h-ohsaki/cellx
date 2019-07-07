#!/usr/bin/env python3
#
#
# Copyright (c) 2018-2019, Hiroyuki Ohsaki.
# All rights reserved.
#
# $Id: null.py,v 1.4 2019/03/10 11:49:59 ohsaki Exp ohsaki $
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

    def render(self, obj):
        pass

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
