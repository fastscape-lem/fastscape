import numpy as np
import xsimlab as xs

from .grid import UniformRectilinearGrid2D
from .surface import BedrockSurface, SurfaceTopography, TotalErosion


@xs.process
class FlatSurface:
    """Initialize surface topography as a flat surface at sea-level with
    random perturbations (white noise).

    """
    shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    elevation = xs.foreign(SurfaceTopography, 'elevation', intent='out')

    def initialize(self):
        self.elevation = np.random.rand(*self.shape)


@xs.process
class Escarpment:
    """Initialize surface topography as a steep escarpment separating two
    nearly flat surfaces.

    Random perturbations are added to the elevation of each plateau.

    """
    x_position = xs.variable(
        description='position of the escarpment along the x-axis'
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

        # align scarp position
        x_idx = np.argmax(self.x > self.x_position)

        self.elevation[:, x_idx:] = self.elevation_right

        # ensure lower elevation on x limits for good drainage patterns
        self.elevation[:, 1:-1] += np.random.rand(*self.shape)[:, 1:-1]


@xs.process
class BareRockSurface:
    """Initialize topographic surface as a bare rock surface."""

    surf_elevation = xs.foreign(SurfaceTopography, 'elevation')
    bedrock_elevation = xs.foreign(BedrockSurface, 'elevation', intent='out')

    def initialize(self):
        self.bedrock_elevation = self.surf_elevation.copy()


@xs.process
class NoErosionHistory:
    """Initialize erosion to zero (no erosion history)."""

    erosion = xs.foreign(TotalErosion, 'cumulative_erosion', intent='out')

    def initialize(self):
        self.erosion = 0.
