import numpy as np

def calculate_error(original_matrix, reconstructed_matrix):
    """
    Compute absolute error:
        |original - reconstructed|
    """
    error_matrix = np.abs(original_matrix - reconstructed_matrix)
    return error_matrix

def calculate_relative_error(original_matrix, reconstructed_matrix):
    """
    Compute relative error:
        |original - reconstructed| / |original|

    If original value is 0 :
        relative error is forced to 0 to avoid division by zero.
    """
    relative_error_matrix = np.divide(
        np.abs(original_matrix - reconstructed_matrix),
        np.abs(original_matrix),
        out=np.zeros_like(original_matrix, dtype=float),
        where=original_matrix != 0
    )

    return relative_error_matrix