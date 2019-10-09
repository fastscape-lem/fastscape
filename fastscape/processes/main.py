import fastscapelib_fortran as fs
import numpy as np
import xsimlab as xs

from .grid import UniformRectilinearGrid2D


@xs.process
class TotalVerticalMotion:
    """Sum up all vertical motions of bedrock and topographic surface,
    respectively.

    Vertical motions may result from external forcing, erosion and/or
    feedback of erosion on tectonics (isostasy).

    """
    #TODO: remove any_upward_vars
    # see https://github.com/benbovy/xarray-simlab/issues/64
    any_upward_vars = xs.group('any_upward')
    bedrock_upward_vars = xs.group('bedrock_upward')
    surface_upward_vars = xs.group('surface_upward')
    surface_downward_vars = xs.group('surface_downward')

    bedrock = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='bedrock motion in upward direction'
    )
    surface = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='topographic surface motion in upward direction'
    )

    def run_step(self):
        sum_any = sum(self.any_upward_vars)

        self.bedrock = sum_any + sum(self.bedrock_upward_vars)

        self.surface = (sum_any +
                        sum(self.surface_upward_vars) -
                        sum(self.surface_downward_vars))


@xs.process
class SurfaceTopography:
    """Update the elevation of the (land and/or submarine) surface
    topography.

    """
    elevation = xs.variable(
        dims=('y', 'x'),
        intent='inout',
        description='surface topography elevation'
    )

    surface_motion = xs.foreign(TotalVerticalMotion, 'surface')

    def finalize_step(self):
        self.elevation += self.surface_motion


@xs.process
class SurfaceToErode:
    """Defines the topographic surface used for the computation of erosion
    processes.

    In this process class, it simply corresponds to the topographic
    surface, unchanged, at the current time step.

    Sometimes it would make sense to compute erosion processes after
    having applied other processes such as tectonic forcing. This
    could be achieved by subclassing.

    """
    topo_elevation = xs.foreign(SurfaceTopography, 'elevation')

    elevation = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='surface elevation before erosion'
    )

    def run_step(self):
        self.elevation = self.topo_elevation


@xs.process
class BedrockSurface:
    """Update the elevation of bedrock (i.e., land and/or submarine
    basement).

    """
    elevation = xs.variable(
        dims=('y', 'x'),
        intent='inout',
        description='bedrock elevation'
    )

    depth = xs.on_demand(
        dims=('y', 'x'),
        description='bedrock depth from topographic surface'
    )

    bedrock_motion = xs.foreign(TotalVerticalMotion, 'bedrock')
    surface_motion = xs.foreign(TotalVerticalMotion, 'surface')

    surface_elevation = xs.foreign(SurfaceTopography, 'elevation')

    @depth.compute
    def _depth(self):
        return self.surf_elevation - self.elevation

    def initialize(self):
        if np.any(self.elevation > self.surface_elevation):
            raise ValueError("Encountered bedrock elevation higher than "
                             "topographic surface elevation.")

    def finalize_step(self):
        self.elevation = np.minimum(
            self.elevation + self.bedrock_motion,
            self.surface_elevation + self.surface_motion
        )


@xs.process
class UniformSedimentLayer:
    """Uniform soil (or regolith, or sediment) layer."""

    surf_elevation = xs.foreign(SurfaceTopography, 'elevation')
    bedrock_elevation = xs.foreign(BedrockSurface, 'elevation')

    thickness = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='soil layer thickness'
    )

    @thickness.compute
    def _get_thickness(self):
        return self.surf_elevation - self.bedrock_elevation

    def initialize(self):
        self.thickness = self._get_thickness()

    def run_step(self):
        self.thickness = self._get_thickness()


@xs.process
class TerrainDerivatives:
    """Compute, on demand, terrain derivatives such as slope or
    curvature.

    """
    shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    spacing = xs.foreign(UniformRectilinearGrid2D, 'spacing')
    elevation = xs.foreign(SurfaceTopography, 'elevation')

    slope = xs.on_demand(
        dims=('y', 'x'),
        description='terrain local slope'
    )
    curvature = xs.on_demand(
        dims=('y', 'x'),
        description='terrain local curvature'
    )

    @slope.compute
    def _slope(self):
        slope = np.empty_like(self.elevation)
        ny, nx = self.shape
        dy, dx = self.spacing

        fs.slope(self.elevation.ravel(), slope.ravel(), nx, ny, dx, dy)

        return slope

    @curvature.compute
    def _curvature(self):
        curv = np.empty_like(self.elevation)
        ny, nx = self.shape
        dy, dx = self.spacing

        fs.curvature(self.elevation.ravel(), curv.ravel(), nx, ny, dx, dy)

        return curv
