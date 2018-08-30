import numpy as np
import xsimlab as xs

from .grid import UniformRectilinearGrid2D


@xs.process
class ClosedBoundaryFaces(object):
    """Set closed boundaries at each face of the grid."""
    grid_shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    active_nodes = xs.variable(
        dims=('y', 'x'), intent='out',
        description='active grid nodes inside the domain')

    def initialize(self):
        self.active_nodes = np.ones(self.grid_shape, dtype=bool)
        self.active_nodes[[0, -1], :] = False
        self.active_nodes[:, [0, -1]] = False
