#!/usr/bin/env python3

for n in range(100 + 1):
    y = n * 6
    print('define b{0} box 1 .01 heat{0} .5 {1}'.format(n, y))
print('display')
print('wait')

