#!/usr/bin/env python3

N = 15
M = 3

for i in range(N):
    print('def v{} ellipse 10 10 cyan'.format(i))
print('spring /^v/')

for i in range(1, N):
    print('def l{} link v{} v{} 2 blue'.format(i, i-1, i))
print('fix /./')

for m in range(M):
    print('def ball{0} ellipse 15 15 yellow v{0}'.format(m))

for _ in range(100):
    for m in range(M):
        v = (_ + m) % N
        print('animate ball{} v{}'.format(m, v))
    print('display')
