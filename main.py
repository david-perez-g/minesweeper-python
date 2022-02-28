"""A minesweeper implementation in Python"""

from typing import List
from time import sleep
import random
import config


class Block:
    """A block of the board"""

    def __init__(self, type_: str):
        """
        :param type_: can be either "mine" or "normal"
        """
        self.type = type_
        self.is_visible = False

    def is_mine(self) -> bool:
        return self.type == 'mine'

    def is_normal(self) -> bool:
        return self.type == 'normal'


class MineSweeper:
    def __init__(self, board_width: int, board_height: int, number_of_mines: int):
        self.board_width = board_width
        self.board_height = board_height
        self.number_of_mines = number_of_mines
        self.board = self.make_board(board_width, board_height, number_of_mines)

    @staticmethod
    def make_board(board_width: int, board_height: int, number_of_mines: int) -> List[List[Block]]:
        """
        Returns a board in the form of a list with the size of the board.
        Each element of the board is a Block instance.
        Mines are randomly placed after creating the board with the given
        proportions.
        """
        # Creating board with no bombs
        board = [[Block('normal') for _ in range(board_width)] for _ in range(board_height)]

        # Placing bombs
        n = 0
        while n < number_of_mines:
            mine_x_location = random.randint(0, board_width - 1)
            mine_y_location = random.randint(0, board_height - 1)
            if board[mine_y_location][mine_x_location].is_mine():
                # block is already a mine
                continue
            board[mine_y_location][mine_x_location] = Block('mine')
            n += 1

        return board

    @staticmethod
    def convert_move_to_tuple(move: str) -> tuple:
        """Takes a (valid) move with the x and y coordinates and returns them as a tuple."""

        return tuple(map(lambda x: int(x), move.split(' ')))

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

        if not (x.isdigit() and y.isdigit()):
            return False

        x, y = int(x), int(y)

        # x and y are valid coordinates
        if (not (0 <= x <= self.board_width - 1)) or (not (0 <= y <= self.board_height - 1)):
            return False

        # checking if the block is valid
        return not self.board[y][x].is_visible

    def request_move(self) -> str:
        """
        Requests a move to the user. The function will keep doing this until a valid
        move or 'q' (meaning the end of the game) is entered. If the user enters 'q' the
        function will return ''.
        """

        while True:
            move = input('Please make your move -> ')
            if move == 'h':
                print('A valid move would look like this:\n4 5\nWhere the first digit and the second digit are the '
                      'coordinates (x and y) of your move. Of course this digits have to be valid in the game context.')
                continue
            elif move == 'q':
                return ''
            elif self.is_valid_move(move):
                return move

            print("Invalid move. Please insert a valid move. You can also get help by pressing 'h' or 'q' "
                  "to end the game.")

    def get_block_near_bombs(self, block_position: tuple) -> int:
        """Get a block near bombs."""

        x_position, y_position = block_position
        num_of_near_bombs = 0
        for y in range(y_position - 1, y_position + 2):
            for x in range(x_position - 1, x_position + 2):
                # checking if x and y are valid values
                if (not (0 <= y <= self.board_height - 1)) or (not (0 <= x <= self.board_width - 1)):
                    continue

                if self.board[y][x].is_mine():
                    num_of_near_bombs += 1

        return num_of_near_bombs

    def get_block_representation(self, block_position: tuple, get_true_representation=False) -> str:
        """Returns the block representation.

        :param block_position: the block position as a tuple with its x and y values as keys.
        :param get_true_representation: in case is set to True, the function will return the true representation of
        the block.
        """
        x, y = block_position
        block = self.board[y][x]

        if get_true_representation:
            if block.is_mine():
                return '#'

            near_bombs = self.get_block_near_bombs(block_position)
            if not near_bombs:
                return '·'

            return str(near_bombs)

        if block.is_visible:
            if block.is_mine():
                return '#'

            block_near_bombs = self.get_block_near_bombs(block_position)

            if not block_near_bombs:
                return '·'

            return str(block_near_bombs)

        return ' '

    def print_board(self, game_finished=False):
        """Prints the board to the console."""

        def draw_line(line: str, repetitions: int) -> None:
            """Draws a line of the board."""

            print('      ', end='')

            for _ in range(repetitions - 1):
                print(line, end='')

            print(line + line[0])

        draw_line(' _____', self.board_width)

        for y in range(self.board_height):
            draw_line('|     ', self.board_width)

            print(f'   {y}  ', end='')
            for x in range(self.board_width):
                block = self.get_block_representation(self.convert_move_to_tuple(f'{x} {y}'), game_finished)

                print(f'|  {block}  ', end='')

            print('|')

            draw_line('|_____', self.board_width)

        print('      ', end='')
        for x in range(self.board_width):
            print(f'   {x}  ', end='')

        print()

    def do_move(self, move: tuple) -> None:
        """Does the requested move and recursively applies its consequences to the board"""

        x, y = move
        self.board[y][x].is_visible = True
        if self.board[y][x].is_mine():
            return None

        # the block has bombs near
        if self.get_block_near_bombs(move):
            return None

        for y_ in range(y - 1, y + 2):
            for x_ in range(x - 1, x + 2):
                # checking if x and y are valid values
                if (not (0 <= y_ <= self.board_height - 1)) or (not (0 <= x_ <= self.board_width - 1)):
                    continue

                # is another normal block
                if not self.board[y_][x_].is_visible:
                    self.do_move((x_, y_))

    def is_game_over(self) -> str:
        """A game is over when a mine is discovered, or all the other blocks have been discovered.
        The function returns:
         > "player-pressed" in case the user found a mine.
         > '' in case the game is not finished yet.
         > "game-completed" in case the user finished the game successfully.
        """
        normal_block_unseen = False
        for blocks in self.board:
            for block in blocks:
                if block.is_mine() and block.is_visible:
                    return 'player-pressed-mine'
                if block.is_normal() and (not block.is_visible):
                    normal_block_unseen = True

        if normal_block_unseen:
            return ''

        return 'game-completed'

    @staticmethod
    def print_game_over() -> None:
        """Prints GAME OVER in a very fancy way."""

        print()
        for letter in 'G A M E  O V E R ...':
            print(letter, end='')
            sleep(.2)

        sleep(2)

    def drive_game(self):
        print('WELCOME TO MINESWEEPER!\n\nBy: david-perez-g\nhttps://github.com/david-perez-g/')
        sleep(2)
        while True:
            self.print_board()
            move = self.request_move()
            # user entered 'q'
            if not move:
                print('Ending game ...')
                break

            self.do_move(self.convert_move_to_tuple(move))

            game_state = self.is_game_over()
            # game not finished yet
            if not game_state:
                continue

            if game_state == 'player-pressed-mine':
                self.print_board(game_finished=True)
                self.print_game_over()
                break

            self.print_board(game_finished=True)
            print('\nCongrats! You finished the game :)')
            break


if __name__ == '__main__':
    minesweeper = MineSweeper(config.BOARD_WIDTH, config.BOARD_HEIGHT, config.NUMBER_OF_MINES)
    minesweeper.drive_game()
