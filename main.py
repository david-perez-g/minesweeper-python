from typing import List
from time import sleep
from enum import Enum, auto
import random

from soupsieve import select
import config

# Block representations
MINE = '#'
NO_SURROUNDING_MINES = '·'
UNKNOWN_BLOCK = ' '


class MoveResult(Enum):
    FOUND_MINE = auto()
    ALL_OK = auto()


class BlockType(Enum):
    MINE = auto()
    NORMAL = auto()


class BlockVisibility:
    VISIBLE = auto()
    INVISIBLE = auto()


class Position:
    def __init__(self, move: str):
        self.x, self.y = tuple(
            map(lambda x: int(x), move.split(' '))
        )


class Block:
    def __init__(self, type_: BlockType):
        self.type_ = type_
        self.visibility = BlockVisibility.INVISIBLE

    def is_mine(self) -> bool:
        return self.type_ == BlockType.MINE

    def is_normal(self) -> bool:
        return self.type_ == BlockType.NORMAL

    def is_visible(self) -> bool:
        return self.visibility == BlockVisibility.VISIBLE

    def is_invisible(self) -> bool:
        return self.visibility == BlockVisibility.INVISIBLE

    def make_visible(self) -> None:
        self.visibility = BlockVisibility.VISIBLE


class Board:
    def __init__(self, board_width: int, board_height: int, number_of_mines: int):
        self.width = board_width - 1
        self.height = board_height - 1
        self.number_of_mines = number_of_mines
        self.unseen_blocks = (board_width * board_height) - number_of_mines
        self.board = self.make_board(
            board_width, board_height, number_of_mines
        )

    @staticmethod
    def make_board(board_width: int, board_height: int, number_of_mines: int) -> List[List[Block]]:
        """
        Returns a board in the form of a list with the size of the board.
        Each element of the board is a Block instance.
        Mines are randomly placed after creating the board with the given
        proportions.
        """
        # Creating board with no bombs
        board = [[Block(BlockType.NORMAL) for _ in range(board_width)]
                 for _ in range(board_height)]

        # Placing bombs
        n = 0
        while n < number_of_mines:
            mine_x_location = random.randint(0, board_width - 1)
            mine_y_location = random.randint(0, board_height - 1)

            # block is already a mine
            if board[mine_y_location][mine_x_location].is_mine():
                continue

            board[mine_y_location][mine_x_location] = Block(BlockType.MINE)
            n += 1

        return board

    def is_in_valid_height_range(self, num: int) -> bool:
        return 0 <= num <= self.height

    def is_in_valid_width_range(self, num: int) -> bool:
        return 0 <= num <= self.width

    def get_block(self, position: Position) -> Block:
        return self.board[position.y][position.x]

    def get_block_near_bombs(self, position: Position) -> int:
        """Get a block near bombs"""

        num_of_near_bombs = 0
        for y in range(position.y - 1, position.y + 2):
            for x in range(position.x - 1, position.x + 2):
                # checking if x and y are valid values
                if (not self.is_in_valid_height_range(y)) or (not self.is_in_valid_width_range(x)):
                    continue

                if self.board[y][x].is_mine():
                    num_of_near_bombs += 1

        return num_of_near_bombs

    def get_block_true_repr(self, position: Position):
        """Returns the block true representation"""

        block = self.get_block(position)

        if block.is_mine():
            return MINE

        near_bombs = self.get_block_near_bombs(position)
        if near_bombs == 0:
            return NO_SURROUNDING_MINES

        return str(near_bombs)

    def get_block_repr(self, position: Position, get_true_representation=False) -> str:
        """Returns the block representation"""

        block = self.get_block(position)

        if block.is_invisible():
            return UNKNOWN_BLOCK

        if block.is_mine():
            return MINE

        block_near_bombs = self.get_block_near_bombs(position)

        if not block_near_bombs:
            return NO_SURROUNDING_MINES

        return str(block_near_bombs)

    def print_board(self, game_finished=False) -> None:
        """Prints the board to the console."""

        height = self.height + 1
        width = self.width + 1

        def draw_line(line: str, repetitions: int) -> None:
            """Draws a line of the board."""

            print('      ', end='')

            for _ in range(repetitions - 1):
                print(line, end='')

            print(line + line[0])

        draw_line(' _____', width)

        for y in range(height):
            draw_line('|     ', width)

            print(f'   {y}  ', end='')
            for x in range(width):
                position = Position(f'{x} {y}')
                if not game_finished:
                    block_repr = self.get_block_repr(position)
                else:
                    block_repr = self.get_block_true_repr(position)

                print(f'|  {block_repr}  ', end='')

            print('|')

            draw_line('|_____', width)

        print('      ', end='')
        for x in range(width):
            print(f'   {x}  ', end='')

        print()


class GameDriver:
    def __init__(self, board_width: int, board_height: int, number_of_mines: int):
        self.game_board = Board(board_width, board_height, number_of_mines)
        self.unseen_blocks = board_height * board_width - number_of_mines

    def is_valid_move(self, move: str) -> bool:
        """Detects if a user move is valid.

        A move is valid when:
        > The x and y coordinates are separated by a ' ' in the input string
        > The x and y coordinates reflect a position on the board
        > The selected block is a valid block.
        """

        try:
            x, y = move.split(' ')
        except ValueError:
            return False

        # x and y are digits
        if not (x.isdigit() and y.isdigit()):
            return False

        x, y = int(x), int(y)

        # x and y are valid coordinates
        if (not self.game_board.is_in_valid_width_range(x)) or (not self.game_board.is_in_valid_height_range(y)):
            return False

        # checking if the block is already seen
        return self.game_board.board[y][x].is_invisible()

    def request_move(self) -> Position:
        """
        Requests a move to the user. The function will keep doing this until a valid
        move or 'q' (meaning the end of the game) is entered. If the user enters 'q'
        the program will end.
        When the user enters a valid move it will be put on a Position object.
        """

        while True:
            move = input('\nMake your move -> ')

            if move == 'h':
                print('A valid move would look like this:\n4 5\n'
                      'Where the first digit and the second digit are the '
                      'coordinates (x and y) of your move.\n'
                      'Of course this digits have to represent a valid move in the board.')
                continue

            elif move == 'q':
                print('\nEnding game ... :(\n')
                exit(0)

            elif self.is_valid_move(move):
                return Position(move)

            print("Invalid move. Please insert a valid move. You can also get help by pressing 'h' or 'q' "
                  "to end the game.")

    def do_move(self, move: Position) -> MoveResult:
        """
        Does the requested move.
        If the player found a mine the function will return MoveResult.FOUND_MINE otherwise MoveResult.ALL_OK
        """

        self.game_board.board[move.y][move.x].make_visible()
        self.unseen_blocks -= 1
        if self.game_board.get_block(move).is_mine():
            return MoveResult.FOUND_MINE

        # the block has bombs near
        if self.game_board.get_block_near_bombs(move) > 0:
            return MoveResult.ALL_OK

        # if the block has no bombs near, the function will recursively explore
        # the surrounding blocks and reveal them
        for y in range(move.y - 1, move.y + 2):
            for x in range(move.x - 1, move.x + 2):
                # checking if x and y are valid values
                if (not self.game_board.is_in_valid_height_range(y)) or (not self.game_board.is_in_valid_width_range(x)):
                    continue

                # is another normal block
                if self.game_board.board[y][x].is_invisible():
                    self.do_move(Position(f'{x} {y}'))

        return MoveResult.ALL_OK

    def is_game_over(self) -> bool:
        """Evaluates if the game is over"""

        return self.unseen_blocks == 0

    def start(self):
        print('WELCOME TO MINESWEEPER!\n\nBy: david-perez-g\nhttps://github.com/david-perez-g/')
        sleep(2)
        print(f'\nStarting a game with a {self.game_board.width + 1}x{self.game_board.height + 1} '
              f'board and {self.game_board.number_of_mines} mines.')

        while True:
            self.game_board.print_board()
            move = self.request_move()
            result = self.do_move(move)

            if result == MoveResult.FOUND_MINE:
                self.game_board.print_board(game_finished=True)
                print('\nGame over... :(\n')
                break

            if self.is_game_over():
                print('\nCongrats! You finished the game :)')
                self.game_board.print_board(game_finished=True)
                break


if __name__ == '__main__':
    game_driver = GameDriver(
        config.BOARD_WIDTH, config.BOARD_HEIGHT, config.NUMBER_OF_MINES
    )

    game_driver.start()
