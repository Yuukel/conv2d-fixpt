import numpy as np

from py_lib.config import N_BITS

from py_lib.read import read_matrix_from_file, read_interval_matrix_from_file
from py_lib.intervals import Interval, add_interval, sub_interval, mul_interval, create_interval_from_matrix
from py_lib.display import print_matrix
from py_lib.formats import fill_format, find_format
from py_lib.conversion import convert_matrix_to_fixed_point
from py_lib.c_generator import generate_c_file


# Read input data
M = read_matrix_from_file('./data/matrix.txt')
K = read_matrix_from_file('./data/filter.txt')
I = read_interval_matrix_from_file('./data/intervals.txt')


# Display input matrices
print("Matrix M:")
print_matrix(M)

print("Kernel K:")
print_matrix(K)

print("Interval Matrix I:")
print_matrix(I)


# Convert kernel values into intervals
KI = create_interval_from_matrix(K)

print("Interval Matrix KI:")
print_matrix(KI)


# Find fixed-point formats
F = fill_format(I, N_BITS)
KF = fill_format(KI, N_BITS)

print("Format Matrix F:")
print_matrix(F)

print("Format Matrix KF:")
print_matrix(KF)


# Convert matrices to fixed-point
M_fixed = convert_matrix_to_fixed_point(M, F)
K_fixed = convert_matrix_to_fixed_point(K, KF)

print("Matrix M (convertie en fixed-point):")
print_matrix(M_fixed)

print("Matrix K (convertie en fixed-point):")
print_matrix(K_fixed)

# Display conversion summary
header = (
        f"{'Original':>15}"
        f"{'Format':>15}"
        f"{'Interval':>15}"
        f"{'Fixed':>15}"
)

print(header)
print("-" * len(header))

for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        print(
            f"{M[i][j]:>15.8g}"
            f"{str(F[i][j]):>15}"
            f"{str(I[i][j]):>15}"
            f"{M_fixed[i][j]:>15}"
        )


# Generate C source file
generate_c_file(M, K, F, KF, I, KI, N_BITS)


# Small interval arithmetic test
A = (Interval)(1.5, 2)
B = (Interval)(0.25, 0.75)

min_val = -(2**(N_BITS-1))
max_val = 2**(N_BITS-1)-1

print(A)
print(B)

print(find_format(A,min_val,max_val, N_BITS))
print(find_format(B,min_val,max_val, N_BITS))

print(add_interval(A,B))
print(find_format(add_interval(A,B),min_val,max_val, N_BITS))

print(sub_interval(A,B))
print(find_format(sub_interval(A,B),min_val,max_val, N_BITS))

print(mul_interval(A,B))
print(find_format(mul_interval(A,B),min_val,max_val, N_BITS))