import numpy as np
import xsimlab as xs


@xs.process
class UniformGrid1D(UniformRectilinearGrid):
    """Create a uniform (static) 1-dimensional grid."""

    size = xs.variable(description='nb. of grid nodes')
    spacing = xs.variable(description='grid node spacing')
    origin = xs.variable(description='x coordinate of grid origin')

    length = xs.variable(intent='out', description='total grid length')
    x = xs.variable(dims='x', intent='out', description='grid x coordinate')

    dx = xs.variable(intent='out', description="alias of spacing")
    nx = xs.variable(intent='out', description="alias of size")

    def initialize(self):
        self.length = (self.size - 1) * self.spacing

        self.dx = self.spacing
        self.nx = self.size

        self.x = np.linspace(self.origin, self.length, self.shape)


@xs.process
class UniformRectilinearGrid2D(object):
    """Create a uniform rectilinear (static) 2-dimensional grid."""

    shape = xs.variable(dims='grid_shape',
                        description='nb. of grid nodes in (y, x)')
    spacing = xs.variable(dims='grid_shape',
                          description='grid node spacing in (y, x)')
    origin = xs.variable(dims='grid_shape',
                         description='(y, x) coordinates of grid origin')

    length = xs.variable(dims='grid_shape', intent='out',
                         description='total grid length in (y, x)')

    size = xs.variable(intent='out', description='total nb. of nodes')
    cell_area = xs.variable(intent='out', description='fixed grid cell area')

    dx = xs.variable(intent='out', description="grid spacing in x (cols)")
    dy = xs.variable(intent='out', description="grid spacing in y (rows)")

    nx = xs.variable(intent='out', description="nb. of nodes in x (cols)")
    ny = xs.variable(intent='out', description="nb. of nodes in y (rows)")

    x = xs.variable(dims='x', intent='out', description='grid x coordinate')
    y = xs.variable(dims='y', intent='out', description='grid y coordinate')

    def initialize(self):
        self.length = (self.shape - 1) * self.spacing
        self.size = np.prod(self.shape)
        self.cell_area = np.prod(self.spacing)

        self.dx = self.spacing[1]
        self.dy = self.spacing[0]
        self.nx = self.shape[1]
        self.ny = self.shape[0]

        self.x = np.linspace(self.origin[1], self.length[1], self.shape[1])
        self.y = np.linspace(self.origin[0], self.length[0], self.shape[0])


@xs.process
class RasterGrid2D(UniformRectilinearGrid2D):
    """Create a raster 2-dimensional grid."""

    resolution = xs.variable(description='fixed grid resolution')

    spacing = xs.variable(dims='grid_shape', intent='out',
                          description='grid node spacing in (y, x)')

    def initialize(self):
        self.spacing = np.array([self.resolution, self.resolution])
        super(RasterGrid2D, self).initialize()
