========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis|
        |
        | |codacy|
    * - package
      - | |version| |downloads| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/xmldiffng/badge/?style=flat
    :target: https://readthedocs.org/projects/xmldiffng
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/openSUSE/xmldiffng.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/openSUSE/xmldiffng

.. |codacy| image:: https://img.shields.io/codacy/REPLACE_WITH_PROJECT_ID.svg
    :target: https://www.codacy.com/app/openSUSE/xmldiffng
    :alt: Codacy Code Quality Status

.. |version| image:: https://img.shields.io/pypi/v/xmldiffng.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/xmldiffng

.. |commits-since| image:: https://img.shields.io/github/commits-since/openSUSE/xmldiffng/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/openSUSE/xmldiffng/compare/v0.1.0...master

.. |downloads| image:: https://img.shields.io/pypi/dm/xmldiffng.svg
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/xmldiffng

.. |wheel| image:: https://img.shields.io/pypi/wheel/xmldiffng.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/xmldiffng

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/xmldiffng.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/xmldiffng

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/xmldiffng.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/xmldiffng


.. end-badges

Diffing XML with RELAX NG schema

* Free software: BSD license

Installation
============

::

    pip install xmldiffng

Documentation
=============

https://xmldiffng.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
