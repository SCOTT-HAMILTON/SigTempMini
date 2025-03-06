import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

T0 = 273.15+25
B = 4887
R0 = 1e3

T = np.linspace(273.15-30, 373.15, 1000)

# def R1(T):
#     return np.exp(B*(1/T-1/T0))

# def R2(T):
#     return 1/(1+np.exp(B*(T-T0)/(T0*T)))

# plt.figure()
# plt.plot(T-273.15, np.vectorize(R1)(T), label="R1")
# plt.plot(T-273.15, np.vectorize(R2)(T), label="R2")
# plt.plot(T-273.15, R2(T0)-B/(4*T0**2)*(T-T0), "--")
# plt.grid()
# plt.xlabel("T [°C]")
# plt.legend()

# def H1(T):
#     return 1/(1+1/R2(T))

# def H2(T):
#     return 1/(1+2/(1-B*(T-T0)/(2*T0**2)))

# def H3(T):
#     return (1/3)*(1-B*(T-T0)/(6*T0**2))


# plt.figure()
# plt.plot(T-273.15, np.vectorize(H1)(T), label="H1")
# plt.plot(T-273.15, np.vectorize(H2)(T), label="H2")
# plt.plot(T-273.15, np.vectorize(H3)(T), label="H3")
# plt.grid()
# plt.xlabel("T [°C]")
# plt.legend()


# def K1(T):
#     return 1/(1+1/R1(T))
# def K2(T):
#     return 1-np.exp(B/T0-B/T)

# plt.figure()
# plt.plot(T-273.15, np.vectorize(K1)(T), label="K1")
# plt.plot(T-273.15, np.vectorize(K2)(T), label="K2")
# plt.grid()
# plt.xlabel("T [°C]")
# plt.legend()



# def Tr(R):
#     H = 0.6
#     alpha = R/R0
#     return -B/np.log((1/H-1)/(alpha*np.exp(B/T0)))

# plt.figure()
# R = np.linspace(R0*0.9, R0*1.1, 1000)
# plt.plot(R, np.vectorize(Tr)(R))
# plt.grid()
# plt.xlabel("R [Ω]")
# plt.axvline(x=R0)
# plt.legend()

def Ht(T):
    return 1/(1+np.exp(B*(1/T-1/T0)))
def Th1(H):
    alpha = 1
    return -1/np.log((1/H-1)/(alpha*np.exp(B/T0)))

def Th2(H):
    alpha = 1
    H0 = Ht(T0)
    return T0-(T0**2/B)*((1+alpha)**2/alpha)*(H-H0)

plt.figure()
H = np.linspace(0.1, 0.9, 1000)
x = H
y = np.vectorize(Th1)(H)
fit = np.polyfit(x, y, 6)
print(repr(fit))
# plt.plot(np.vectorize(Th1)(H)-273.15, np.vectorize(Th1)(H)-np.vectorize(Th2)(H), label="Th1")
plt.plot(H, np.vectorize(Th1)(H), label="Th1")
plt.plot(H, np.polyval(fit, H), label="pol")
# plt.plot(H, np.vectorize(Th2)(H)-273.15, label="Th2")
plt.grid()
plt.xlabel("H [∅]")
plt.ylabel("T [K]")
plt.legend()



# T = np.array([8.6, 9.7, 17.2, 17.7, 18.2, 20.0, 22.6])
# H = np.array([0.692, 0.64, 0.607, 0.604, 0.603, 0.564, 0.54])

# mask = (T < 10)
# T = T[mask]
# H = H[mask]
# def plot_T0(T0):
#     x = T/T0-1
#     y = T*np.log(1/H-1)
#     fit, stats = np.polynomial.polynomial.polyfit(x, y, 1, full=True)
#     # R2 = stats[0][0]
#     R2 = 0
#     B = fit[1]
#     print(fit)
#     print(f"B={B}K, R²={R2:.2f}")
#     plt.plot(x, y, "P", label=f"T0={T0-273.15}°C")
#     plt.plot(x, x*fit[1]+fit[0], "--", label=f"fit-T0={T0-273.15}°C")

# plt.figure()
# plot_T0(273.15+25)
# plot_T0(273.15+20)

def Th1(H, B, T0):
    alpha = 1
    return -B/np.log((1/H-1)/(alpha*np.exp(B/T0)))

T = np.array([17.2, 17.7, 18.2, 20.0, 22.6])
H = np.array([0.607, 0.604, 0.603, 0.564, 0.54])


# # Estimation initiale des paramètres
initial_guess = [2900, 25+273.15]
# # Ajustement des données
params, covariance = curve_fit(Th1, H, T+273.15, p0=initial_guess)
B_opt, T0_opt = params
print(f"fit results: B={B_opt:.2f} K, T0={T0_opt:.2f} K")
H_range = np.linspace(0.1, 0.9, 1000)
T_fit = Th1(H_range, *params)
# T_fit = Th1(H_range, 2900.0, 298.15, 285.01)
# Tracé de la courbe
plt.figure(figsize=(8, 6))
plt.plot(H_range, T_fit-273.15, label='Fitted Curve', color='blue')
plt.scatter(H, T, color='red', label='Data Points')
plt.xlabel('H')
plt.ylabel('T')
plt.legend()
plt.grid(True)

# # Affichage des résultats
# print(f"alpha: {alpha_opt}")
# print(f"B: {B_opt}")
# print(f"T0: {T0_opt}")

# Hs = np.linspace(0.5, 0.7, 1000)
# T2 = np.vectorize(Th1)(Hs)-273.15
# plt.plot(Hs, T2, "-", label="formula")
# plt.plot(H, T, "P", label="reel")
# plt.grid()
# plt.xlabel("T [°C]")
# plt.legend()

plt.show()
