import xsimlab as xs

from ..processes.boundary import BorderBoundary
from ..processes.channel import (StreamPowerChannel,
                                 DifferentialStreamPowerChannelTD)
from ..processes.context import FastscapelibContext
from ..processes.flow import DrainageArea, SingleFlowRouter
from ..processes.grid import RasterGrid2D
from ..processes.hillslope import LinearDiffusion, DifferentialLinearDiffusion
from ..processes.initial import BareRockSurface, FlatSurface, NoErosionHistory
from ..processes.surface import (BedrockSurface,
                                 SurfaceTopography,
                                 TerrainDerivatives,
                                 TotalErosion,
                                 TotalVerticalMotion,
                                 UniformSoilLayer)
from ..processes.tectonics import (BlockUplift,
                                   SurfaceAfterTectonics,
                                   TectonicsForcing)


basic_model = xs.Model({
    'grid': RasterGrid2D,
    'fs_context': FastscapelibContext,
    'boundary': BorderBoundary,
    'uplift': BlockUplift,
    'tectonics': TectonicsForcing,
    'surf2erode': SurfaceAfterTectonics,
    'flow': SingleFlowRouter,
    'drainage': DrainageArea,
    'spl': StreamPowerChannel,
    'diffusion': LinearDiffusion,
    'erosion': TotalErosion,
    'vmotion': TotalVerticalMotion,
    'topography': SurfaceTopography,
    'terrain': TerrainDerivatives,
    'init_topography': FlatSurface,
    'init_erosion': NoErosionHistory
})


soil_model = basic_model.update_processes({
    'bedrock': BedrockSurface,
    'soil': UniformSoilLayer,
    'init_bedrock': BareRockSurface,
    'spl': DifferentialStreamPowerChannelTD,
    'diffusion': DifferentialLinearDiffusion
})
