# keyboard

Functions and classes related to the usage of keyboards. Keyboards declared through the syntax `@keyboard {}` are of the type [Keyboard](#class-keyboard).

 > **NOTE** This module is automatically imported for all scripts, and thus never needs to be manually imported.

## class Keyboard
A keyboard can be thought of as a dictionary of keys and actions.

### is_closed
> is_closed : bool

Returns `true` when the keyboard is closed (inactive) and `false` when it is open (active).

    #!musikla
    if $kb::is_closed then $kb::open() else $kb::close();


### keys
> keys : Dict[[KeyboardEvent](#class-keyboardevent), [KeyAction](#class-keyaction)]

Dictionary containing the keys and their associated actions. Can be treated just like any other dictionary in Python.

    #!musikla
    for $key, $action in $kb::keys::items() {
        print( $key, $action );
    };

### manual_lifetime
> manual_lifetime : bool = false

When `false`, the keyboard is automatically closed when a new one is created from it (this means, when it is cloned or mapped, for example). This prevents two identical keyboards from being active at the same time, and is the most common behavior. Switch to `true` and you'll need to close it manually whenever you want.

    #!musikla
    $kb::manual_lifetime = true;

### player
> _readonly_ player : Player

Returns an instance of the player associated to the keyboard.

    #!musikla
    # By default, all keyboards have the default player
    $kb::player == $script::player;

### start_all()
> start_all()

Plays all the key actions in this keyboard.

### stop_all()
> stop_all()

Stops all the (active) key actions in this keyboard.

### start()
> start( key : [KeyboardEvent](#class-keyboardevent) | str | int | Music )

If there is an action associated with this key in this keyboard, then starts it.

### stop()
> stop( key : [KeyboardEvent](#class-keyboardevent) | str | int | Music )

If there is an action associated with this key in this keyboard, then stops it.

### close()
> close() -> [Keyboard](#class-keyboard)

Close this keyboard (if it is open, otherwise do nothing). Returns self.

### open()
> open() -> [Keyboard](#class-keyboard)

Open this keyboard (if it is closed, otherwise do nothing). Returns self.

### clone()
> clone( auto_close : bool = true ) -> [Keyboard](#class-keyboard)

Creates a (deep) copy of the current keyboard, cloning it's actions as well.

**Note** When auto_close is `true`, this functions respects the value of the [manual lifetime](#manual_lifetime) attribute. When it is `false`, the original keyboard is kept always active.

### map()
> map(mapper : ([KeyboardEvent](#class-keyboardevent), Any) -> Any) -> [Keyboard](#class-keyboard)

Returns a new keyboard. When a key is activated, the `mapper` function is called with two arguments: the key, and the value resulting from evaluatin the action's expression. Beware that this mapping is therefore lazy, which means, the mapping function is not called once at the beginning, but is rather called every time a key is activated.

    #!musikla
    $times = 1;

    @keyboard {
        up: { $times += 1 }; down: { $times -= 1 }
    };

    @keyboard {
        1: C;  2: D; 3: E;
    }::map( fun ($k, $m) => $m * $times );

In this example, each note will be repeated `$times` If we change the value of `$times` up or down at some point, and then play the notes again, the repetition will reflect the new value, not the old one.

**Note** This functions respects the value of the [manual lifetime](#manual_lifetime) attribute.

### map_actions()
> map_actions(mapper : ([KeyAction](#class-keyaction)) -> [KeyAction](#class-keyaction)) -> [Keyboard](#class-keyboard)

Returns a new keyboard. The mapper function is called once, when creating the new keyboard.

    #!musikla
    @keyboard hold {
        1: C;  2: D; 3: E;
    }::map_actions( fun ( $act ) => $act::clone( hold = false ) );

This example removes the `hold` modifier from all key actions.

**Note** This functions respects the value of the [manual lifetime](#manual_lifetime) attribute.

### filter()
> filter(predicate : ([KeyAction](#class-keyaction)) -> bool) -> [Keyboard](#class-keyboard)

Called once, keeps only the key actions for which the `predicate` function returns `true`.

**Note** This functions respects the value of the [manual lifetime](#manual_lifetime) attribute.

### with_grid()
> with_grid(grid : [Grid](music.md#class-grid), mode : str = 'start_end') -> [Keyboard](#class-keyboard)

For every musical arrangement emitted by a key in this keyboard, aligns it with the given grid. Check out the Grid documentation for more information about the supported alignment modes.

**Note** Since internally this function uses the [Keyboard#map](#map) method, this functions respects the value of the [manual lifetime](#manual_lifetime) attribute.

    #!musikla
    fun with_grid ( $kb, $grid, $mode ) =>
        $kb::map( fun ( $k, $m ) => $grid::align( $m, $mode ) );

### +=
> \_\_iadd\_\_( other : [Keyboard](#class-keyboard) ) -> [Keyboard](#class-keyboard)

Merges all the keys from `other` into the current keyboard, replacing any possible duplicates, and returns itself. If the [manual lifetime](#manual_lifetime) attribute is set to `false` in the `other` keyboard, then that one is automatically closed.

### -=
> \_\_isub\_\_( other : [Keyboard](#class-keyboard) ) -> [Keyboard](#class-keyboard)

Removes from `self` all keys found in `other`, and returns itself. Both keyboards remaing open.

### +
> \_\_add\_\_( other : [Keyboard](#class-keyboard) ) -> [Keyboard](#class-keyboard)

Returns a new keyboard with both keys from `self` and from `other`. Note that if either keyboard has the [manual lifetime](#manual_lifetime) attribute is set to `false`, then they are automatically closed.

### -
> \_\_sub\_\_( other : [Keyboard](#class-keyboard) ) -> [Keyboard](#class-keyboard)

Returns a new keyboard with the keys from `self` that are not present in `other` (equivalent to the set difference operation). Note that if the `self` keyboard has the [manual lifetime](#manual_lifetime) attribute is set to `false`, then it is automatically closed. The `other` keyboard always remains open.

## class KeyAction

### key
> key : [KeyboardEvent](#class-keyboardevent)

The key associated with this action

### expr
> expr : Node

The AST Node for the expression. It is evaluated each time the key is activated.

### args
> args : List\[str\]

The list of arguments' names to extract from the keyboard event to expose to the expression when evaluating it.

### context
> context : Context

The base context with which the expression will be evaluated.

### hold
> hold : bool

A flag that, when true, indicates that this action should start playing when the key is pressed, and stop when it is released. Cannot be used at the same time as the [toggle](#toggle) flag.

### toggle
> toggle : bool

A flag that, when true, indicates that this action should start playing when the key is pressed, and stop when it is pressed again. Cannot be used at the same time as the [hold](#flag) flag.

### repeat
> repeat : bool

A flag that, when true, indicates that if the music returned by the evaluated expression ends and the key is still active (has not stopped), then the expression should be evaluated again a played.

### extend
> extend : bool

A flag that, when true, indicates that all `note_off` events are buffered (instead of being emitted) until the key is stopped. This means that instead of the notes played lasting whatever length is set in the code, they last as long as the key is active.

This flag is frequently used with either the `hold` or `toggle` flags, and means that the notes last until the key is released or pressed again, respectively.

### release
> release : bool

Ignores the `press` event, and only evaluates the expression when the release event is triggered. This flag is only valid for [binary events](#binary), for other events it is ignored.

### is_pressed
> _readonly_ is_pressed : bool

Read-only flag that indicates whether the key is pressed or not.

### is_playing
> _readonly_ is_playing : bool

Returns whether the current key is still playing (this is different from being pressed, thanks to the different behaviors that can be set by the flags listed above).

### sync
> sync : bool

Internal flag used for replaying keyboards synchronously instead of in realtime, as is usual.

### play()
> play( player : PlayerLike, parameters : Dict[str, Any], cb : (InteractivePlayer) => void = none )

### stop()
> stop( player : PlayerLike )

### on_press()
> on_press( player : PlayerLike, parameters : Dict[str, Any], cb : (InteractivePlayer) => void = none )

### on_release()
> stop( player : PlayerLike, cb : (InteractivePlayer) => void = none )

### clone()
> clone( **kargs ) -> [KeyAction](#class-keyaction)

Creates a clone of the `KeyAction`. Allows passing any number of attributes as arguments to the function to be set in the cloned action.

    #!musikla
    $action::hold = true;

    $cloned = $action::clone( hold = false );

    # Prints "True False"
    print( $action::hold, $cloned::hold ); 

## class KeyboardEvent
This is an **abstract** class that serves as the basis for the various kinds of keyboard events that are supported.

### binary
> binary : bool

When an event type is binary, it has two stages: `press` and `release`. This applies to keyboard and piano events, for instance. On the other hand, an *unary* event only has the `press` stage. This applies to the movement of the mouse, or to a scroll wheel, for instance.

### get_parameters()
> get_parameters() -> Dict[str, Any]

Should return a dictionary with all the parameters that the event contains.
