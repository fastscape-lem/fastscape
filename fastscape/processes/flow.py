import warnings

import fastscapelib_fortran as fs
import numpy as np
import numba
import xsimlab as xs

from .context import FastscapelibContext
from .grid import UniformRectilinearGrid2D
from .main import SurfaceToErode


@xs.process
class FlowRouter:
    """Base process class to route flow on the topographic surface.

    Do not use this base class directly in a model! Use one of its
    subclasses instead.

    However, if you need one or several of the variables declared here
    in another process, it is preferable to pass this base class in
    :func:`xsimlab.foreign`.

    """
    shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    elevation = xs.foreign(SurfaceToErode, 'elevation')
    fs_context = xs.foreign(FastscapelibContext, 'context')

    stack = xs.variable(
        dims='node',
        intent='out',
        description='DFS ordered grid node indices'
    )
    nb_receivers = xs.variable(
        dims='node',
        intent='out',
        description='number of flow receivers'
    )
    receivers = xs.variable(
        dims=['node', ('node', 'nb_rec_max')],
        intent='out',
        description='flow receiver node indices'
    )
    lengths = xs.variable(
        dims=['node', ('node', 'nb_rec_max')],
        intent='out',
        description='out flow path length'
    )
    weights = xs.variable(
        dims=['node', ('node', 'nb_rec_max')],
        intent='out',
        description='flow partition weights'
    )
    nb_donors = xs.variable(
        dims='node',
        intent='out',
        description='number of flow donors'
    )
    donors = xs.variable(
        dims=('node', 'nb_don_max'),
        intent='out',
        description='flow donors node indices'
    )

    basin = xs.on_demand(
        dims=('y', 'x'),
        description='river catchments'
    )
    lake_depth = xs.on_demand(
        dims=('y', 'x'),
        description='lake depth'
    )

    def route_flow(self):
        # must be implemented in sub-classes
        pass

    def run_step(self):
        # bypass fastscapelib_fortran global state
        self.fs_context["h"] = self.elevation.ravel()

        self.route_flow()

        self.nb_donors = self.fs_context["ndon"].astype('int')
        # Fortran 1 vs Python 0 index
        self.donors = self.fs_context["don"].astype('int') - 1

    @basin.compute
    def _basin(self):
        catch = self.fs_context["catch"].reshape(self.shape)

        # storing basin ids as integers is safer
        return (catch * catch.size).astype(np.int)

    @lake_depth.compute
    def _lake_depth(self):
        return self.fs_context["lake_depth"].reshape(self.shape).copy()


@xs.process
class SingleFlowRouter(FlowRouter):
    """Single direction (convergent) flow router."""

    slope = xs.on_demand(
        dims='node',
        description='out flow path slope'
    )

    def initialize(self):
        # for compatibility
        self.nb_receivers = np.ones_like(self.fs_context["rec"])
        self.weights = np.ones_like(self.fs_context["length"])

    def route_flow(self):
        fs.flowroutingsingleflowdirection()

        # Fortran 1 vs Python 0 index
        self.stack = self.fs_context["stack"].astype('int') - 1
        self.receivers = self.fs_context["rec"] - 1
        self.lengths = self.fs_context["length"]

    @slope.compute
    def _slope(self):
        elev_flat = self.elevation.ravel()
        elev_flat_diff = elev_flat - elev_flat[self.receivers]

        # skip base levels
        slope = np.zeros_like(self.lengths)
        idx = np.argwhere(self.lengths > 0)

        slope[idx] = elev_flat_diff[idx] / self.lengths[idx],

        return slope


@xs.process
class MultipleFlowRouter(FlowRouter):
    """Multiple direction (convergent/divergent) flow router with uniform
    slope exponent.

    """
    slope_exp = xs.variable(
        description='MFD partioner slope exponent',
        static=True
    )

    def initialize(self):
        self.fs_context["p"] = self.slope_exp

    def route_flow(self):
        fs.flowrouting()

        # Fortran 1 vs Python 0 index | Fortran col vs Python row layout
        self.stack = self.fs_context["mstack"].astype('int') - 1
        self.nb_receivers = self.fs_context["mnrec"].astype('int')
        self.receivers = self.fs_context["mrec"].astype('int').transpose() - 1
        self.lengths = self.fs_context["mlrec"].transpose()
        self.weights = self.fs_context["mwrec"].transpose()


@xs.process
class AdaptiveFlowRouter(MultipleFlowRouter):
    """Multiple direction (convergent/divergent) flow router where the
    slope exponent is itself a function of slope.

    slope_exp = 0.5 + 0.6 * slope

    """
    slope_exp = xs.on_demand(description='MFD partioner slope exponent')

    def initialize(self):
        # this is defined like that in fastscapelib-fortran
        self.fs_context["p"] = -1.

    @slope_exp.compute
    def _slope_exp(self):
        # see https://github.com/fastscape-lem/fastscapelib-fortran/issues/24
        warnings.warn("'AdaptiveFlowRouter.slope_exp' "
                      "has no meaningful value.",
                      UserWarning)
        return -1


# TODO: remove when possible to use fastscapelib-fortran
# see https://github.com/fastscape-lem/fastscapelib-fortran/issues/24
@numba.njit
def _flow_accumulate_sd(field, stack, receivers):
    for inode in stack[-1::-1]:
        if receivers[inode] != inode:
            field[receivers[inode]] += field[inode]


@numba.njit
def _flow_accumulate_mfd(field, stack, nb_receivers, receivers, weights):
    for inode in stack:
        if nb_receivers[inode] == 1 and receivers[inode, 0] == inode:
            continue

        for k in range(nb_receivers[inode]):
            irec = receivers[inode, k]
            field[irec] += field[inode] * weights[inode, k]


@xs.process
class FlowAccumulator:
    """Accumulate the flow from upstream to downstream."""

    runoff = xs.variable(
        dims=[(), ('y', 'x')],
        description='surface runoff (source term) per area unit'
    )

    shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    cell_area = xs.foreign(UniformRectilinearGrid2D, 'cell_area')
    stack = xs.foreign(FlowRouter, 'stack')
    nb_receivers = xs.foreign(FlowRouter, 'nb_receivers')
    receivers = xs.foreign(FlowRouter, 'receivers')
    weights = xs.foreign(FlowRouter, 'weights')

    flowacc = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='flow accumulation from up to downstream'
    )

    def run_step(self):
        field = np.broadcast_to(
            self.runoff * self.cell_area,
            self.shape
        ).flatten()

        if self.receivers.ndim == 1:
            _flow_accumulate_sd(field, self.stack, self.receivers)

        else:
            _flow_accumulate_mfd(field, self.stack, self.nb_receivers,
                                 self.receivers, self.weights)

        self.flowacc = field.reshape(self.shape)


@xs.process
class DrainageArea(FlowAccumulator):
    """Upstream contributing area."""

    runoff = xs.variable(dims=[(), ('y', 'x')], intent='out')

    # alias of flowacc, for convenience
    area = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='drainage area'
    )

    def initialize(self):
        self.runoff = 1

    def run_step(self):
        super(DrainageArea, self).run_step()

        self.area = self.flowacc
