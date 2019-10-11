import numpy as np
import xsimlab as xs

from .context import FastscapelibContext


@xs.process
class BorderBoundary:
    status = xs.variable(
        dims=[(), 'border'],
        description='node status at borders'
    )

    border = xs.variable(
        dims='border',
        intent='out',
        description='4-border boundaries coordinate'
    )
    border_status = xs.variable(
        dims='border',
        intent='out',
        description='node status at the 4-border boundaries'
    )

    fs_context = xs.foreign(FastscapelibContext, 'context')

    ibc = xs.variable(
        intent='out',
        description='boundary code used by fastscapelib-fortran'
    )

    def initialize(self):
        self.border = np.array(['left', 'right', 'top', 'bottom'])
        self.border_status = np.broadcast_to(self.status, 4)

        # convert to fastscapelib-fortran ibc code
        arr_bc = np.array([1 if st == 'fixed_value' else 0
                           for st in self.border_status])

        # different border order
        self.ibc = sum(arr_bc * np.array([1, 100, 10, 1000]))

        self.fs_context.ibc = self.ibc
