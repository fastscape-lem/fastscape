import numpy as np
import xsimlab as xs


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
