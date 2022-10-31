from board import Direction, Rotation, Action
from random import Random
import time


class Player:
    def choose_action(self, board):
        raise NotImplementedError


class RandomPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def print_board(self, board):
        print("--------")
        for y in range(24):
            s = ""
            for x in range(10):
                if (x,y) in board.cells:
                    s += "#"
                else:
                    s += "."
            print(s, y)




    def choose_action(self, board):
        self.print_board(board)
        time.sleep(0.5)
        if self.random.random() > 0.97:
            # 3% chance we'll discard or drop a bomb
            return self.random.choice([
                Action.Discard,
                Action.Bomb,
            ])
        else:
            # 97% chance we'll make a normal move
            return self.random.choice([
                Direction.Left,
                Direction.Right,
                Direction.Down,
                Rotation.Anticlockwise,
                Rotation.Clockwise,
            ])

class AutoPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed);
        return

    prevScore = 0
    prevBlocks = 0
    prevHeight = 24

    # Scoring heuristics
    heightHeuristic = -0.51
    linesHeuristic = 1.3
    holesHeuristic = -0.95
    bumpinessHeuristic = -0.18

    #Score lines using the score
    def score_complete_lines(self, board):
        currentScore = board.score
        diff = currentScore - self.prevScore
        # print("line diff", diff)
        # print("current score", currentScore)
        # print("prev score", self.prevScore)

        linesCleared = 0

        if diff >= 1600:
            linesCleared = 4
            return 100
        elif diff >= 400:
            linesCleared = 3
        elif diff >= 100:
            linesCleared = 2
        elif diff >= 25:
            linesCleared = 1

        # print("Lines cleared: ", linesCleared)

        return linesCleared * self.linesHeuristic

    # def get_blocks_num(self,board):
    #     count = 0
    #     for x in board.cells:
    #         print(x)
    #         count += 1
    #     print("count", count)
    #     return count

    # Score lines using the number of blocks
    # def score_complete_lines(self, board):
    #     print("prev", self.prevBlocks)
    #     blocks = self.get_blocks_num(board)
    #     diff = self.prevBlocks - blocks
    #     print("prev", self.prevBlocks,"current",blocks,"diff",diff)

    #     lines = 0
    #     if self.prevBlocks > blocks:
    #         lines += (9 % diff) + 1
    #         print("LINES",lines)
    #         return 0.961 * lines
    #     else:
    #         return 0


    def get_height(self, board):
        maxY = 24
        for (x,y) in board.cells:
            if y < maxY:
                maxY = y

        # print("maxY is ", maxY)
        return 24 - maxY

    # def score_height(self, board):
    #     cols = self.get_cols_height(board)
    #     height = (sum(cols) / len(cols))
    #     return height * self.heightHeuristic

    def get_cols_height(self,board):
        cols = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        for y in reversed(range(24)):
            for x in range(10):
                if (x,y) in board.cells:
                    height = abs(24 - y)
                    cols[x] = height
        return cols

    def score_holes(self, board):
        holes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        cols = self.get_cols_height(board)

        for x in range(10):
            for y in range(24 - cols[x], 24):
                if (x, y) not in board.cells:
                   holes[x] += 1
        return sum(holes) * self.holesHeuristic

    def get_score(self, board):
        return board.score

    def score_height(self, board):
        lowestY = 24
        for (x,y) in board.cells:
            if y < lowestY:
                lowestY = y
        # print("X: ", x, "Y: ", y)

        diff = (24 - lowestY) - self.prevHeight

        # print("Prev height", self.prevHeight, "lowestY", lowestY)
        #if diff == -4:
         #   return 0
        if diff > 0:
            # print("diff: ", diff)
            return diff * self.heightHeuristic
        else:
            # print("else diff: ", diff)
            return 0

    def score_wells(self,board):
        holes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        cols = self.get_cols_height(board)
        for x in range(10):
            for y in range(24 - cols[x],24):
                if (x,y) not in board.cells:
                    holes[x] += 1
        highest = max(holes)
        return highest * self.holesHeuristic * 1.4

    def score_bumpiness(self, board):
        count = 0
        cols = self.get_cols_height(board)
        for i in range(9):
            count += abs(cols[i] - cols[i+1])
        return count * self.bumpinessHeuristic

    def score_move(self, board):
        score = self.score_height(board) + self.score_complete_lines(board) + self.score_holes(board) + self.score_bumpiness(board) + self.score_wells(board)
#         print("score is", score)
        return score

    def find_holes(self, board):
        holes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        cols = self.get_cols_height(board)

        for x in range(10):
            for y in range(24 - cols[x], 24):
                if (x, y) not in board.cells:
                   holes[x] += 1
        return sum(holes)

    def lone_block(self, board):
        count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for y in reversed(range(24)):
            for x in range(10):
                if y > 2:
                    print("Y TRUE", y)
                    if (x,y) not in board.cells and (x,y-1) in board.cells:
                        print("YES")
                        count[x] += 1
                        return [True, x]

        for x in range(10):
            if count[x] == 1:
                return [True, x - 1]

        return [False, 0]

        return 0

    blockcount = 1

    def choose_action(self, board):
        self.blockcount += 1
        print(self.blockcount)
        xPos = board.falling.left
        highScore = -10000
        bestMove = []
        currentBlock = str(board.falling.shape)
        nextBlock = str(board.next.shape)
        print(nextBlock)
        totalScore = 0
        totalHighScore = -10000

        print("*************************")
        print("NEW BLOCK")
        print("*************************")
        # self.prevBlocks = self.get_blocks_num(board)
        # print("prev block set to ", self.prevBlocks)
        self.prevScore = self.get_score(board)
        # print("PREV SCORE SET TO", self.prevScore)

        initialHoles = self.find_holes(board)
        bestHoles = 0

        maxHeight = max(self.get_cols_height(board))
        minHeight = min(self.get_cols_height(board))
        diff = maxHeight - minHeight

        # isLoneBlock = self.lone_block(board)
        # print(isLoneBlock)

        # if isLoneBlock[0] == True:
        #     x = isLoneBlock[1]
        #     if x == 4:
        #         return Action.Bomb
        #     elif x < 4:
        #         move = []
        #         dir = Direction.Left
        #         move.extend([dir])
        #         move.append(Action.Bomb)
        #         return move
        #     elif x > 4:
        #         move = []
        #         dir = Direction.Right
        #         move.extend([dir] )
        #         move.append(Action.Bomb)
        #         return move

        #     return []

        if maxHeight < 6 and diff != 4:
            for x in range(1,10):
                for rotations in range(0, 4):
                    sandbox = board.clone()
                    movesHistory = []
                    landed = False

                    if rotations > 0:
                        for i in range(0, rotations):
                            if sandbox.falling is not None and currentBlock != "Shape.O":
                                sandbox.rotate(Rotation.Anticlockwise)
                                movesHistory.append(Rotation.Anticlockwise)

                    if sandbox.falling is not None:
                        xPos = sandbox.falling.left

                        while xPos > x and landed is False:
                            sandbox.move(Direction.Left)
                            movesHistory.append(Direction.Left)
                            if sandbox.falling is not None:
                                xPos = sandbox.falling.left
                            else:
                                landed = True
                                break

                        while xPos < x and landed is False:
                            sandbox.move(Direction.Right)
                            movesHistory.append(Direction.Right)

                            if sandbox.falling is not None:
                                xPos = sandbox.falling.left
                            else:
                                landed = True
                                break


                        if landed is False:
                            sandbox.move(Direction.Drop)
                            movesHistory.append(Direction.Drop)
                            landed = True

                        score = self.score_move(sandbox)
                        # print("First score ", score)

                    if landed is True:
                        for x2 in range(10):
                            for rotations2 in range(4):
                                secondSandbox = sandbox.clone()
                                secondMoves = []
                                secondLanded = False

                                if rotations2 > 0:
                                    for j in range(0, rotations2):
                                        if secondSandbox.falling is not None and currentBlock != "Shape.O":
                                            secondSandbox.rotate(Rotation.Anticlockwise)
                                            secondMoves.append(Rotation.Anticlockwise)

                                if secondSandbox.falling is not None:
                                    xPos2 = secondSandbox.falling.left

                                    while xPos2 > x2 and secondLanded is False:
                                        secondSandbox.move(Direction.Left)
                                        secondMoves.append(Direction.Left)

                                        if secondSandbox.falling is not None:
                                            xPos2 = secondSandbox.falling.left
                                        else:
                                            secondLanded = True
                                            break

                                    while xPos2 < x2 and secondLanded is False:
                                        secondSandbox.move(Direction.Right)
                                        secondMoves.append(Direction.Right)

                                        if secondSandbox.falling is not None:
                                            xPos2 = secondSandbox.falling.left
                                        else:
                                            secondLanded = True
                                            break

                                    if secondLanded is False:
                                        secondSandbox.move(Direction.Drop)
                                        secondMoves.append(Direction.Drop)

                                    secondScore = self.score_move(secondSandbox)
                                    # print("second score", secondScore)
                                    totalScore = secondScore

                                if totalScore > totalHighScore:
                                    totalHighScore = totalScore
                                    bestMove = movesHistory
                                    # print(bestMove)
        else:
            for x in range(10):
                for rotations in range(0, 4):
                    sandbox = board.clone()
                    movesHistory = []
                    landed = False

                    if rotations > 0:
                        for i in range(0, rotations):
                            if sandbox.falling is not None:
                                sandbox.rotate(Rotation.Anticlockwise)
                                movesHistory.append(Rotation.Anticlockwise)

                    if sandbox.falling is not None:
                        xPos = sandbox.falling.left

                        while xPos > x and landed is False:
                            sandbox.move(Direction.Left)
                            movesHistory.append(Direction.Left)
                            if sandbox.falling is not None:
                                xPos = sandbox.falling.left
                            else:
                                landed = True
                                break

                        while xPos < x and landed is False:
                            sandbox.move(Direction.Right)
                            movesHistory.append(Direction.Right)

                            if sandbox.falling is not None:
                                xPos = sandbox.falling.left
                            else:
                                landed = True
                                break


                        if landed is False:
                            sandbox.move(Direction.Drop)
                            movesHistory.append(Direction.Drop)
                            landed = True

                        score = self.score_move(sandbox)
                        # print("First score ", score)

                    if landed is True:
                        for x2 in range(10):
                            for rotations2 in range(4):
                                secondSandbox = sandbox.clone()
                                secondMoves = []
                                secondLanded = False

                                if rotations2 > 0:
                                    for j in range(0, rotations2):
                                        if secondSandbox.falling is not None:
                                            secondSandbox.rotate(Rotation.Anticlockwise)
                                            secondMoves.append(Rotation.Anticlockwise)

                                if secondSandbox.falling is not None:
                                    xPos2 = secondSandbox.falling.left

                                    while xPos2 > x2 and secondLanded is False:
                                        secondSandbox.move(Direction.Left)
                                        secondMoves.append(Direction.Left)

                                        if secondSandbox.falling is not None:
                                            xPos2 = secondSandbox.falling.left
                                        else:
                                            secondLanded = True
                                            break

                                    while xPos2 < x2 and secondLanded is False:
                                        secondSandbox.move(Direction.Right)
                                        secondMoves.append(Direction.Right)

                                        if secondSandbox.falling is not None:
                                            xPos2 = secondSandbox.falling.left
                                        else:
                                            secondLanded = True
                                            break

                                    if secondLanded is False:
                                        secondSandbox.move(Direction.Drop)
                                        secondMoves.append(Direction.Drop)

                                    secondScore = self.score_move(secondSandbox)
                                    # print("second score", secondScore)
                                    totalScore = secondScore

                                if totalScore > totalHighScore:
                                    totalHighScore = totalScore
                                    bestMove = movesHistory
                                    bestHoles = self.find_holes(secondSandbox)
                                    # print(bestMove)


                    # if score > highScore:
                    #     highScore = score
                    #     bestMove = movesHistory
                    #     bestHoles = self.find_holes(sandbox)



        print("best holes", bestHoles, "initial holes", initialHoles + 2)
        if bestHoles > (initialHoles) and board.discards_remaining > 0 and self.blockcount > 180:
            print("***********DISCARDED************")
            return Action.Discard

        self.prevHeight = self.get_height(board)
        return bestMove

SelectedPlayer = AutoPlayer
