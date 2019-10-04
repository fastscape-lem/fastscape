import fastscapelib_fortran as fs
import numpy as np
import xsimlab as xs

from .grid import UniformRectilinearGrid2D
from .surface import SurfaceTopography


@xs.process
class FastscapelibContext:
    """This process takes care of proper initialization,
    update and clean-up of fastscapelib-fortran internal
    state.

    """
    shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    length = xs.foreign(UniformRectilinearGrid2D, 'length')

    elevation = xs.foreign(SurfaceTopography, 'elevation')

    context = xs.variable(
        intent='out',
        description='accessor to fastscapelib-fortran internal variables'
    )

    def initialize(self):
        fs.fastscape_init()
        fs.fastscape_set_nx_ny(*np.flip(self.shape))
        fs.fastscape_setup()
        fs.fastscape_set_xl_yl(*np.flip(self.length))

        self.context = fs.fastscapecontext

        self.context.h = self.elevation.flatten()

    @xs.runtime(args='step_delta')
    def run_step(self, dt):
        self.context.dt = dt
        self.context.h = self.elevation.flatten()

    def finalize(self):
        fs.fastscape_destroy()
