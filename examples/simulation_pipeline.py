import numpy as np
import h5py
import os

import imageio
import multiprocessing as mp
pool = mp.Pool(2)

# reproducibility
np.random.seed(42)

import fastpli.simulation
import fastpli.io

FILE_NAME = os.path.abspath(__file__)
FILE_PATH = os.path.dirname(FILE_NAME)
FILE_BASE = os.path.basename(FILE_NAME)
FILE_OUT = os.path.join(FILE_PATH, f'fastpli.example.{FILE_BASE}')

# Setup Simpli for Tissue Generation
simpli = fastpli.simulation.Simpli()
simpli.omp_num_threads = 2

# define model
simpli.voxel_size = 2.0  # in micro meter
simpli.set_voi([-100, -100, -25], [2350, 550, 25])  # in micro meter
simpli.fiber_bundles = fastpli.io.fiber_bundles.load(
    os.path.join(FILE_PATH, 'fastpli.dat'))

# define layers (e.g. axon, myelin) inside fibers of each fiber_bundle fiber_bundle
simpli.fiber_bundles_properties = [[(1.0, -0.001, 10, 'p')]]
# (_0, _1, _2, _3)
# _0: layer_scale times radius
# _1: strength of birefringence
# _2: absorption coefficient I = I*exp(-mu*x)
# _3: model: 'p'-parallel, 'r'-radial or 'b'-background

# define pli setup
simpli.filter_rotations = np.deg2rad([0, 30, 60, 90, 120, 150])  # in deg
simpli.light_intensity = 26000  # a.u.
simpli.interpolate = "Slerp"
simpli.wavelength = 525  # in nm
simpli.pixel_size = 10  # in micro meter
simpli.tilts = np.deg2rad(
    np.array([(0, 0), (5.5, 0), (5.5, 90), (5.5, 180), (5.5, 270)]))  # in deg
simpli.sensor_gain = 3
simpli.optical_sigma = 0.71  # in voxel size
simpli.verbose = True

print(f'creating file: {FILE_OUT}.h5')
with h5py.File(f'{FILE_OUT}.h5', 'w') as h5f:
    with open(os.path.abspath(__file__), 'r') as script:
        _, _, _, fom = simpli.run_pipeline(h5f=h5f,
                                           script=script.read(),
                                           save=['all'],
                                           crop_tilt=True,
                                           mp_pool=pool)

    imageio.imwrite(f'{FILE_OUT}.fom.png', np.swapaxes(fom, 0, 1))

pool.close()

print('Done - You can look at the data e.g with Fiji and the hdf5 plugin')
