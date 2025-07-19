from setuptools import setup, find_packages

setup(
    name="alx-backend-python",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'parameterized>=0.9.0',
        'requests>=2.31.0',
    ],
)
