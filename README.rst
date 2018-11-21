========
Overview
========

Version |version|

.. start-badges

|travis| |scrutinizer|

.. |travis| image:: https://travis-ci.org/openSUSE/xmldiffng.svg?branch=develop
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/openSUSE/xmldiffng

.. |scrutinizer| image:: https://scrutinizer-ci.com/g/openSUSE/xmldiffng/badges/quality-score.png?b=develop
    :alt: Scrutinizer Build Status
    :target: https://scrutinizer-ci.com/g/openSUSE/xmldiffng

.. end-badges

Diffing XML with RELAX NG schema

* Free software: GPL license

Installation
============

To install :program:`xmldiffng`, use the following command::

    pip install xmldiffng


Development
===========

To run the all tests run::

    tox

Get Ready
===========

Optional but recommended Tools
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* `gitprompt <https://github.com/magicmonty/bash-git-prompt>`_
* `GitFlow <https://github.com/petervanderdoes/gitflow-avh>`_

Install required packages (SUSE)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As a requirement, install the following packages for openSUSE::

    sudo zypper install libxml2-devel libxml2-tools libxslt-devel gcc-c++ make
    sudo zypper install readline-devel python-devel python3-devel python-virtualenv

Setup a virtual python environment (VPE)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Create a VPE::

    python3 -m venv .env

#. Activate the VPE::

    source .env/bin/activate

#. Install the project in develop-mode::

   ./setup.py develop

Some helpful commands:

* Show python modules inside the VPE::

    pip list

* Install python modules from `PyPI <https://pypi.org>`_::

    pip install MODULE

