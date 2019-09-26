import fastscapelib_fortran as fs
import numpy as np
import xsimlab as xs

from .context import FastscapelibContext
from .flow import FlowRouter
from .grid import RasterGrid2D


@xs.process
class StreamPowerChannel(object):
    """Channel erosion computed using the Stream-Power Law."""

    k_coef = xs.variable([(), ('y', 'x')],
                         description='stream-power coefficient')
    area_exp = xs.variable(description='drainage area exponent')
    slope_exp = xs.variable(description='slope exponent')

    shape = xs.foreign(RasterGrid2D, 'shape')
    elevation = xs.foreign(FlowRouter, 'elevation')
    fs_context = xs.foreign(FastscapelibContext, 'context')

    erosion = xs.variable(dims=('y', 'x'), intent='out', group='erosion')

    chi = xs.on_demand(('y', 'x'),
                       description='integrated drainage area (chi)')

    # TODO: remove when those variables will really be computed in FlowRouter
    drainage_area = xs.foreign(FlowRouter, 'drainage_area')

    # ---
    # Insane hack to bypass xarray-simlab so that we can declare
    # output variables in FlowRouter process and set their value here
    # (fastscapelib-fortran does all the routing within the
    # streampowerlaw function)
    # ---

    def _get_store_key(self, varname):
        for k, p in self.__xsimlab_model__.items():
            skeys = p.__xsimlab_store_keys__

            if varname in skeys:
                v = skeys[varname]

                if v[0] == k:
                    return (k, varname)

        return None

    def _get_from_store(self, key):
        return self.__xsimlab_store__.get(key)

    def _set_in_store(self, key, value):
        if key is not None:
            self.__xsimlab_store__[key] = value

    # ---
    # End of the hack
    # ---

    def initialize(self):
        self._mfd_key = self._get_store_key('mfd_exp')
        self._area_key = self._get_store_key('drainage_area')

    def _set_g_in_context(self):
        # transport/deposition feature is exposed in subclasses
        self.fs_context.g = 0.
        self.fs_context.gsed = -1.

    @xs.runtime(args='step_delta')
    def run_step(self, dt):
        self.fs_context.p = self._get_from_store(self._mfd_key)

        kf = np.broadcast_to(self.k_coef, self.shape).flatten()
        self.fs_context.kf = kf

        # we don't use the kfsed fastscapelib-fortran feature directly
        self.fs_context.kfsed = -1.

        self.fs_context.m = self.area_exp
        self.fs_context.n = self.slope_exp

        # fs.streampowerlaw() updates elevation in-place: not desired here
        # TODO: uplift is applied within the streampowerlaw() function
        #   -> temporarily reset u to zero in context
        #   -> set h in context from self.elevation
        elevation = self.fs_context.h.copy()

        fs.streampowerlaw()

        erosion_flat = elevation - self.fs_context.h
        self.erosion = erosion_flat.reshape(self.shape)

        self.fs_context.h = elevation

        # hack! update values of flow routing variables
        self._set_in_store(self._area_key,
                           self.fs_context.a.reshape(self.shape))

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
