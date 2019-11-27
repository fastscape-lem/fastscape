import numpy as np
import pytest

from fastscape.processes import (Bedrock,
                                 SurfaceToErode,
                                 SurfaceTopography,
                                 TotalVerticalMotion,
                                 UniformSedimentLayer)


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

    p.run_step()

    np.testing.assert_equal(p.elevation, p.topo_elevation)


def test_bedrock_error():
    elevation = np.ones((3, 2))
    surface_elevation = np.zeros_like(elevation)

    with pytest.raises(ValueError, match=r".* bedrock elevation higher .*"):
        p = Bedrock(elevation=elevation,
                    surface_elevation=surface_elevation,
                    bedrock_motion_up=np.zeros_like(elevation),
                    surface_motion_up=np.zeros_like(elevation))

        p.initialize()


def test_berock():
    elevation = np.array([[0., 0., 0.],
                          [2., 2., 2.]])
    surface_elevation = np.array([[1., 1., 1.],
                                  [2., 2., 2.]])

    p = Bedrock(elevation=elevation,
                bedrock_motion_up=np.full_like(elevation, 0.5),
                surface_motion_up=np.full_like(elevation, -0.1),
                surface_elevation=surface_elevation)

    p.initialize()
    p.run_step()

    expected = np.array([[1., 1., 1.],
                         [0., 0., 0.]])
    np.testing.assert_equal(p._depth(), expected)

    p.finalize_step()

    expected = np.array([[0.5, 0.5, 0.5],
                         [1.9, 1.9, 1.9]])
    np.testing.assert_equal(p.elevation, expected)


def test_uniform_sediment_layer():
    grid_shape = (3, 2)
    bedrock_elevation = np.random.uniform(size=grid_shape)
    surf_elevation = np.random.uniform(size=grid_shape) + 1
    expected = surf_elevation - bedrock_elevation

    p = UniformSedimentLayer(bedrock_elevation=bedrock_elevation,
                             surf_elevation=surf_elevation)

    p.initialize()
    np.testing.assert_equal(p.thickness, expected)

    p.run_step()
    np.testing.assert_equal(p.thickness, expected)
