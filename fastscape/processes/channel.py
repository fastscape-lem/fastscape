import fastscapelib_fortran as fs
import numpy as np
import xsimlab as xs

from .context import FastscapelibContext
from .flow import FlowAccumulator, FlowRouter
from .grid import UniformRectilinearGrid2D


@xs.process
class StreamPowerChannel:
    """Channel erosion computed using the Stream-Power Law."""

    k_coef = xs.variable(
        dims=[(), ('y', 'x')],
        description='stream-power coefficient'
    )
    area_exp = xs.variable(description='drainage area exponent')
    slope_exp = xs.variable(description='slope exponent')

    shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    elevation = xs.foreign(FlowRouter, 'elevation')
    receivers = xs.foreign(FlowRouter, 'receivers')
    flowacc = xs.foreign(FlowAccumulator, 'flowacc')
    fs_context = xs.foreign(FastscapelibContext, 'context')

    erosion = xs.variable(dims=('y', 'x'), intent='out', group='erosion')

    chi = xs.on_demand(
        dims=('y', 'x'),
        description='integrated drainage area (chi)'
    )

    def initialize(self):
        # TODO: move
        pass
        self.drainage_area = self.fs_context.a.reshape(self.shape)

    def _set_g_in_context(self):
        # transport/deposition feature is exposed in subclasses
        self.fs_context.g = 0.
        self.fs_context.gsed = -1.

    @xs.runtime(args='step_delta')
    def run_step(self, dt):
        kf = np.broadcast_to(self.k_coef, self.shape).flatten()
        self.fs_context.kf = kf

        # we don't use the kfsed fastscapelib-fortran feature directly
        self.fs_context.kfsed = -1.

        self.fs_context.m = self.area_exp
        self.fs_context.n = self.slope_exp

        # bypass fastscapelib_fortran global state
        h_bak = self.fs_context.h.copy()
        self.fs_context.h = self.elevation.flatten()

        if self.receivers.ndim == 1:
            fs.streampowerlawsingleflowdirection()
        else:
            fs.streampowerlaw()

        erosion_flat = self.elevation.ravel() - self.fs_context.h
        self.erosion = erosion_flat.reshape(self.shape)

        # restore fastscapelib_fortran global state
        self.fs_context.h = h_bak

    @chi.compute
    def _chi(self):
        chi_arr = np.empty_like(self.elevation, dtype='d')
        self.fs_context.copychi(chi_arr.ravel())

        return chi_arr


@xs.process
class StreamPowerChannelTD(StreamPowerChannel):
    """Channel erosion computed using a extended version of
    the Stream-Power Law that also models sediment transport and
    deposition.

    """
    td_coef = xs.variable(
        description='sediment deposition/transport coefficient')

    def _set_g_in_context(self):
        self.fs_context.g = self.td_coef

        # we don't use the gsed fastscapelib-fortran feature directly
        self.fs_context.gsed = -1.
