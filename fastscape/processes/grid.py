import numpy as np
import xsimlab as xs


@xs.process
class UniformRectilinearGrid2D:
    """Create a uniform rectilinear (static) 2-dimensional grid."""

    shape = xs.variable(dims="shape_yx", description="nb. of grid nodes in (y, x)", static=True)
    spacing = xs.variable(dims="shape_yx", description="grid node spacing in (y, x)", static=True)
    origin = xs.variable(
        dims="shape_yx", description="(y, x) coordinates of grid origin", static=True
    )

    length = xs.variable(dims="shape_yx", intent="out", description="total grid length in (y, x)")
    size = xs.variable(intent="out", description="total nb. of nodes")
    area = xs.variable(intent="out", description="total grid area")
    cell_area = xs.variable(intent="out", description="fixed grid cell area")

    dx = xs.variable(intent="out", description="grid spacing in x (cols)")
    dy = xs.variable(intent="out", description="grid spacing in y (rows)")

    nx = xs.variable(intent="out", description="nb. of nodes in x (cols)")
    ny = xs.variable(intent="out", description="nb. of nodes in y (rows)")

    x = xs.index(dims="x", description="grid x coordinate")
    y = xs.index(dims="y", description="grid y coordinate")

    def _set_length_or_spacing(self):
        self.length = (self.shape - 1) * self.spacing

    def initialize(self):
        self._set_length_or_spacing()
        self.size = np.prod(self.shape)
        self.cell_area = np.prod(self.spacing)
        self.area = self.cell_area * self.size

        self.dx = self.spacing[1]
        self.dy = self.spacing[0]
        self.nx = self.shape[1]
        self.ny = self.shape[0]

        self.x = np.linspace(self.origin[1], self.origin[1] + self.length[1], self.shape[1])
        self.y = np.linspace(self.origin[0], self.origin[0] + self.length[0], self.shape[0])


@xs.process
class RasterGrid2D(UniformRectilinearGrid2D):
    """Create a raster 2-dimensional grid."""

    length = xs.variable(
        dims="shape_yx", intent="in", description="total grid length in (y, x)", static=True
    )
    origin = xs.variable(
        dims="shape_yx", intent="out", description="(y, x) coordinates of grid origin"
    )
    spacing = xs.variable(dims="shape_yx", intent="out", description="grid node spacing in (y, x)")

    def _set_length_or_spacing(self):
        self.spacing = self.length / (self.shape - 1)

    def initialize(self):
        self.origin = np.array([0.0, 0.0])
        super().initialize()
