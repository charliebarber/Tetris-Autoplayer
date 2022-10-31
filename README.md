# Tetris-Autoplayer

This program plays Tetris by choosing the optimum move possible to get the highest overall score. It simulates all of the next two possible moves and ranks the options of block positions and gives it a score based on the given heuristics. These heuristics were found using a hill climbing algorithm which runs the game X amount of times until the heuristics tend towards the best value.

The autoplayer code can be found in `player.py`. To run the program, run `python player.py` in the directory.
