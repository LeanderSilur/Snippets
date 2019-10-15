import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import scipy.integrate
import mpl_toolkits.mplot3d.axes3d as p3

# transform θ and φ to euler coordinates
def coords(θ, φ):
    X = np.sin(θ) * np.cos(φ)
    Y = np.sin(θ) * np.sin(φ)
    Z = - np.cos(θ)
    return np.array([X, Y, Z])

# the pendulum derivatives
def pend(y, t, mass, gravity, L, c):
    θ, dθ, φ, dφ = y
    dydt = [dθ,
            np.square(dφ) * np.sin(θ) * np.cos(θ) - gravity/L * np.sin(θ) - c/mass * dθ,
            dφ,
            (-2) * dθ * dφ / np.tan(θ) - c/mass * dφ
            ]
    return dydt

mass = 10
gravity = 10
L = 0.2
friction = 8



# intial values
y0 = [np.pi/2.5, 0.0, 0.0, 4]

# time values
t = np.linspace(0, 4, 200)

# create the solver
sol = scipy.integrate.odeint(pend, y0, t, args=(mass, gravity, L, friction))

# plot the graph
plt.plot(t, sol[:, 0], label='θ(t)')
plt.plot(t, sol[:, 1], label='dθ(t)')
plt.plot(t, sol[:, 2], label='φ(t)')
plt.plot(t, sol[:, 3], label='dφ(t)')
plt.legend(loc='best')
plt.xlabel('t')
plt.grid()
plt.axis([None, None, -5, 5])
plt.show()

# plot the animation
fig = plt.figure()
ax = p3.Axes3D(fig)

string, = ax.plot(*np.zeros((3, 2)), color='k', lw=1, zorder=3)
bob, = ax.plot([0], [0], 'ro', color='#dd5500', zorder=4)
projx, = ax.plot(*np.zeros((3, 2)), color='r', alpha=0.3, lw=1)
projy, = ax.plot(*np.zeros((3, 2)), color='g', alpha=0.3, lw=1)
projz, = ax.plot(*np.zeros((3, 2)), color='b', alpha=0.3, lw=1)
positions = [coords(sol[i, 0], sol[i, 2]).reshape((3, 1)) for i in range(len(sol))]
positions = np.array(positions)
swapped = np.swapaxes(positions, 0, 1).reshape((3, -1))
trace = plt.plot(*swapped, color='#cccccc', lw=1)[0]

def drawPendulum(i):
    x, y, z = positions[i,:,0]
    bob.set_data(positions[i][:2])
    bob.set_3d_properties(positions[i][2])
    string_data = np.concatenate([np.zeros((3, 1)), positions[i]], axis = 1)
    string.set_data(string_data[:2])
    string.set_3d_properties(string_data[2])
    projx.set_data([0, x], [y, y])
    projx.set_3d_properties([z, z])
    projy.set_data([x, x], [0, y])
    projy.set_3d_properties([z, z])
    projz.set_data([x, x], [y, y])
    projz.set_3d_properties([0, z])
    return bob, string, trace, projx, projy, projz

#create a grid
divisions = 5
def grid(pmin, pmax, other = 0, pdiv=5):
    if other: return np.repeat(np.linspace(pmin, pmax, pdiv).reshape(-1, 1), pdiv, axis = 1)
    return np.repeat(np.linspace(pmin, pmax, pdiv).reshape(1, -1), pdiv, axis = 0)
ax.plot_wireframe(grid(0, 0), grid(-1, 1), grid(-1, 1, 1), colors='r', alpha=0.05)
ax.plot_wireframe(grid(-1, 1), grid(0, 0), grid(-1, 1, 1), colors='g', alpha=0.05)
ax.plot_wireframe(grid(-1, 1, 1), grid(-1, 1), grid(0, 0), colors='b', alpha=0.05)
ax.set_xticks([])
ax.set_yticks([])
ax.set_zticks([])

myAnimation = animation.FuncAnimation(fig, drawPendulum, frames= len(positions),
                                      interval=20, blit=False, repeat=False)

plt.show()