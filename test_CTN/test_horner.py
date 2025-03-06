import numpy as np
from fixedpoint import FixedPoint
import matplotlib.pyplot as plt
from tabulate import tabulate

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
def horner_arduino_simulation(coefficients, x, n_int_bits, n_frac_bits):
    """
    Evaluate polynomial using Horner's method with fixed-point arithmetic.

    Args:
        coefficients: List of polynomial coefficients [a_n, a_{n-1}, ..., a_1, a_0]
        x: Value at which to evaluate the polynomial
        n_int_bits: Number of bits for integer part
        n_frac_bits: Number of bits for fractional part

    Returns:
        Polynomial value at x using fixed-point arithmetic
    """
    # Convert x to fixed-point
    x_fixed = FixedPoint(x, signed=True, m=n_int_bits, n=n_frac_bits)

    # Initialize result as fixed-point
    result = FixedPoint(0, signed=True, m=n_int_bits, n=n_frac_bits)

    # Apply Horner's method with fixed-point arithmetic
    for coefficient in coefficients:
        coef_fixed = FixedPoint(coefficient, signed=True, m=n_int_bits, n=n_frac_bits)
        result = result * x_fixed + coef_fixed

    return float(result)

# Function to compare the implementations and analyze error
def compare_implementations(coefficients, x_values, n_int_bits=8, n_frac_bits=8):
    """
    Compare high-precision and Arduino-like fixed-point implementations.

    Args:
        coefficients: List of polynomial coefficients
        x_values: List of x values to evaluate
        n_int_bits: Number of bits for integer part in fixed-point representation
        n_frac_bits: Number of bits for fractional part in fixed-point representation

    Returns:
        DataFrame with comparison results
    """
    high_precision_results = []
    arduino_results = []
    absolute_errors = []
    relative_errors = []

    for x in x_values:
        high_precision = horner_high_precision(coefficients, x)
        arduino = horner_arduino_simulation(coefficients, x, n_int_bits, n_frac_bits)

        abs_error = abs(high_precision - arduino)
        rel_error = abs_error / abs(high_precision) if high_precision != 0 else float('inf')

        high_precision_results.append(high_precision)
        arduino_results.append(arduino)
        absolute_errors.append(abs_error)
        relative_errors.append(rel_error)

    # Prepare results
    results = []
    for i, x in enumerate(x_values):
        results.append([
            x,
            high_precision_results[i],
            arduino_results[i],
            absolute_errors[i],
            relative_errors[i] * 100  # Convert to percentage
        ])

    return results

# Example usage
def main():
    # Define a polynomial: 2x^3 - 4x^2 + 3x - 1
    coefficients = [2, -4, 3, -1]

    # Define range of x values to test
    x_values = np.linspace(-2, 2, 9)

    # Compare implementations with 8 bits for integer part and 8 bits for fractional part (common for Arduino)
    results_8_8 = compare_implementations(coefficients, x_values, n_int_bits=8, n_frac_bits=8)

    # Compare implementations with 8 bits for integer part and 16 bits for fractional part
    results_8_16 = compare_implementations(coefficients, x_values, n_int_bits=8, n_frac_bits=16)

    # Print results in a table
    headers = ["x", "High Precision", "Arduino (8.8)", "Absolute Error", "Relative Error (%)"]
    print("Results with 8.8 fixed-point format:")
    print(tabulate(results_8_8, headers=headers, floatfmt=".8f"))

    # Print results with higher precision
    headers = ["x", "High Precision", "Arduino (8.16)", "Absolute Error", "Relative Error (%)"]
    print("\nResults with 8.16 fixed-point format:")
    print(tabulate(results_8_16, headers=headers, floatfmt=".8f"))

    # Plot the results
    plt.figure(figsize=(12, 10))

    # Plot polynomial evaluations
    plt.subplot(2, 2, 1)
    plt.plot(x_values, [res[1] for res in results_8_8], 'b-', label='High Precision')
    plt.plot(x_values, [res[2] for res in results_8_8], 'r--', label='Arduino (8.8)')
    plt.title('Polynomial Evaluation')
    plt.xlabel('x')
    plt.ylabel('P(x)')
    plt.legend()
    plt.grid(True)

    # Plot absolute error for 8.8 format
    plt.subplot(2, 2, 2)
    plt.plot(x_values, [res[3] for res in results_8_8], 'g-')
    plt.title('Absolute Error (8.8 format)')
    plt.xlabel('x')
    plt.ylabel('Error')
    plt.grid(True)

    # Plot relative error for 8.8 format
    plt.subplot(2, 2, 3)
    plt.plot(x_values, [res[4] for res in results_8_8], 'm-')
    plt.title('Relative Error % (8.8 format)')
    plt.xlabel('x')
    plt.ylabel('Error %')
    plt.grid(True)

    # Plot comparison of relative errors between 8.8 and 8.16 formats
    plt.subplot(2, 2, 4)
    plt.plot(x_values, [res[4] for res in results_8_8], 'm-', label='8.8 format')
    plt.plot(x_values, [res[4] for res in results_8_16], 'c--', label='8.16 format')
    plt.title('Relative Error % Comparison')
    plt.xlabel('x')
    plt.ylabel('Error %')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
