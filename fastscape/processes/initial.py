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
