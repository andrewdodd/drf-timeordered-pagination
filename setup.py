import codecs
import os
import re

from setuptools import setup, find_packages


###############################################################################

NAME = "drf_timeordered_pagination"
PACKAGES = find_packages(where="src")
META_PATH = os.path.join("src", "timeordered_pagination", "__init__.py")
KEYWORDS = ["Django Rest Framework", "Django", "Pagination"]
CLASSIFIERS = [
    "Private :: Do Not Upload", # Prevent from ever loading to PyPI (thanks
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "License :: Other/Proprietary License",
    "Operating System :: OS Independent",
    'Framework :: Django',
    'Framework :: Django :: 1.9',
    'Intended Audience :: Developers',
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
INSTALL_REQUIRES = [
    'django>=1.9',
]

###############################################################################

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


VERSION = find_meta("version")
URI = find_meta("uri")
LONG = (
    read("README.rst") + "\n\n" +
    "Release Information\n" +
    "===================\n\n" +
    re.search("(\d+.\d.\d \(.*?\)\n.*?)\n\n\n----\n\n\n",
              read("CHANGELOG.rst"), re.S).group(1)
)


if __name__ == "__main__":
    setup(
        name=NAME,
        description=find_meta("description"),
        license=find_meta("license"),
        url=URI,
        version=VERSION,
        author=find_meta("author"),
        author_email=find_meta("email"),
        maintainer=find_meta("author"),
        maintainer_email=find_meta("email"),
        keywords=KEYWORDS,
        long_description=LONG,
        packages=PACKAGES,
        package_dir={"": "src"},
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
    )
