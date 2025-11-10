Sapphire++ — Plot
=================

.. image:: https://img.shields.io/badge/GitHub-sapphirepp--sapphireppplot-blue?logo=github
   :target: https://github.com/sapphirepp/sapphireppplot
   :alt: GitHub

A `ParaView <https://www.paraview.org/>`__
`Python <https://docs.paraview.org/en/latest/UsersGuide/introduction.html#getting-started-with-pvpython>`__
package to plot the results from
`Sapphire++ <https://sapphirepp.org/>`__.

It is highly recommended to first familiarize yourself with 
the `ParaView <https://www.paraview.org/>`_ GUI,
for example using the
`Sapphire++ ParaView Tutorial <https://sapphirepp.org/latest/paraview-tutorial.html>`_.

This package is built on top of the 
`ParaView Python <https://docs.paraview.org/en/latest/UsersGuide/introduction.html#getting-started-with-pvpython>`_
interface.
It tries to abstract it and provide standard plots,
so the user is not exposed to the (cumbersome) ParaView Python interface.
Nevertheless, you might need to fall back on it for custom options.
An extensive
`ParaView Python Introduction <https://sapphirepp.org/latest/paraview-python.html>`_
is provided on the Sapphire++ website.

An introduction to Sapphire++ — Plot is given in the
:doc:`examples/plot_quick_start`
and the :doc:`examples/jupyter_tutorial`.
More example scripts can be found in the 
`Sapphire++ examples <https://github.com/sapphirepp/sapphirepp/tree/main/examples>`_.

.. caution::
   This package is developed for personal use
   and is therefore not claimed to be generally applicable to all Sapphire++ results
   and might exhibit unexpected behaviours.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   examples/plot_quick_start
   examples/jupyter_tutorial
   tips
   api
