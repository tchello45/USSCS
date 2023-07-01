from setuptools import setup
VERSION = '2.0.4'
DESCRIPTION = 'USSCS: Universal Server Side Chat System ENC'
LONG_DESCRIPTION = 'A package that allows you to create a encrypted chat system using encpp (AES and RSA)!'
setup(
    name='usscs_enc',
    version=VERSION,
    author='Tilman Kurmayer',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=['usscs_enc'],
    install_requires=['rsa', 'encpp'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)