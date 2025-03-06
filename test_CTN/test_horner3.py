import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
from fixedpoint import FixedPoint

def horner_fixed_point(coefficients, x, int_bits, frac_bits):
    """
    Evaluate polynomial using Horner's method with fixed-point arithmetic.

    Args:
        coefficients: List of polynomial coefficients [a_n, a_{n-1}, ..., a_1, a_0]
        x: Value at which to evaluate the polynomial
        int_bits: Number of bits for integer part
        frac_bits: Number of bits for fractional part

    Returns:
        Polynomial value at x using fixed-point arithmetic
    """
    # Convert x to fixed-point
    x_fixed = FixedPoint(x, signed=True, m=int_bits, n=frac_bits)

    # Initialize result as fixed-point
    result = FixedPoint(0, signed=True, m=int_bits, n=frac_bits)

    # Apply Horner's method with fixed-point arithmetic
    for coefficient in coefficients:
        coef_fixed = FixedPoint(coefficient, signed=True, m=int_bits, n=frac_bits)
        result = result * x_fixed + coef_fixed

    return float(result)

p = np.array([ 0.65360594, -2.45201911,  3.66681941, -2.87040581,  1.27712266,
       -0.35692813,  0.15802103])
em = 0.0011760858526838373

data = np.genfromtxt("arduino_xy.csv", delimiter=" ")
print(data)

plt.figure()
H = np.linspace(0.1, 0.9, 1000)
# em = (np.polyval(p, H)-np.vectorize(lambda x: horner_fixed_point(p, x, 8, 8))(H)).mean()
em = (np.polyval(p, data[:,0])-data[:,1]).mean()
print(em)
plt.plot(H, 2900*np.polyval(p, H), label="pol")
# plt.plot(H, np.vectorize(lambda x: horner_fixed_point(p, x, 8, 8))(H)+em, label="fp")
plt.plot(data[:,0], data[:,1], label="arduino")
# plt.plot(data[:,0], data[:,1]+em, label="arduino-fixed")
plt.grid()
plt.xlabel("H [∅]")
plt.ylabel("T [°C]")
plt.legend()
plt.show()
