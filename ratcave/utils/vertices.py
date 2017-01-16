import itertools
import numpy as np

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def struct_to_ndarray(array):
    """Turns returns a view of a structured array as a regular ndarray."""
    return array.view(array.dtype[0]).reshape((array.shape[0], -1))


def reindex_vertices(arrays=None):

    all_arrays = np.hstack(arrays)
    array_ncols = tuple(array.shape[1] for array in arrays)

    # Build a new array list, composed of only the unique combinations  (no redundant data)
    row_searchable_array = all_arrays.view(all_arrays.dtype.descr * all_arrays.shape[1])
    unique_combs = np.sort(np.unique(row_searchable_array))

    new_indices = np.array([np.searchsorted(unique_combs, vert) for vert in row_searchable_array]).flatten().astype(np.uint32)

    ucombs = struct_to_ndarray(unique_combs)
    new_arrays = tuple(ucombs[:, start:end] for start, end in pairwise(np.append(0, np.cumsum(array_ncols))))
    new_arrays = tuple(np.array(array, dtype=np.float32) for array in new_arrays)
    return new_arrays, new_indices


def calculate_normals(vertices):
    """Return Nx3 normal array from Nx3 vertex array."""
    verts = np.array(vertices, dtype=float)
    normals = np.zeros_like(verts)
    for start, end in pairwise(np.arange(0, verts.shape[0] + 1, 3)):
        vecs = np.vstack((verts[start + 1] - verts[start], verts[start + 2] - verts[start]))  # Get triangle of vertices and calculate 2-1 and 3-1
        vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)  # normalize vectors
        normal = np.cross(*vecs)  # normal is the cross products of vectors.
        normals[start:end, :] = normal / np.linalg.norm(normal)
    return normals
