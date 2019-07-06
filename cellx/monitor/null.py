#!/usr/bin/env python3
#
#
# Copyright (c) 2018, Hiroyuki Ohsaki.
# All rights reserved.
#
# $Id: null.py,v 1.4 2019/03/10 11:49:59 ohsaki Exp ohsaki $
#

COLOR_MAP = {
    'blue': 'SteelBlue', 'red': 'chocolate1', 'magenta': 'orange', 'cyan':
    'SkyBlue', 'green': 'PaleGreen', 'yellow': 'LightGoldenrod'
}

# http://psychology.wikia.com/wiki/HSV_color_space
def hsv2rgb(h, s, v):
    hi = int(h / 60) % 6
    f = h / 60 - hi
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    if hi == 0:
        return v, t, p
    elif hi == 1:
        return q, v, p
    elif hi == 2:
        return p, v, t
    elif hi == 3:
        return p, q, v
    elif hi == 4:
        return t, p, v
    elif hi == 5:
        return v, p, q

class Null:
    def __init__(self,
                 width=800,
                 height=600,
                 color_type=0,
                 alpha=1,
                 outfile=None):
        self.width = width
        self.height = height
        self.color_type = color_type
        self.alpha = alpha
        self.outfile = outfile
        self.palette = {}

        self.init_palette()

    # automatically generate gray/HSV colors
    def _generate_colors(self):
        for level in range(100 + 1):
            p = level / 100
            self.define_palette('gray{}'.format(level), p, p, p)

            if self.color_type == 0:  # HSV
                rgb = hsv2rgb(240 * (1 - p), 0.9, 1.0)
            elif self.color_type == 1:  # cyan-red
                rgb = hsv2rgb(0 + 180 * (1 - p), abs(p - 0.5) * 2, 1.0)
            elif self.color_type == 2:  # blue-orange
                rgb = hsv2rgb(30 + 180 * (1 - p), abs(p - 0.5) * 2, 1.0)
            elif self.color_type == 3:  # blue-yellow
                rgb = hsv2rgb(60 + 180 * (1 - p), abs(p - 0.5) * 2, 1.0)
            elif self.color_type == 4:  # purple-green
                rgb = hsv2rgb(90 + 180 * (1 - p), abs(p - 0.5) * 2, 1.0)
            elif self.color_type == 5:  # green-magenta
                rgb = hsv2rgb(120 + 180 * p, abs(p - 0.5) * 2, 1.0)
            elif self.color_type == 6:  # green-red
                rgb = hsv2rgb(150 + 180 * p, abs(p - 0.5) * 2, 1.0)
            self.define_palette('heat{}'.format(level), *rgb)
            q = 1 - p
            self.define_palette('cool{}'.format(level), 0.0 * p + 0.0 * q,
                                0.8 * p + 0.0 * q, 0.9 * p + 0.4 * q)

    def _load_x11_colors(self, file):
        with open(file) as f:
            for line in f:
                line = line.rstrip()
                if line.startswith('!'):
                    continue
                color, name = line.split('\t\t')
                r, g, b = color.split()
                self.define_palette(name, int(r), int(g), int(b))

    def _define_color_aliases(self):
        for color in COLOR_MAP:
            self.define_palette(color, *self.rgba(COLOR_MAP[color]))

    def init_palette(self):
        self._generate_colors()
        self._load_x11_colors('/usr/share/X11/rgb.txt')
        self._define_color_aliases()

    def define_palette(self, name, r, g, b, a=1):
        if r <= 1:
            r *= 0xff
        if g <= 1:
            g *= 0xff
        if b <= 1:
            b *= 0xff
        if a <= 1:
            a *= 0xff
        self.palette[name] = [r, g, b, a]

    def rgba(self, name, alpha=1):
        try:
            color = self.palette[name]
        except KeyError:
            return None
        r, g, b, a = color
        return r, g, b, a * alpha

    def rgb(self, color):
        return self.rgba(color)[0:3]

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
