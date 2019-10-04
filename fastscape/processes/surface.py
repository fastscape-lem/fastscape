import fastscapelib_fortran as fs
import numpy as np
import xsimlab as xs

from .grid import UniformRectilinearGrid2D


@xs.process
class SurfaceTopography:
    """Update a surface topography as resulting from
    multiple processes either rising or lowering elevation.

    """
    elevation = xs.variable(dims=('y', 'x'), intent='inout',
                            description='surface topography elevation')

    elevation_up_vars = xs.group('elevation_up')
    elevation_down_vars = xs.group('elevation_down')

    def run_step(self):
        elevation_up = np.sum((v for v in self.elevation_up_vars))
        elevation_down = np.sum((v for v in self.elevation_down_vars))
        self.elevation_change = elevation_up - elevation_down

    def finalize_step(self):
        self.elevation += self.elevation_change


@xs.process
class TotalErosion:
    """Combine (sum) all erosion processes."""
    erosion_vars = xs.group('erosion')
    cumulative_erosion = xs.variable(dims=[(), ('y', 'x')], intent='inout')
    erosion = xs.variable(dims=[(), ('y', 'x')], intent='out',
                          description='total erosion',
                          group='elevation_down')

    def run_step(self):
        self.erosion = np.sum((err for err in self.erosion_vars))
        self.cumulative_erosion += self.erosion


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
