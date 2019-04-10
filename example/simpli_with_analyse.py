import h5py
import numpy as np
import sys
import os
import time

# save images
import scipy.misc
import nibabel as nib

# fastpli
from fastpli.simulation import Simpli
from fastpli.analysis import images

np.random.seed(42)

FILE_PATH = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
FILE_OUTPUT = '/tmp/'

# PliGeneration ###
simpli = Simpli()
simpli.pixel_size = 64
simpli.resolution = 64
simpli.set_voi([0, 1600, 0, 1600, 0, 64])
fiber_bundles = [[]]

# corner
fiber_bundles[-1].append(
    np.array([[0, 0, 30, 128],
              [
                  simpli.dim[0] * simpli.pixel_size,
                  simpli.dim[1] * simpli.pixel_size, 30, 64
              ]]))

# left right up
fiber_bundles[-1].append(
    np.array([[0, simpli.dim[1] * simpli.pixel_size * 0.5, 30, 64],
              [
                  simpli.dim[0] * simpli.pixel_size,
                  simpli.dim[1] * simpli.pixel_size * 0.5, 30, 64
              ], [simpli.dim[0] * simpli.pixel_size, 0, 30, 64]]))

# circle
t = np.linspace(0, 2 * np.pi, 50)
x = (np.sin(t) * (simpli.dim[0] // 3) + simpli.dim[0] // 2) * simpli.pixel_size
y = (np.cos(t) * (simpli.dim[1] // 3) + simpli.dim[1] // 2) * simpli.pixel_size
z = t * 0 + simpli.dim[2] * simpli.pixel_size / 2
r = t * 0 + 128
fiber_bundles[-1].append(np.array([x, y, z, r]).T)

simpli.fiber_bundles = fiber_bundles
simpli.fiber_bundles_properties = [[(1.0, 0.004, 1, 'p')]]

print("MemoryUseage:", '~' + str(int(simpli.MemoryUseage())) + ' MB')

with h5py.File(
        os.path.join(FILE_OUTPUT, 'example.' + FILE_NAME + '.new.h5'),
        'w') as h5f:

    with open(os.path.abspath(__file__), 'r') as f:
        h5f['script'] = f.read()

    label_field, vec_field, tissue_properties = simpli.GenerateTissue()

    dset = h5f.create_dataset('tissue', label_field.shape, np.uint16)
    dset[:] = label_field

    h5f['vectorfield'] = vec_field

    # PliSimulation ###
    simpli.filter_rotations = np.deg2rad([90, 120, 150, 0, 30, 60])
    simpli.light_intensity = 26000
    simpli.untilt_sensor = True
    simpli.wavelength = 525

    tilts = [(0, 0), (5.5, 0), (5.5, 90), (5.5, 180), (5.5, 270)]
    image_stack = []

    mask = None
    # mask = np.sum(label_field, 2) > 0
    # mask = simpli.apply_resize_mask(mask) > 0.1

    print("Run Simulations:")
    for t, (theta, phi) in enumerate(tilts):
        print('Step:', t, theta, phi)
        image = simpli.RunSimulation(label_field, vec_field, tissue_properties,
                                     np.deg2rad(theta), np.deg2rad(phi))
        h5f['data/' + str(t)] = image

        image = simpli.apply_optic(image)
        h5f['optic/' + str(t)] = image

        epa = simpli.apply_epa(image)
        h5f['epa/' + str(t) + '/transmittance'] = epa[0]
        h5f['epa/' + str(t) + '/direction'] = np.rad2deg(epa[1])
        h5f['epa/' + str(t) + '/retardation'] = epa[2]

        image_stack.append(image)

    # save mask for analysis, but restore None value so that everything gets analysed
    mask = np.sum(label_field, 2) > 0
    mask = simpli.apply_resize_mask(mask) > 0.1
    h5f['optic/mask'] = np.uint8(mask)
    # mask = None

    print("Run ROFL:")
    t0 = time.time()
    rofl_direction, rofl_incl, rofl_t_rel = simpli.apply_rofl(
        image_stack, mask=mask)

    print("ROFL time:", time.time() - t0)

    h5f['rofl/direction'] = np.rad2deg(rofl_direction)
    h5f['rofl/inclination'] = np.rad2deg(rofl_incl)

    print("Unit Vectors")
    unit_x, unit_y, unit_z = images.unit_vectors(rofl_direction, rofl_incl,
                                                 mask)
    img = nib.Nifti1Image(unit_x, np.eye(4))
    nib.save(img,
             os.path.join(FILE_OUTPUT, 'example.' + FILE_NAME + '.UnitX.nii'))
    img = nib.Nifti1Image(unit_y, np.eye(4))
    nib.save(img,
             os.path.join(FILE_OUTPUT, 'example.' + FILE_NAME + '.UnitY.nii'))
    img = nib.Nifti1Image(unit_z, np.eye(4))
    nib.save(img,
             os.path.join(FILE_OUTPUT, 'example.' + FILE_NAME + '.UnitZ.nii'))

    print("FOMs")
    img = images.fom_hsv_black(rofl_direction, rofl_incl, mask)
    scipy.misc.imsave(
        os.path.join(FILE_OUTPUT, 'example.' + FILE_NAME + '.hsv_black.png'),
        np.swapaxes(np.flip(img, 1), 0, 1))

    img = images.fom_rgb(rofl_direction, rofl_incl, mask)
    scipy.misc.imsave(
        os.path.join(FILE_OUTPUT, 'example.' + FILE_NAME + '.rgb.png'),
        np.swapaxes(np.flip(img, 1), 0, 1))

    img = images.hsvblack_sphere()
    scipy.misc.imsave(
        os.path.join(FILE_OUTPUT,
                     'example.' + FILE_NAME + '.hsv_black_sphere.png'),
        np.swapaxes(np.flip(img, 1), 0, 1))

    img = images.rgb_sphere()
    scipy.misc.imsave(
        os.path.join(FILE_OUTPUT, 'example.' + FILE_NAME + '.rgb_sphere.png'),
        np.swapaxes(np.flip(img, 1), 0, 1))
