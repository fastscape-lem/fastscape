import numpy as np
import xsimlab as xs

from .boundary import BorderBoundary
from .context import FastscapelibContext
from .grid import RasterGrid2D


@xs.process
class BlockUplift(object):
    """Vertical tectonic uplift.

    Automatically resets uplift to zero at grid borders where
    'fixed_value' boundary conditions are set.

    """
    rate = xs.variable(dims=[(), ('y', 'x')], description='uplift rate')

    shape = xs.foreign(RasterGrid2D, 'shape')
    status = xs.foreign(BorderBoundary, 'border_status')
    fs_context = xs.foreign(FastscapelibContext, 'context')

    uplift = xs.variable(dims=[(), ('y', 'x')], intent='out',
                         group='elevation_up')

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
