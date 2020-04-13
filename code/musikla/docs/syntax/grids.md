# Grids
Grids provide a way for the user to define rules for how to align musical events (also referred to as [quantization](https://en.wikipedia.org/wiki/Quantization_(music))) in order to remove imprecisions resulting from the process of performing the music live. Grids can change just the duration of events, or only their start time. They can also affect each event individually, of treat certain groups of events as one atomic unit.

The most important parameter of a grid is it's **cell duration** (or length). Any events that don't fall on the edges of a grid cell are pushed to the closest one.

    #!musikla
    $grid = keyboard\Grid( 1/2 );

    # We can then instruct a keyboard to use this grid
    @keyboard toggle extend {
        z: C;
        x: D;
        c: E;
    }::with_grid( $grid );

In the example below, **Event A** would be moved to the position **0**, while **Event B** would be moved to the position **1/2**.
![Screenshot](/assets/grids_default.png)

## Direction

It is also possible to condition a grid to only align events `left` (backards in time) or `right` (forwards in time) relative to the event's original timestamp.

    #!musikla
    $grid = keyboard\Grid( 1/2, direction = 'left' );

In this case, both events would be moved to the position **0**.

![Screenshot](/assets/grids_direction_left.png)

Aditionally, there are also two parameters that control when the alignment should occur, and when the event should be left untouched.

  - **Range** How close (in time units) the event has to be from a cell edge to still be realigned.
  - **Forgiveness** How close (in time units) the event has to be from a cell edge to *not* be realigned.

Both of those parameters can be set once equally, or customized for each side (`left` and `right`).

## Range
Range describes how close to a cell edge an event has to be to still be realigned. This means that events too far away are ignored. When no custom range is provided, the grid covers the entire cell duration. We can provide a equal range for both directions, or specify different values for the `left` and `right` directions.

    #!musikla
    $grid = keyboard\Grid( 1/2, range_left = 600, range_right = 200 );

As we can see, a grid cell does not have to be completely covered, neither do both ranges have to be the same.

In this case, the **Event A** will be left untouched, while **Event B** will be moved to the position **1/2**.

![Screenshot](/assets/grids_ranges.png)

## Forgiveness
We've seen how ranges can leave events far away from the edges left untouched. But what if we want to ignore the ones close to the edges?
Forgiveness is the opposite of *range*.

    #!musikla
    $grid = keyboard\Grid( 1/2, forgiveness_left = 300 );

Here we see that every cell edge has a gap to their left with the duration of `300ms`. This leaves **Event B** untouched, while **Event A** is still pulled to the left.
![Screenshot](/assets/grids_forgiveness.png)

## Composition
We've covered above how we can customize to our needs how each grid affects each event. But using only one grid is still limiting. That's why we can compose multiple grids, each with their own ranges and forgiveness, in a sequential manner, to 

    #!musikla
    $grid = $keyboard\Grid::compose(
        keyboard\Grid( 1/2, direction = 'left', forgiveness_left = 500 ), #g1
        keyboard\Grid( 1/2, direction = 'right' ) #g2
    );

In this example, we see how the first grid aligns **Event A** to the left, but ignores **EventB** because of the forgiveness parameter. Right after, the second grid then ignores **Event A** because it is already aligned, and aligns **Event B** to the right.
![Screenshot](/assets/grids_composition_1.png)
![Screenshot](/assets/grids_composition_2.png)