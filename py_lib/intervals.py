import numpy as np

class Interval:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return f"[{self.start}, {self.end}]"

def create_interval_from_val(val):
    return (Interval)(val, val)

def create_interval_from_matrix(matrix):
    n,m = matrix.shape

    intervals = np.empty((n,m), dtype=object)

    for i in range(n):
        for j in range(m):
            intervals[i,j] = create_interval_from_val(matrix[i,j])

    return intervals

def add_interval(i1, i2):
    return (Interval)(i1.start + i2.start, i1.end + i2.end)

def sub_interval(i1, i2):
    return (Interval)(i1.start - i2.end, i1.end - i2.start)

def mul_interval(i1, i2):
    ac = i1.start * i2.start
    bc = i1.end * i2.start
    ad = i1.start * i2.end
    bd = i1.end * i2.end
    return (Interval)(min(ac, bc, ad, bd), max(ac, bc, ad, bd))