"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages

# Get the long description from the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lensrec",
    version="0.0.4",
    author="James Whitehead",
    author_email="james.whitehead490@gmail.com",
    description="Tool for recording metasurface lenses in a motion control setup",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JamesWhitehead5/lensrec",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        'numpy==1.16.4',
        'xarray==0.12.3',
        'pyserial==3.4',
        'opencv-python==4.1.2.30',
        'pymba==0.3.5',
        'numpngw==0.0.8',
        'Pillow==8.1.1',
        'matplotlib',
        'pypng==0.0.20',
        'screeninfo==0.4',

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
