import numpy as np
import re
from py_lib.intervals import Interval

def read_matrix_from_file(filename):
    """
    Read a numeric matrix from a text file.
    """

    with open(filename, 'r') as file:
        lines = file.readlines()
        matrix = []
        for line in lines:
            row = list(map(float, line.split()))
            matrix.append(row)
        return np.array(matrix)

def read_interval_matrix_from_file(filename):
    """
    Read an interval matrix from a text file.

    Expected format :
        [a,b] [c,d] [e,f] ...
    """

    matrix = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            matches = re.findall(r'\[(-?\d+),(-?\d+)\]',line)

            row = [Interval(int(a), int(b)) for a,b in matches]
            matrix.append(row)

    return np.array(matrix, dtype=object)