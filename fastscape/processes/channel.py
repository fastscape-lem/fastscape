import fastscapelib_fortran as fs
import numpy as np
import xsimlab as xs

from .context import FastscapelibContext
from .flow import FlowAccumulator, FlowRouter
from .grid import UniformRectilinearGrid2D
from .main import UniformSedimentLayer


@xs.process
class ChannelErosion:
    """Base class for continental channel erosion and/or deposition.

    Do not use this base class directly in a model! Use one of its
    subclasses instead.

    However, if you need one or several of the variables declared here
    in another process, it is preferable to pass this base class in
    :func:`xsimlab.foreign`.

    """
    erosion = xs.variable(
        dims=('y', 'x'),
        intent='out',
        groups='erosion',
        description='channel erosion and/or deposition'
    )


@xs.process
class StreamPowerChannel(ChannelErosion):
    """Stream-Power channel erosion."""

    k_coef = xs.variable(
        dims=[(), ('y', 'x')],
        description='bedrock channel incision coefficient'
    )
    area_exp = xs.variable(
        default=0.4,
        description='drainage area exponent'
    )
    slope_exp = xs.variable(
        default=1,
        description='slope exponent'
    )

    tol_rel = xs.variable(
        default=1e-4,
        description='relative tolerance (Gauss-Siedel convergence)'
    )
    tol_abs = xs.variable(
        default=1e-4,
        description='absolute tolerance (Gauss-Siedel convergence)'
    )
    max_iter = xs.variable(
        default=100,
        description='max nb. of iterations (Gauss-Siedel convergence)'
    )

    shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    elevation = xs.foreign(FlowRouter, 'elevation')
    receivers = xs.foreign(FlowRouter, 'receivers')
    flowacc = xs.foreign(FlowAccumulator, 'flowacc')
    fs_context = xs.foreign(FastscapelibContext, 'context')

    chi = xs.on_demand(
        dims=('y', 'x'),
        description='integrated drainage area (chi)'
    )

    def _set_g_in_context(self):
        # transport/deposition feature is exposed in subclasses
        self.fs_context["g1"] = 0.
        self.fs_context["g2"] = 0.

    def _set_tolerance(self):
        self.fs_context["tol_rel"] = self.tol_rel
        self.fs_context["tol_abs"] = self.tol_abs
        self.fs_context["nGSStreamPowerLawMax"] = self.max_iter

    def run_step(self):
        kf = np.broadcast_to(self.k_coef, self.shape).flatten()
        self.fs_context["kf"] = kf

        # we don't use kfsed fastscapelib-fortran feature directly
        self.fs_context["kfsed"] = -1.

        self._set_g_in_context()

        self.fs_context["m"] = self.area_exp
        self.fs_context["n"] = self.slope_exp

        # note: this is ignored in fastscapelib_fortran <2.8.3 !!
        self._set_tolerance()

        # bypass fastscapelib_fortran global state
        self.fs_context["h"] = self.elevation.flatten()
        self.fs_context["a"] = self.flowacc.flatten()

        if self.receivers.ndim == 1:
            fs.streampowerlawsingleflowdirection()
        else:
            fs.streampowerlaw()

        erosion_flat = self.elevation.ravel() - self.fs_context["h"]
        self.erosion = erosion_flat.reshape(self.shape)

    @chi.compute
    def _chi(self):
        chi_arr = np.empty_like(self.elevation, dtype='d')
        self.fs_context["copychi"](chi_arr.ravel())

        return chi_arr


@xs.process
class DifferentialStreamPowerChannel(StreamPowerChannel):
    """Stream-Power channel (differential) erosion.

    Channel incision coefficient may vary depending on whether the
    topographic surface is bare rock or covered by a soil (sediment)
    layer.

    """
    k_coef_bedrock = xs.variable(
        dims=[(), ('y', 'x')],
        description='bedrock channel incision coefficient'
    )
    k_coef_soil = xs.variable(
        dims=[(), ('y', 'x')],
        description='soil (sediment) channel incision coefficient'
    )

    k_coef = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='differential channel incision coefficient'
    )

    active_layer_thickness = xs.foreign(UniformSedimentLayer, 'thickness')

    def run_step(self):
        self.k_coef = np.where(self.active_layer_thickness <= 0.,
                               self.k_coef_bedrock,
                               self.k_coef_soil)

        super(DifferentialStreamPowerChannel, self).run_step()


@xs.process
class StreamPowerChannelTD(StreamPowerChannel):
    """Extended stream power channel erosion, transport and deposition."""

    # TODO: https://github.com/fastscape-lem/fastscapelib-fortran/pull/25
    # - update input var dimensions
    # - set self.get_context.g instead of g1 and g2

    g_coef = xs.variable(
        #dims=[(), ('y', 'x')],
        description='detached bedrock transport/deposition coefficient'
    )

    def _set_g_in_context(self):
        # TODO: set g instead
        self.fs_context["g1"] = self.g_coef
        self.fs_context["g2"] = -1.


@xs.process
class DifferentialStreamPowerChannelTD(DifferentialStreamPowerChannel):
    """Extended stream power channel (differential) erosion, transport and
    deposition.

    Both channel incision and transport/deposition coefficients may
    vary depending on whether the topographic surface is bare rock or
    covered by a soil (sediment) layer.

    """
    # TODO: https://github.com/fastscape-lem/fastscapelib-fortran/pull/25
    # - update input var dimensions
    # - set self.get_context.g instead of g1 and g2

    g_coef_bedrock = xs.variable(
        #dims=[(), ('y', 'x')],
        description='detached bedrock transport/deposition coefficient'
    )

    g_coef_soil = xs.variable(
        #dims=[(), ('y', 'x')],
        description='soil (sediment) transport/deposition coefficient'
    )

    g_coef = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='differential transport/deposition coefficient'
    )

    def _set_g_in_context(self):
        # TODO: set g instead
        self.fs_context["g1"] = self.g_coef_bedrock
        self.fs_context["g2"] = self.g_coef_soil

    def run_step(self):
        self.g_coef = np.where(self.active_layer_thickness <= 0.,
                               self.g_coef_bedrock,
                               self.g_coef_soil)

        super(DifferentialStreamPowerChannelTD, self).run_step()
