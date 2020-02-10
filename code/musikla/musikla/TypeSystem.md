# Type System

## Entities
> **Note:** The actual implementation might use different (but equivalent) types for practical reasons, like classes instead of tuples, or iterators instead of Lists
```python
# Aliases
Program = int
Name = str
PitchClass = int, Octave = int, Accidental = int, Value = Fraction, Tempo = int, Visible = bool
Filename = str, Volume = int
Timestamp = int

# Types
Instrument = Tuple[Program]

Voice = Tuple[Name, Instrument, Velocity, Octave, Value, Tempo]

Note = Tuple[PitchClass, Octave, Accidental, Value, Voice]

Rest = Tuple[Visible, Value, Voice]

Chord = Tuple[List[Note], Value]

SoundWave = Tuple[Filename, Volume]

MusicEvent = Tuple[Timestamp, Union[Note, Rest, Chord, SoundWave]]

Music = List[MusicEvent]
```

## Implicit Casts
```python
Note -> MusicEvent
Rest -> MusicEvent
Chord -> MusicEvent

MusicEvent -> Music
```

## Syntatic Operators
```python
def concat ( a : Music, b : Music ) -> Music: pass
def parallel ( a : Music, b : Music ) -> Music: pass
```

## Standard Library
```python
def arpeggio ( chord : Chord, pattern : Optional[Music], bars : Optional[int] ) -> Music: pass
def play ( music : Music ) -> None: pass
```
