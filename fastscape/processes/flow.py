import numpy as np
import xsimlab as xs

from .context import FastscapelibContext
from .grid import RasterGrid2D
from .surface import SurfaceTopography
from .tectonics import BlockUplift


@xs.process
class FlowSurface(object):
    """Defines the surface on which to apply flow routing
    and all dependent processes.

    This surface here corresponds to the topographic surface at
    the current time step.

    """
    topo_elevation = xs.foreign(SurfaceTopography, 'elevation')

    elevation = xs.variable(
        ('y', 'x'), intent='out',
        description='surface elevation before flow'
    )

    def run_step(self, dt):
        self.elevation = self.topo_elevation


@xs.process
class UpliftedFlowSurface(FlowSurface):
    """Use this process to apply flow routing on the already
    uplifted topographic surface.

    """
    uplift = xs.foreign(BlockUplift, 'uplift')

    def run_step(self, dt):
        self.elevation = self.topo_elevation + self.uplift


@xs.process
class FlowRouter(object):
    """Route flow at the topographic surface."""

    mfd_exp = xs.variable(description='MFD slope exponent')

    shape = xs.foreign(RasterGrid2D, 'shape')
    elevation = xs.foreign(FlowSurface, 'elevation')
    fs_context = xs.foreign(FastscapelibContext, 'context')

    # this is insane! drainage area is further computed
    # in StreamPowerChannelErosion but we do this to avoid
    # later API breaking changes
    drainage_area = xs.variable(('y', 'x'), intent='out',
                                description='drainage area')

    # those variables won't return meaningful value
    # if called before StreamPowerChannel run_step!!
    basin = xs.on_demand(('y', 'x'), description='river catchments')
    lake_depth = xs.on_demand(('y', 'x'), description='lake depth')

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

    mfd_exp = xs.variable(intent='out')

    def initialize(self):
        # high mfd slope exponent value -> mimics convergent flow.
        self.mfd_exp = 10.


@xs.process
class MultipleFlowRouter(FlowRouter):
    """Multiple (convergent/divergent) flow router with uniform
    slope exponent.

    """
    slope_exp = xs.variable(description='MFD partioner slope exponent')

    mfd_exp = xs.variable(intent='out')

    def initialize(self):
        self.mfd_exp = self.slope_exp


@xs.process
class MixedFlowRouter(FlowRouter):
    """Multiple (convergent/divergent) flow router where the
    slope exponent is itself a function of slope.

    slope_exp = 0.5 + 0.6 * slope

    """
    mfd_exp = xs.variable(intent='out')

    def initialize(self):
        # this is defined like that in fastscapelib-fortran
        self.mfd_exp = -1.
