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
        mat_diffuse = (0, 1, 1, 1)
        light_position = (-.25, .25, .5, 0)
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_SPECULAR,
                        struct.pack('4f', *mat_specular))
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_DIFFUSE,
                        struct.pack('4f', *mat_diffuse))
        gl.glMaterialf(gl.GL_FRONT, gl.GL_SHININESS, 50)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION,
                     struct.pack('4f', *light_position))
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT,
                     struct.pack('4f', .3, .3, .3, 1))
        gl.glLightModelfv(gl.GL_LIGHT_MODEL_AMBIENT,
                          struct.pack('4f', .3, .3, .3, 1))

    def normalize_position(self, x, y):
        return (x - self.width / 2) / self.width, (
            y - self.height / 2) / self.height

    def normalize_size(self, l):
        return l / self.width

    def _render_box(self, obj):
        x, y = self.normalize_position(obj.x, obj.y)
        w, h = self.normalize_size(obj.width), self.normalize_size(obj.height)
        color = self.palette.rgba(obj.color, obj.alpha)
        gl.glColor4ub(*color)
        gl.glPushMatrix()
        gl.glTranslatef(x, y, obj.priority)
        gl.glScalef(w, h, (w + h) / 2)
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_EMISSION,
                        struct.pack('4f', .2, .2, 0, 1))
        glut.glutSolidCube(1)
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_EMISSION,
                        struct.pack('4f', 0, 0, 0, 1))
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

        pygame.display.flip()

        pygame.display.flip()
        import time
        time.sleep(10)

    def _display(self):
        pygame.display.flip()
