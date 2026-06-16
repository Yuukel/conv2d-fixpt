from pathlib import Path
import numpy as np

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

            # Load operands.
            code.append(f"""
            A = {convert_to_fixed_point(M[0+i][0+j], F[0+i][0+j])};
            B = {convert_to_fixed_point(K[0+i][0+j], KF[0+i][0+j])};
            C = R;
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
            """)

            # Align accumulator C to target format
            current_c_b = C_format.b
            shift_c = target_b - current_c_b

            if shift_c > 0:
                code.append(f"""
                C = C << {shift_c};
                """)
            elif shift_c < 0:
                code.append(f"""
                C = C >> {-shift_c};
                """)

            # Addition in n_bits
            code.append(f"""
            R = fp{n_bits}_add(C, tmp);
            """)

            # Update accumulator state
            C_format = interval_add_format
            C_interval = interval_add

    # print(f"Final C_format: {C_format}, "
    #       f"Final C_interval: {C_interval}")
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

def generate_c_file_loop(M, K, F, KF, I, KI, n_bits, output_path="gen/conv_pixel_loop.c"):
    """
    Generate full C source file.
    """

    header_code = generate_c_header()

    k_h = K.shape[0]
    k_w = K.shape[1]

    out_h = M.shape[0] - k_h + 1
    out_w = M.shape[1] - k_w + 1

    shift_tmp = []
    shift_c = []

    C_format = Format(1, n_bits-1)
    C_interval = Interval(0, 0)
    
    for i in range(K.shape[0]):
        for j in range(K.shape[1]):
            # Number of fractional bits of A and B
            f_bits_b = n_bits - F[0+i][0+j].a
            kf_bits_b = n_bits - KF[0+i][0+j].a

            # Number of fractional bits of raw product
            current_tmp_b = f_bits_b + kf_bits_b

            # Interval analysis
            tmp_interval = mul_interval(I[i][j], KI[i][j])
            interval_add = add_interval(C_interval, tmp_interval)
            interval_add_format = find_format(interval_add, -(2 ** (n_bits - 1)), 2 ** (n_bits - 1) - 1, n_bits)

            target_b = interval_add_format.b

            # Shift needed after multiplication to get target format
            shift_tmp.append(current_tmp_b - target_b)

            # Align accumulator C to target format
            current_c_b = C_format.b
            shift_c.append(target_b - current_c_b)

            C_format = interval_add_format
            C_interval = interval_add
    
    current_b = C_format.b
    # print("Final format =", C_format)
    
    M_fixed = np.empty((out_h*out_w, k_h * k_w), dtype=int)
    for y in range(out_h):
        for x in range(out_w):
            pixel_idx = y * out_w + x

            for i in range(k_h):
                for j in range(k_w):
                    idx = i * k_w + j
                    M_fixed[pixel_idx][idx] = convert_to_fixed_point(M[y + i][x + j], F[i][j])
    
    K_fixed = []
    for i in range(k_h):
        for j in range(k_w):
            K_fixed.append(K[i][j])

    def c_2d_array(name, array, c_type):
        rows = []
        for row in array:
            rows.append("{"+", ".join(map(str, row))+"}")
        return(
            f"{c_type} {name}[{array.shape[0]}][{array.shape[1]}] = {{\n"
            f" " + ",\n ".join(rows)+ "\n};"
        )

    c_code = f"""{header_code}

int main(){{
    float OUT[{out_h}][{out_w}];
    fp{n_bits}_t OUT_fp[{out_h}][{out_w}];

    fp{n_bits}_t A, B, C, tmp, R;

    fp{n_bits}_t K_fixed[{k_h*k_w}] = {{
        {", ".join(map(str, K_fixed))}
    }};

    int shift_tmp[{k_h*k_w}] = {{
        {", ".join(map(str, shift_tmp))}
    }};

    int shift_c[{k_h*k_w}] = {{
        {", ".join(map(str, shift_c))}
    }};

    int current_b = {current_b};

    {c_2d_array("M_fixed", M_fixed, f"fp{n_bits}_t")}
"""

    c_code += f"""
    for(int y = 0 ; y < {out_h} ; y++){{
        for(int x = 0 ; x < {out_w} ; x++){{
            int pixel_idx = y*{out_w}+x;
            R = 0;

            for(int i = 0 ; i < {k_h} ; i++){{
                for(int j = 0 ; j < {k_w} ; j++){{
                    int idx = i * {k_w} + j;

                    A = M_fixed[pixel_idx][idx];
                    B = K_fixed[idx];
                    C = R;

                    tmp = fp{n_bits}_mul(A, B, shift_tmp[idx]);

                    if(shift_c[idx] > 0){{
                        C = C << shift_c[idx];
                    }} else if(shift_c[idx] < 0){{
                        C = C >> (-shift_c[idx]);
                    }}

                    R = fp{n_bits}_add(C, tmp);
                }}
            }}

            OUT_fp[y][x] = R;
            OUT[y][x] = (float)R / (1 << current_b);
        }}
    }}

    printf("Output Matrix Fixed-Point:\\n");
    for(int i = 0; i < {out_h}; i++){{
        for(int j = 0; j < {out_w}; j++){{
            printf("%d ", OUT_fp[i][j]);
        }}
        printf("\\n");
    }}

    printf("Output Matrix Float:\\n");
    for(int i = 0; i < {out_h}; i++){{
        for(int j = 0; j < {out_w}; j++){{
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