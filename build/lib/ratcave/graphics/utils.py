import pyglet.gl as gl
import numpy as np
import pdb

def vec(floatlist,newtype='float'):

        """ Makes GLfloat or GLuint vector containing float or uint args.
        By default, newtype is 'float', but can be set to 'int' to make
        uint list. """

        if 'float' in newtype:
            return (gl.GLfloat * len(floatlist))(*list(floatlist))
        elif 'int' in newtype:
            return (gl.GLuint * len(floatlist))(*list(floatlist))

def plot3_square(axis_object, data, color='b', limits=None):
    """Convenience function for plotting a plot3 scatterplot with square axes."""
    # Set axis limits, if not already set.

    if limits == None:
        tot_range = (data.max(axis=0) - data.min(axis=0)).max() * .55
        mn = data.mean(axis=0, keepdims=True) - tot_range
        mx = data.mean(axis=0, keepdims=True) + tot_range
        limits = np.vstack([mn, mx]).transpose()

    # apply limits to the axis
    for coord, idx in zip('xyz', range(3)):
        getattr(axis_object, 'set_{0}lim3d'.format(coord))(limits[idx])

    # Plot
    axis_object.plot3D(data[:, 0], data[:, 1], data[:, 2], color+'o', zdir='y')

    return limits

def setpriority(pid=None,priority=1):
    
    """ Set The Priority of a Windows Process.  Priority is a value between 0-5 where
        2 is normal priority.  Default sets the priority of the current
        python process but can take any valid process ID. """
        
    import win32api,win32process,win32con
    
    priorityclasses = [win32process.IDLE_PRIORITY_CLASS,
                       win32process.BELOW_NORMAL_PRIORITY_CLASS,
                       win32process.NORMAL_PRIORITY_CLASS,
                       win32process.ABOVE_NORMAL_PRIORITY_CLASS,
                       win32process.HIGH_PRIORITY_CLASS,
                       win32process.REALTIME_PRIORITY_CLASS]
    if pid == None:
        pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, priorityclasses[priority])	
