# Game of Life with the MongoDB Aggregation Pipeline

This repo contains an implementation of the Game of Life using the MongoDB Aggregation Framework.

![Game of Life GIF](game_of_life_small.gif)

# How to get started

Update the parameters in the `game_of_life.py` program:

```python
DB = "game_of_life"
COLL = "coll"
START_RATIO_ALIVE_CELLS = 0.4
SIZE_X = 50
SIZE_Y = 50
NB_GEN = 50
```

Then you can just start the program and point to a MongoDB instance of your choice:

```shell
python3.9 game_of_life.py "mongodb+srv://USER:PASSWORD@gameoflife.abcde.mongodb.net/test?w=1"
```

# Visualization

To see the game of life in action, I'm using a chart in MongoDB Atlas Charts that is setup like this: 

- Chart Type: Heatmap
- X Axis: "x"
- Y Axis: "y"
- Intensity: "alive" with Aggregate "SUM"

In the `Customize` tab, I selected the back & white color palette.
