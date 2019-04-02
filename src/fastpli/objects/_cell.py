from .__cell import _Cell
import numpy as np


class Cell(_Cell):

    def __init__(self, points, radii):
        super().__init__(
            np.asarray(points, dtype=np.float32),
            np.asarray(radii, dtype=np.float32))

    @property
    def data(self):
        return (self.points, self.radii)

    def rotate(self, mat):
        super().rotate(mat.flatten())

    def rotate_around_point(self, mat, p):
        super().rotate_around_point(mat.flatten(), p)