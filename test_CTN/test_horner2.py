import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
from decimal import Decimal, getcontext, ROUND_HALF_UP

# Function to evaluate polynomial using Horner's method with high precision
def horner_high_precision(coefficients, x):
    """
    Evaluate polynomial using Horner's method with Python's native floating-point precision.

    Args:
        coefficients: List of polynomial coefficients [a_n, a_{n-1}, ..., a_1, a_0]
        x: Value at which to evaluate the polynomial

    Returns:
        Polynomial value at x
    """
    result = 0
    for coefficient in coefficients:
        result = result * x + coefficient
    return result

# Function to evaluate polynomial using Horner's method with Arduino-like fixed-point precision
def horner_arduino_simulation(coefficients, x, precision):
    """
    Evaluate polynomial using Horner's method with fixed-point arithmetic using Decimal.

    Args:
        coefficients: List of polynomial coefficients [a_n, a_{n-1}, ..., a_1, a_0]
        x: Value at which to evaluate the polynomial
        precision: Number of decimal places for the fixed-point arithmetic

    Returns:
        Polynomial value at x using fixed-point arithmetic
    """
    # Set context precision for this calculation
    getcontext().prec = precision
    getcontext().rounding = ROUND_HALF_UP

    # Convert x to Decimal with proper rounding to simulate fixed-point
    x_fixed = Decimal(str(x)).quantize(Decimal('0.' + '0' * (precision-1) + '1'))

    # Initialize result
    result = Decimal('0')

    # Apply Horner's method with fixed-point arithmetic
    for coefficient in coefficients:
        coef_fixed = Decimal(str(coefficient)).quantize(Decimal('0.' + '0' * (precision-1) + '1'))
        result = (result * x_fixed).quantize(Decimal('0.' + '0' * (precision-1) + '1'))
        result = (result + coef_fixed).quantize(Decimal('0.' + '0' * (precision-1) + '1'))

    return float(result)

# Function to simulate Arduino's 8-bit fixed-point implementation more accurately
def horner_arduino_8bit(coefficients, x, int_bits, frac_bits):
    """
    More accurate simulation of Arduino's fixed-point arithmetic using an 8-bit microcontroller.

    Args:
        coefficients: List of polynomial coefficients
        x: Value at which to evaluate the polynomial
        int_bits: Number of bits for the integer part
        frac_bits: Number of bits for the fractional part

    Returns:
        Polynomial value using 8-bit fixed-point arithmetic
    """
    # Calculate scale factor based on fractional bits
    scale = 2 ** frac_bits

    # Convert x to fixed-point integer representation
    x_fixed = int(x * scale)

    # Clamp to representable range for Q(int_bits.frac_bits) format
    max_val = (2 ** (int_bits + frac_bits - 1)) - 1
    min_val = -(2 ** (int_bits + frac_bits - 1))

    if x_fixed > max_val:
        x_fixed = max_val
    elif x_fixed < min_val:
        x_fixed = min_val

    # Initialize result
    result = 0

    # Apply Horner's method with fixed-point arithmetic and overflow handling
    for coefficient in coefficients:
        # Convert coefficient to fixed-point
        coef_fixed = int(coefficient * scale)

        # Clamp coefficient to representable range
        if coef_fixed > max_val:
            coef_fixed = max_val
        elif coef_fixed < min_val:
            coef_fixed = min_val

        # Multiply: Need to scale down after multiplication to maintain fixed-point format
        result = (result * x_fixed) // scale

        # Clamp after multiplication
        if result > max_val:
            result = max_val
        elif result < min_val:
            result = min_val

        # Add coefficient
        result = result + coef_fixed

        # Clamp after addition
        if result > max_val:
            result = max_val
        elif result < min_val:
            result = min_val

    # Convert back to floating point
    return result / scale

# Function to compare the implementations and analyze error
def compare_implementations(coefficients, x_values, precisions, bit_formats):
    """
    Compare high-precision, Decimal-based fixed-point, and 8-bit fixed-point implementations.

    Args:
        coefficients: List of polynomial coefficients
        x_values: List of x values to evaluate
        precisions: List of decimal precisions to test
        bit_formats: List of (int_bits, frac_bits) tuples for 8-bit simulation

    Returns:
        Dictionary of results
    """
    results = {
        'decimal': {},
        '8bit': {}
    }

    # Test decimal-based fixed-point with different precisions
    for precision in precisions:
        high_precision_results = []
        arduino_results = []
        absolute_errors = []
        relative_errors = []

        for x in x_values:
            high_precision = horner_high_precision(coefficients, x)

            try:
                arduino = horner_arduino_simulation(coefficients, x, precision)
                abs_error = abs(high_precision - arduino)
                rel_error = abs_error / abs(high_precision) if high_precision != 0 else float('inf')
            except Exception as e:
                arduino = "Error"
                abs_error = float('inf')
                rel_error = float('inf')

            high_precision_results.append(high_precision)
            arduino_results.append(arduino)
            absolute_errors.append(abs_error)
            relative_errors.append(rel_error)

        # Prepare results for this precision
        precision_results = []
        for i, x in enumerate(x_values):
            if arduino_results[i] != "Error":
                precision_results.append([
                    x,
                    high_precision_results[i],
                    arduino_results[i],
                    absolute_errors[i],
                    relative_errors[i] * 100  # Convert to percentage
                ])
            else:
                precision_results.append([
                    x,
                    high_precision_results[i],
                    "Error",
                    "N/A",
                    "N/A"
                ])

        results['decimal'][precision] = precision_results

    # Test 8-bit fixed-point with different bit formats
    for int_bits, frac_bits in bit_formats:
        high_precision_results = []
        arduino_results = []
        absolute_errors = []
        relative_errors = []

        for x in x_values:
            high_precision = horner_high_precision(coefficients, x)

            try:
                arduino = horner_arduino_8bit(coefficients, x, int_bits, frac_bits)
                abs_error = abs(high_precision - arduino)
                rel_error = abs_error / abs(high_precision) if high_precision != 0 else float('inf')
            except Exception as e:
                arduino = "Error"
                abs_error = float('inf')
                rel_error = float('inf')

            high_precision_results.append(high_precision)
            arduino_results.append(arduino)
            absolute_errors.append(abs_error)
            relative_errors.append(rel_error)

        # Prepare results for this bit format
        format_results = []
        for i, x in enumerate(x_values):
            if arduino_results[i] != "Error":
                format_results.append([
                    x,
                    high_precision_results[i],
                    arduino_results[i],
                    absolute_errors[i],
                    relative_errors[i] * 100  # Convert to percentage
                ])
            else:
                format_results.append([
                    x,
                    high_precision_results[i],
                    "Error",
                    "N/A",
                    "N/A"
                ])

        results['8bit'][(int_bits, frac_bits)] = format_results

    return results

# Plot results for decimal-based fixed-point
def plot_decimal_results(x_values, results, precisions):
    plt.figure(figsize=(15, 10))

    # Plot polynomial evaluations
    plt.subplot(2, 2, 1)
    plt.plot(x_values, [res[1] for res in results[precisions[0]]], 'b-', label='High Precision')

    for precision in precisions:
        valid_indices = [i for i, res in enumerate(results[precision]) if res[2] != "Error"]
        valid_x = [x_values[i] for i in valid_indices]
        valid_y = [results[precision][i][2] for i in valid_indices]

        if valid_x:
            plt.plot(valid_x, valid_y, '--', label=f'Decimal (prec={precision})')

    plt.title('Polynomial Evaluation (Decimal)')
    plt.xlabel('x')
    plt.ylabel('P(x)')
    plt.legend()
    plt.grid(True)

    # Plot absolute errors
    plt.subplot(2, 2, 2)
    for precision in precisions:
        valid_indices = [i for i, res in enumerate(results[precision]) if res[3] != "N/A"]
        valid_x = [x_values[i] for i in valid_indices]
        valid_abs_errors = [results[precision][i][3] for i in valid_indices]

        if valid_x:
            plt.plot(valid_x, valid_abs_errors, '-', label=f'Precision={precision}')

    plt.title('Absolute Error (Decimal)')
    plt.xlabel('x')
    plt.ylabel('Error')
    plt.legend()
    plt.grid(True)
    plt.yscale('log')  # Log scale for better visualization

    # Plot relative errors
    plt.subplot(2, 2, 3)
    for precision in precisions:
        valid_indices = [i for i, res in enumerate(results[precision]) if res[4] != "N/A"]
        valid_x = [x_values[i] for i in valid_indices]
        valid_rel_errors = [results[precision][i][4] for i in valid_indices]

        if valid_x:
            plt.plot(valid_x, valid_rel_errors, '-', label=f'Precision={precision}')

    plt.title('Relative Error % (Decimal)')
    plt.xlabel('x')
    plt.ylabel('Error %')
    plt.legend()
    plt.grid(True)
    plt.yscale('log')

    # Comparison of errors at a specific x value
    plt.subplot(2, 2, 4)
    middle_x_index = len(x_values) // 2
    precision_values = []
    error_values = []

    for precision in precisions:
        if results[precision][middle_x_index][4] != "N/A":
            precision_values.append(precision)
            error_values.append(results[precision][middle_x_index][4])

    if precision_values:
        plt.bar([str(p) for p in precision_values], error_values)
        plt.title(f'Relative Error % at x={x_values[middle_x_index]} (Decimal)')
        plt.xlabel('Precision')
        plt.ylabel('Error %')
        plt.grid(True)

    plt.tight_layout()
    plt.show()

# Plot results for 8-bit fixed-point
def plot_8bit_results(x_values, results, bit_formats):
    plt.figure(figsize=(15, 10))

    # Plot polynomial evaluations
    plt.subplot(2, 2, 1)
    first_format = bit_formats[0]
    plt.plot(x_values, [res[1] for res in results[first_format]], 'b-', label='High Precision')

    for bit_format in bit_formats:
        valid_indices = [i for i, res in enumerate(results[bit_format]) if res[2] != "Error"]
        valid_x = [x_values[i] for i in valid_indices]
        valid_y = [results[bit_format][i][2] for i in valid_indices]

        if valid_x:
            plt.plot(valid_x, valid_y, '--', label=f'Q{bit_format[0]}.{bit_format[1]}')

    plt.title('Polynomial Evaluation (8-bit)')
    plt.xlabel('x')
    plt.ylabel('P(x)')
    plt.legend()
    plt.grid(True)

    # Plot absolute errors
    plt.subplot(2, 2, 2)
    for bit_format in bit_formats:
        valid_indices = [i for i, res in enumerate(results[bit_format]) if res[3] != "N/A"]
        valid_x = [x_values[i] for i in valid_indices]
        valid_abs_errors = [results[bit_format][i][3] for i in valid_indices]

        if valid_x:
            plt.plot(valid_x, valid_abs_errors, '-', label=f'Q{bit_format[0]}.{bit_format[1]}')

    plt.title('Absolute Error (8-bit)')
    plt.xlabel('x')
    plt.ylabel('Error')
    plt.legend()
    plt.grid(True)
    plt.yscale('log')

    # Plot relative errors
    plt.subplot(2, 2, 3)
    for bit_format in bit_formats:
        valid_indices = [i for i, res in enumerate(results[bit_format]) if res[4] != "N/A"]
        valid_x = [x_values[i] for i in valid_indices]
        valid_rel_errors = [results[bit_format][i][4] for i in valid_indices]

        if valid_x:
            plt.plot(valid_x, valid_rel_errors, '-', label=f'Q{bit_format[0]}.{bit_format[1]}')

    plt.title('Relative Error % (8-bit)')
    plt.xlabel('x')
    plt.ylabel('Error %')
    plt.legend()
    plt.grid(True)
    plt.yscale('log')

    # Comparison of errors at a specific x value
    plt.subplot(2, 2, 4)
    middle_x_index = len(x_values) // 2
    format_labels = []
    error_values = []

    for bit_format in bit_formats:
        if results[bit_format][middle_x_index][4] != "N/A":
            format_labels.append(f'Q{bit_format[0]}.{bit_format[1]}')
            error_values.append(results[bit_format][middle_x_index][4])

    if format_labels:
        plt.bar(format_labels, error_values)
        plt.title(f'Relative Error % at x={x_values[middle_x_index]} (8-bit)')
        plt.xlabel('Fixed-point Format')
        plt.ylabel('Error %')
        plt.grid(True)

    plt.tight_layout()
    plt.show()

# Example usage
def main():
    # Define a polynomial: 2x^3 - 4x^2 + 3x - 1
    coefficients = [2, -4, 3, -1]

    # Define range of x values to test
    x_values = np.linspace(-2, 2, 9)

    # Define precisions to test for decimal-based fixed-point
    precisions = [3, 6, 9]

    # Define bit formats to test for 8-bit fixed-point
    # Format: (int_bits, frac_bits)
    bit_formats = [(4, 4), (3, 5), (2, 6)]

    # Compare implementations
    results = compare_implementations(coefficients, x_values, precisions, bit_formats)

    # Print results for decimal-based fixed-point
    print("Results using Decimal with different precisions:")
    for precision in precisions:
        headers = ["x", "High Precision", f"Decimal (prec={precision})", "Absolute Error", "Relative Error (%)"]
        print(f"\nResults with precision = {precision}:")
        print(tabulate(results['decimal'][precision], headers=headers, floatfmt=".9f"))

    # Print results for 8-bit fixed-point
    print("\n\nResults using 8-bit fixed-point with different formats:")
    for int_bits, frac_bits in bit_formats:
        headers = ["x", "High Precision", f"8-bit Q{int_bits}.{frac_bits}", "Absolute Error", "Relative Error (%)"]
        print(f"\nResults with Q{int_bits}.{frac_bits} format:")
        print(tabulate(results['8bit'][(int_bits, frac_bits)], headers=headers, floatfmt=".9f"))

    # Plot results
    plot_decimal_results(x_values, results['decimal'], precisions)
    plot_8bit_results(x_values, results['8bit'], bit_formats)

    # Test with a more complex polynomial
    print("\n\nTesting with a more complex polynomial:")
    complex_coefficients = [0.0001, -0.0153, 0.2341, -1.4532, 3.8761, -2.1]

    complex_results = compare_implementations(complex_coefficients, x_values, precisions, bit_formats)

    # Plot results for complex polynomial
    plot_decimal_results(x_values, complex_results['decimal'], precisions)
    plot_8bit_results(x_values, complex_results['8bit'], bit_formats)

if __name__ == "__main__":
    main()
