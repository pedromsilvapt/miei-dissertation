# Sound Files
We've seen how to play notes and chords from instruments, but sometimes it can be interesting to mix things up a bit and play sound files directly.

Sound files can be played just like notes, and to do so, they simply have to be loaded first.

    #!musikla
    A B sample( "cihat.wav" );

To avoid loading the sample every time, we can load it once and save it in a [variable](programming.md#variables).

    #!musikla
    $cihat = sample( "cihat.wav" );

    A B $cihat;
    
The sound files can be in virtually any common format. If they are already optimized, they are loaded straight away. If not, they are converted in runtime in memory using [FFMPEG](https://ffmpeg.org/) in the background.

> **NOTE** Optimizing files in the background requires FFMPEG to be installed and available in the `$PATH`.

## Optimal Format
Sound files in this format do not require any kind of preprocessing and can be loaded directly into memory, minimizing the performance overhead. When possible, use of convert files to this format.

| Setting           | Value      |
|-------------------|------------|
| **Format**        | WAVE       |
| **Sample Rate**   | 41.100hz   |
| **Channels**      | 1 (*Mono*) |
| **Bit depth**     | 16bit      |
| **Compression**   | None       |

## Optimizing
When the file format is not optimal, optimizing it beforehand can make the whole program more performant and reduce load times. To simplify the experience, and to avoid forcing the user to figure out what tool to use and what configurations to apply to convert the files, the language comes equipped with two utility functions that simplify this process.

The user simply has to provide the file or folder paths containing the files he wishes to optimize, and indicate where the optimized versions should be saved.

    #!musikla
    # Converts a single file and stores it in the given path
    optimize_sample( "cihat.mp3", "cihat.mp3" );

    # Converts every file inside the `samples/` folder into an optimized version 
    #and stores them, with the same name inside the `samples-optimized/` folder.
    optimize_samples_folder( "samples/", "samples-optimized/" );