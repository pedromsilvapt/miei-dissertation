import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="musikla", # Replace with your own username
    version="0.6.0",
    author="Pedro M. Silva",
    author_email="pemiolsi@hotmail.com",
    description="A programming environment for music accompaniements and keyboards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pedromsilvapt/miei-dissertation",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=['bin/musikla'],
    python_requires='>=3.7',
    package_data={ 'musikla': ['parser/grammar.peg', 'libraries/keyboard/library.mkl'] },
    install_requires=[
        'typeguard',
        'pynput',
        'mido',
        'python-rtmidi',
        'arpeggio',
        'colorama',
        'typing_extensions',
        'prompt_toolkit',
        'pygments',
        'pyFluidSynth-musikla'
    ],
    entry_points={
        "console_scripts": [
            "musikla=musikla.__main__:main",
        ]
    },
)
