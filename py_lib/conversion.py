import numpy as np

def convert_to_fixed_point(value, format_obj):
    a = format_obj.a
    b = format_obj.b
    if(value == 0):
        return 0
    else:
        fixed_value = np.round(value * (2**b))
        return int(fixed_value)

def convert_matrix_to_fixed_point(matrix, format_matrix):
    fixed_matrix = []
    for i in range(format_matrix.shape[0]):
        row = []
        for j in range(format_matrix.shape[1]):
            format_obj = format_matrix[i][j]
            value = matrix[i][j]
            fixed_value = convert_to_fixed_point(value, format_obj)
            row.append(fixed_value)
        fixed_matrix.append(row)
    return np.array(fixed_matrix)

def reconstruct_from_fixed_point(fixed_value, format_obj):
    return fixed_value / (2**format_obj.b)

def reconstruct_matrix_from_fixed_point(fixed_matrix, format_matrix):
    reconstructed_matrix = []
    for i in range(format_matrix.shape[0]):
        row = []
        for j in range(format_matrix.shape[1]):
            format_obj = format_matrix[i][j]
            fixed_value = fixed_matrix[i][j]
            value = reconstruct_from_fixed_point(fixed_value, format_obj)
            row.append(value)
        reconstructed_matrix.append(row)
    return np.array(reconstructed_matrix)