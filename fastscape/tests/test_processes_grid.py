import numpy as np

from fastscape.processes import (RasterGrid2D,
                                 UniformRectilinearGrid2D)


def test_uniform_rectilinear_grid_2d():

    p = UniformRectilinearGrid2D(shape=np.array([3, 4]),
                                 spacing=np.array([5., 10.]),
                                 origin=np.array([0., 1.]))

    p.initialize()

    np.testing.assert_equal(p.shape, (3, 4))
    np.testing.assert_equal(p.spacing, (5., 10.))
    np.testing.assert_equal(p.origin, (0., 1.))
    np.testing.assert_equal(p.length, (10., 30.))
    assert p.size == 12
    assert p.area == 600.
    assert p.cell_area == 50.
    assert p.dx == 10.
    assert p.dy == 5.
    assert p.nx == 4
    assert p.ny == 3
    np.testing.assert_equal(p.x, np.array([1., 11., 21., 31.]))
    np.testing.assert_equal(p.y, np.array([0., 5., 10.]))


def test_raster_grid_2d():

    p = RasterGrid2D(shape=np.array([3, 4]),
                     length=np.array([10., 30.]))

    p.initialize()

    np.testing.assert_equal(p.spacing, (5., 10.))
    np.testing.assert_equal(p.origin, (0., 0.))
