# Keyboards

One of the strenghts of the **musikla** (and the reason there's even a `k` in the name) is its ability to build custom keyboards. These keyboards can be thought of as dictionaries that map an event (like a a key press) to an action (which can be a function, a code block, an expression or music to play).

    #!musikla
    $repeat = 1;

    @keyboard {
        c: c * $repeat;
        ctrl+up: { $repeat += 1 };
        ctrl+down: { $repeat -= 1 };
    };

In this example we can observe how to play a note when a key is triggered. We cal also see how it is possible to change the state of the program with the keyboard and code blocks, which can be associated with keys as well.

## Event Types
The most basic type of events a keyboard can react to are the actual key presses of the computer's keyboard. However, the keyboard is built with extensibility in mind, and features multiple events on it's own.

    #!musikla
    $int = 0;
    
    @keyboard {
        # Keyboard c key
        c: c;
        # More complex keystrokes
        ctrl+c: ^c;
        # Raw Keyboard Scan Code
        [16]: d;
        # MIDI Note Event
        [c']: e;
        # Listen for mouse scroll events
        [ keyboard\MouseScroll() ] ( $dy ): { $int += $dy; e + $int };
    };

But the syntax above is just syntatic sugar. In reality, the example above is the same as the one below, just with less verbosity.

    #!musikla
    $int = 0;
    
    @keyboard {
        # Keyboard c key
        [ keyboard\KeyStroke( 'c' ) ]: c;
        # More complex keystrokes
        [ keyboard\KeyStroke( 'c', ctrl = true ) ]: ^c;
        # Raw Keyboard Scan Code
        [ keyboard\KeyStroke( 16 ) ]: d;
        # MIDI Note Event
        [ keyboard\PianoKey( c' ) ]: e;
        # Listen for mouse scroll events
        [ keyboard\MouseScroll() ] ( $dy ): { $int += $dy; e + $int };
    };

The currently available types of events provided out-of-the-box by the language are the following:

| Type                   | Parameters                        | Description                                  |
|------------------------|-----------------------------------|----------------------------------------------|
| `keyboard\KeyStroke`   | `$vel`                            | Is triggered by a bey press/release.         |
| `keyboard\PianoKey`    | `$vel`                            | Is triggered by a note on/off midi event.    |
| `keyboard\MouseClick`  | `$x`, `$y`, `$button`, `$pressed` | Is triggered when a mouse button is clicked. |
| `keyboard\MouseMove`   | `$x`, `$y`                        | Is triggered when the mouse moves.           |
| `keyboard\MouseScroll` | `$x`, `$y`, `$dx`, `$dy`          | Is triggered when the mouse scrolls.         |

## Event Flags
It is possible to customize how each event behaves with some flags. These flags can be placed at the top near the `@keyboard` keyword, to act as global flags that apply to all keys in that keyboard, or they can also be placed on each individual key.

    #!musikla
    @keyboard toggle {
        a repeat: C;
        s: G/2;
    };

Currently there are four flags available to customize the behavior of the keyboard. Without any flags, the default behavior of a key is to start playing it's music in full when pressed.

| Flag   | Description                                                                      |
|--------|----------------------------------------------------------------------------------|
| repeat | Repeats the music played by this key infinitely, until the key is stopped.       |
| hold   | Starts playing on key press, but stops when the key is released.                 |
| toggle | Starts playing when the key is pressed once, and stops when it is pressed again. |
| extend | Ignores the length of the note(s), and instead play it while the key is active.  |
