.. _models:

Models
======

Fastscape provides a few landscape evolution model "presets", i.e.,
:class:`xsimlab.Model` objects that can be used as-is or as a basis
for building custom models. Those presets are built from a large
collection of :doc:`processes`.

For help on how to run and further customize those models, see the
:doc:`examples` section or `xarray-simlab's documentation`_.

.. _`xarray-simlab's documentation`: http://xarray-simlab.readthedocs.io/

Bootstrap model
---------------

``bootstrap_model`` has the minimal set of processes required to
simulate on a 2D uniform grid the evolution of topographic surface
under the action of tectonic and erosion processes.

None of such processes is included. This model only provides the
"skeleton" of a landscape evolution model and might be used as a basis
to create custom models.

.. ipython:: python

    from fastscape.models import bootstrap_model
    bootstrap_model

Basic model
-----------

``basic_model`` is a "standard" landscape evolution model that
includes block uplift, (bedrock) channel erosion using the stream
power law and hillslope erosion/deposition using linear diffusion.

Initial topography is a flat surface with random perturbations.

Flow is routed on the topographic surface using a D8, single flow
direction algorithm.

All erosion processes are computed on a topographic surface that is
first updated by tectonic forcing processes.

.. ipython:: python

    from fastscape.models import basic_model
    basic_model

Sediment model
--------------

``sediment_model`` is built on top of ``basic_model`` ; it tracks the
evolution of both the topographic surface and the bedrock, separated
by a uniform, active layer of sediment.

This model uses an extended version of the stream-power law that also
includes channel transport and deposition.

Flow is routed using a multiple flow direction algorithm.

Differential erosion/deposition is enabled for both hillslope and
channel processes, i.e., distinct values may be set for the erosion
and transport coefficients (bedrock vs soil/sediment).

.. ipython:: python

    from fastscape.models import sediment_model
    sediment_model

Marine model
------------

``marine_model`` simulates the erosion, transport and deposition of
bedrock or sediment in both continental and submarine environments.

It is built on top of ``sediment_model`` to which it
adds a process for sediment transport, deposition and compaction in
the submarine domain (under sea level).

The processes for the initial topography and uplift both allow easy
set-up of the two land vs. marine environments.

An additional process keeps track of a fixed number of stratigraphic
horizons over time.

.. ipython:: python

    from fastscape.models import marine_model
    marine_model
