import xsimlab as xs

from ..processes.boundary import BorderBoundary
from ..processes.channel import StreamPowerChannel
from ..processes.context import FastscapelibContext
from ..processes.flow import (DrainageArea, SingleFlowRouter,
                              UpliftedFlowSurface)
from ..processes.grid import RasterGrid2D
from ..processes.hillslope import LinearDiffusion
from ..processes.initial import FlatSurface, NoErosionHistory
from ..processes.surface import (SurfaceTopography, TerrainDerivatives,
                                 TotalErosion)
from ..processes.tectonics import BlockUplift


basic_model = xs.Model({
    'grid': RasterGrid2D,
    'fs_context': FastscapelibContext,
    'boundary': BorderBoundary,
    'uplift': BlockUplift,
    'flow_surface': UpliftedFlowSurface,
    'flow': SingleFlowRouter,
    'drainage': DrainageArea,
    'spl': StreamPowerChannel,
    'diffusion': LinearDiffusion,
    'erosion': TotalErosion,
    'topography': SurfaceTopography,
    'terrain': TerrainDerivatives,
    'init_topography': FlatSurface,
    'init_erosion': NoErosionHistory
})
