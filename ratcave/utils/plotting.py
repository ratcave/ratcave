__author__ = 'nickdg'
import numpy as np

def plot_3d(array3d, title='', ax=None, line=False, color='', square_axis=False, show=False):
    """
    Make 3D scatterplot that plots the x, y, and z columns in a dataframe. Returns figure.

    Args:
        -array3d (Nx3 Numpy Array): data to plot.
        -ax (PyPlot Axis Object=None): Axis object to use.
        -line (bool=True):Whether to plot with lines instead of just points
        -color (str=''): the color to set.
        -square_axis (bool=False): Whether to square the axes to fit the data.
        -show (bool=False): Whether to immediately show the figure.  This is a blocking operation.

    Returns:
        -ax (PyPlot Axis Object): The Axis the data is plotted on.
    """

    from matplotlib import pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    if not ax:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

    if square_axis:
        tot_range = (array3d.max(axis=0) - array3d.min(axis=0)).max() * .55
        mn = array3d.mean(axis=0, keepdims=True) - tot_range
        mx = array3d.mean(axis=0, keepdims=True) + tot_range
        limits = np.vstack([mn, mx]).transpose()
        for coord, idx in zip('xyz', range(3)):
            getattr(ax, 'set_{0}lim3d'.format(coord))(limits[idx])

    plot_fun = ax.plot if line else ax.scatter
    if color:
        plot_fun(array3d[:, 0], array3d[:, 2], array3d[:, 1], color=color)
    else:
        plot_fun(array3d[:, 0], array3d[:, 2], array3d[:, 1])
    plt.title(title)
    plt.xlabel('x'), plt.ylabel('z')

    # Immediately display figure is show is True
    if show:
        plt.show()

    return ax