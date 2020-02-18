from .__solver import _Solver

from ... import io
from ... import objects
from ... import tools
from ... import version

import numpy as np
import warnings
import os


class Solver(_Solver):

    __isfrozen = False

    def __setattr__(self, key, value):
        if self.__isfrozen and not hasattr(self, key):
            raise TypeError("%r is a frozen class" % self)
        object.__setattr__(self, key, value)

    def __freeze(self):
        self.__isfrozen = True

    def __init__(self):
        super().__init__()

        self._drag = 0
        self._obj_min_radius = 0
        self._obj_mean_length = 0
        self._col_voi = None
        self._omp_num_threads = 1
        self._step_num = 0
        self.__display = None

        super()._set_omp_num_threads(self._omp_num_threads)

        self.__freeze()

    def get_dict(self):
        """
        Get all member variables which are properties
        """
        members = dict()
        for key, value in self.__dict__.items():
            if key == '_cells_populations' or key == '_fiber_bundles':
                continue
            if key.startswith("_") and not key.startswith(
                    "__") and not key.startswith("_Solver"):
                if isinstance(value, np.ndarray):
                    members[key[1:]] = value.tolist()
                else:
                    members[key[1:]] = value
        return members

    def set_dict(self, input):
        for key, value in input.items():
            if key.startswith("_"):
                raise ValueError("member variable cant be set directly")

            if value is not None:
                setattr(self, key, value)
            else:
                warnings.warn("None value in dict detected")

    @property
    def fiber_bundles(self):
        return super()._get_fiber_bundles()

    @fiber_bundles.setter
    def fiber_bundles(self, fbs):
        fbs = objects.fiber_bundles.Cast(fbs)
        super()._set_fiber_bundles(fbs)

    @property
    def drag(self):
        return super()._get_parameters()[0]

    @drag.setter
    def drag(self, value):
        self._drag = value
        super()._set_parameters(self._drag, self._obj_min_radius,
                                self._obj_mean_length)

    @property
    def step_num(self):
        return self._step_num

    @drag.setter
    def step_num(self, value):
        self._step_num = int(value)

    @property
    def reset_step_num(self):
        self._step_num = 0

    @property
    def obj_min_radius(self):
        return super()._get_parameters()[1]

    @obj_min_radius.setter
    def obj_min_radius(self, value):
        self._obj_min_radius = value
        super()._set_parameters(self._drag, self._obj_min_radius,
                                self._obj_mean_length)

    @property
    def obj_mean_length(self):
        return super()._get_parameters()[2]

    @obj_mean_length.setter
    def obj_mean_length(self, value):
        self._obj_mean_length = value
        super()._set_parameters(self._drag, self._obj_min_radius,
                                self._obj_mean_length)

    @property
    def parameters(self):
        parameters = super()._get_parameters()
        self._drag = parameters[0]
        self._obj_min_radius = parameters[1]
        self._obj_mean_length = parameters[2]
        return parameters

    @property
    def col_voi(self):
        return self._col_voi

    @col_voi.setter
    def col_voi(self, voi):
        # TODO:
        if not isinstance(voi, tuple):
            raise TypeError("col_voi := (min, max)")
        self._col_voi = voi
        super()._set_col_voi(self._col_voi[0], self._col_voi[1])

    @property
    def omp_num_threads(self):
        return self._omp_num_threads

    @omp_num_threads.setter
    def omp_num_threads(self, num):
        self._omp_num_threads = int(num)
        self._omp_num_threads = super()._set_omp_num_threads(
            self._omp_num_threads)

    def step(self):
        self._step_num += 1
        return super().step()

    def draw_scene(self):
        if self.__display is None:
            try:
                os.environ['DISPLAY']
                self.__display = True
            except BaseException:
                warnings.warn("test_opengl: no display detected")
                self.__display = False

        if self.__display:
            super().draw_scene()

    def apply_boundary_conditions(self, n_max=10):
        if not isinstance(n_max, int) or n_max <= 0:
            raise TypeError("only integer > 0 allowed")

        super().apply_boundary_conditions(n_max)

        return self.fiber_bundles

    def save_parameter_h5(self, h5f, script=None):
        h5f.attrs['fastpli/version'] = version.__version__
        h5f.attrs['fastpli/compiler'] = version.__compiler__
        h5f.attrs['fastpli/libraries'] = version.__libraries__
        h5f.attrs['fastpli/pip_freeze'] = tools.helper.pip_freeze()
        h5f.attrs['fastpli/solver'] = str(self.get_dict())
        if script:
            h5f.attrs['script'] = script

    def save_h5(self, h5f, script=None):
        io.fiber_bundles.save_h5(h5f, self.fiber_bundles)
        self.save_parameter_h5(h5f, script)

    def load_h5(self, h5f):
        self.fiber_bundles = io.fiber_bundles.load_h5(h5f)
        self.set_dict(dict(eval(str(h5f.attrs['fastpli/solver']))))

        if h5f.attrs['fastpli/version'] != version.__version__:
            warnings.warn("__version__ changed")

        if h5f.attrs['fastpli/pip_freeze'] != tools.helper.pip_freeze():
            warnings.warn("pip_freeze changed")