def print_matrix(matrix):
    width = max(len(str(x)) for row in matrix for x in row) + 2

    for row in matrix:
        for x in row:
            print(f"{str(x):>{width}}", end="")
        print()
    print()