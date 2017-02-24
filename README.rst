drf-timeordered-pagination
======================================

|build-status-image| |pypi-version|

Overview
--------

Pagination utilities for Django REST Framework to allow for pagination by a mutable, but time-ordered field (like 'modified').

Requirements
------------

-  Python (2.7, 3.3, 3.4)
-  Django (1.8+)
-  Django REST Framework (3.1+)

Installation
------------

Install using ``pip``\ …

.. code:: bash

    $ pip install drf-timeordered-pagination

In ``views.py``, hook up your own integration into the pagination, or use one of the provided ones like so:

.. code:: python

    class ExampleClass(django.Model):
        ...
        modified = DateTimeField(...)
        ...


    from 
    class ExampleClassView(
        ModifiedFilterApiViewSetMixin,
        ...,
        viewsets.ModelViewSet)
        ...



Example
-------

http://api.example.org/examples/ gives default pagination.
http://api.example.org/examples/?modified_after=1900-01-01T00:00:00Z gives all examples, modified after (greater than) Midnight, 1 Jan 1900, in modified order
http://api.example.org/examples/?modified_from=1900-01-01T00:00:00Z gives all examples, modified from (greater than or equal to) Midnight, 1 Jan 1900, in modified order

Testing
-------

Install testing requirements.

.. code:: bash

    $ pip install -r requirements.txt

Run with runtests.

.. code:: bash

    $ ./runtests.py

You can also use the excellent `tox`_ testing tool to run the tests
against all supported versions of Python and Django. Install tox
globally, and then simply run:

.. code:: bash

    $ tox

Documentation
-------------

To build the documentation, you’ll need to install ``mkdocs``.

.. code:: bash

    $ pip install mkdocs

To preview the documentation:

.. code:: bash

    $ mkdocs serve
    Running at: http://127.0.0.1:8000/

To build the documentation:

.. code:: bash

    $ mkdocs build

.. _tox: http://tox.readthedocs.org/en/latest/

.. |build-status-image| image:: https://secure.travis-ci.org/andrewdodd/drf-timeordered-pagination.svg?branch=master
   :target: http://travis-ci.org/andrewdodd/drf-timeordered-pagination?branch=master
.. |pypi-version| image:: https://img.shields.io/pypi/v/drf-timeordered-pagination.svg
   :target: https://pypi.python.org/pypi/drf-timeordered-pagination
