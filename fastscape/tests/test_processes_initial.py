import numpy as np
import pytest

from fastscape.processes import (
    BareRockSurface,
    Escarpment,
    FlatSurface,
    NoErosionHistory,
)


def test_flat_surface():
    shape = (3, 2)
    rs = np.random.RandomState(seed=1234)
    elevation = rs.rand(*shape)

    np.random.default_rng(1234)
    p = FlatSurface(shape=shape, seed=1234)
    p.initialize()

    np.testing.assert_equal(shape, p.shape)
    np.testing.assert_allclose(elevation, p.elevation)

    p2 = FlatSurface(shape=shape, seed=None)
    p2.initialize()
    assert np.all(p2.elevation > 0.0)
    assert np.all(p2.elevation <= 1.0)


@pytest.mark.parametrize(
    "inputs",
    [
        (
            {
                "x_left": 10,
                "x_right": 20,
                "elevation_left": 0.0,
                "elevation_right": 100.0,
                "shape": (11, 31),
                "x": np.linspace(0, 30, 31),
            }
        ),
        (
            {
                "x_left": 15,
                "x_right": 15,
                "elevation_left": 0.0,
                "elevation_right": 100.0,
                "shape": (11, 31),
                "x": np.linspace(0, 30, 31),
            }
        ),
    ],
)
def test_escarpment(inputs):
    p = Escarpment(**inputs)
    p.initialize()

    # test invariant elevation along the rows (y-axis) up to random values
    assert np.all(np.abs(p.elevation - p.elevation[0, :]) < 1.0)

    # shape and x-coordinate values chosen so that the escaprement limits
    # match the grid
    assert abs(p.elevation[0, int(p.x_left)] - p.elevation_left) < 1.0
    assert abs(p.elevation[0, int(p.x_right) + 1] - p.elevation_right) < 1.0


def test_bare_rock_surface():
    elevation = np.array([[2, 3], [4, 1]])

    p = BareRockSurface(surf_elevation=elevation)
    p.initialize()

    np.testing.assert_equal(elevation, p.bedrock_elevation)
    # bedrock_elevation must be a copy of surf_elevation
    assert p.bedrock_elevation.base is not p.surf_elevation


def test_no_erosion_history():
    p = NoErosionHistory()
    p.initialize()

    assert p.height == 0
