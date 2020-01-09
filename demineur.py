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
"""


class Demineur:
    def __init__(self, length=15, width=15, nb_mines=None):
        self.board = np.zeros((length, width, 4), dtype="int8")

        self.length = length
        self.width = width

        default = (self.length + self.width) * 2
        self.nb_mines = default if nb_mines is None else nb_mines

        self._init_mines()
        self._fill_coll_neighbor_mines()

        self.alive = True

    def _init_mines(self):
        for i in range(self.nb_mines):
            x, y = self._get_empty_case()
            self.board[x, y, 1] = 1

    def _get_empty_case(self):
        while True:
            x = random.randint(0, self.length - 1)
            y = random.randint(0, self.width - 1)

            if self.board[x, y, 1] != 1:
                return x, y

    def _fill_coll_neighbor_mines(self):

        kernel = np.array(
            [
                [1, 1, 1],
                [1, 0, 1],
                [1, 1, 1],
            ]
        )

        self.board[:, :, 3] = convolve2d(self.board[:, :, 1], kernel, "same")

    def _if_no_bomb_near(self, x, y):
        if self.board[x, y, 1] != 1:
            self.board[x, y, 0] = 1

    def _extend_vision(self, x, y):
        # methode appelee apres discover_case()
        
        def propagate(_from, on):
            # si pas dans le tableau
            if on[0] < 0 or on[0] >= self.width or on[1] < 0 or on[1] >= self.length:
                return
            # si je suis deja visible
            if self.board[on[0], on[1], 0] == 1:
                return
            # si je suis une bombe
            if self.board[on[0], on[1], 1] == 1:
                return
            # si je suis un drapeau
            if self.board[on[0], on[1], 2] == 1:
                return

            if self.board[on[0], on[1], 3] == 0:
                self.board[on[0], on[1], 0] = 1

                for r in range(on[0] - 1, on[0] + 2):
                    for c in range(on[1] - 1, on[1] + 2):
                        if r != _from[0] or c != _from[1]:
                            propagate(on, (r, c))
            else:
                self.board[on[0], on[1], 0] = 1
            return

        for r in range(x - 1, x + 2):
            for c in range(y - 1, y + 2):
                if r != x or c != y:
                    propagate((x, y), (r, c))

    def place_flag(self, x, y):
        """
        Place un flag sur la case
        return: False si l'action n'est pas autorise
        """
        if self.board[x, y, 2] != 1 and self.board[x, y, 0] != 1:
            self.board[x, y, 2] = 1
            self._extend_vision(x, y)
            return True, 0
        else:
            return False, -1

    def remove_flag(self, x, y):
        
        if self.board[x, y, 2] == 1:
            self.board[x, y, 2] = 0
            return True, 0
        else:
            return False, -1

    def discover_case(self, x, y):
        """
        Decouvre la case (equivalent d'une clic)
        return: False si la case a deja ete decouverte
        """
        if self.board[x, y, 0] == 1 or self.board[x, y, 2] == 1:
            return False, -1
        else:
            if self.board[x, y, 1] == 1:
                self.board[x, y, 0] = 1
                self.alive = False
                return True, -1
            else:
                self.board[x, y, 0] = 1
                self._extend_vision(x, y)
                return True, 1

    def _gpb_numpy(self):
        """
        return: le board de la vue du joueur
        de la forme : 
            [
            [0, -1, 1, 0, ...],
            [...]
            ...
            ]
        ou :
        -1 : correspond a un drapeau
        un nombre 1<n<8: le nombre de mine aux alentours de la case (dans l'exemple: "1")
        0 sinon si pas d'informations, donc case pas connue => pas de vision
        """

        # n'affiche que les cases sur lequels on a la vision
        # case avec nombre de bombe au alentour si vision
        t = self.board[:, :, 3] * self.board[:, :, 0]

        # get des cases a drapeaux
        # si flag, case = 0
        # sinon case = 1
        cases_drapeau = -(self.board[:, :, 2] - 1)

        # remise a zero des cases a drapeaux et on met les cases a drapeaux a -1 pour pouvoir les distingues ensuite
        # case = -1 => drapeaux
        #      = 0 on sais rien
        #      > 0 nombre de mines voisines
        # TODO: gerer la difference entre une case deja clique qui est vide et une case ou on a pas la vision
        t = t * cases_drapeau - self.board[:, :, 2]

        return t

    def _gpb_loop(self):

        array = []
        for r in range(self.width):
            array.append([])
            for c in range(self.length):
                if self.board[r, c, 0] == 1:
                    if self.board[r, c, 1] == 1:
                        array[r].append("*")
                    else:
                        array[r].append(self.board[r, c, 3])
                elif self.board[r, c, 2] == 1:
                    array[r].append(-1)
                else:
                    array[r].append(".")

        return np.array(array)

    def get_player_board(self, type=None):
        return self._gpb_numpy() if type is None else self._gpb_loop()

    def is_resolve(self):
        """
        return: True si le demineur est resolue
        CAD: si toutes les cases m'etant pas une bombe ont ete revelees.

        """
        return np.sum(self.board[:, :, 1] + self.board[:, :, 0]) == self.length * self.width
