from setuptools import setup, find_packages

setup(
    name="mini-cms",
    version="0.1.0",
    packages=find_packages(),
    package_dir={"": "src"},
    install_requires=[
        "requests",
    ],
)