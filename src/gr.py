import math

def gr(x, a, b):
    return 10 ** (a - b * x)

def gr_a(event_cnt, m, b):
    return math.log10(event_cnt) + (b * m)
