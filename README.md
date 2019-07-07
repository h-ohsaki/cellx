# NAME

cellx - command-driven drawing/visualization/animation/presentation tool

# SCREENSHOTS

- DTN simulator visualization

![screenshot](https://raw.githubusercontent.com/h-ohsaki/cellx/master/screenshot/pdtnsim.png)

- DTN simulator visualization with blurring

![screenshot](https://raw.githubusercontent.com/h-ohsaki/cellx/master/screenshot/pdtnsim-filter.png)

- CCN simulator visualization with blurring

![screenshot](https://raw.githubusercontent.com/h-ohsaki/cellx/master/screenshot/ccn-filter.png)

- CCN simulator visualization with blurring and blue-yellow (#3) color map

![screenshot](https://raw.githubusercontent.com/h-ohsaki/cellx/master/screenshot/ccn-filter-3.png)

- DFC-BP+ visualization

![screenshot](https://raw.githubusercontent.com/h-ohsaki/cellx/master/screenshot/pdfcsim-random.png)

- DFC-BP+ visualization

![screenshot](https://raw.githubusercontent.com/h-ohsaki/cellx/master/screenshot/pdfcsim-grid.png)

- WSN simulator visualization

![screenshot](https://raw.githubusercontent.com/h-ohsaki/cellx/master/screenshot/pwsnsim.png)

# DESCRIPTION

This manual page documents **cellx**, a one-pass interpreter of the CELL
language.  CELL language is a simple line-oriented language for dynamic
graphics drawing.  **cellx** reads a source code written in the CELL language
from the standard input or specified files.  Every line in the source code is
parsed and interpreted.  The output is drawn on a window using SDL library via
**pygame** module.

# CELL LANGUAGE COMMANDS

```
alpha (name|regexp) alpha
animate name (goal_x goal_y|name[(+|-)dx(+|-)dy])
attach name parent_name dx dy
color (name|regexp) color
define name bitmap file [(x y|name[(+|-)dx(+|-)dy])]
define name box [-f color] [width height color (x y|name[(+|-)dx(+|-)dy])]
define name ellipse [-f color] [rx ry color] [(x y|name[(+|-)dx(+|-)dy])]
define name line [-ht] sx sy dx dy [width color]
define name link src_name dst_name [width color]
define name polygon [-f color] [-r degree] n r [color (x y|name[(+|-)dx(+|-)dy])]
define name spline x1 y1 x2 y2 x3 y3 [width color]
define name text [-lcr] string [size color (x y|name[(+|-)dx(+|-)dy])]
define name wire [-ht] sx sy dx dy [width color]
display
fade (name|regexp)...
fix (name|regexp)...
hide (name|regexp)...
kill (name|regexp)...
move (name|regexp) (x y|name[(+|-)dx(+|-)dy])
palette symbol r g b [alpha]
play file
priority (name|regexp) level
resize (name|regexp) (x y|name[(+|-)dx(+|-)dy])
scale (name|regexp) ratio
shift (name|regexp) dx dy
sleep x
spring [-f filter] [-r degree] (name|regexp)... [x1 y1 x2 y2]
unhide (name|regexp)...
wait
```

# EXAMPLES

Many examples are found in `ex` directory contained in the source archive.

- M/M/1 queue:
```c
#define font_size 20
#define packet_color gray80

#define add_note_above(name, str) \
define name##_note text str font_size white name+0-40

#define add_note_below(name, str) \
define name##_note text str font_size white name+0+40

#define create_slot(name) \
  define name box -f black 10 50 white

#define create_slot_at(name, pos) \
  create_slot(name) pos

#define create_customer(name) \
  define name box -f black 10 50 packet_color

#define create_customer_at(name, pos) \
  create_customer(name) pos

define server ellipse -f black 30 30 white
add_note_below(server, server) 
move server_note server+.02+.08

create_slot_at(b1, server-35+0)
create_slot_at(b2, b1-10+0)
create_slot_at(b3, b2-10+0)
create_slot_at(b4, b3-10+0)
create_slot_at(b5, b4-10+0)
add_note_below(b5, buffer)
move b5_note b5+0+.08

define lb line -h .25 .5 b5-10+0 undef 2 black
define la line -h server+30+0 undef .65 .5 2 black

create_customer_at(c1, .33 .44)
create_customer_at(c2, .36 .44)
create_customer_at(c3, .56 .44)
create_customer_at(c4, .62 .44)

add_note_above(c1, customer)

display
wait

```
# INSTALLATION

```python
pip3 install cellx
```

# AVAILABILITY

The latest version of **cellx** is available at PyPI
(https://pypi.org/project/cellx/) .

# SEE ALSO

cell - CELL language interpreter for visualization using SDL/OpenGL/PostScript/AVI/PDF (http://www.lsnl.jp/~ohsaki/software/cell)

# AUTHOR

Hiroyuki Ohsaki <ohsaki[atmark]lsnl.jp>
