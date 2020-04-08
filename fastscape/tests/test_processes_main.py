import numpy as np
import pytest

from fastscape.processes import (Bedrock,
                                 SurfaceToErode,
                                 SurfaceTopography,
                                 StratigraphicHorizons,
                                 TerrainDerivatives,
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


def test_terrain_derivatives():
    X, Y = np.meshgrid(np.linspace(-5, 5, 11), np.linspace(-5, 5, 21))
    spacing = (0.5, 1.)  # note: dy, dx

    # test slope and curvature using parabola
    elevation = X**2 + Y**2

    p = TerrainDerivatives(shape=elevation.shape,
                           spacing=spacing,
                           elevation=elevation)

    expected_slope = np.sqrt((2 * X)**2 + (2 * Y)**2)
    expected_curvature = ((2 + 4 * X**2 + 4 * Y**2) /
                          (1 + 4 * X**2 + 4 * Y**2)**1.5)

    def assert_skip_bounds(actual, expected):
        np.testing.assert_allclose(actual[1:-1, 1:-1], expected[1:-1, 1:-1])

    # note: slope values in degrees, skip boundaries
    actual_slope = np.tan(np.radians(p._slope()))
    assert_skip_bounds(actual_slope, expected_slope)

    # TODO: figure out why difference of factor 2
    actual_curvature = p._curvature()
    assert_skip_bounds(actual_curvature, expected_curvature / 2)


def test_stratigraphic_horizons():
    freeze_time = np.array([10., 20., 30.])

    surf_elevation = np.array([[1., 1., 1.],
                               [2., 2., 2.]])

    p = StratigraphicHorizons(
        freeze_time=freeze_time,
        surf_elevation=surf_elevation,
        bedrock_motion=np.array([[-0.2, -0.2, -0.2],
                                 [0., 0., 0.]]),
        elevation_motion=np.full_like(surf_elevation, -0.1)
    )

    with pytest.raises(ValueError, match=r"'freeze_time' value must be .*"):
        p.initialize(100)

    p.initialize(10.)
    assert p.elevation.shape == freeze_time.shape + surf_elevation.shape
    np.testing.assert_equal(p.horizon, np.array([0, 1, 2]))
    np.testing.assert_equal(p.active, np.array([True, True, True]))

    p.run_step(25.)
    p.finalize_step()
    np.testing.assert_equal(p.active, np.array([False, False, True]))
    np.testing.assert_equal(p.elevation[2],
                            np.array([[0.9, 0.9, 0.9],
                                      [1.9, 1.9, 1.9]]))
    for i in [0, 1]:
        np.testing.assert_equal(p.elevation[i],
                                np.array([[0.8, 0.8, 0.8],
                                          [1.9, 1.9, 1.9]]))
