.. Python Flight Data Processing documentation master file, created by
   sphinx-quickstart on Tue Sep 12 12:57:03 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction
============
Welcome to Python Flight Data Processing's documentation! This project is intended to make the life 
easier when plotting and analyzing some data of the Aurora archives.

The three main classes that were created for this project are:

* :class:`~utils.field.Field`, describes a field
* :class:`~utils.dataset.DataSet`, implements the process of reading a list of fields from a folder or a list of folders
* :class:`~estimators.estimators.Estimator`, estimates the attitude using the sensors data and has methods to plot the results

Another common class is :class:`~utils.quat.Quat`, that provides easy  manipulation of quaternion objects. This project also relays heavily on the `matplotlib`_ for the plots and on the `pandas`_ modules, as it uses the :class:`pandas.DataFrame` data structure to store the time-series information. 

Contents
========

.. toctree::
   :maxdepth: 2
   
   intro
   apidoc/modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

External documentation
======================
For more information about the libraries used:

* `Pandas Documentation <https://pandas.pydata.org/pandas-docs/stable/>`_
* `Matplotlib Tutorials <https://matplotlib.org/users/tutorials.html>`_

.. _pandas: https://pandas.pydata.org/pandas-docs/stable/
.. _matplotlib: https://matplotlib.org/index.html
.. _dataframe: https://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe

