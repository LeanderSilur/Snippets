import numpy as np
from scipy import integrate
import matplotlib.pyplot as plt

def solvr(Y, t):
    return [Y[1], -2 * Y[0]-Y[1]]

a_t = np.arange(0, 25.0, 0.01)
asol = integrate.odeint(solvr, [1, 0], a_t)

plt.plot(a_t, asol)
plt.show()
print(asol)