# Honeycomb Compass

A bee researcher discovered how to improve honey production by guiding bees in a honeycomb to certain cells, in such a way that arranging a group of bees in a very specific layout, their production as a team is greatly improved.

The honeycomb is an N by N rectangular shape. The location of a bee in the honeycomb is identified by x and y coordinates of the cell, and the orientation (that is, the cardinal point where the bee is pointing at: Nort, South, East and West). Bees move from one cell to the other one in single step movements, and can rotate left/right within a cell.

The initial position for such a design is `0, 0, N`, which identifies a bee located in the bottom left corner and facing North. The cell directly to the North from `x, y` is `x, y+1`.

In order to guide a bee to its final location, the researcher designed a bio-interface to trigger the following actions:
- spin 90 degrees left or right, without moving from its current spot: in this case, the bio-interface accepts commands `L` and `R`, for left and right rotation respectively
- move forward one cell in the honecomb, maintain the same heading: in this case, the bio-interface accepts command `M`

# Model and algorithmic

Design and implement a systm to support the bio-interface. 
- the system must be initialized with the honeycomb shape parameters, that is, the upper-right coordinates (lower-left coordinates are assumed to be `0, 0`). 
- the system must accept instructions to guide bees, each at a time, comprising the position of cell where the bee lands together with the orientation, and a stream of `L, R, M` instructions as described before.
- the output for each stream processed is the final position and heading where the bee ended up

## Example
### Input
```
5 5
1 2 N
LMLMLMLMM
3 3 E
MMRMMRMRRM
```
### Expected Output
```
1 3 N
5 1 E
````

# REST API
Since the bio-interface device is meant to be used by different researchers to conduct experiments, you are asked to design and implement a robust REST API that allows to operate remotely, re-using the system defined above.

# Web UI
Create a simple Web UI to visualize:
- honeycomb grid: the user enters the shape of the honeycomb so it can be initialized and rendered
- bee tour: the user specifies where the bee starts, where is heading to, and visualize it the honecomb
- final position: the user enters instructions for a specific bee, and visualize the final position
