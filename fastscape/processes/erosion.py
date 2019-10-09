import numpy as np
import xsimlab as xs


@xs.process
class TotalErosion:
    """Sum up all erosion processes."""

    erosion_vars = xs.group('erosion')

    cumulative_erosion = xs.variable(
        dims=[(), ('y', 'x')],
        intent='inout'
    )

    erosion = xs.variable(
        dims=[(), ('y', 'x')],
        intent='out',
        description='total erosion',
        group='surface_downward'
    )

    erosion_rate = xs.on_demand(
        dims=[(), ('y', 'x')],
        description='erosion rate (all processes)'
    )

    @xs.runtime(args='step_delta')
    def run_step(self, dt):
        self._dt = dt

        self.erosion = np.sum(self.erosion_vars)
        self.cumulative_erosion += self.erosion

    @erosion_rate.compute
    def _erosion_rate(self):
        return self.erosion / self._dt
