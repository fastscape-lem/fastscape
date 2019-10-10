.. _develop:

Contributor Guide
=================

fastscape is an open-source project. Contributions are welcome, and they are
greatly appreciated!

You can contribute in many ways, e.g., by reporting bugs, submitting feedbacks,
contributing to the development of the code and/or the documentation, etc.

This page provides resources on how best to contribute.

Issues
------

The `Github Issue Tracker`_ is the right place for reporting bugs and for
discussing about development ideas. Feel free to open a new issue if you have
found a bug or if you have suggestions about new features or changes.

For now, as the project is still very young, it is also a good place for
asking usage questions.

.. _`Github Issue Tracker`: https://github.com/fastscape-lem/fastscape/issues

Development environment
-----------------------

If you wish to contribute to the development of the code and/or the
documentation, here are a few steps for setting a development environment.

Fork the repository and download the code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To further be able to submit modifications, it is preferable to start by
forking the fastscape repository on GitHub_ (you need to have an account).

Then clone your fork locally::

  $ git clone git@github.com:your_name_here/fastscape.git

Alternatively, if you don't plan to submit any modification, you can clone the
original fastscape git repository::

   $ git clone git@github.com:fastscape-lem/fastscape.git

.. _GitHub: https://github.com

Install
~~~~~~~

To install the dependencies, we recommend using the conda_ package manager with
the conda-forge_ channel. For development purpose, you might consider installing
the packages in a new conda environment::

  $ conda create -n fastscape_dev xarray-simlab fastscapelib-f2py -c conda-forge
  $ source activate fastscape_dev

Then install fastscape locally using ``pip``::

  $ cd fastscape
  $ pip install -e .

.. _conda: http://conda.pydata.org/docs/
.. _conda-forge: https://conda-forge.github.io/

Run tests
~~~~~~~~~

To make sure everything behaves as expected, you may want to run
fastscape's unit tests locally using the `pytest`_ package. You
can first install it with conda::

  $ conda install pytest -c conda-forge

Then you can run tests from the main fastscape directory::

  $ pytest fastscape --verbose

.. _pytest: https://docs.pytest.org/en/latest/

Contributing to code
--------------------

Below are some useful pieces of information in case you want to contribute
to the code.

Local development
~~~~~~~~~~~~~~~~~

Once you have setup the development environment, the next step is to create
a new git branch for local development::

  $ git checkout -b name-of-your-bugfix-or-feature

Now you can make your changes locally.

Submit changes
~~~~~~~~~~~~~~

Once you are done with the changes, you can commit your changes to git and
push your branch to your fastscape fork on GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

(note: this operation may be repeated several times).

We you are ready, you can create a new pull request through the GitHub_ website
(note that it is still possible to submit changes after your created a pull
request).

Python versions
~~~~~~~~~~~~~~~

fastscape supports Python versions 3.4 and higher. It is not
compatible with Python versions 2.x. We don't plan to make it
compatible with Python 2.7.x.

Test
~~~~

fastscape's uses unit tests extensively to make sure that every
part of the code behaves as we expect. Test coverage is required for
all code contributions.

Unit test are written using `pytest`_ style (i.e., mostly using the
``assert`` statement directly) in various files located in the
``xsimlab/tests`` folder.  You can run tests locally from the main
fastscape directory::

  $ pytest fastscape --verbose

All tests are also executed automatically on continuous integration
platforms on every push to every pull request on GitHub.

Docstrings
~~~~~~~~~~

Everything (i.e., classes, methods, functions...) that is part of the public API
should follow the numpydoc_ standard when possible.

.. _numpydoc: https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

Coding style
~~~~~~~~~~~~

The fastscape code mostly follows the style conventions defined in PEP8_.

.. _PEP8: https://www.python.org/dev/peps/pep-0008/

Source code checker
~~~~~~~~~~~~~~~~~~~

To check about any potential error or bad style in your code, you might want
using a source code checker like flake8_. You can install it in your
development environment::

  $ conda install flake8 -c conda-forge

.. _flake8: http://flake8.pycqa.org

Release notes entry
~~~~~~~~~~~~~~~~~~~

Every significative code contribution should be listed in the
:doc:`release_notes` section of this documentation under the
corresponding version.

Contributing to documentation
-----------------------------

fastscape uses Sphinx_ for documentation, hosted on http://readthedocs.org .
Documentation is maintained in the RestructuredText markup language (``.rst``
files) in ``fastscape/doc``.

To build the documentation locally, first install requirements (for example here
in a separate conda environment)::

   $ conda env create -n fastscape_doc -f doc/environment.yml
   $ source activate fastscape_doc

Then build documentation with ``make``::

   $ cd doc
   $ make html

The resulting HTML files end up in the ``build/html`` directory.

You can now make edits to rst files and run ``make html`` again to update
the affected pages.

.. _Sphinx: http://www.sphinx-doc.org/
