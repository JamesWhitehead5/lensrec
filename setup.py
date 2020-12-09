"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""


# Always prefer setuptools over distutils
# from setuptools import setup, find_packages
import pathlib



here = pathlib.Path(__file__).parent.resolve()




# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

from distutils.core import setup

setup(name='lensrec',
    version='0.0.4',
    description='Tool for recording metasurface lenses in a motion control setup',
    author='James Whitehead',
    author_email='james.whitehead490@gmail.com',
    url='https://github.com/JamesWhitehead5/lensrec',
    package_dir = {
        '': 'src',
    },
    install_requires=[
        'numpy',
        'xarray',
        'pyserial',
        'opencv-python',
        'pymba',
        'numpngw',
        'Pillow',
        'matplotlib',
        'pypng',
        'screeninfo',
    ],
     )

# setup(
#     name="lensrec",
#     version="0.0.3",
#     author="James Whitehead",
#     author_email="james.whitehead490@gmail.com",
#     description="Tool for recording metasurface lenses in a motion control setup",
#     long_description=long_description,
#     long_description_content_type="text/markdown",
#     url="https://github.com/JamesWhitehead5/lensrec",
#     package_dir={'': 'C:/Users/bcollins/UHD_PY/uhd/host/build/python'},
#     classifiers=[
#         "Programming Language :: Python :: 3",
#         "Operating System :: OS Independent",
#     ],
#     python_requires='>=3.6',
#     install_requires=[
#         'numpy',
#         'xarray',
#         'pyserial',
#         'opencv-python',
#         'pymba',
#         'numpngw',
#         'Pillow',
#         'matplotlib',
#         'png',
#         'screeninfo',
#     ],
#
#
# )