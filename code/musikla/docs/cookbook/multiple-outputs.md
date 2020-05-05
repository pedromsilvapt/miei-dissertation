# Multiple Outputs

By default musikla plays the notes through fluidsynth to whatever sound output device the computer has. However, we can provide one output to replace that, or event more.

Right now, there are multiple outputs supported:

 - Sound Devices (such as `pulseaudio`, `alsa`, etc...) (format `fluidsynth`)
 - WAV Files (format `fluidsynth`)
 - MIDI Files/Ports (format `midi`)
 - ABC Files (format `abc`)
 - HTML files (through `$ABC_UI`) (format `html`)

Each output can be specified through the `-o` or `--output` options in the command line. Usually the type of output is inferred, but it can be forced through the `-f` or `--format` option right after the output. Any additional options after the `-o` and either until the end of the command or until the next output will be forward to the current output only.

## Examples
The following command will output to a *ALSA* device and at the same time will create a virtual MIDI port named `custom_port`, that will received only events for the voice `piano`.

    #!bash
    musikla song.mkl \
        --output alsa --audio-bufcount 4 --gain 1 \
        --output custom_port --format midi --virtual --voice piano