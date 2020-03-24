import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="musikla", # Replace with your own username
    version="0.4.0",
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
    package_data={ 'musikla': ['parser/grammar.peg'] },
    install_requires=[
        'typeguard',
        'pynput',
        'mido',
        'python-rtmidi',
        'imgui[glfw]',
        'arpeggio',
        'pyfluidsynth-musikla @ http://github.com/pedromsilvapt/pyfluidsynth/archive/master.tar.gz'
    ]
)
