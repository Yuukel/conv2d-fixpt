from pathlib import Path

from py_lib.intervals import Interval, add_interval, mul_interval
from py_lib.formats import Format, find_format, mul_format, reduce_format, add_format
from py_lib.conversion import convert_to_fixed_point

def generate_c_header():
    """
    Generate required C headers.
    """

    code = []

    code.append(f"#include <stdio.h>")
    code.append(f"#include \"fixed_point.h\"")

    return "\n".join(code)

def generate_conv_pixel_c(M, K, F, KF, I, KI, n_bits):
    """
    Generate C code for one convolution pixel.
    """

    code = []

    # Initial accumulator format
    C_format = Format(1, n_bits-1)

    # Initial accumulator interval
    C_interval = Interval(0, 0)

    for i in range(K.shape[0]):
        for j in range(K.shape[1]):
            print(f"Etape {i},{j} : {i*K.shape[1]+j+1}")

            # Load operands.
            code.append(f"""
            printf("Etape {i},{j} : {i*K.shape[1]+j+1}\\n\\n");
            A = {convert_to_fixed_point(M[0+i][0+j], F[0+i][0+j])};
            B = {convert_to_fixed_point(K[0+i][0+j], KF[0+i][0+j])};
            C = R;
            """)

            # Debug display
            code.append(f"""
            printf("A : ");
            print_binary(A, {n_bits});
            printf("B : ");
            print_binary(B, {n_bits});
            printf("C : ");
            print_binary(C, {n_bits});
            """)

            # Number of fractional bits of A and B
            f_bits_b = n_bits - F[0+i][0+j].a
            kf_bits_b = n_bits - KF[0+i][0+j].a

            # Number of fractional bits of raw product
            current_tmp_b = f_bits_b + kf_bits_b

            # Interval analysis
            tmp_interval = mul_interval(I[0+i][0+j], KI[0+i][0+j])
            interval_add = add_interval(C_interval, tmp_interval)
            interval_add_format = find_format(interval_add, -(2 ** (n_bits - 1)), 2 ** (n_bits - 1) - 1, n_bits)

            target_b = interval_add_format.b

            # Shift needed after multiplication to get target format
            shift_tmp = current_tmp_b - target_b

            # Multiply fixed-point values
            code.append(f"""
            tmp = fp{n_bits}_mul(A, B, {shift_tmp});

            printf("TMP : ");
            print_binary(tmp, {n_bits});

            printf("\\n");
            """)

            # Align accumulator C to target format
            current_c_b = C_format.b
            shift_c = target_b - current_c_b

            if shift_c > 0:
                code.append(f"""
                C = C << {shift_c};
                printf("C après shift : ");
                print_binary(C, {n_bits});
                printf("\\n");
                """)
            elif shift_c < 0:
                code.append(f"""
                C = C >> {-shift_c};
                printf("C après shift : ");
                print_binary(C, {n_bits});
                printf("\\n");
                """)

            # Addition in n_bits
            code.append(f"""
            R = fp{n_bits}_add(C, tmp);
            printf("R : ");
            print_binary(R, {n_bits});
            printf("\\n");
            """)

            # Update accumulator state
            C_format = interval_add_format
            C_interval = interval_add

    print(f"Final C_format: {C_format}, "
          f"Final C_interval: {C_interval}")
    current_b = C_format.b
    code.append(f"""
    current_b = {current_b};
    """)
    return "\n".join(code)

def generate_c_file(M, K, F, KF, I, KI, n_bits, output_path="gen/conv_pixel.c"):
    """
    Generate full C source file.
    """

    header_code = generate_c_header()

    out_h = M.shape[0] - K.shape[0] + 1
    out_w = M.shape[1] - K.shape[1] + 1

    c_code = f"""{header_code}

int main(){{
    float OUT[{out_h}][{out_w}];
    fp{n_bits}_t OUT_fp[{out_h}][{out_w}];
    int current_b;
    size_t i = 0, j;
    fp{n_bits}_t A, B, C, tmp, R;
    R = 0;
"""

    # Generate 2D convolution code
    for i in range(M.shape[0]-K.shape[0]+1):
        for j in range(M.shape[1]-K.shape[1]+1):
            pixel_code = generate_conv_pixel_c(M[i:i+K.shape[0],j:j+K.shape[1]], K, F[i:i+K.shape[0],j:j+K.shape[1]], KF, I[i:i+K.shape[0],j:j+K.shape[1]], KI, n_bits)
            c_code += pixel_code
            c_code += f"""
            OUT_fp[{i}][{j}] = R;
            OUT[{i}][{j}] = (float)R / (1 << current_b);
            R = 0;
            """

    c_code += f"""
    // Final output (fixed_point) display
    printf("Output Matrix Fixed-Point:\\n");
    for(i = 0; i < {out_h}; i++){{
        for(j = 0; j < {out_w}; j++){{
            printf("%d ", OUT_fp[i][j]);
        }}
        printf("\\n");
    }}

    printf("\\n");

    // Final output (float) display
    printf("Output Matrix Float:\\n");
    for(i = 0; i < {out_h}; i++){{
        for(j = 0; j < {out_w}; j++){{
            printf("%f ", OUT[i][j]);
        }}
        printf("\\n");
    }}
    """

    c_code += "return 0;\n}"

    # Create output directory if needed
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write generated C code
    output_path.write_text(c_code)