#!/usr/bin/env python3
#
#
# Copyright (c) 2018-2019, Hiroyuki Ohsaki.
# All rights reserved.
#
# $Id: object.py,v 1.6 2019/03/10 11:49:50 ohsaki Exp ohsaki $
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

import cellx
from perlcompat import die

max_id = 0

class Object:
    def generate_name(self, atype, id_):
        return '_{}{}'.format(atype, id_)

    def __init__(
            self,
            type=None,
            name=None,
            x=None,
            y=None,
            width=None,
            height=None,
            color='white',
            alpha=1,
            priority=0,
            fixed=None,
            visible=True,
            fade_out=False,
            n=None,
            rotation=None,
            text=None,
            size=None,
            align=None,
            file=None,
            x2=None,
            y2=None,
            x3=None,
            y3=None,
            parent=None,
            src=None,
            dst=None,
            frame_color=None,
    ):
        global max_id
        max_id += 1
        if name is None:
            name = self.generate_name(type, max_id)
        self.id_ = max_id
        self.type_ = type
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.frame_color = frame_color
        self.alpha = alpha
        self.priority = priority

        self.fixed = fixed
        self.visible = visible
        self.fade_out = fade_out

        self.n = n
        self.rotation = rotation

        self.text = text
        self.size = size
        self.align = align
        self._text_cache = []

        self.file = file
        self._bitmap_cache = None

        # x2, y2, x3, y3 are used for multipurposes
        # (x2, y2): child: offset to the parent
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3

        self.parent = parent
        self.children = []

        self.src = src
        self.dst = dst

        self.goal_x = None
        self.goal_y = None
        self.velocity = None

    def __repr__(self):
        # box [b1] 24 x 345 @ (34, 38) cyan
        repr = '{} [{}] {} x {} @ ({}, {}) {}\n'.format(
            self.type_, self.name, self.width, self.height, self.x, self.y,
            self.color)
        return repr

    def move(self, x, y):
        """Change the geometry of the object to (X, Y).  If this object has
        children, their geometries are updated."""
        if self.parent:
            die("move: cannot move attached object '{}'".format(self.name))
        else:
            self.x, self.y = x, y
            for child in self.children:
                child.reposition()

    def shift(self, dx, dy):
        """Change the geometry of the object by (DX, DY)."""
        self.move(self.x + dx, self.y + dy)

    def resize(self, width, height):
        """Update the size of the object to WIDTH x HEIGHT."""
        self.width = width
        self.height = height

    def dist_to_goal(self):
        """Return the Euclidian distance to the goal geometry."""
        return math.sqrt((self.goal_x - self.x)**2 + (self.goal_y - self.y)**2)

    def attach(self, parent, dx, dy):
        """Make the current object be a child of PARENT object with the
        positional offset of (DX, DY)."""
        parent.children.append(self)
        self.parent = parent
        self.x2, self.y2 = dx, dy
        self.reposition()

    def reposition(self):
        """Update the geometry of the object according to the position of its
        parent.  If the object has any children, recursively update their
        geometrires."""
        if self.parent:
            self.x = self.parent.x + self.x2
            self.y = self.parent.y + self.y2
        for child in self.children:
            child.reposition()

    def vertices(self):
        """Return the list of geometries of all vertices of the polygon
        object."""
        if self.type_ != 'polygon':
            die("vertices: object type muyst be 'polygon'")
        vertices = []
        theta = cellx.deg2rad(self.rotation) - math.pi / 2
        r = self.width / 2
        for _ in range(self.n):
            vertices.append(
                [self.x + math.cos(theta) * r, self.y + math.sin(theta) * r])
            theta += 2 * math.pi / self.n
        return vertices

    def rotate_around(self, degree, cx, cy):
        """Rotate the geometry of the object by degree DEGREE with the center
        (CX, CY)."""
        theta = cellx.deg2rad(degree)
        (dx, dy) = (self.x - cx, self.y - cy)
        (dx, dy) = (dx * math.cos(theta) + dy * math.sin(theta),
                    dx * math.sin(theta) - dy * math.cos(theta))
        self.move(cx + dx, cy + dy)
