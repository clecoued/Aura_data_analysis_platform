from codecs import open
from setuptools import setup, find_packages

# Get long description in READ.md file
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="hrvanalysis",
    version="0.0.1",
    author="Robin Champseix",
    license="GPL",
    author_email="robin.champseix@gmail.com",
    description="a package to calculate features from Rr Interval for HRV analyses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aura-healthcare/Aura_data_analysis_platform",
    packages=find_packages(),
    install_requires=[
        "astropy>=3.0.4",
        "future>=0.16.0",
        "nolds>=0.4.1",
        "numpy>=1.15.1",
        "scipy>=1.1.0",
        "pandas>=0.23.4"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ]
)
