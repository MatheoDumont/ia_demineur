import numpy as np

"""
0: pas d'infos
1: pas de mine
2: drapeau
3: mine
4: nb mine voisine
"""

class Demineur:
    def __init__(self, longueur=10, largeur=10, nb_mines=10):
        self.board = np.zero(longueur, largeur, 5)

