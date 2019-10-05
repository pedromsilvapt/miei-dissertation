# SoundPlaygroundPy
Python port of the experiments that were started in the .NET project.

## Python Dependencies
 - `imgui[glfw]` (requires `libglfw3` and `libglfw3-dev`)
 - `py_linq`
 - `arpeggio`
 - `pyFluidSynth` (required `fluidsynth >=1.1.9`)
 > **Note** Instead of installing pyFluidSynth from PyPi, we need to use the more up-to-date version (which accepts pulseaudio) from the git repo
 > ```shell
 >pip3 install git+https://github.com/nwhitehead/pyfluidsynth@9a8ecee996e83a279e8d29d75e8a859aee4aba67
 >```
 
## Usage
```shell
python3 __init__.py
```

## Porting
 - [x] Abstract Syntax Tree
 - [x] Grammar & Parser
 - [ ] Graphical Interface
 - [x] FluidSynth
