#!/usr/bin/env python3
#
#
# Copyright (c) 2023, Hiroyuki Ohsaki.
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

import math

from cellx.monitor.null import Null
import OpenGL.GL as gl
import OpenGL.GLUT as glut

FONT_HIRO16B = """\
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
38 44 40 38 04 44 38 00 11 11 11 1f 11 11 11 00
38 44 40 38 04 44 38 00 11 11 0a 04 0a 11 11 00
7c 40 40 78 40 40 7c 00 11 11 0a 04 0a 11 11 00
7c 40 40 78 40 40 7c 00 1f 04 04 04 04 04 04 00
7c 40 40 78 40 40 7c 00 0e 11 11 11 15 12 0d 00
10 28 44 7c 44 44 44 00 11 12 14 18 14 12 11 00
78 44 44 78 44 44 78 00 10 10 10 10 10 10 1f 00
78 44 44 78 44 44 78 00 0e 11 10 0e 01 11 0e 00
44 44 44 7c 44 44 44 00 1f 04 04 04 04 04 04 00
40 40 40 40 40 40 7c 00 1f 10 10 1e 10 10 10 00
44 44 44 7c 44 44 44 00 11 1b 1b 15 15 11 11 00
38 44 40 40 40 44 38 00 10 10 10 10 10 10 1f 00
38 44 40 40 40 44 38 00 1e 11 11 1e 14 12 11 00
38 44 40 38 04 44 38 00 0e 11 11 11 11 11 0e 00
38 44 40 38 04 44 38 00 0e 04 04 04 04 04 0e 00
78 44 44 44 44 44 78 00 1f 10 10 1e 10 10 1f 00
78 44 44 44 44 44 78 00 04 0c 04 04 04 04 0e 00
78 44 44 44 44 44 78 00 0e 11 01 02 04 08 1f 00
78 44 44 44 44 44 78 00 0e 11 01 0e 01 11 0e 00
78 44 44 44 44 44 78 00 02 04 0a 12 1f 02 02 00
44 44 64 54 4c 44 44 00 11 12 14 18 14 12 11 00
38 44 40 38 04 44 38 00 11 11 19 15 13 11 11 00
7c 40 40 78 40 40 7c 00 1e 11 11 1e 11 11 1e 00
38 44 40 40 40 44 38 00 11 11 19 15 13 11 11 00
7c 40 40 78 40 40 7c 00 11 1b 1b 15 15 11 11 00
38 44 40 38 04 44 38 00 1e 11 11 1e 11 11 1e 00
7c 40 40 78 40 40 7c 00 0e 11 10 10 10 11 0e 00
00 00 08 08 04 04 7e 04 04 08 08 00 00 00 00 00
00 00 10 10 20 20 7e 20 20 10 10 00 00 00 00 00
00 00 08 08 1c 1c 2a 2a 08 08 08 08 08 08 00 00
00 00 08 08 08 08 08 08 2a 2a 1c 1c 08 08 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 18 18 18 18 18 18 18 00 18 18 18 00 00
00 00 00 36 36 36 36 00 00 00 00 00 00 00 00 00
00 00 00 36 36 36 7f 36 36 36 7f 36 36 36 00 00
00 00 18 18 3e 7b 59 38 1e 1b 5b 7b 3e 18 18 00
00 00 00 31 6b 6e 34 0c 08 18 36 2b 4b 46 00 00
00 00 00 1c 36 36 36 14 18 2c 67 66 66 3b 00 00
00 00 00 18 18 18 18 00 00 00 00 00 00 00 00 00
00 00 06 0c 18 18 30 30 30 30 30 18 18 0c 06 00
00 00 30 18 0c 0c 06 06 06 06 06 0c 0c 18 38 00
00 00 00 00 18 18 5a 3c 18 3c 5a 18 18 00 00 00
00 00 00 00 18 18 18 18 7e 18 18 18 18 18 00 00
00 00 00 00 00 00 00 00 00 00 00 38 18 18 30 00
00 00 00 00 00 00 00 00 7f 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 18 3c 18 00 00
00 00 00 03 03 06 06 0c 1c 18 30 30 60 60 00 00
00 00 00 1c 36 63 63 63 63 63 63 63 36 1c 00 00
00 00 00 0c 1c 3c 0c 0c 0c 0c 0c 0c 0c 3f 00 00
00 00 00 3e 63 63 03 03 06 0c 18 30 60 7f 00 00
00 00 00 7f 03 06 0c 18 3e 03 03 63 63 3e 00 00
00 00 00 06 0e 0e 1e 16 36 26 66 7f 06 06 00 00
00 00 00 7f 60 60 60 7e 63 03 03 63 63 3e 00 00
00 00 00 1e 30 60 60 7e 63 63 63 63 63 3e 00 00
00 00 00 7f 03 03 06 06 0c 18 18 30 60 60 00 00
00 00 00 3e 63 63 63 22 1c 22 63 63 63 3e 00 00
00 00 00 3e 63 63 63 63 3f 03 03 63 62 3c 00 00
00 00 00 00 00 18 3c 18 00 18 3c 18 00 00 00 00
00 00 00 00 00 38 38 00 00 38 18 18 30 00 00 00
00 00 00 03 06 0c 18 30 60 30 18 0c 06 03 00 00
00 00 00 00 00 00 00 7f 00 00 7f 00 00 00 00 00
00 00 00 60 30 18 0c 06 03 06 0c 18 30 60 00 00
00 00 00 3e 63 03 03 06 0c 18 18 00 18 18 00 00
00 00 00 1c 32 6f 6b 6b 6b 6b 6b 6b 6f 30 1f 00
00 00 00 1c 36 22 63 63 7f 63 63 63 63 63 00 00
00 00 00 7c 66 63 66 7c 66 63 63 63 66 7c 00 00
00 00 00 3e 63 63 60 60 60 60 60 61 63 3e 00 00
00 00 00 7c 66 63 63 63 63 63 63 63 66 7c 00 00
00 00 00 7f 60 60 60 7c 60 60 60 60 60 7f 00 00
00 00 00 7f 60 60 60 60 7e 60 60 60 60 60 00 00
00 00 00 3e 63 63 60 60 67 63 63 63 63 3d 00 00
00 00 00 63 63 63 63 63 7f 63 63 63 63 63 00 00
00 00 00 7e 18 18 18 18 18 18 18 18 18 7e 00 00
00 00 00 0f 06 06 06 06 06 06 06 66 66 3c 00 00
00 00 00 63 66 6c 78 70 70 78 6c 66 63 61 00 00
00 00 00 60 60 60 60 60 60 60 60 60 60 7f 00 00
00 00 00 41 63 63 77 7f 6b 63 63 63 63 63 00 00
00 00 00 63 63 63 73 7b 6f 67 63 63 63 63 00 00
00 00 00 3e 63 63 63 63 63 63 63 63 63 3e 00 00
00 00 00 7c 66 63 63 66 7c 60 60 60 60 60 00 00
00 00 00 3e 63 63 63 63 63 63 63 7b 6d 36 03 01
00 00 00 7e 63 63 63 63 7e 6c 66 63 63 63 00 00
00 00 00 3e 63 63 30 18 0c 06 03 63 63 3e 00 00
00 00 00 ff 18 18 18 18 18 18 18 18 18 18 00 00
00 00 00 63 63 63 63 63 63 63 63 63 63 3e 00 00
00 00 00 63 63 63 36 36 36 1c 1c 1c 08 08 00 00
00 00 00 63 63 63 63 63 6b 6b 6b 7f 36 36 00 00
00 00 00 63 63 36 36 1c 08 1c 36 36 63 63 00 00
00 00 00 c3 c3 67 66 3c 3c 18 18 18 18 18 00 00
00 00 00 7f 03 02 06 0c 08 18 30 20 60 7f 00 00
00 00 3e 30 30 30 30 30 30 30 30 30 30 30 3e 00
00 00 00 60 60 30 30 18 1c 0c 06 06 03 03 00 00
00 00 3c 0c 0c 0c 0c 0c 0c 0c 0c 0c 0c 0c 3c 00
00 00 00 0c 1e 33 61 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 7f 00 00
30 18 0c 04 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 3e 63 03 3f 63 63 63 3f 00 00
00 00 00 60 60 60 7e 63 63 63 63 63 63 7e 00 00
00 00 00 00 00 00 3e 63 63 60 60 63 63 3e 00 00
00 00 00 03 03 03 3f 63 63 63 63 63 63 3f 00 00
00 00 00 00 00 00 3e 63 63 7f 60 60 63 3e 00 00
00 00 00 0e 1b 18 18 7e 18 18 18 18 18 18 00 00
00 00 00 00 00 00 3d 67 66 66 66 3c 20 7e 63 3e
00 00 00 60 60 60 6e 73 63 63 63 63 63 63 00 00
00 00 00 18 18 00 38 18 18 18 18 18 18 3c 00 00
00 00 00 06 06 00 0e 06 06 06 06 06 06 36 36 1c
00 00 00 60 60 62 66 6c 78 70 78 6c 66 63 00 00
00 00 00 1c 0c 0c 0c 0c 0c 0c 0c 0c 0c 1e 00 00
00 00 00 00 00 00 76 7f 6b 6b 6b 6b 6b 63 00 00
00 00 00 00 00 00 6e 73 63 63 63 63 63 63 00 00
00 00 00 00 00 00 3e 63 63 63 63 63 63 3e 00 00
00 00 00 00 00 00 7c 66 63 63 63 63 66 7c 60 60
00 00 00 00 00 00 1f 33 63 63 63 63 33 1f 03 03
00 00 00 00 00 00 6e 73 63 60 60 60 60 60 00 00
00 00 00 00 00 00 3e 63 30 1c 06 03 63 3e 00 00
00 00 00 18 18 18 7e 18 18 18 18 18 1b 0e 00 00
00 00 00 00 00 00 63 63 63 63 63 63 67 3b 00 00
00 00 00 00 00 00 81 c3 e7 66 3c 3c 18 18 00 00
00 00 00 00 00 00 63 63 6b 6b 6b 6b 7f 36 00 00
00 00 00 00 00 00 63 63 36 1c 1c 36 63 63 00 00
00 00 00 00 00 00 63 63 63 63 63 67 3b 03 66 3c
00 00 00 00 00 00 7f 03 06 0c 18 30 60 7f 00 00
00 00 0e 18 18 18 18 18 30 18 18 18 18 18 0e 00
00 00 18 18 18 18 18 18 18 18 18 18 18 18 00 00
00 00 38 0c 0c 0c 0c 0c 06 0c 0c 0c 0c 0c 38 00
00 00 00 39 6f 46 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"""

class OpenGL(Null):
    def __init__(self, *kargs, **kwargs):
        super().__init__(*kargs, **kwargs)
        self.window = None
        self.fixed_list = None
        self.font_bitmap = self.load_font()
        self.pause = False
        self.last_button = None
        # View port settings.
        self.xoffset = 0.
        self.yoffset = 0.
        self.zoom = 1.
        self.rot_x = 0.
        self.rot_y = 0.
        self.rot_z = 0.
        self.init()

    def init(self):
        # Initialize OpenGL.
        glut.glutInit()
        glut.glutInitDisplayMode(glut.GLUT_RGBA | glut.GLUT_DOUBLE
                                 | glut.GLUT_DEPTH | glut.GLUT_ALPHA)
        glut.glutInitWindowSize(self.width, self.height)
        self.window = glut.glutCreateWindow('cellx')
        gl.glShadeModel(gl.GL_SMOOTH)
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
        gl.glMaterial(gl.GL_FRONT, gl.GL_AMBIENT, (.8, .0, .2, 1.))
        gl.glMaterial(gl.GL_FRONT, gl.GL_DIFFUSE, (1., 1., 1., 1.))
        gl.glMaterial(gl.GL_FRONT, gl.GL_SPECULAR, (.4, .4, .4, 1.))
        gl.glMaterialf(gl.GL_FRONT, gl.GL_SHININESS, 80)

        gl.glLight(gl.GL_LIGHT0, gl.GL_POSITION, (-100, 100, 100, 0))
        gl.glLight(gl.GL_LIGHT0, gl.GL_AMBIENT, (.3, .3, .3, 1))
        gl.glLight(gl.GL_LIGHT0, gl.GL_DIFFUSE, (.7, .7, .7, 1))
        gl.glLight(gl.GL_LIGHT0, gl.GL_SPECULAR, (1, 1, 1, 1))

    def normalize_position(self, x, y):
        """Normalize a 2D position (x, y) relative to the center of the
        screen."""
        return (x - self.width /
                2) / self.width, -(y - self.height / 2) / self.height

    def normalize_size(self, l):
        """Normalize a size (length) L relative to the screen width. """
        # Force the minimum size to be one pixel.
        return max(1 / self.width, l / self.width)

    def relative_position(self, x, y):
        """Calculate the relative position of a point (x, y) on the screen."""
        return x / self.width, y / self.height

    def load_font(self):
        # FIXME: should not hard-code font size
        # FIXME: support Kanji characters
        font_data = bytes.fromhex(FONT_HIRO16B)
        # Split font data per 16 bytes.
        return [
            font_data[i:i + 16][::-1] for i in range(0, len(font_data), 16)
        ]

    def draw_line(self, sx, sy, dx, dy, width, color, alpha, use_line=False):
        """Draw a line or a square rod between two points with specified
        attributes.  This function allows drawing either a line segment or a
        square rod connecting two points in a graphical context.  The
        appearance of the drawn object can be customized with options such as
        WIDTH, COLOR, and ALPHA transparency."""
        if sx > dx:
            sx, sy, dx, dy = dx, dy, sx, sy
        sx, sy = self.normalize_position(sx, sy)
        dx, dy = self.normalize_position(dx, dy)
        w = self.normalize_size(width)
        color = self.palette.rgba(color, alpha)
        gl.glColor4ub(*color)
        if use_line:
            # Draw a line segment between (SX, SY) and (DX, DY).
            gl.glLineWidth(w)
            gl.glBegin(gl.GL_LINES)
            gl.glVertex2d(sx, sy)
            gl.glVertex2d(dx, dy)
            gl.glEnd()
            return

        # Place a square rod connecting (SX, SY) and (DX, DY).
        # This code assumes SX is smaller than DX.
        gl.glPushMatrix()
        gl.glTranslatef(sx, sy, 0)
        angle = math.degrees(math.atan2(dy - sy, dx - sx))
        gl.glRotatef(angle, 0, 0, 1)
        l = math.sqrt((dx - sx)**2 + (dy - sy)**2)
        gl.glScalef(l, w, w)
        gl.glTranslatef(.5, 0, 0)
        glut.glutSolidCube(1)
        gl.glPopMatrix()

    def draw_ellipse(self, x, y, r, color, alpha):
        """Draw an ellipse at a specified position with given attributes.
        This function draws an ellipse at the specified (X, Y) position with a
        given radius R. The appearance of the ellipse can be customized with
        options such as COLOR and ALPHA transparency."""
        x, y = self.normalize_position(x, y)
        r = self.normalize_size(r)
        color = self.palette.rgba(color, alpha)
        gl.glColor4ub(*color)
        gl.glBegin(gl.GL_POLYGON)
        # Draw the ellipse with 20 segments.
        for degree in range(0, 360, 360 // 20):
            radians = math.radians(degree)
            x1, y1 = x + r * math.cos(radians), y + r * math.sin(radians)
            gl.glVertex2d(x1, y1)
        gl.glEnd()

    def _render_bitmap(self, obj):
        raise NotImplementedError

    def _render_box(self, obj):
        """Render a 3D box object OBJ with specified attributes.  This
        function renders a 3D box at the position (x, y) with dimensions
        (width, height) and a priority level. The appearance of the box can be
        customized with options such as COLOR and ALPHA transparency."""
        x, y = self.normalize_position(obj.x, obj.y)
        w, h = self.normalize_size(obj.width), self.normalize_size(obj.height)
        z = self.normalize_size(obj.priority)
        color = self.palette.rgba(obj.color, obj.alpha)
        gl.glColor4ub(*color)
        gl.glPushMatrix()
        gl.glTranslatef(x, y, z)
        gl.glScalef(w, h, (w + h) / 2)
        glut.glutSolidCube(1)
        gl.glPopMatrix()

    def _render_ellipse(self, obj, use_polygon=False):
        """Render an ellipse object with specified attributes.  This function
        renders an ellipse at the position (x, y) with a specified width and
        priority level. The appearance of the ellipse can be customized with
        options such as color and alpha transparency. The ellipse can be
        rendered as either a polygon or a solid sphere in 3D space."""
        if use_polygon:
            self.draw_ellipse(obj.x, obj.y, obj.width / 2, obj.color,
                              obj.alpha)
            return

        x, y = self.normalize_position(obj.x, obj.y)
        z = self.normalize_size(obj.priority)
        r = self.normalize_size(obj.width / 2)
        color = self.palette.rgba(obj.color, obj.alpha)
        gl.glColor4ub(*color)
        gl.glPushMatrix()
        gl.glTranslatef(x, y, z)
        glut.glutSolidSphere(r, 20, 20)
        gl.glPopMatrix()

    def _render_polygon(self, obj):
        """Render a filled polygon object OBJ with specified attributes.  This
        function renders a filled polygon using the specified vertices, color,
        and alpha transparency. The appearance of the polygon can be
        customized with options such as color and alpha transparency."""
        vertices = obj.vertices()
        color = self.palette.rgba(obj.color, obj.alpha)
        gl.glColor4ub(*color)
        gl.glBegin(gl.GL_POLYGON)
        for v in vertices:
            x, y = self.normalize_position(*v)
            gl.glVertex2d(x, y)
        gl.glEnd()

    def _render_spline(self, obj):
        """Render a spline (curve) object OBJ with specified attributes. This
        function is intended to render a spline, but it currently renders a
        sequence of connected line segments between control points. The
        appearance of the spline can be customized with options such as color,
        alpha transparency, width, and control points."""
        x, y = self.normalize_position(obj.x, obj.y)
        x2, y2 = self.normalize_position(obj.x2, obj.y2)
        x3, y3 = self.normalize_position(obj.x3, obj.y3)
        w = self.normalize_size(obj.width)
        color = self.palette.rgba(obj.color, obj.alpha)
        # FIXME: Spline is not implemented.
        gl.glLineWidth(w)
        gl.glColor4ub(*color)
        # FIXME: Rewrite with glMatrix1fv.
        gl.glBegin(gl.GL_LINE_STRIP)
        gl.glVertex2d(x, y)
        gl.glVertex2d(x2, y2)
        gl.glVertex2d(x3, y3)
        gl.glEnd()

    def _render_text(self, obj):
        """Render text with specified attributes.  This function renders text
        at the specified (x, y) position with the provided text string, color,
        and alpha transparency. The appearance of the text can be customized
        with options such as color and alpha transparency.  Currently, it uses
        a fixed-size font and aligns the text to the left."""
        # FIXME: Support scalable fonts.
        # FIXME: Align text (e.g., centerling).
        x, y = self.normalize_position(obj.x, obj.y)
        w = self.normalize_size(8 * len(obj.text))
        color = self.palette.rgba(obj.color, obj.alpha)
        gl.glColor4ub(*color)
        gl.glPushMatrix()
        gl.glRasterPos3f(x - w / 2, y, .1)
        for c in obj.text:
            gl.glBitmap(8, 16, 0, 0, 8, 0, self.font_bitmap[ord(c)])
        gl.glPopMatrix()

    def render_objects(self, objs):
        """Render a list of objects with specified rendering attributes.  This
        function takes a list of objects and renders them according to their
        rendering attributes. Objects can be categorized as fixed and
        non-fixed, and they are rendered separately."""
        # Render fixed but not-rendered objects.
        if not self.fixed_list:
            self.fixed_list = gl.glGenLists(1)
            gl.glNewList(self.fixed_list, gl.GL_COMPILE)
            for obj in objs:
                if not obj.fixed:
                    continue
                self.render(obj)
            gl.glEndList()

        # Reset to pre-rendered suface.
        self.clear()
        gl.glCallList(self.fixed_list)

        # Render non-fixed objects.
        for obj in objs:
            if obj.fixed:
                continue
            self.render(obj)

    def process_events(self):
        def _key(*args):
            key, x, y = args
            if key == b'q' or key == 0x1b:
                exit()
            if key == b' ':
                self.pause = not self.pause
                # FIXME: Implement pause.

        def _button(*args):
            button, is_off, x, y = args
            if is_off:
                self.last_button = None
            else:
                if button == 3:
                    self.zoom *= .99
                if button == 4:
                    self.zoom *= 1.01
                self.last_button = button

        def _motion(*args):
            x, y = args
            rx, ry = self.relative_position(x, y)
            # Dragging the left button tilts the view.
            if self.last_button == 0:
                self.rot_x = (rx - .5) * 180
                self.rot_y = (ry - .5) * 180
            # Dragging the right button change the visialbe area.
            if self.last_button == 2:
                self.xoffset = -(rx - .5)
                self.yoffset = ry - .5

        glut.glutKeyboardFunc(_key)
        glut.glutMouseFunc(_button)
        glut.glutMotionFunc(_motion)
        glut.glutMainLoopEvent()

    def display(self):
        glut.glutSwapBuffers()
        gl.glFlush()
        self.process_events()
        # Slowly rotate the screen.
        self.rot_z += .07
        self.zoom *= 0.999
        # self.zoom *= 1.0001

    def clear(self):
        """Clear the graphics context and initialize view settings.  This
        function clears the graphics context by clearing the color and depth
        buffers. It then initializes the view settings including the view
        volume and rotation."""
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # Initialize view port settings.
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(self.xoffset - .5 * self.zoom,
                   self.xoffset + .5 * self.zoom,
                   self.yoffset - .5 * self.zoom,
                   self.yoffset + .5 * self.zoom, -100, 100)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glRotatef(self.rot_x, 0, 1, 0)
        gl.glRotatef(self.rot_y, 1, 0, 0)
        gl.glRotatef(self.rot_z, 0, 0, 1)
