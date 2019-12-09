import numpy as np
import random
from scipy.signal import convolve2d

"""
Le board est un array en 3 dimensions
Les deux premieres (X, Y) sont les coordonnes de la case sur le board
La 3eme contient les infos de la case

0: decouverte (correspond a un clic de souris sur la case)
1: mine
2: drapeau
3: nb mine voisine
4: vision (vision cad que l'on a clique sur une case adjacente) TODO: a ameliorer
"""


class Demineur:
    def __init__(self, length=10, width=10, nb_mines=50):
        self.board = np.zeros((length, width, 5))
        self.board[:, :, 0] = np.ones((length, width))

        self.length = length
        self.width = width

        self.nb_mines = nb_mines

        self.init_mines(nb_mines)
        self.fill_coll_neighbor_mines()

        self.alive = True

    def init_mines(self, nb_mines):
        for i in range(nb_mines):
            x, y = self.get_empty_case()
            self.board[x, y, 1] = 1

    def get_empty_case(self):
        while True:
            x = random.randint(0, self.length - 1)
            y = random.randint(0, self.width - 1)

            if self.board[x, y, 1] != 1:
                return x, y

    def place_flag(self, x, y):
        """
        Place un flag sur la case
        return: False si l'action n'est pas autorise
        """
        if self.board[x, y, 2] != 1 and self.board[x, y, 0] != 1:
            self.board[x, y, 2] = 1
            self.extend_vision(x, y)
            return True
        else:
            return False

    def discover_case(self, x, y):  # TODO: trouver un meilleur nom
        """
        Decouvre la case (equivalent d'une clic)
        return: False si la case a deja ete decouverte
        """
        if self.board[x, y, 0] == 1 and self.board[x, y, 2] == 1:
            return False
        else:
            if self.board[x, y, 1] == 1:
                self.board[x, y, 0] = 1
                self.alive = False

            self.board[x, y, 0] = 1
            self.extend_vision(x, y)
            return True

    def extend_vision(self, x, y):
        if x + 1 < self.length:
            self.board[x + 1, y, 4] = 1
        if x - 1 >= 0:
            self.board[x - 1, y, 4] = 1
        if y + 1 < self.length:
            self.board[x, y + 1, 4] = 1
        if y - 1 >= 0:
            self.board[x, y - 1, 4] = 1

    def get_player_board(self):
        """
        return: le board de la vue du joueur
        """
        # n'affiche que les cases sur lequels on a la vision
        t = self.board[:, :, 3] * self.board[:, :, 4]

        # get des cases a drapeaux
        cases_drapeau = - (self.board[:, :, 2] - 1)

        # remise a zero des cases a drapeaux et on met les cases a drapeaux a -1 pour pouvoir les distingues ensuite
        # case = -1 => drapeaux
        #      = 0 on sais rien
        #      > 0 nombre de mines voisines
        # TODO: gerer la difference entre une case deja clique qui est vide et une case ou on a pas la vision
        t = t * cases_drapeau - self.board[:, :, 2]

        return t

    def fill_coll_neighbor_mines(self):
        
        kernel = np.array(
            [
                [1, 1, 1],
                [1, 0, 1],
                [1, 1, 1],
            ]
        )

        self.board[:, :, 3] = convolve2d(self.board[:, :, 1], kernel, "same")

    # TODO
    def is_resolve(self):
        """
        return: True si le demineur est resolue
        """
        pass
