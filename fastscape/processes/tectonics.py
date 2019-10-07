import fastscapelib_fortran as fs
import numpy as np
import xsimlab as xs

from .boundary import BorderBoundary
from .context import FastscapelibContext
from .grid import UniformRectilinearGrid2D
from .surface import SurfaceTopography


@xs.process
class BaseVerticalUplift:
    """Base class for vertical uplift forcing.

    Do not use this base class directly in a model! Use one of its
    subclasses instead.

    However, if you need the 'uplift' variable declared here
    in another process, it is preferable to pass this base class in
    :func:`xsimlab.foreign`.

    """
    uplift = xs.variable(
        dims=[(), ('y', 'x')],
        intent='out',
        group='bedrock_upward',
        description='imposed vertical uplift'
    )


@xs.process
class BlockUplift(BaseVerticalUplift):
    """Vertical tectonic uplift.

    Automatically resets uplift to zero at grid borders where
    'fixed_value' boundary conditions are set.

    """
    rate = xs.variable(dims=[(), ('y', 'x')], description='uplift rate')

    shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    status = xs.foreign(BorderBoundary, 'border_status')
    fs_context = xs.foreign(FastscapelibContext, 'context')

    def initialize(self):
        # build uplift rate binary mask according to border status
        self._mask = np.ones(self.shape)

        _all = slice(None)
        slices = [(_all, 0), (_all, -1), (0, _all), (-1, _all)]

        for status, border in zip(self.status, slices):
            if status == 'fixed_value':
                self._mask[border] = 0.

    @xs.runtime(args='step_delta')
    def run_step(self, dt):
        rate = np.broadcast_to(self.rate, self.shape) * self._mask
        self.fs_context.u = rate.ravel()

        self.uplift = rate * dt


@xs.process
class HorizontalAdvection:
    """Horizontal rock advection imposed by a velocity field."""

    u = xs.variable(
        dims=[(), ('y', 'x')],
        description='velocity field component in x-direction'
    )
    v = xs.variable(
        dims=[(), ('y', 'x')],
        description='velocity field component in y-direction'
    )

    shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    fs_context = xs.foreign(FastscapelibContext, 'context')
    elevation = xs.foreign(SurfaceTopography, 'elevation')

    vertical_motion = xs.variable(
        dims=('y', 'x'),
        intent='out',
        group='bedrock_upward',
        description='effect of advection on topographic elevation'
    )

    def run_step(self):
        self.fs_context.vx = np.broadcast_to(self.u, self.shape).flatten()
        self.fs_context.vy = np.broadcast_to(self.v, self.shape).flatten()

        # bypass fastscapelib-fortran state
        h_bak = self.fs_context.h.copy()
        self.fs_context.h = self.elevation.flatten()

        fs.advect()

        elevation_advected = self.fs_context.h.reshape(self.shape)
        self.vertical_motion = elevation_advected - self.elevation

        # restore fastscapelib-fortran state
        self.fs_context.h = h_bak
