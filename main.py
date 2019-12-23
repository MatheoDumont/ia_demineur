from demineur import Demineur

import numpy as np
import random
from rl import RL


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
                break

    print("Perdu !!")


def reinforc():
    r = RL()
    r.train()


if __name__ == "__main__":
    reinforc()
