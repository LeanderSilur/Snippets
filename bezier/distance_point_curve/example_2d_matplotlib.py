import math
import numpy as np
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import bezier

# Point the curve to a matplotlib figure.
# maxes         ... the axes of a matplotlib figure
def plot_bezier(bezier, maxes):
    Path = mpath.Path
    pp1 = mpatches.PathPatch(
        Path(bezier.points, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]),
        fc="none")#, transform=ax.transData)
    pp1.set_alpha(1)
    pp1.set_color('#00cc00')
    pp1.set_fill(False)
    pp2 = mpatches.PathPatch(
        Path(bezier.points, [Path.MOVETO, Path.LINETO , Path.LINETO , Path.LINETO]),
        fc="none")#, transform=ax.transData)
    pp2.set_alpha(0.2)
    pp2.set_color('#666666')
    pp2.set_fill(False)

    maxes.scatter(*zip(*bezier.points), s=4, c=((0, 0.8, 1, 1), (0, 1, 0.5, 0.8), (0, 1, 0.5, 0.8),
                                                (0, 0.8, 1, 1)))
    maxes.add_patch(pp2)
    maxes.add_patch(pp1)


def matplotlib_example(bez, use_text):
    import matplotlib.pyplot as plt
    import matplotlib.path as mpath
    import matplotlib.patches as mpatches
    
    def onclick(event):
        if event.inaxes == None:return
        pt = np.array((event.xdata, event.ydata), dtype=np.float)
        print("pt", pt)
        points, distances, index = bez.measure_distance(pt)
        closest = points[index]
        distance = math.floor(distances[index])

        Path = mpath.Path
        pp1 = mpatches.PathPatch(Path([pt, closest], [Path.MOVETO, Path.LINETO]), fc="none")
        pp1.set_color("#95a7df")
        ax.add_patch(pp1)
        ax.scatter(*pt, s=32, facecolors='none', edgecolors='b')

        if use_text:
            ax.text(*((pt+closest)/2), str(distance))
            ax.text(*pt, str(pt.astype(np.int)))
            ax.text(*closest, str(closest.astype(np.int)))

        fig.canvas.draw()
        return None

    fig, ax = plt.subplots()
    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    ax.grid()
    ax.axis('equal')
    ax.margins(0.4)
    plot_bezier(bez, ax)
    plt.title("Click next to the curve.")
    plt.show()

if __name__ == "__main__":
    points = np.array([[0, 0], [0, 1], [1,.8], [1.5,1]]).astype(np.float32)
    points *= 50
    points += 10
    bez = bezier.Bezier(points)
    
    matplotlib_example(bez, use_text = False)