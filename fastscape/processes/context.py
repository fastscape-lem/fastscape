import fastscapelib_fortran as fs
import numpy as np
import xsimlab as xs

from .boundary import BorderBoundary
from .grid import UniformRectilinearGrid2D


class SerializableFastscapeContext:
    """Fastscapelib-fortran context getter/setter that is serializable.

    (Fortran objects can't be pickled).
    """

    def __getitem__(self, key):
        return getattr(fs.fastscapecontext, key)

    def __setitem__(self, key, value):
        setattr(fs.fastscapecontext, key, value)


@xs.process
class FastscapelibContext:
    """This process takes care of proper initialization,
    update and clean-up of fastscapelib-fortran internal
    state.

    """

    shape = xs.foreign(UniformRectilinearGrid2D, "shape")
    length = xs.foreign(UniformRectilinearGrid2D, "length")
    ibc = xs.foreign(BorderBoundary, "ibc")

    context = xs.any_object(description="accessor to fastscapelib-fortran internal variables")

    def initialize(self):
        fs.fastscape_init()
        fs.fastscape_set_nx_ny(*np.flip(self.shape))
        fs.fastscape_setup()
        fs.fastscape_set_xl_yl(*np.flip(self.length))

        fs.fastscape_set_bc(self.ibc)

        self.context = SerializableFastscapeContext()

    @xs.runtime(args="step_delta")
    def run_step(self, dt):
        # fastscapelib-fortran runtime routines use dt from context
        self.context["dt"] = dt

    def finalize(self):
        fs.fastscape_destroy()
