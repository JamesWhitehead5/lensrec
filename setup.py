with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lensrec",
    version="0.0.2",
    author="James Whitehead",
    author_email="james.whitehead490@gmail.com",
    description="Tool for recording metasurface lenses in a motion control setup",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JamesWhitehead5/lensrec",
    packages=setuptools.find_packages(),
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
    ]
)
