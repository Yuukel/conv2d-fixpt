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

            # Load operands.
            code.append(f"""
            A = {convert_to_fixed_point(M[0+i][0+j], F[0+i][0+j])};
            B = {convert_to_fixed_point(K[0+i][0+j], KF[0+i][0+j])};
            C = R;
            """)

            # Debug display
            code.append(f"""
            printf("A : ");
            for (int i = 7; i >= 0; i--) {{
                printf("%d", (A >> i) & 1);
            }}
            printf(" (%d) ", A);
            printf("B : ");
            for (int i = 7; i >= 0; i--) {{
                printf("%d", (B >> i) & 1);
            }}
            printf(" (%d) ", B);
            printf("C : ");
            for (int i = 7; i >= 0; i--) {{
                printf("%d", (C >> i) & 1);
            }}
            printf(" (%d) ", C);

            printf("\\n");
            """)

            # Multiply fixed-point values
            code.append(f"""
            tmp = fp{n_bits}_mul(A, B);

            printf(" TMP : ");
            for (int i = 7; i >= 0; i--) {{
                printf("%d", (tmp >> i) & 1);
            }}
            printf(" (%d) ", tmp);

            printf("\\n");
            """)

            # Theoretical multiplication format
            tmp_format = mul_format(F[0+i][0+j], KF[0+i][0+j])

            # Reduce format if it exceed n_bits
            reduce_format(tmp_format, n_bits)

            # Interval multiplication
            tmp_interval = mul_interval(I[0+i][0+j], KI[0+i][0+j])

            # Minimal format from interval analysis
            tmp_format_interval = find_format(tmp_interval, -(2**(n_bits-1)), 2**(n_bits-1)-1, n_bits)

            print(f"tmp_format: {tmp_format}, "
                  f"tmp_interval: {tmp_interval}, "
                  f"tmp_format_interval: {tmp_format_interval}")

            # Align tmp scaling
            shift = tmp_format.a - tmp_format_interval.a

            if shift > 0:
                code.append(f"""
                tmp = tmp << {shift};
                printf("(1) TMP après shift : ");
                for (int i = 7; i >= 0; i--) {{
                    printf("%d", (tmp >> i) & 1);
                }}
                printf(" (%d) ", tmp);
                printf("\\n");
                """)

            # Align accumulator format
            if(tmp_format_interval.a > C_format.a):
                code.append(f"""
                C = C << {tmp_format_interval.a - C_format.a};
                printf("(2) C après shift : ");
                for (int i = 7; i >= 0; i--) {{
                    printf("%d", (C >> i) & 1);
                }}
                printf("\\n");
                """)
            elif(tmp_format_interval.a < C_format.a):
                code.append(f"""
                tmp = C << {C_format.a - tmp_format_interval.a};
                printf("(2) TMP après shift : ");
                for (int i = 7; i >= 0; i--) {{
                    printf("%d", (tmp >> i) & 1);
                }}
                printf("\\n");
                """)

            # Interval after accumulation
            interval_add = add_interval(C_interval, tmp_interval)

            # Minimal accumulation format
            interval_add_format = find_format(interval_add, -(2**(n_bits-1)), 2**(n_bits-1)-1, n_bits)

            print(f"interval_add: {interval_add}, "
                  f"interval_add_format: {interval_add_format}")

            # Theoretical addition format
            format_add = add_format(C_format, tmp_format_interval)

            # Handle carry bit
            if(interval_add_format.a == format_add.a):
                code.append(f"""
                C = C << 1;
                printf("(3) C après shift : ");
                for (int i = 7; i >= 0; i--) {{
                    printf("%d", (C >> i) & 1);
                }}
                printf("\\n");

                tmp = tmp << 1;
                printf("(3) TMP après shift : ");
                for (int i = 7; i >= 0; i--) {{
                    printf("%d", (tmp >> i) & 1);
                }}
                printf("\\n");
                """)

            # Final accumulation
            code.append(f"""
            R = fp{n_bits}_add(C, tmp);
            printf("R : ");
            for (int i = 7; i >= 0; i--) {{
                printf("%d", (R >> i) & 1);
            }}
            printf(" (%d) ", R);
            printf("\\n");
            printf("\\n");
            """)

            # Update accumulator state
            C_format = interval_add_format
            C_interval = interval_add

    print(f"Final C_format: {C_format}, "
          f"Final C_interval: {C_interval}")
    return "\n".join(code)

def generate_c_file(M, K, F, KF, I, KI, n_bits, output_path="gen/conv_pixel.c"):
    """
    Generate full C source file.
    """

    header_code = generate_c_header()

    c_code = f"""{header_code}

int main(){{
    fp{n_bits}_t A, B, C, tmp, R;
"""

    # Generate one convolution pixel
    for i in range(1):
        for j in range(1):
            pixel_code = generate_conv_pixel_c(M[i:i+K.shape[0],j:j+K.shape[1]], K, F[i:i+K.shape[0],j:j+K.shape[1]], KF, I, KI, n_bits)
            c_code += pixel_code

    c_code += "return 0;\n}"

    # Create output directory if needed
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write generated C code
    output_path.write_text(c_code)