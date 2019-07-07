#!/usr/bin/env python3
#
#
# Copyright (c) 2018, Hiroyuki Ohsaki.
# All rights reserved.
#
# $Id: cell.py,v 1.8 2019/03/10 11:49:46 ohsaki Exp $
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
import os
import re
import tempfile
import time

import cellx
from perlcompat import die

class Cell:
    def __init__(self,
                 width=800,
                 height=600,
                 monitor=None,
                 frame_rate=30,
                 rate_limit=30):
        self.width = width
        self.height = height
        self.monitor = monitor
        self.frame_rate = frame_rate
        self.rate_limit = rate_limit
        self.objects = {}
        self.palette = {}
        self.frame_count = 0
        self.time_started = time.time()
        self.last_display = None

    def object(self, name):
        """Return the cell object having name NAME."""
        return self.objects.get(name, None)

    def all_object_names(self):
        """Return the list of all cell object names."""
        return self.objects.keys()

    def all_objects(self):
        """Return the list of all cell objects."""
        return self.objects.values()

    def add(self, obj):
        """Register cell object OBJ.  If the cell object the same name already
        exists, it is overwritten; i.e., the older object is simply
        discarded."""
        self.objects[obj.name] = obj

    def delete(self, name):
        """Unregister cell object having name NAME."""
        try:
            del self.objects[name]
        except KeyError:
            die("delete: cannot delete non-existing object '{}'".format(name))

    def animate(self, name, x, y):
        """Set the goal of cell object NAME to the geometry (X, Y)."""
        obj = self.object(name)
        if not obj:
            die("animate: object '{}' not found".format(name))
        obj.goal_x, obj.goal_y = x, y
        obj.velocity = max(obj.dist_to_goal() / self.frame_rate, 1.)

    def as_dot_string(self, names):
        """Generate a string representing all cell objects and their linkages
        as an undirected graph in the DOT (GraphViz) format."""
        astr = 'graph export {\n'
        is_exported = {}
        for name in names:
            # FIXME: node size should use object width and height
            astr += '  "{}" [width="2"];\n'.format(name)
            is_exported[name] = True
        for obj in self.all_objects():
            if obj.type_ == 'link':
                src, dst = obj.src.name, obj.dst.name
                if is_exported.get(src, None) and is_exported.get(dst, None):
                    astr += '"{}" -- "{}";\n'.format(src, dst)
        astr += '}\n'
        return astr

    def fit_within(self, x1, y1, x2, y2, names):
        """Map the geometry of all cell objects in NAMES within the region of
        corners (X1, Y1) and (X2, Y2).  For instance, the object at the most
        south-west position is moved to (X1, Y1).  The object at the most
        north-east position is moved to (X2, Y2).  The relative geometries of
        objects are preserved."""
        xmin = min([self.object(name).x for name in names])
        xmax = max([self.object(name).x for name in names])
        ymin = min([self.object(name).y for name in names])
        ymax = max([self.object(name).y for name in names])
        for name in names:
            obj = self.object(name)
            x, y = obj.x, obj.y
            x = x1 + (x2 - x1) * (x - xmin) / (xmax - xmin)
            y = y1 + (y2 - y1) * (y - ymin) / (ymax - ymin)
            obj.move(x, y)

    def spring(self, x1, y1, x2, y2, names, opts):
        """Automatically position all objects in NAMES within the area
        surrounded by (X1, Y1) and (X2, Y2).  Options are passed with
        dictionary OPTS.  OPTS['f'] specifies a layout command (default:
        'neato').  OPTS['r'] specifies the rotation in degrees (default:
        0)."""
        filter = opts.get('f', 'neato')
        rotate = opts.get('r', 0)

        # export parent objects in DOT format
        tmpf = tempfile.NamedTemporaryFile(delete=False)
        pipe = os.popen('{} >{}'.format(filter, tmpf.name), mode='w')
        names = [name for name in names \
                    if not self.object(name).parent and self.object(name).type_ != 'link'
        ]
        pipe.write(self.as_dot_string(names))
        pipe.close()

        # parse GraphViz output and extract object positions
        buf = tmpf.read().decode()
        buf = re.sub('\n', '', buf)
        for line in buf.split(']'):
            m = re.search(r'(\S+)\s*\[.*pos="([\d.-]+),([\d.-]+)",', line)
            if m:
                name, x, y = m.group(1), float(m.group(2)), float(m.group(3))
                name = name.replace('\"', '')
                self.object(name).move(x, y)

        # rotate all objects if necessary
        if rotate:
            for name in names:
                self.object(name).rotate_around(rotate,
                                                self.width() / 2,
                                                self.height() / 2)
        # rescale all objects to fit within the area
        self.fit_within(x1, y1, x2, y2, names)

    def display(self):
        """Display all cell objects through its monitor object.  Render
        animation of objects with their goals by gradually changing their
        geometries toward their goals.  Fading objects are also rendered by
        gradually changig its alpha channle."""

        def _display(self, objects):
            if not self.last_display:
                self.last_display = time.time()
            # actual rendering is performed by the monitor object
            self.monitor.clear()
            self.monitor.render_objects(objects)
            self.monitor.display()
            self.frame_count += 1

            # adjust the frame rate if necessary
            if self.rate_limit:
                if time.time() - self.last_display < 1 / self.rate_limit:
                    delay = 1 / self.rate_limit - (time.time() -
                                                   self.last_display)
                    if delay > 0:
                        time.sleep(delay)
                self.last_display = time.time()

        def _update_position(self, obj):
            dx = obj.goal_x - obj.x
            dy = obj.goal_y - obj.y
            # close encough to the destination?
            if abs(dx) < obj.velocity and abs(dy) < obj.velocity:
                obj.velocity = None
                return
            dist = math.sqrt(dx**2 + dy**2)
            obj.shift(dx / dist * obj.velocity, dy / dist * obj.velocity)

        def _update_alpha(self, obj):
            obj.alpha = obj.alpha - 1 / self.frame_rate
            if obj.alpha <= 0:
                self.delete(obj.name)
                sorted_objs.remove(obj)

        objs = [obj for obj in self.all_objects() if obj.visible]
        sorted_objs = sorted(objs, key=lambda x: x.priority)
        # loop while any object is moving or fading
        while True:
            changed = False
            for obj in sorted_objs:
                if obj.velocity:  # is moving?
                    _update_position(self, obj)
                    changed = True
                if obj.fade_out:  # is fading?
                    _update_alpha(self, obj)
                    changed = True
            _display(self, sorted_objs)
            if not changed:
                break
        self.update_status()

    def wait(self):
        """Perform wait operation through the monior object."""
        self.monitor.wait()

    def update_status(self):
        """Redefine the cell object with name '_status', which is used to
        display the running status."""

        def status_string(self):
            """Compose and return a string summarizing the current display status."""
            elapsed = time.time() - self.time_started
            if elapsed <= 1.:
                return ''
            fps = self.frame_count / elapsed
            nobjs = len(self.objects)
            return 'FPS: {:.2f}, OBJ: {}'.format(fps, nobjs)

        # FIXME: avoid hard-coding
        obj = cellx.Object(
            type='text',
            name='_status',
            text=status_string(self),
            size=10,
            x=96,
            y=self.height - 10,
            color='white',
            priority=10,
        )
        self.add(obj)
