import numpy as np
import random

""" 
Le board est un array en 3 dimensions
Les deux premieres (X, Y) sont les coordonnes de la case sur le board
La 3eme contient les infos de la case

0: pas d'infos
1: mine
2: drapeau
3: nb mine voisine
"""

class Demineur:
    def __init__(self, longueur=10, largeur=10, nb_mines=50):
        self.board = np.zeros((longueur, largeur, 4))
        self.board[:, :, 0] = np.ones((longueur, largeur))

        self.longueur = longueur
        self.largeur = largeur

        self.nb_mines = nb_mines

        self.init_mines(nb_mines)

    def init_mines(self, nb_mines):
        for i in range(nb_mines):
            x, y = self.getCaseVide()
            self.board[x, y, 1] = 1

    def getCaseVide(self):
        while True:
            x = random.randint(0, self.longueur -1)
            y = random.randint(0, self.largeur -1)

            if self.board[x, y, 1] != 1:
               return x, y
