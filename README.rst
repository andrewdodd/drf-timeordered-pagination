drf-timeordered-pagination
======================================

|build-status-image| |pypi-version|

Overview
--------
Pagination utilities for Django REST Framework to allow for pagination by a mutable, but time-ordered field (like 'modified').

Why use this?
-------------
If you want to ask your REST endpoint "give me everything that was updated since XXX", but where that answer might span multiple pages.

More completely...if you have:

 - a collection that you want to retrieve in a paginated way;
 - ordered by a temporal field (like a "modified" timestamp); but
 - the collection is mutable, such that it can change while you are paginating through it.
 
then using this library will **guarantee that your pagination will only exhaust once every update has been seen**.

For example, say your collection has five elements ``[A, B, C, D, E]`` and they are 'modified' in that order.

 1. You begin pagination with a page size of 3.
 2. You receive the first page which contains ``[A, B, C]`` and a link to the ``next`` page.
 3. Something modifies A and B, causing the ordered list to look like: ``[C, D, E, A, B]``.
 4. You collect the `next` page which returns with ``[D, E, A]`` and a new link to the ``next`` page.
 5. Something modifies A again, causing the ordered list to look like: ``[C, D, E, B, A]``.
 6. You collect the `next` page which returns with ``[B, A]`` and no link to the ``next`` page, indicating that you are done.

This library also takes care of the situation where all the modified times of more than one page of results are identical.

Requirements
------------

-  Python (2.7, 3.3, 3.4)
-  Django (1.8+)
-  Django REST Framework (3.1+)

Important notes
---------------

The layout of the docs and the Git project were borrowed from:

- drf-proxy-pagination
- django-nsync (which was borrowed from other people too!)

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


    from timeordered_pagination.views import TimeOrderedPaginationViewSetMixin
    class ExampleClassView(
        TimeOrderedPaginationViewSetMixin,
        ...,
        viewsets.ModelViewSet)
        ...



Example
-------

- http://api.example.org/examples/ gives default pagination.
- http://api.example.org/examples/?modified_after=1900-01-01T00:00:00Z gives all examples, modified after (greater than) Midnight, 1 Jan 1900, in modified order
- http://api.example.org/examples/?modified_from=1900-01-01T00:00:00Z gives all examples, modified from (greater than or equal to) Midnight, 1 Jan 1900, in modified order

Testing
-------

Install testing requirements.

.. code:: bash

    $ pip install -r requirements.txt

Run with pytest.

.. code:: bash

    $ py.test

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
