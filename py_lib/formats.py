import numpy as np

class Format:
    """
    Fixed-point format:
        a = integer bits, including sign bit
        b = fractional bits
    """

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __repr__(self):
        return "<" + str(self.a) + "," + str(self.b) + ">"

def find_format(val, min_val, max_val, n_bits):
    """
    Find the smallest format able to represent val.end.
    """

    x = max(abs(val.start), abs(val.end))
    if(-1 < x < 1):
        a = 1
    elif(x > max_val or x < min_val):
        print(f"Value {x} is out of range for {n_bits} bits.")
        return []
    else:
        a = np.floor(np.log2(x))+2

    b = n_bits - a
    return Format(int(a), int(b))

def fill_format(matrix, n_bits):
    """
    Build a format matrix from an interval matrix.
    """

    format_matrix = []

    min_val = -(2**(n_bits-1))
    max_val = 2**(n_bits-1)-1

    for row in matrix:
        liste = []
        for i in row:
            format_obj = find_format(i, min_val, max_val, n_bits)
            liste.append(format_obj)
        format_matrix.append(liste)
    return np.array(format_matrix, dtype=object)

def find_max_format(format_matrix):
    """
    Find the largest format in the matrix.
    """

    max_format = None

    for row in format_matrix:
        for fmt in row:
            if max_format is None or (fmt.a > max_format.a) or (fmt.a == max_format.a and fmt.b > max_format.b):
                max_format = fmt

    return max_format

def convert_all_format(format_matrix, new_format):
    """
    Replace all formats with the same format.
    """

    converted_format_matrix = []
    for row in format_matrix:
        converted_row = []
        for format_obj in row:
            converted_row.append(new_format)
        converted_format_matrix.append(converted_row)
    return np.array(converted_format_matrix)

def reduce_format(f, n_bits):
    """
    Reduce fractional precision if total bits exceed n_bits.
    """

    if(f.a + f.b > n_bits):
        f.b = n_bits - f.a

def mul_format(f1, f2):
    """
    Fixed-point multiplication:
        integer bits add
        fractional bits add
    """

    a = f1.a + f2.a
    b = f1.b + f2.b
    return Format(a, b)

def add_format(f1, f2, n_bits):
    """
    Fixed-point addition:
        keep max integer/fractional bits

    +1 integer bit for carry/overflow
    """

    a = max(f1.a, f2.a) + 1
    b = n_bits - a
    return Format(a, b)