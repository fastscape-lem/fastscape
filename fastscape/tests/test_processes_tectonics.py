import numpy as np

import pytest

from fastscape.processes import (BlockUplift,
                                 HorizontalAdvection,
                                 SurfaceAfterTectonics,
                                 TectonicForcing,
                                 TwoBlocksUplift)
from fastscape.processes.context import FastscapelibContext


def test_tectonic_forcing():
    grid_shape = (3, 2)
    uplift = np.random.uniform(size=grid_shape)
    isostasy = np.random.uniform(size=grid_shape)
    bedrock_advect = np.random.uniform(size=grid_shape)
    surf_advect = np.random.uniform(size=grid_shape)
    area = 300.
    dt = 10.

    p = TectonicForcing(bedrock_forcing_vars=[uplift, isostasy, bedrock_advect],
                        surface_forcing_vars=[uplift, isostasy, surf_advect],
                        grid_area=area)

    p.run_step(dt)

    sum_bedrock_forcing_vars = uplift + isostasy + bedrock_advect
    np.testing.assert_equal(p.bedrock_upward, sum_bedrock_forcing_vars)

    sum_surface_forcing_vars = uplift + isostasy + surf_advect
    np.testing.assert_equal(p.surface_upward, sum_surface_forcing_vars)

    domain_rate = np.sum(sum_surface_forcing_vars) * area / dt
    assert p._domain_rate() == domain_rate


def test_surface_after_tectonics():
    grid_shape = (3, 2)
    topo_elevation = np.random.uniform(size=grid_shape)
    forced_motion = np.random.uniform(size=grid_shape)

    p = SurfaceAfterTectonics(topo_elevation=topo_elevation,
                              forced_motion=forced_motion)

    p.run_step()

    expected = topo_elevation + forced_motion
    np.testing.assert_equal(p.elevation, expected)


@pytest.mark.parametrize('b_status, expected_mask, expected_uplift', [
    (np.array(['fixed_value', 'fixed_value', 'fixed_value', 'fixed_value']),
    np.array([[0., 0., 0., 0.],
              [0., 1., 1., 0.],
              [0., 0., 0., 0.]]),
    np.array([[0., 0., 0., 0.],
              [0., 50., 50., 0.],
              [0., 0., 0., 0.]])),
    (np.array(['looped', 'looped', 'looped', 'looped']),
    np.ones((3, 4)),
    np.full((3, 4), 50)),
    (np.array(['core', 'core', 'core', 'core']),
    np.ones((3, 4)),
    np.full((3, 4), 50)),
    (np.array(['fixed_value', 'looped', 'core', 'fixed_value']),
    np.array([[0., 1., 1., 1.],
              [0., 1., 1., 1.],
              [0., 0., 0., 0.]]),
    np.array([[0., 50., 50., 50.],
              [0., 50., 50., 50.],
              [0., 0., 0., 0.]]))
])
def test_block_uplift(b_status, expected_mask, expected_uplift):
    rate = 5
    grid = (3,4)
    dt = 10.
    f = FastscapelibContext(shape=grid, length=(10., 30.), ibc=1010)
    f.initialize()
    f.run_step(dt)

    p = BlockUplift(rate=rate, 
                    shape=grid,
                    status=b_status,
                    fs_context=f)

    p.initialize()
    np.testing.assert_equal(p._mask, expected_mask)

    p.run_step(dt)
    np.testing.assert_equal(p.uplift, expected_uplift)


@pytest.mark.parametrize('x, expected_x_idx, expected_uplift', [
    (2,
     0,
    np.full((3, 4), 30.)),
    (np.array([1, 2, 3]),
     1,
     np.array([[20., 30., 30., 30.],
               [20., 30., 30., 30.],
               [20., 30., 30., 30.]]))
])
def test_two_blocks_uplift(x, expected_x_idx, expected_uplift):
    x_pos = 1
    rate_l = 2
    rate_r = 3
    grid = (3, 4)
    dt = 10.

    p = TwoBlocksUplift(x_position=x_pos,
                        rate_left=rate_l,
                        rate_right=rate_r,
                        shape=grid,
                        x=x)

    p.initialize()
    assert p._x_idx == expected_x_idx

    p.run_step(dt)
    np.testing.assert_equal(p.uplift, expected_uplift)


@pytest.mark.parametrize('u, v, expected_surface_veffect, expected_bedrock_veffect', [
    (np.array([[1, 2]]),
     np.array([[1, 2]]),
     np.array([[ 0.        ,  0.        ],
               [-0.03748965, -0.08303031],
               [ 0.        ,  0.        ]]),
     np.array([[ 0.        , -0.70662827],
               [-0.07276812, -0.47956039],
               [ 0.        , -0.31266382]])),
    (1,
     3,
     np.array([[ 0.        ,  0.        ],
               [-0.04820098, -0.08896105],
               [ 0.        ,  0.        ]]),
     np.array([[ 0.        , -0.70662827],
               [-0.09355901, -0.48549112],
               [ 0.        , -0.31266382]]))
])
def test_horizontal_advection(u,
                              v,
                              expected_surface_veffect,
                              expected_bedrock_veffect):
    np.random.seed(12)
    grid = (3, 2)
    f = FastscapelibContext(shape=grid, length=(10., 30.), ibc=1010)
    f.initialize()
    bedrock_elevation = np.random.uniform(size=grid)
    surface_elevation = np.random.uniform(size=grid)

    p = HorizontalAdvection(u=u,
                            v=v,
                            shape=grid,
                            fs_context=f.context,
                            bedrock_elevation=bedrock_elevation,
                            surface_elevation=surface_elevation)

    p.run_step()

    np.testing.assert_allclose(p.surface_veffect, expected_surface_veffect, 1e-9, 1e-8)
    np.testing.assert_allclose(p.bedrock_veffect, expected_bedrock_veffect, 1e-9, 1e-8)
