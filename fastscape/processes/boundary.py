import numpy as np
import xsimlab as xs

from .context import FastscapelibContext


@xs.process
class BorderBoundary(object):
    status = xs.variable([(), 'border'], description='node status at borders')

    border = xs.variable('border', intent='out')
    border_status = xs.variable('border', intent='out')

    fs_context = xs.foreign(FastscapelibContext, 'context')

    def initialize(self):
        self.border = np.array(['left', 'right', 'top', 'bottom'])
        self.border_status = np.broadcast_to(self.status, 4)

        # convert to fastscapelib-fortran ibc code
        arr_bc = np.array([1 if st == 'fixed_value' else 0
                           for st in self.border_status])
        arr_bc *= np.array([1, 100, 10, 1000])   # different border order
        ibc = arr_bc.sum()

        self.fs_context.ibc = ibc
