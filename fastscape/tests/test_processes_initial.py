import numpy as np
import xsimlab as xs

import pytest

from fastscape.processes import (BareRockSurface,
                                 Escarpment,
                                 FlatSurface,
                                 NoErosionHistory)

def test_flat_surface():
    np.random.seed(5)

    grid = (3, 2)
    elevation = np.random.rand(*grid)

    np.random.seed(5)
    p = FlatSurface(shape=grid)
    p.initialize()
    
    np.testing.assert_equal(grid, p.shape)
    np.testing.assert_equal(elevation, p.elevation)


@pytest.mark.parametrize('inputs, expected_result', [
    ({'x_left': 2,
      'x_right': 3,
      'elevation_left': 7.,
      'elevation_right': 2.,
      'shape': np.array([3,2]),
      'x': np.array([1., 11., 21., 31.])},  np.array([[7., 2.],[7., 2.],[7., 2.]])),
    ({'x_left': 2,
      'x_right': 3,
      'elevation_left': 2.,
      'elevation_right': 7.,
      'shape': np.array([3,2]),
      'x': np.array([1., 11., 21., 31.])},  np.array([[2., 7.],[2., 7.],[2., 7.]])),
    ({'x_left': 2,
      'x_right': 3,
      'elevation_left': 7.,
      'elevation_right': 7.,
      'shape': np.array([3,2]),
      'x': np.array([1., 11., 21., 31.])},  np.array([[7., 7.],[7., 7.],[7., 7.]]))
])
def test_escarpment(inputs, expected_result):
    p = Escarpment(**inputs)
    p.initialize()

    np.testing.assert_equal(p.elevation, expected_result)

def test_bare_rock_surface():
    grid = (3, 2)
    elevation = np.random.rand(*grid)

    p = BareRockSurface(surf_elevation=elevation)
    p.initialize()

    np.testing.assert_equal(elevation, p.bedrock_elevation)


def test_no_erosion_history():
    p = NoErosionHistory()
    p.initialize()
    
    assert(p.height == 0)
