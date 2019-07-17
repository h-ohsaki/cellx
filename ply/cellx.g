@start : (NEWLINE | stmt)+ ; 

stmt : (
				ANIMATE pattern geometry
        | ATTACH name name geometry?
        | COLOR pattern color
        | DISPLAY
        | FADE pattern
        | MOVE pattern geometry
        | PLAY string
        | PRIORITY pattern number
        | RESIZE pattern geometry
        | SHIFT pattern geometry
        | SPRING pattern (geometry geometry)?
        | WAIT
        | define_cmd
        ) (NEWLINE | EOF) ;

define_cmd: bitmap_cmd
    | box_cmd
    | ellipse_cmd
    | line_cmd
    | link_cmd
    | palette_cmd
    | polygon_cmd
    | spline_cmd
    | text_cmd
    | wire_cmd 
    ;

bitmap_cmd: DEFINE name BITMAP (option)* string geometry? ;
box_cmd: DEFINE name BOX (option)* (number number (color geometry?)?)? ;
ellipse_cmd: DEFINE name ELLIPSE (option)* (number number (color geometry?)?)? ;
line_cmd: DEFINE name LINE (option)* geometry geometry (number color?)? ;
link_cmd: DEFINE name LINK (option)* name name (number color?)? ;
palette_cmd: PALETTE name color ;
polygon_cmd: DEFINE name POLYGON (option)* number number (color geometry?)? ;
spline_cmd: DEFINE name SPLINE (option)* geometry geometry geometry (number color)? ;
text_cmd: DEFINE name TEXT (option)* string (number (color geometry?)?)? ;
wire_cmd: DEFINE name WIRE (option)* geometry geometry (number color?)? ;

pattern : name | regexp ;

color: name
    | number number number number?
    | hexcolor
    | color number
    ;

geometry: number number
    | name (sign number sign number)?
    ;

sign: PLUS | MINUS ;

number: '[+-]?[\d.]+' ;

string: '".+?"' | '\'.+?\'';

regexp: '/.+?/';

option: MINUS name;

WS: ' +' (%ignore);

name: NAME | UNDERSCORE | DBLUNDERSCORE ;

hexcolor: '#[\da-f]{6,8}';

PLUS: '\+';
MINUS: '-';
TIMES: '\*';
UNDERSCORE: '_';
DBLUNDERSCORE: '__';

NAME: '[A-Za-z_][0-9A-Za-z_]*'
        (%unless
    ANIMATE: 'animate';
    ATTACH: 'attach';
    BITMAP: 'bitmap';
    BOX: 'box';
    COLOR: 'color';
    DEFINE: 'define';
    DISPLAY: 'display';
    ELLIPSE: 'ellipse';
    FADE: 'fade';
    LINE: 'line';
    LINK: 'link';
    MOVE: 'move';
    PALETTE: 'palette';
    PLAY: 'play';
    POLYGON: 'polygon';
    PRIORITY: 'priority';
    RESIZE: 'resize';
    SHIFT: 'shift';
    SPLINE: 'spline';
    SPRING: 'spring';
    TEXT: 'text';
    WAIT: 'wait';
    WIRE: 'wire';
        );

NEWLINE: '\n+' (%newline) ;
EOF: '<EOF>' ;
