from random import uniform

from matplotlib.patches import Rectangle
from matplotlib.pyplot import show, subplots, scatter


def random_color():
    return uniform(0, 1), uniform(0, 1), uniform(0, 1)


def visualize(things):
    # define Matplotlib figure and axis
    figure, axis = subplots()

    max_x = 0
    max_y = 0
    min_x = 0
    min_y = 0
    for label, thing in things:
        ints = thing
        if len(ints) == 2:
            scatter(ints[0], ints[1], color=random_color())
            max_x = max(max_x, ints[0])
            max_y = max(max_y, ints[1])
            min_x = min(min_x, ints[0])
            min_y = min(min_y, ints[1])
        elif len(ints) == 4:
            axis.add_patch(
                Rectangle(
                    (ints[0], ints[1]),
                    ints[2],
                    ints[3],
                    facecolor=(0, 0, 0, 0),
                    edgecolor=random_color(),
                    linewidth=2,
                )
            )
            max_x = max(max_x, ints[0], ints[0] + ints[2])
            max_y = max(max_y, ints[1], ints[1] + ints[3])
            min_x = min(min_x, ints[0], ints[0] + ints[2])
            min_y = min(min_y, ints[1], ints[1] + ints[3])
        else:
            raise RuntimeError("invalid input")
        axis.annotate(label, (ints[0], ints[1]))

    margin = 32
    min_dim = min(min_x, max_x, min_y, max_y)
    max_dim = max(min_x, max_x, min_y, max_y)
    axis.set_xbound(lower=min_dim - margin, upper=max_dim + margin)
    axis.set_ylim(max_dim + margin, min_dim - margin)

    # display plot
    show()
