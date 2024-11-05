import os

from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="rw5_to_python",
    version="0.1.0",
    author="Joseph Long",
    author_email="joseph.long@dmse.ca",
    description="Parse RW5 files into CSV files of GPS and SS records.",
    license="BSD",
    keywords="rw5 totalstation processing",
    url="https://github.com/j-osephlong/rw5_to_csv",
    packages=["rw5_to_csv", "tests"],
    long_description=read("README.md"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
