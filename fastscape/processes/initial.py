import numpy as np
import xsimlab as xs

from .erosion import TotalErosion
from .grid import UniformRectilinearGrid2D
from .main import Bedrock, SurfaceTopography


@xs.process
class FlatSurface:
    """Initialize surface topography as a flat surface at sea-level with
    random perturbations (white noise).

    """
    seed = xs.variable(default=None, description='random seed')
    shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    elevation = xs.foreign(SurfaceTopography, 'elevation', intent='out')

    def initialize(self):
        rs = np.random.RandomState(seed=self.seed)
        self.elevation = rs.rand(*self.shape)


@xs.process
class Escarpment:
    """Initialize surface topography as an escarpment separating two
    nearly flat surfaces.

    The slope of the escarpment is uniform (linear interpolation
    between the two plateaus). Random perturbations are added to the
    elevation of each plateau.

    """
    x_left = xs.variable(
        description="location of the scarp's left limit on the x-axis",
        static=True
    )
    x_right = xs.variable(
        description="location of the scarp's right limit on the x-axis",
        static=True
    )

    elevation_left = xs.variable(
        description='elevation on the left side of the scarp'
    )
    elevation_right = xs.variable(
        description='elevation on the right side of the scarp')

    shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    x = xs.foreign(UniformRectilinearGrid2D, 'x')
    elevation = xs.foreign(SurfaceTopography, 'elevation', intent='out')

    def initialize(self):
        self.elevation = np.full(self.shape, self.elevation_left)

        # align scarp limit locations
        idx_left = np.argmax(self.x > self.x_left)
        idx_right = np.argmax(self.x > self.x_right)

        self.elevation[:, idx_right:] = self.elevation_right

        # ensure lower elevation on x-axis limits for nice drainage patterns
        self.elevation[:, 1:-1] += np.random.rand(*self.shape)[:, 1:-1]

        # create scarp slope
        scarp_width = self.x[idx_right] - self.x[idx_left]

        if scarp_width > 0:
            scarp_height = (self.elevation_right - self.elevation_left)
            scarp_slope = scarp_height / scarp_width
            scarp_coord = self.x[idx_left:idx_right] - self.x[idx_left]

            self.elevation[:, idx_left:idx_right] = (
                self.elevation_left + scarp_slope * scarp_coord
            )


@xs.process
class BareRockSurface:
    """Initialize topographic surface as a bare rock surface."""

    surf_elevation = xs.foreign(SurfaceTopography, 'elevation')
    bedrock_elevation = xs.foreign(Bedrock, 'elevation', intent='out')

    def initialize(self):
        self.bedrock_elevation = self.surf_elevation.copy()


@xs.process
class NoErosionHistory:
    """Initialize erosion to zero (no erosion history)."""

    height = xs.foreign(TotalErosion, 'cumulative_height', intent='out')

    def initialize(self):
        self.height = 0.
