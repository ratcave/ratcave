__author__ = 'ratcave'

import numpy as np


def hist_mask(data, threshold=.95, keep='lower'):
    """
    Returns boolean mask of values below a frequency percentage threshold (0-1).

    Args:
        -data (1D array)
        -threshold (float): 0-1
        -keep (str): lower, greater, middle. If middle, threshold is ignored,
                     and a single cluster is searched out.
    """

    bins = len(data)/100 if keep.lower() == 'middle' else len(data) / 2
    freq, val = np.histogram(data, bins=bins)
    freq = freq / np.sum(freq).astype(float)  # Normalize frequency data

    if keep.lower() in ('lower', 'upper'):
        cutoff_value = val[np.where(np.diff(np.cumsum(freq) < threshold))[0] + 1]
        cutoff_value = val[1] if len(cutoff_value)==0 else cutoff_value
        if keep.lower() == 'lower':
            return data < cutoff_value
        else:
            return data > cutoff_value
    else:
        histmask = np.ones(data.shape[0], dtype=bool)  # Initializing mask with all True values

        # Slowly increment the parameter until a strong single central cluster is found
        for param in np.arange(0.0005, .02, .0003):
            cutoff_values = val[np.where(np.diff(freq < param))[0]]
            if len(cutoff_values) == 2:
                histmask &= data > cutoff_values[0]
                histmask &= data < cutoff_values[1]
                return histmask
        else:
            return data > -100000.  # Return an all-true mask
            print("Warning: Histogram filter not finding a good parameter to form a central cluster. Please try again.")