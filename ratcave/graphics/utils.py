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


def axis_lims(data, buffer_perc=.1):
    """Returns axis limits for fitting 3D data into a square axis."""
    ranges = data.max(axis=0) - data.min(axis=0)
    tot_range = ranges.max() * (1 + buffer_perc) * 0.5
    mn = data.mean(axis=0, keepdims=True) - tot_range
    mx = data.mean(axis=0, keepdims=True) + tot_range
    return np.vstack([mn, mx]).transpose()


def set_all_lim3d(axis_object, axis_lims):
    """Applies axis limits to an Axis"""
    axis_object.set_xlim3d(axis_lims[0])
    axis_object.set_ylim3d(axis_lims[1])
    axis_object.set_zlim3d(axis_lims[2])
    return axis_object


def plot3_square(axis_object, data, color='b', lims=None):
    """Convenience function for plotting a plot3 scatterplot with square axes."""
    lims = lims if lims != None else axis_lims(data)

    axis_object = set_all_lim3d(axis_object, lims)
    plot = axis_object.plot3D(data[:, 0], data[:, 1], data[:, 2], color+'o', zdir='y')
    return lims

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
