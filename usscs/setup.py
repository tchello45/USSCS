from setuptools import setup
VERSION = '3.0.3'
DESCRIPTION = 'USSCS: Universal Server Side Chat System'
LONG_DESCRIPTION = 'A package that allows you to create a chat system!'
setup(
    name='usscs',
    version=VERSION,
    author='Tilman Kurmayer',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=['usscs'],
    install_requires=['rsa', 'encpp'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)