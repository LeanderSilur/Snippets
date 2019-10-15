# pythonmatplotlibtips.blogspot.com/2018/01/solve-animate-single-pendulum-odeint-artistanimation.html

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.integrate import odeint


"""
θ       ... angle
ω′      ... velocity

θ′(t)=ω(t)
ω′(t)=−b ω(t)−c sin(θ(t))

y(t)=(  θ(t)   )
        ω(t)


y(0)=(    π−0.1   )
          0.0
"""


def pend(y, t, b, c):
    θ, ω = y
    dydt = [ω, -b*ω - c*np.sin(θ)]
    return dydt


b = 0.01        # friction
c = 5.0         # gravity / length
y0 = [np.pi/2, 0]
t = np.linspace(0, 20, 301)

sol = odeint(pend, y0, t, args=(b, c))

plt.plot(t, sol[:, 0], 'b', label='θ(t)')
plt.plot(t, sol[:, 1], 'g', label='ω(t)')
plt.legend(loc='best')
plt.xlabel('t')
plt.grid()
plt.show()

