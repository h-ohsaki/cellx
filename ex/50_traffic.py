#!/usr/bin/env python3

import random
import graph_tools

N = 100
E = 200

G = graph_tools.Graph().create_random_graph(N, E)
for v in G.vertices():
    print('define v{} ellipse 3 3 yellow'.format(v))
for u, v in G.edges():
    print('define - link v{} v{} 2 blue'.format(u, v))
print('spring /./')

for p in range(N):
    n = 1 + random.randrange(N)
    c = 'heat{}'.format(random.randrange(100 + 1))
    print('define p{} box 10 10 {} v{}'.format(p, c, n))
print('display')

for _ in range(100):
    for p in range(N):
        n = 1 + random.randrange(N)
        print('animate p{} v{}'.format(p, n))
    print('display')
