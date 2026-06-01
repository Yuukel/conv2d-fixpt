from pathlib import Path

from py_lib.intervals import interval_add, interval_sub, interval_mul
from py_lib.formats import find_format
from py_lib.conversion import convert_to_fixed_point

def generate_c_header():
    code = []

    code.append(f"#include <stdio.h>")
    code.append(f"#include <stdint.h>")

    return "\n".join(code)

def generate_conv_pixel_c(M, K, F, KF, I, KI, n_bits):
    code = []
    code.append(f"""
    A = {convert_to_fixed_point(M[0][0], F[0][0])};
    B = {convert_to_fixed_point(K[0][0], KF[0][0])};
    tmp = A*B;
    printf(\"%d\\n\", tmp);
    """)
    return "\n".join(code)

def generate_c_file(M, K, F, KF, I, KI, n_bits, output_path="gen/conv_pixel.c"):
    header_code = generate_c_header()
    pixel_code = generate_conv_pixel_c(M[0:8], K, F, KF, I, KI, n_bits)

    c_code = f"""{header_code}

int main(){{
    int{n_bits}_t A, B, C, R, tmp;
    C = 0;
    {pixel_code}
    return 0;
}}"""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(c_code)