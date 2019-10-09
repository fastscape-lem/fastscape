import numpy as np
import xsimlab as xs

from .grid import UniformRectilinearGrid2D


@xs.process
class TotalErosion:
    """Sum up all erosion processes."""

    erosion_vars = xs.group('erosion')

    cumulative_height = xs.variable(
        dims=[(), ('y', 'x')],
        intent='inout',
        description='erosion height accumulated over time'
    )

    height = xs.variable(
        dims=[(), ('y', 'x')],
        intent='out',
        description='total erosion height at current step',
        group='surface_downward'
    )

    rate = xs.on_demand(
        dims=[(), ('y', 'x')],
        description='total erosion rate at current step'
    )

    grid_area = xs.foreign(UniformRectilinearGrid2D, 'area')

    domain_rate = xs.on_demand(
        description='domain-integrated volumetric erosion rate'
    )

    @xs.runtime(args='step_delta')
    def run_step(self, dt):
        self._dt = dt

        self.height = np.sum(self.erosion_vars)
        self.cumulative_height += self.height

    @rate.compute
    def _rate(self):
        return self.height / self._dt

    @domain_rate.compute
    def _domain_rate(self):
        return np.sum(self.height) * self.grid_area / self._dt
