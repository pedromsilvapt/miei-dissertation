# SoundPlaygroundPy
Python port of the experiments that were started in the .NET project.

## Python Dependencies
 - `typeguard`
 - `pynput`
 - `mido`
 - `python-rtmidi` (requires `libasound2-dev` (or `--install-option="--no-alsa"`) and `libjack-dev` (or `--install-option="--no-jack"`))
 - `imgui[glfw]` (requires `libglfw3` and `libglfw3-dev`
 - `arpeggio`
 - `pyFluidSynth` (required `fluidsynth >=1.1.9`)
 > **Note** Instead of installing pyFluidSynth from PyPi, we need to use the more up-to-date version (which accepts pulseaudio) from the git repo
 > ```shell
 >pip3 install git+https://github.com/nwhitehead/pyfluidsynth@9a8ecee996e83a279e8d29d75e8a859aee4aba67
 >```
 
## Usage
To launch the graphical application, run:
```shell
python3 __init__.py --gui
```

To run the app in the terminal:
```shell
python3 __init__.py examples/westworld.ml
python3 __init__.py examples/minecraft.ml -o pulseaudio -o minecraft.abc
python3 __init__.py examples/keyboard.ml -i keyboard
```

For a more detailed view of the available options, check:
```shell
python3 __init__.py -h
```

## Porting
 - [x] Abstract Syntax Tree
 - [x] Grammar & Parser
 - [ ] Graphical Interface
 - [x] FluidSynth
