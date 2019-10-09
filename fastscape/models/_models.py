import xsimlab as xs

from ..processes.boundary import BorderBoundary
from ..processes.channel import (StreamPowerChannel,
                                 DifferentialStreamPowerChannelTD)
from ..processes.context import FastscapelibContext
from ..processes.flow import DrainageArea, SingleFlowRouter, MultipleFlowRouter
from ..processes.erosion import TotalErosion
from ..processes.grid import RasterGrid2D
from ..processes.hillslope import LinearDiffusion, DifferentialLinearDiffusion
from ..processes.initial import (BareRockSurface,
                                 Escarpment,
                                 FlatSurface,
                                 NoErosionHistory)
from ..processes.main import (Bedrock,
                              StratigraphicHorizons,
                              SurfaceTopography,
                              SurfaceToErode,
                              TerrainDerivatives,
                              TotalVerticalMotion,
                              UniformSedimentLayer)
from ..processes.marine import MarineSedimentTransport, Sea
from ..processes.tectonics import (BlockUplift,
                                   SurfaceAfterTectonics,
                                   TectonicForcing,
                                   TwoBlocksUplift)


# ``bootstrap_model`` has the minimal set of processes required to
# simulate on a 2D uniform grid the evolution of topographic surface
# under the action of tectonic and erosion processes. None of such
# processes are included. It only provides the "skeleton" of a
# landscape evolution model and might be used as a basis to create
# custom models.

bootstrap_model = xs.Model({
    'grid': RasterGrid2D,
    'fs_context': FastscapelibContext,
    'boundary': BorderBoundary,
    'tectonics': TectonicForcing,
    'surf2erode': SurfaceToErode,
    'erosion': TotalErosion,
    'vmotion': TotalVerticalMotion,
    'topography': SurfaceTopography,
})

# ``basic_model`` is a "standard" landscape evolution model that
# includes block uplift, (bedrock) channel erosion using the stream
# power law and hillslope erosion/deposition using linear
# diffusion. Initial topography is a flat surface with random
# perturbations. Flow is routed on the topographic surface using a D8,
# single flow direction algorithm. All erosion processes are computed
# on a topographic surface that is first updated by tectonic forcing
# processes.

basic_model = bootstrap_model.update_processes({
    'uplift': BlockUplift,
    'surf2erode': SurfaceAfterTectonics,
    'flow': SingleFlowRouter,
    'drainage': DrainageArea,
    'spl': StreamPowerChannel,
    'diffusion': LinearDiffusion,
    'terrain': TerrainDerivatives,
    'init_topography': FlatSurface,
    'init_erosion': NoErosionHistory
})

# ``sediment_model`` is built on top of ``basic_model`` ; it tracks
# the evolution of both the topographic surface and the bedrock,
# separated by a uniform, active layer of sediment. This model uses an
# extended version of the stream-power law that also includes channel
# transport and deposition. Flow is routed using a multiple flow
# direction algorithm. Differential erosion/deposition is enabled for
# both hillslope and channel processes, i.e., distinct values may be
# set for the erosion and transport coefficients (bedrock vs
# soil/sediment).

sediment_model = basic_model.update_processes({
    'bedrock': Bedrock,
    'active_layer': UniformSedimentLayer,
    'init_bedrock': BareRockSurface,
    'flow': MultipleFlowRouter,
    'spl': DifferentialStreamPowerChannelTD,
    'diffusion': DifferentialLinearDiffusion
})

# ``marine_model`` simulates the erosion, transport and deposition of
# bedrock or sediment in both continental and submarine
# environments. It is built on top of ``sediment_model`` to which it
# adds a process for sediment transport, deposition and compaction in
# the submarine domain (under sea level). The processes for the
# initial topography and uplift both allow easy set-up of the two land
# vs. marine environments. An additional process keeps track of a
# fixed number of stratigraphic horizons over time.

marine_model = sediment_model.update_processes({
    'init_topography': Escarpment,
    'uplift': TwoBlocksUplift,
    'sea': Sea,
    'marine': MarineSedimentTransport,
    'strati': StratigraphicHorizons
})
