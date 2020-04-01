# Musikla

Musikla is a domain-specific language to create dynamic music and music keyboards.

## Command Line
```text
usage: musikla [-h] [-i IMPORTS] [-o OUTPUTS] [--midi MIDI]
               [--soundfont SOUNDFONT] [--print-events]
               [file]

positional arguments:
  file                  Files to evaluate. No file means the input will be
                        read from the stdin

optional arguments:
  -h, --help            show this help message and exit
  -i IMPORTS, --import IMPORTS
                        Import an additional library. These can be builtin
                        libraries, or path to .ml and .py files
  -o OUTPUTS, --output OUTPUTS
                        Where to output to. By default outputs the sounds to
                        the device's speakers.
  --midi MIDI           Use a custom MIDI port by default when no name is
                        specified
  --soundfont SOUNDFONT
                        Use a custom soundfont .sf2 file
  --print-events        Print events (notes) to the console as they are
                        played.
```

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Installation
To install, clone the repository. Then go to the `code/musikla/` folder and install with pip:
```shell
git clone git@github.com:pedromsilvapt/miei-dissertation.git
cd miei-dissertation/code/musikla
pip3 install -e .
```

## Python Dependencies
 - `typeguard`
 - `pynput`
 - `mido`
 - `python-rtmidi` (requires `libasound2-dev` (or `--install-option="--no-alsa"`) and `libjack-dev` (or `--install-option="--no-jack"`))
 - `imgui[glfw]` (requires `libglfw3` and `libglfw3-dev`
 - `arpeggio`
 - `pyFluidSynth` (required `fluidsynth >=1.1.9`)
 > **Note** Instead of installing pyFluidSynth from PyPi, we need to use the more up-to-date version (which accepts pulseaudio) from the git repo
 >
 > `pip3 install git+https://github.com/pedromsilvapt/pyfluidsynth`

    