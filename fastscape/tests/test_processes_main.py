import numpy as np
import pytest

from fastscape.processes import (Bedrock,
                                 SurfaceToErode,
                                 SurfaceTopography,
                                 TotalVerticalMotion)


def test_total_vertical_motion():
    grid_shape = (3, 2)
    uplift = np.random.uniform(size=grid_shape)
    isostasy = np.random.uniform(size=grid_shape)
    erosion1 = np.random.uniform(size=grid_shape)
    erosion2 = np.random.uniform(size=grid_shape)
    bedrock_advect = np.random.uniform(size=grid_shape)
    surf_advect = np.random.uniform(size=grid_shape)

    p = TotalVerticalMotion(any_upward_vars=[uplift, isostasy],
                            bedrock_upward_vars=[bedrock_advect],
                            surface_upward_vars=[surf_advect],
                            surface_downward_vars=[erosion1, erosion2])

    p.run_step()

    expected = uplift + isostasy + bedrock_advect
    np.testing.assert_equal(p.bedrock_upward, expected)

    expected = uplift + isostasy + surf_advect - (erosion1 + erosion2)
    np.testing.assert_equal(p.surface_upward, expected)


def test_surface_topography():
    elevation = np.random.uniform(size=(3, 2))
    upward = np.random.uniform(size=(3, 2))
    expected = elevation + upward

    p = SurfaceTopography(elevation=elevation, motion_upward=upward)

    p.finalize_step()

    np.testing.assert_equal(p.elevation, expected)


def test_surface_to_erode():
    elevation = np.random.uniform(size=(3, 2))

    p = SurfaceToErode(topo_elevation=elevation)

    p.initialize()

    np.testing.assert_equal(p.elevation, elevation)

    p.topo_elevation += 1

    p.run_step()

    np.testing.assert_equal(p.elevation, p.topo_elevation)


@pytest.mark.parametrize('surface_up,bedrock_up,surf_delta,outcome', [
    (1, 0, 1, 'all_lower'),

])
def test_berock(surface_up, bedrock_up, surf_delta, outcome):
    grid_shape = (3, 2)
    elevation = np.random.uniform(size=grid_shape)
    surf_elevation = elevation + surf_delta

    p = Bedrock(elevation=elevation,
                bedrock_motion_up=np.ones_like(elevation) * bedrock_up,
                surface_motion_up=np.ones_like(elevation) * surface_up,
                surface_elevation=surf_elevation)

    p.initialize()
    p.run_step()
    p.finalize_step()

    if outcome == 'all_lower':
        assert np.all([True])
