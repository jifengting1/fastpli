import numpy as np


def epa(data):

    data = np.array(data, copy=False)

    n = data.shape[-1]
    rho_2 = 2 * np.linspace(0, np.pi, n, False, dtype=data.dtype)

    a0 = np.sum(data, -1) / n
    a1 = 2 * np.sum(data * np.sin(rho_2), -1) / n
    b1 = 2 * np.sum(data * np.cos(rho_2), -1) / n

    t = 2 * a0
    d = 0.5 * np.arctan2(-b1, a1) + np.pi
    r = np.sqrt(a1 * a1 + b1 * b1) / (a0 + 1e-16)

    d = d % np.pi

    return t, d, r


def direction(data):

    data = np.array(data, copy=False)

    n = data.shape[-1]
    rho_2 = 2 * np.linspace(0, np.pi, n, False, dtype=data.dtype)

    a1 = 2 * np.sum(data * np.sin(rho_2), 2) / n
    b1 = 2 * np.sum(data * np.cos(rho_2), 2) / n

    d = 0.5 * np.arctan2(-b1, a1) + np.pi

    d = d % np.pi

    return d
