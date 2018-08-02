from bitstring import BitArray

class GomokuBoard:
    """
    Models 19x19 Gomoku board.
    """
    def __init__(self):
        self.blackBoard = BitArray(int=0, length=361)
        self.whiteBoard = BitArray(int=0, length=361)

    def play(self, x, y, player):
        assert(0 <= x and x <= 18)
        assert(0 <= y and y <= 18)
        assert(player == 0 or player == 1)

        if player == 0:
            self.blackBoard.set(1, GomokuBoard.getIndexFromCoordinates(x, y))

        if player == 1:
            self.whiteBoard.set(1, GomokuBoard.getIndexFromCoordinates(x, y))

        assert(self.checkOverlaps())
        if (self.checkVictory()):
            print("The game is over!\n")
            self.displayBoards() 

    def checkOverlaps(self):
        if self.blackBoard.__and__(self.whiteBoard).any(1):
            return False
        else:
            return True

    def checkVictory(self):
        for row in range(19):
            for column in range(15):
                if (self.blackBoard.all(1, range(GomokuBoard.getIndexFromCoordinates(column, row), column+5)) or
                    self.whiteBoard.all(1, range(GomokuBoard.getIndexFromCoordinates(column, row), column+5))):
                    self.displayBoards()
                    return True

        for column in range(19):
            for row in range(15):
                if (self.blackBoard.all(1, range(GomokuBoard.getIndexFromCoordinates(column, row), 361, 19)) or
                    self.whiteBoard.all(1, range(GomokuBoard.getIndexFromCoordinates(column, row), 361, 19))):
                    self.displayBoards()
                    return True

        for row in range(15):
            for column in range(15):
                if (self.blackBoard.all(1, range(GomokuBoard.getIndexFromCoordinates(column, row), GomokuBoard.getIndexFromCoordinates(column, row) + 5*20, 20)) or 
                    self.whiteBoard.all(1, range(GomokuBoard.getIndexFromCoordinates(column, row), GomokuBoard.getIndexFromCoordinates(column, row) + 5*20, 20))):
                    self.displayBoards()
                    return True

        for row in range(4, 19):
            for column in range(15):
                if (self.blackBoard.all(1, range(GomokuBoard.getIndexFromCoordinates(column, row), GomokuBoard.getIndexFromCoordinates(column, row) + 5*18, 18)) or 
                    self.whiteBoard.all(1, range(GomokuBoard.getIndexFromCoordinates(column, row), GomokuBoard.getIndexFromCoordinates(column, row) + 5*18, 18))):
                    self.displayBoards()
                    return True

        return False 

    def displayBits(self):
        print(self.blackBoard.bin)
        print(self.whiteBoard.bin)

    def displayBoards(self):
        for row in range(19):
            print(self.blackBoard[19*row:19*row + 19].bin)
        print('\n')
        for row in range(19):
            print(self.whiteBoard[19*row:19*row + 19].bin)
        print('\n')

    @staticmethod
    def getIndexFromCoordinates(x, y):
        return 19*y + x
