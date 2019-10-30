import numpy as np


def Resize(fiber, scale, mod='all'):
    fiber = np.array(fiber, copy=True)
    if mod is 'all':
        fiber *= scale
    elif mod is 'points':
        fiber[:, :3] *= scale
    elif mod is 'radii':
        fiber[:, -1] *= scale
    else:
        raise ValueError('mod = [all, points, radii]')
    return fiber


def Rotate(fiber, rot, offset=None):
    rot = np.array(rot, copy=False)
    fiber = np.array(fiber, copy=True)
    if offset is None:
        fiber[:, :3] = np.dot(rot, fiber[:, :3].T).T
    else:
        offset = np.array(offset, copy=False)
        fiber[:, :3] = np.dot(rot, (fiber[:, :3] - offset).T).T + offset
    return fiber


def Translate(fiber, offset):
    fiber = np.array(fiber, copy=True)
    offset = np.array(offset, copy=False)
    fiber[:, :3] += offset
    return fiber
