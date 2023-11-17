#!/usr/bin/env python3
#
#
# Copyright (c) 2018, Hiroyuki Ohsaki.
# All rights reserved.
#
# $Id: sdl.py,v 1.9 2019/07/06 16:11:41 ohsaki Exp ohsaki $
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
import struct

import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut
import cellx
import pygame
from cellx.monitor.sdl import SDL

import tbdump

class OpenGL(SDL):
    def __init__(self, *kargs, **kwargs):
        super().__init__(*kargs, **kwargs)

    def init(self):
        super().init()
        width, height = self.width, self.height
        self.hwscreen = pygame.display.set_mode(
            (width, height), pygame.OPENGL | pygame.DOUBLEBUF)
        glut.glutInit()

        # Initialize projection and model view matrices.
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(-.5, .5, -.5, .5, -100, 100)
        gl.glMatrixMode(gl.GL_MODELVIEW)

        gl.glShadeModel(gl.GL_SMOOTH)
        # FIXME: Not supported?
        # gl.glShadeModel(gl.GL_LINE_SMOOTH)

        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)

        # Enable alpha-blending.
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # Enable lighting.
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_LIGHT0)
        gl.glDepthFunc(gl.GL_LESS)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_NORMALIZE)
        gl.glEnable(gl.GL_COLOR_MATERIAL)

        # Configure lights.
        mat_specular = (1, 1, 0, 1)
        gl.glMaterial(gl.GL_FRONT, gl.GL_SPECULAR, *mat_specular)
        mat_diffuse = (0, 1, 1, 1)
        gl.glMaterial(gl.GL_FRONT, gl.GL_DIFFUSE, *mat_diffuse)
        gl.glMaterialf(gl.GL_FRONT, gl.GL_SHININESS, 50)
        light_position = (-.25, .25, .5, 0)
        gl.glLight(gl.GL_LIGHT0, gl.GL_POSITION, *light_position)
        gl.glLight(gl.GL_LIGHT0, gl.GL_AMBIENT, (.3, .3, .3, 1))
        # FIXME: Not supported?
        # gl.glLightModel(gl.GL_LIGHT_MODEL_AMBIENT, (.3, .3, .3, 1))

    def normalize_position(self, x, y):
        return (x - self.width / 2) / self.width, (
            y - self.height / 2) / self.height

    def normalize_size(self, l):
        return l / self.width

    def draw_line(self, sx, sy, dx, dy, width, color, alpha):
        sx, sy = self.normalize_position(sx, sy)
        dx, dy = self.normalize_position(dx, dy)
        color = self.palette.rgba(color, alpha)
        gl.glLineWidth(width)
        gl.glColor4ub(*color)
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2d(sx, sy)
        gl.glVertex2d(dx, dy)
        gl.glEnd()

    def _render_box(self, obj):
        x, y = self.normalize_position(obj.x, obj.y)
        w, h = self.normalize_size(obj.width), self.normalize_size(obj.height)
        color = self.palette.rgba(obj.color, obj.alpha)
        gl.glColor4ub(*color)
        gl.glPushMatrix()
        gl.glTranslatef(x, y, obj.priority)
        gl.glScalef(w, h, (w + h) / 2)
        gl.glMaterial(gl.GL_FRONT, gl.GL_EMISSION, (.2, .2, 0, 1))
        glut.glutSolidCube(1)
        gl.glMaterial(gl.GL_FRONT, gl.GL_EMISSION, (0, 0, 0, 1))
        gl.glPopMatrix()

    def _render_ellipse(self, obj):
        x, y = self.normalize_position(obj.x, obj.y)
        r = self.normalize_size(obj.width / 2)
        color = self.palette.rgba(obj.color, obj.alpha)
        gl.glColor4ub(*color)
        gl.glPushMatrix()
        gl.glTranslatef(x, y, obj.priority)
        glut.glutSolidSphere(r, 20, 20)
        gl.glPopMatrix()

    def render_objects(self, objs):
        # FIXME: support `fix' objects.
        super().render_objects(objs)

    def _clear(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        xoffset, yoffset = 0, 0
        zoom = .7
        gl.glMatrixMode(gl.GL_PROJECTION)
        # gl.glLoadIdentity();
        # gl.glOrtho(
        #     xoffset - .5 * zoom,
        #         xoffset + .5 * zoom,
        #             yoffset - .5 * zoom,
        #                 yoffset + .5 * zoom,
        #                     -100, 100
        #                         )

        gl.glMatrixMode(gl.GL_MODELVIEW);
        # gl.glLoadIdentity();


    def _display(self):
        pygame.display.flip()


        gl.glRotatef(.01, .01, .02, 1)
