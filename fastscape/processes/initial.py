import numpy as np
import xsimlab as xs

from .grid import UniformRectilinearGrid2D
from .surface import SurfaceTopography, TotalErosion


@xs.process
class FlatSurface:
    shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    elevation = xs.foreign(SurfaceTopography, 'elevation', intent='out')

    def initialize(self):
        self.elevation = np.random.rand(*self.shape)


@xs.process
class NoErosionHistory:
    erosion = xs.foreign(TotalErosion, 'cumulative_erosion', intent='out')

    def initialize(self):
        self.erosion = 0.
