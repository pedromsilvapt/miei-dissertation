# Combinators
We've already covered how to describe notes and rests, some of the basic building blocks of our language. It is useful to discuss how these blocks can be combined with each other, from single notes and rests to something more interesting.

## Sequential
The most basic form of music composition is sequential: each value is played after the last one ends. To do this in our language, just write each value one after the other separated by whitespace.
```musikla
C F G
```

## Grouping
Another possible combinator is grouping values with parenthesis `(` `)`. This is not very interesting in and of itself (simply grouping together a sequence of notes is exatcly the same as just playing the notes sequentially), grouping can be extremely powerful when employed alongside the other combinators.
```musikla
( C F ) G
```

## Parallel
Sequential notes can be played simply by writing them in a sequence (one after the other). Parallel notes, however, can be described by using a pipe separator `|` between them.

```musikla
C | G
```

Since playing each note in parallel can become cumbersome, we can use groups to make the task more straighforward.
```musikla
( C E | G B )
```
This example is equivalent to `(C | G) (E | B)`, which means the notes `C` and `G` play in parallel, and after, the notes `E` and `B` also play in parallel. Since the complexity of the expressions that compose the parallel operator can vary, and they are not required to have the same length (this is, to last the same time), the length of the entire parallel expression is always determined by the longer component.

## Repeat
It is possible to repeat any musical element by using the multiply operator `*`. For instance, playing the not `A` five times could be acomplished like so `A*5`.

However, more interesting than repeating a single note, is repeating groups of notes.
```musika
( C F G ) * 2
```
