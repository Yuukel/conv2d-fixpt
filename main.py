import numpy as np

from py_lib.config import N_BITS

from py_lib.read import read_matrix_from_file, read_interval_matrix_from_file
from py_lib.intervals import Interval, add_interval, sub_interval, mul_interval, create_interval_from_matrix, find_global_interval
from py_lib.display import print_matrix
from py_lib.formats import fill_format, find_format, find_max_format
from py_lib.conversion import convert_matrix_to_fixed_point
from py_lib.c_generator import generate_c_file, generate_c_file_loop


# Read input data
M = read_matrix_from_file('./data/matrix.txt')
K = read_matrix_from_file('./data/filter.txt')
I = read_interval_matrix_from_file('./data/intervals.txt')


# Display input matrices
# print("Matrix M:")
# print_matrix(M)

# print("Kernel K:")
# print_matrix(K)

# print("Interval Matrix I:")
# print_matrix(I)


# Convert kernel values into intervals
KI = create_interval_from_matrix(K)

# print("Interval Matrix KI:")
# print_matrix(KI)


# Find fixed-point formats
F = fill_format(I, N_BITS)
KF = fill_format(KI, N_BITS)

# print("Format Matrix F:")
# print_matrix(F)

# print("Format Matrix KF:")
# print_matrix(KF)


# Convert matrices to fixed-point
M_fixed = convert_matrix_to_fixed_point(M, F)
K_fixed = convert_matrix_to_fixed_point(K, KF)

# print("Matrix M (convertie en fixed-point):")
# print_matrix(M_fixed)

# print("Matrix K (convertie en fixed-point):")
# print_matrix(K_fixed)

# Display conversion summary
# header = (
#         f"{'Original':>15}"
#         f"{'Format':>15}"
#         f"{'Interval':>15}"
#         f"{'Fixed':>15}"
# )

# print(header)
# print("-" * len(header))

# for i in range(M.shape[0]):
#     for j in range(M.shape[1]):
#         print(
#             f"{M[i][j]:>15.8g}"
#             f"{str(F[i][j]):>15}"
#             f"{str(I[i][j]):>15}"
#             f"{M_fixed[i][j]:>15}"
#         )

KH, KW = K.shape
H, W = M.shape

OUT_H = H - KH + 1
OUT_W = W - KW + 1

new_F = np.empty(K.shape, dtype=object)
new_I = np.empty(K.shape, dtype=object)
for i in range(KH):
    for j in range(KW):
        new_F[i][j] = find_max_format(F[i:i+OUT_H, j:j+OUT_W])
        new_I[i][j] = find_global_interval(I[i:i+OUT_H, j:j+OUT_W])


# Generate C source file
generate_c_file(M, K, F, KF, I, KI, N_BITS)
generate_c_file_loop(M, K_fixed, new_F, KF, new_I, KI, N_BITS)