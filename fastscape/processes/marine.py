import fastscapelib_fortran as fs
import xsimlab as xs


from .channel import ChannelErosion
from .context import FastscapelibContext
from .grid import UniformRectilinearGrid2D
from .surface import SurfaceToErode


@xs.process
class Sea:
    """Sea level."""

    # TODO: add diagnostics like shoreline extraction or
    # continental area vs. marine masks.

    level = xs.variable(description='sea level (elevation)')


@xs.process
class MarineSedimentTransport:
    """Marine sediment transport, deposition and compaction.

    The source of sediment used for marine transport originates from
    channel erosion and/or transport, which, integrated over the whole
    continental area, provides a volume of sediment yielded through
    the shoreline.

    A uniform, user-defined ratio of sand/silt is considered for this
    sediment yield. Each of these grain size category has its own
    properties like porosity, the exponential decreasing of porosity
    with depth and the transport coefficient (diffusivity).

    """
    sand_silt_ratio = xs.variable(
        description='sand/silt ratio of continental integrated sediment source'
    )

    surf_porosity_sand = xs.variable(
        description='surface (reference) porosity of sand'
    )
    surf_porosity_silt = xs.variable(
        description='surface (reference) porosity of silt'
    )

    e_depth_sand = xs.variable(
        description='e-folding depth of exp. porosity curve for sand'
    )
    e_depth_silt = xs.variable(
        description='e-folding depth of exp. porosity curve for silt'
    )

    diffusivity_sand = xs.variable(
        description='diffusivity (transport coefficient) for sand'
    )

    diffusivity_silt = xs.variable(
        description='diffusivity (transport coefficient) for silt'
    )

    layer_depth = xs.variable(
        description='mean depth (thickness) of marine active layer'
    )

    shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    fs_context = xs.foreign(FastscapelibContext, 'context')
    elevation = xs.foreign(SurfaceToErode, 'elevation')
    sediment_source = xs.foreign(ChannelErosion, 'erosion')
    sea_level = xs.foreign(Sea, 'level')

    erosion = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='marine erosion or deposition of sand/silt'
    )

    # TODO: ratio sand over silt more consistent?
    silt_fraction = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='silt fraction of marine sediment'
    )

    def run_step(self):
        self.fs_context.ratio = self.sand_silt_ratio

        self.fs_context.poro1 = self.surf_porosity_sand
        self.fs_context.poro2 = self.surf_porosity_silt

        self.fs_context.zporo1 = self.e_depth_sand
        self.fs_context.zporo2 = self.e_depth_silt

        self.fs_context.kdsea1 = self.diffusivity_sand
        self.fs_context.kdsea2 = self.diffusivity_silt

        self.fs_context.layer = self.mean_thickness

        self.fs_context.sealevel = self.sea_level
        self.fs_context.Sedflux = self.sediment_source.ravel()

        # bypass fastscapelib-fortran global state
        h_bak = self.fs_context.h.copy()
        self.fs_context.h = self.elevation.flatten()

        fs.marine()

        erosion_flat = self.elevation.ravel() - self.fs_context.h
        self.erosion = erosion_flat.reshape(self.shape)

        self.silt_fraction = self.fs_context.Fmix.copy().reshape(self.shape)

        # restore fastscapelib_fortran global state
        self.fs_context.h = h_bak
