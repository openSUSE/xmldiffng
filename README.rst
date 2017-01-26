========
Overview
========

.. start-badges

|travis| |scrutinizer|

.. |travis| image:: https://travis-ci.org/openSUSE/xmldiffng.svg?branch=develop
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/openSUSE/xmldiffng

.. |scrutinizer| image:: https://scrutinizer-ci.com/g/openSUSE/xmldiffng/badges/quality-score.png?b=develop
    :alt: Scrutinizer Build Status
    :target: https://scrutinizer-ci.com/g/openSUSE/xmldiffng/

.. end-badges

Diffing XML with RELAX NG schema

* Free software: GPL license

Installation
============

::

    pip install xmldiffng


Development
===========

To run the all tests run::

    tox

Get Ready
===========

^^^^^^^^^^
Optional but recommended Tools
^^^^^^^^^^

* `gitprompt <https://github.com/magicmonty/bash-git-prompt>`_
* `GitFlow <https://github.com/petervanderdoes/gitflow)>`_

^^^^^^^^^^
Install required packages (SUSE)
^^^^^^^^^^

::

    sudo zypper install libxml2-devel libxml2-tool libxslt-devel gcc-c++ make
    sudo zypper install readline-devel python-devel python3-devel python-virtualenv

^^^^^^^^^^
Setup a virtual python environment (VPE)
^^^^^^^^^^

1. Create a VPE:

::

   pyvenv .env

2. Activate the VPE:

::

   source .env/bin/activate

3. Install the project in develop-mode:

::

   ./setup.py develop

Some helpful commands:
* Show python modules inside the VPE::
    pip list

* Install python modules from `PyPI <https://pypi.python.org/pypi>`_

::

    pip install MODULE

