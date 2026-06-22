import numpy as np
import subprocess
import time

from py_lib.config import N_BITS, NB_IT, SIZE, PREC, SEED
from py_lib.read import read_matrix_from_file, read_interval_matrix_from_file
from py_lib.intervals import Interval, create_interval_from_matrix, find_global_interval
from py_lib.formats import fill_format, find_max_format
from py_lib.conversion import convert_matrix_to_fixed_point
from py_lib.c_generator import generate_c_file, generate_c_file_loop


start = time.perf_counter()

rng = np.random.default_rng(SEED)

K = read_matrix_from_file('./data/filter.txt')
# I = read_interval_matrix_from_file('./data/new_intervals.txt')

I = []
for i in range(SIZE):
    row = []
    for j in range(SIZE):
        interval = Interval(-(i+j+1), i+j+1)
        row.append(interval)
    I.append(row)
I = np.array(I)

KI = create_interval_from_matrix(K)

F = fill_format(I, N_BITS)
KF = fill_format(KI, N_BITS)

KH, KW = K.shape
H, W = SIZE, SIZE

OUT_H = H - KH + 1
OUT_W = W - KW + 1

new_F = np.empty(K.shape, dtype=object)
new_I = np.empty(K.shape, dtype=object)
for i in range(KH):
    for j in range(KW):
        new_F[i][j] = find_max_format(F[i:i+OUT_H, j:j+OUT_W])
        new_I[i][j] = find_global_interval(I[i:i+OUT_H, j:j+OUT_W])

K_fixed = convert_matrix_to_fixed_point(K, KF)

subprocess.run(
        ["make", "clean"]
    )

errors = []
for it in range(NB_IT):
    print(f"Iteration {it + 1}/{NB_IT}")

    # Nouvelle matrice M
    M = []
    for i in range(SIZE):
        row = []
        for j in range(SIZE):
            interval = I[i][j]
            value = round(interval.start + (interval.end - interval.start) * rng.random(), PREC)
            row.append(value)
        M.append(row)
    M = np.array(M)
    # print(M)

    generate_c_file(M, K, F, KF, I, KI, N_BITS)
    generate_c_file_loop(M, K_fixed, new_F, KF, new_I, KI, N_BITS)

    subprocess.run(
        ["make", "run-all-c"]
    )

    R1 = read_matrix_from_file('./gen/matrices/prec_matrix.txt')
    R2 = read_matrix_from_file('./gen/matrices/loop_matrix.txt')

    norm_R1 = np.linalg.norm(R1, ord=np.inf)
    if(norm_R1 != 0):
        err = np.linalg.norm(R1 - R2, ord=np.inf) / norm_R1
        errors.append(err)
end = time.perf_counter()
errors = np.array(errors)

print("Nombre de tests =", len(errors))
print("Erreur moyenne (%) =", np.mean(errors)*100)
print("Erreur min (%) =", np.min(errors)*100)
print("Erreur max (%) =", np.max(errors)*100)

print(f"Temps total : {end - start:.3f} s")