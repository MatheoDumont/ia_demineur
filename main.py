from demineur import Demineur

import numpy as np
import random
from rl import RL
import time


def test():
    demineur = Demineur(nb_mines=30)
    print(demineur.board[:, :, 1])
    print(demineur.board[:, :, 3])

    while demineur.alive:
        print("Tjrs vivant, tjrs debout")
        print(demineur.get_player_board())
        # print(demineur.board[:, :, 4])

        while True:
            x = random.randint(0, demineur.length - 1)
            y = random.randint(0, demineur.width - 1)

            if demineur.board[x, y, 1] != 1:
                demineur.discover_case(x, y)
                print(f'(x, y) = ({x}, {y})')
                break

        input()

    print("Perdu !!")


def play():
    demineur = Demineur(nb_mines=30)
    print(
        f"Rules: The board is {demineur.length} length by {demineur.width} width")
    print(f"Actions are: '1' -> place flag\n" +
          "'2' -> discover case")
    print("Exit by entering 'quit'")

    while True:
        print(demineur.get_player_board("s"))
        print("Enter x, y, action:")
        inp = input()

        if not list(inp) and str(inp) and inp == "quit":
            return
        else:
            x, y, action = list(map(int, inp.split(" ")))

        if action == 1:
            demineur.place_flag(x, y)
        elif action == 2:
            demineur.discover_case(x, y)


def reinforc():
    r = RL()
    r.train(100000, True)


def bench():
    demineur = Demineur()

    t = time.time()
    for i in range(1):
        demineur._gpb_loop()
    print(f'time for loop is {time.time() - t}')

    t = time.time()
    for i in range(1):
        demineur._gpb_numpy()
    print(f'time for numpy is {time.time() - t}')


if __name__ == "__main__":
    reinforc()
