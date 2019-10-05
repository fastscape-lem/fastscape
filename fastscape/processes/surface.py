import fastscapelib_fortran as fs
import numpy as np
import xsimlab as xs

from .grid import UniformRectilinearGrid2D


@xs.process
class TotalVerticalMotion:
    """Sum up vertical motions of bedrock and topographic surface."""

    bedrock_upward_vars = xs.group('bedrock_upward')
    surface_downward_vars = xs.group('surface_downward')

    bedrock_upward = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='total bedrock motion in upward direction'
    )
    surface_downward = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='total surface motion in downward direction'
    )

    def run_step(self):
        self.bedrock_upward = sum((v for v in self.bedrock_upward_vars))
        self.surface_downward = sum((v for v in self.surface_downward_vars))


@xs.process
class SurfaceTopography:
    """Update surface topography elevation."""

    elevation = xs.variable(
        dims=('y', 'x'),
        intent='inout',
        description='surface topography elevation'
    )

    bedrock_upward = xs.foreign(TotalVerticalMotion, 'bedrock_upward')
    surface_downward = xs.foreign(TotalVerticalMotion, 'surface_downward')

    def run_step(self):
        self.elevation_diff = self.bedrock_upward - self.surface_downward

    def finalize_step(self):
        self.elevation += self.elevation_diff


@xs.process
class BedrockSurface:
    """Update bedrock elevation."""

    elevation = xs.variable(
        dims=('y', 'x'),
        intent='inout',
        description='bedrock elevation'
    )

    depth = xs.on_demand(
        dims=('y', 'x'),
        description='bedrock depth from topographic surface'
    )

    bedrock_upward = xs.foreign(TotalVerticalMotion, 'bedrock_upward')
    surface_downward = xs.foreign(TotalVerticalMotion, 'surface_downward')
    surf_elevation = xs.foreign(SurfaceTopography, 'elevation')

    @depth.compute
    def _depth(self):
        return self.surf_elevation - self.elevation

    def initialize(self):
        if np.any(self.elevation > self.surf_elevation):
            raise ValueError("Encountered bedrock elevation higher than "
                             "topographic surface elevation.")

    def run_step(self):
        self.elevation_diff = self.bedrock_upward + np.minimum(
            self.surf_elevation - self.surface_downward,
            self.elevation
        )

    def finalize_step(self):
        self.elevation += self.elevation_diff


@xs.process
class UniformSoilLayer:
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
class TotalErosion:
    """Sum up all erosion processes."""

    erosion_vars = xs.group('erosion')

    cumulative_erosion = xs.variable(
        dims=[(), ('y', 'x')],
        intent='inout'
    )

    erosion = xs.variable(
        dims=[(), ('y', 'x')],
        intent='out',
        description='total erosion',
        group='surface_downward'
    )

    erosion_rate = xs.on_demand(
        dims=[(), ('y', 'x')],
        description='erosion rate (all processes)'
    )

    @xs.runtime(args='step_delta')
    def run_step(self, dt):
        self._dt = dt

        self.erosion = np.sum((err for err in self.erosion_vars))
        self.cumulative_erosion += self.erosion

    @erosion_rate.compute
    def _erosion_rate(self):
        return self.erosion / self._dt


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
