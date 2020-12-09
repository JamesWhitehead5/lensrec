"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name="lensrec",
    version="0.0.3",
    author="James Whitehead",
    author_email="james.whitehead490@gmail.com",
    description="Tool for recording metasurface lenses in a motion control setup",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JamesWhitehead5/lensrec",
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
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




# setup(name='lensrec',
#     version='0.0.4',
#     description='Tool for recording metasurface lenses in a motion control setup',
#     author='James Whitehead',
#     author_email='james.whitehead490@gmail.com',
#     url='https://github.com/JamesWhitehead5/lensrec',
#     package_dir = {
#         '': 'lensrec',
#     },
#     install_requires=[
#         'numpy',
#         'xarray',
#         'pyserial',
#         'opencv-python',
#         'pymba',
#         'numpngw',
#         'Pillow',
#         'matplotlib',
#         'pypng',
#         'screeninfo',
#     ],
#      )