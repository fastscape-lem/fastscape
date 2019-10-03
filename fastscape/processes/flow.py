import fastscapelib_fortran as fs
import numpy as np
import xsimlab as xs

from .context import FastscapelibContext
from .grid import RasterGrid2D
from .surface import SurfaceTopography
from .tectonics import BaseVerticalUplift


@xs.process
class FlowSurface:
    """Defines the surface on which to apply flow routing
    and all dependent processes.

    This surface here corresponds to the topographic surface at
    the current time step.

    """
    topo_elevation = xs.foreign(SurfaceTopography, 'elevation')

    elevation = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='surface elevation before flow'
    )

    @xs.runtime(args='step_delta')
    def run_step(self, dt):
        self.elevation = self.topo_elevation


@xs.process
class UpliftedFlowSurface(FlowSurface):
    """Use this process to apply flow routing on the already
    uplifted topographic surface.

    """
    uplift = xs.foreign(BaseVerticalUplift, 'uplift')

    @xs.runtime(args='step_delta')
    def run_step(self, dt):
        self.elevation = self.topo_elevation + self.uplift


@xs.process
class FlowRouter:
    """Base process class to route flow on the topographic surface.

    Do not use this base class directly in a model! Use one of its
    subclasses instead.

    However, if you need one or several of the variables declared here
    in another process, it is preferable to pass this base class in
    :func:`xsimlab.foreign`.

    """
    shape = xs.foreign(RasterGrid2D, 'shape')
    elevation = xs.foreign(FlowSurface, 'elevation')
    fs_context = xs.foreign(FastscapelibContext, 'context')

    single_flow = xs.variable(
        intent='out',
        description='flag for single flow routing'
    )

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

    def initialize(self):
        # views
        self.stack = self.fs_context.stack
        self.nb_donors = self.fs_context.ndon
        self.donors = self.fs_context.don

        # must be defined in sub-classes
        self.single_flow = None

    def route_flow(self):
        # must be implemented in sub-classes
        pass

    def run_step(self):
        # bypass fastscapelib_fortran global state
        h_bak = self.fs_context.h.copy()
        self.fs_context.h = self.elevation.ravel()

        self.route_flow()

        # restore fastscapelib_fortran global state
        self.fs_context.h = h_bak

    @basin.compute
    def _basin(self):
        catch = self.fs_context.catch.reshape(self.shape)

        # storing basin ids as integers is safer
        return (catch * catch.size).astype(np.int)

    @lake_depth.compute
    def _lake_depth(self):
        return self.fs_context.lake_depth.reshape(self.shape).copy()


@xs.process
class SingleFlowRouter(FlowRouter):
    """Single (convergent) flow router."""

    slope = xs.on_demand(
        dims='node',
        description='out flow path slope'
    )

    def initialize(self):
        super(SingleFlowRouter, self).initialize()

        # views
        self.nb_receivers = np.ones_like(self.fs_context.rec)[:, None]
        self.receivers = self.fs_context.rec
        self.lengths = self.fs_context.length
        self.weights = np.ones_like(self.fs_context.length)[:, None]

        self.single_flow = True

    def route_flow(self):
        fs.flowroutingsingleflowdirection()

    @slope.compute
    def _slope(self):
        return (self.elevation - self.elevation[self.receivers]) / self.length


@xs.process
class MultipleFlowRouter(FlowRouter):
    """Multiple (convergent/divergent) flow router with uniform
    slope exponent.

    """
    slope_exp = xs.variable(description='MFD partioner slope exponent')

    def initialize(self):
        super(MultipleFlowRouter, self).initialize()

        # views
        self.stack = self.fs_context.mstack
        self.nb_receivers = self.fs_context.mnrec
        self.receivers = self.fs_context.mrec
        self.lengths = self.fs_context.mlrec
        self.weights = self.fs_context.mwrec

        self.single_flow = False
        self.fs_context.p = self.slope_exp

    def route_flow(self):
        fs.flowrouting()


@xs.process
class SlopeAdaptiveFlowRouter(MultipleFlowRouter):
    """Multiple (convergent/divergent) flow router where the
    slope exponent is itself a function of slope.

    slope_exp = 0.5 + 0.6 * slope

    """
    def initialize(self):
        super(MixedFlowRouter, self).initialize()

        # this is defined like that in fastscapelib-fortran
        self.fs_context.p = -1.


@xs.process
class FlowAccumulator:

    runoff = xs.variable(
        dims=[(), ('y', 'x')],
        description='surface runoff (source term)'
    )

    flowacc = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='flow accumulation from up to downstream'
    )


@xs.process
class DrainageArea(FlowAccumulator):

    # need to re-use runoff for cell area
    runoff = xs.variable(
        dims=[(), ('y', 'x')],
        intent='out',
        description='alias for cell area'
    )

    # alias of flowacc, for convenience
    area = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='drainage area'
    )
