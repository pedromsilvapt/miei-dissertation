# Musikla
A DSL for describing and composing musical arrangements, as well as creating custom musical keyboards.

## Installation
```shell
pip install musikla
```

## Usage
To launch the graphical application, run:
To run the app in the terminal:
```shell
python3 __main__.py file.mkl
python3 __main__.py file.mkl -o pulseaudio -o minecraft.abc
```

For a more detailed view of the available options, check:
```shell
python3 __main__.py -h
```

## Python Dependencies
 - `typeguard`
 - `pynput`
 - `mido`
 - `python-rtmidi` (requires `libasound2-dev` (or `--install-option="--no-alsa"`) and `libjack-dev` (or `--install-option="--no-jack"`))
 - `arpeggio`
 - `colorama`
 - `pyFluidSynth` (required `fluidsynth >=1.1.9`)
 > **Note** Instead of installing pyFluidSynth from PyPi, we need to use the more up-to-date version (which accepts pulseaudio) from the git repo
 > ```shell
 >pip3 install git+https://github.com/pedromsilvapt/pyfluidsynth
 >sudo python3.7 -m pip install git+http://github.com/pedromsilvapt/pyfluidsynth
 >```
 

