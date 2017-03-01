<div class="badges">
    <a href="http://travis-ci.org/andrewdodd/drf-timeordered-pagination">
        <img src="https://travis-ci.org/andrewdodd/drf-timeordered-pagination.svg?branch=master">
    </a>
    <a href="https://pypi.python.org/pypi/drf-timeordered-pagination">
        <img src="https://img.shields.io/pypi/v/drf-timeordered-pagination.svg">
    </a>
</div>

---

# drf-timeordered-pagination

Pagination utilities for Django REST Framework to allow for pagination by a mutable, but time-ordered field (like 'modified').

---

## Overview

Pagination utilities for Django REST Framework to allow for pagination by a mutable, but time-ordered field (like 'modified'). It provides results in a stable order (i.e. by 'modified') and ensures that the 'next' links will allow full walking of the list without omitting values, even if they mutate between calls.

In many ways this is similar to a 'Cursor based' pagination, but is designed to:
 - Not require state on the server
 - Be tailored to getting 'only the things that have updated since I last checked' from an API

## Important notes

The layout of the docs and the Git project were borrowed from:
 - drf-proxy-pagination

## Requirements

* Python (2.7, 3.4+)
* Django (1.8+)
* Django REST Framework (3.1+)

## Installation

Install using `pip`...

```bash
$ pip install drf-timeordered-pagination
```

In `views.py`, hook up your own integration into the pagination, or use one of the provided ones like so:

```python

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
```

## Example

 - [http://api.example.org/examples/](http://api.example.org/examples/) gives default pagination.
 - [http://api.example.org/examples/?modified_after=1900-01-01T00:00:00Z](http://api.example.org/examples/?modified_after=1900-01-01T00:00:00Z) gives all examples, modified after (greater than) Midnight, 1 Jan 1900, in modified order
 - [http://api.example.org/examples/?modified_from=1900-01-01T00:00:00Z](http://api.example.org/examples/?modified_from=1900-01-01T00:00:00Z) gives all examples, modified from (greater than or equal to) Midnight, 1 Jan 1900, in modified order


## Testing

Install testing requirements.

```bash
$ pip install -r requirements.txt
```

Run with pytest.

```bash
$ py.test
```

You can also use the excellent [tox](http://tox.readthedocs.org/en/latest/) testing tool to run the tests against all supported versions of Python and Django. Install tox globally, and then simply run:

```bash
$ tox
```

## Documentation

To build the documentation, you'll need to install `mkdocs`.

```bash
$ pip install mkdocs
```

To preview the documentation:

```bash
$ mkdocs serve
Running at: http://127.0.0.1:8000/
```

To build the documentation:

```bash
$ mkdocs build
```
