import numpy as np
import pytest

from fastscape.processes import (
    BlockUplift,
    SurfaceAfterTectonics,
    TectonicForcing,
    TwoBlocksUplift,
)
from fastscape.processes.context import FastscapelibContext


def test_tectonic_forcing():
    grid_shape = (3, 2)
    uplift = np.full(grid_shape, 1.0)
    isostasy = np.full(grid_shape, 2.0)
    bedrock_advect = np.full(grid_shape, 3.0)
    surf_advect = np.full(grid_shape, 4.0)
    area = 300.0
    dt = 10.0

    p = TectonicForcing(
        bedrock_forcing_vars=[uplift, isostasy, bedrock_advect],
        surface_forcing_vars=[uplift, isostasy, surf_advect],
        grid_area=area,
    )

    p.run_step(dt)

    # uplift + isostasy + bedrock_advect
    np.testing.assert_equal(p.bedrock_upward, np.full(grid_shape, 1.0 + 2.0 + 3.0))

    # uplift + isostasy + surf_advect
    np.testing.assert_equal(p.surface_upward, np.full(grid_shape, 1.0 + 2.0 + 4.0))

    # test scalar values
    p2 = TectonicForcing(surface_forcing_vars=[1.0, 2.0, 3.0], grid_area=area)
    p2.run_step(dt)
    assert p2.surface_upward == 6.0
    assert p2.bedrock_upward == 0.0  # no variables given
    assert p2._domain_rate() == 6.0 * area / dt


def test_surface_after_tectonics():
    grid_shape = (3, 2)
    topo_elevation = np.full(grid_shape, 2.0)
    forced_motion = np.full(grid_shape, 3.0)

    p = SurfaceAfterTectonics(topo_elevation=topo_elevation, forced_motion=forced_motion)

    p.run_step()

    expected = topo_elevation + forced_motion
    np.testing.assert_equal(p.elevation, expected)


@pytest.mark.parametrize(
    "b_status, expected_uplift",
    [
        (
            np.array(["fixed_value", "fixed_value", "fixed_value", "fixed_value"]),
            np.array([[0.0, 0.0, 0.0, 0.0], [0.0, 50.0, 50.0, 0.0], [0.0, 0.0, 0.0, 0.0]]),
        ),
        (
            np.array(["fixed_value", "core", "core", "fixed_value"]),
            np.array([[0.0, 50.0, 50.0, 50.0], [0.0, 50.0, 50.0, 50.0], [0.0, 0.0, 0.0, 0.0]]),
        ),
    ],
)
def test_block_uplift(b_status, expected_uplift):
    rate = 5
    shape = (3, 4)
    dt = 10.0

    # dummy context
    f = FastscapelibContext(shape=shape, length=(10.0, 30.0), ibc=1010)
    f.initialize()
    f.run_step(dt)

    p = BlockUplift(rate=rate, shape=shape, status=b_status, fs_context=f)

    p.initialize()
    p.run_step(dt)
    np.testing.assert_equal(p.uplift, expected_uplift)

    # test variable rate
    p2 = BlockUplift(rate=np.full(shape, 5.0), shape=shape, status=b_status, fs_context=f)
    p2.initialize()
    p2.run_step(dt)
    np.testing.assert_equal(p2.uplift, expected_uplift)


def test_two_blocks_uplift():
    x = np.array([1, 2, 3])
    x_pos = 1
    rate_l = 2
    rate_r = 3
    grid = (3, 4)
    dt = 10.0

    p = TwoBlocksUplift(x_position=x_pos, rate_left=rate_l, rate_right=rate_r, shape=grid, x=x)

    p.initialize()
    p.run_step(dt)

    expected = np.array(
        [[20.0, 30.0, 30.0, 30.0], [20.0, 30.0, 30.0, 30.0], [20.0, 30.0, 30.0, 30.0]]
    )
    np.testing.assert_equal(p.uplift, expected)
