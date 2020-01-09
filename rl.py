"""
En appliquant la policy designee
Q(St, At) = Q(St, At)old + lr * (r + Y * max(at+1)(Q(St`, At`)) - Q(St, At)old)
"""
from demineur import *
from itertools import product
import numpy as np
import random


"""
Idees:
        ne pas apprendre si perdue sur premier coup
            extansion: choisir un premier coup a sa place
        quand flag mis sur bombe donner 1 pts sinon 0
        quand unflag pour case ou il n'y a pas de bombe 1 sinon 0
        non car, permet a l'ia de tricher
TODO:
    - changer extend_vision, mauvais comportement (voir si vrai)
    - Faire explorer la partie du board decouverte plutot qu'une incertaine
    ou il peut perdre parce qu'il etait oblige de choisir une action a effectuer
    (ou alors action "ne rien Faire")
    - fn pour savoir quand l'algo boucle sans ne plus modifier le board
    - Update_for_window => au lieu de donner pour un etat avec la bombe au centre
    pour apprendre de ca donner toutes les possibilites pour lesquels la bombe
    et son environnement son impacte dans la Q-table
    - quand on perd par explosion, faire apprendre negativement dans ce cas la
    le discover_case pour la bombe
    - PEut-etre: modifier la fn de hash : +simple avec hash de la position de la 
    fenetre
    - lui apprendre quand il bloque et lui permettre de continuer la partie plutot
    que recommencer

DONE:
    - Montrer pour un etat que l'ia ne peut pas resoudre les coups possible
    (typiquement, l'ia ne trouve pas une bombe, mettre un flag la et mettre 1
    en recompense)

"""


class RL(object):

    def __init__(self):
        super().__init__()
        self.Q = {}
        self.w_size = 3

        # learning rate
        self.lr = 0.3
        self.Y = 0.9

        self.key_window = []

        # nb d'actions pour une position
        self.nb_action = 3

        pair_pos = product(range(-self.w_size // 2 + 1,
                                 self.w_size // 2 + 1),
                           repeat=2)

        for p in pair_pos:
            for i in range(1, self.nb_action + 1):
                self.key_window.append((p[0], p[1], i))

    def create_state(self, hashage):
        self.Q[hashage] = []
        for i in range(self.w_size**2 * self.nb_action):
            self.Q[hashage].append(0)

    def pick_action(self, state, epsilon, demineur, w_pos):
        hashage = self.hash_state(state)
        action = None
        reward = None

        if hashage not in self.Q:
            self.create_state(hashage)

        if random.uniform(0, 1) < epsilon:
            # exploration
            action = int(random.uniform(0, self.w_size**2 * self.nb_action))

        else:
            # exploitation
            action = np.argmax(np.array(self.Q[hashage]))

        if self.key_window[action][2] == 1:
            reward = demineur.place_flag(
                self.key_window[action][0] + w_pos[0],
                self.key_window[action][1] + w_pos[1]
            )
            # si flag sur bombe reward = 1
            rel_pos = self.key_window[action]
            if demineur.board[w_pos[0] + rel_pos[0],
                              w_pos[1] + rel_pos[1], 1] == 1:
                reward = reward[0], 1

        elif self.key_window[action][2] == 2:
            reward = demineur.discover_case(
                self.key_window[action][0] + w_pos[0],
                self.key_window[action][1] + w_pos[1]
            )
        elif self.key_window[action][2] == 3:
            reward = demineur.remove_flag(
                self.key_window[action][0] + w_pos[0],
                self.key_window[action][1] + w_pos[1]
            )

        return action, reward[1]

    def hash_state(self, state):

        hashage = ""

        for row in range(self.w_size):
            for col in range(self.w_size):
                hashage += str(state[row][col])

        return hashage

    def get_window(self, w, board):
        """
        w : [row, col]

        """
        window = []
        rng = -(self.w_size // 2)
        col = rng + w[1]

        for i in range(self.w_size):
            row = rng + i + w[0]
            window.append(board[row][col:col + self.w_size])

        return np.array(window)

    def move_window(self, w, demineur):
        marge = self.w_size // 2

        if w[0] + marge == demineur.length - 1 and w[1] + marge == demineur.width - 1:
            w[0] = marge
            w[1] = marge
        elif w[1] + marge == demineur.width - 1:
            w[1] = marge
            w[0] += 1
        else:
            w[1] += 1
        return w

    def update_Q(self, s, a, r, n_s, n_a):
        hash_s = self.hash_state(s)
        hash_ns = self.hash_state(n_s)

        # Q function
        self.Q[hash_s][a] = (
            self.Q[hash_s][a] +
            self.lr * (
                r + self.Y * self.Q[hash_ns][n_a] -
                self.Q[hash_s][a])
        )

    def teach_for_death(self, state, action):
        # on cherche la pos de la bombe
        # relative
        bomb_pos = self.key_window[action]
        # abs
        # bomb_pos = (bomb_pos[0] + w[0], bomb_pos[1] + w[1])
        # for row in range(bomb_pos[0] - self.w_size // 2, bomb_pos[0] + (self.w_size // 2) + 1):
        #     for col in range(bomb_pos[1] - self.w_size // 2, bomb_pos[1] + (self.w_size // 2) + 1):
        #         pass
        """
        Attention, a modifier : si bombe dans un coin ou un cote, 
        comportement inconnu de self.get_window()

        Donc potentiellement 9 cas a traiter : 
        coins haut,bas,gauche,droite,
        cote haut, bas, gauche, droite
        ailleur
        """
        # Solution simple: on s'occupe que de la fenetre de la bomb
        hashage = self.hash_state(state)

        if hashage not in self.Q:
            self.create_state(hashage)

        n_s = state
        n_s[bomb_pos[0], bomb_pos[1]] = -1

        ns_hashage = self.hash_state(state)
        if ns_hashage not in self.Q:
            self.create_state(ns_hashage)

        n_a = np.argmax(np.array(self.Q[ns_hashage]))
        self.update_Q(state, action, -1, n_s, n_a)

    def teach_for_unresolved(self, demineur):
        """
        Cette methode est appelee a la fin d'une iteration de teach
        ou l'algo n'a pas reussi a finir le demineur, typiquement
        parce qu'il ne trouve pas ou sont toutes les bombes.
        On lui apprend donc les etats ou il faut placer un flag
        la ou etaient les bombes.
        """
        def change(w, abs_pos, action):
            if action == "unflag":
                demineur.board[abs_pos[0], abs_pos[1], 2] = 0

        def get_action(r, c, a):
            # print(f"row={r}, col={c}, action={a}")
            for i in range(len(self.key_window)):
                if self.key_window[i][0] == r and self.key_window[i][1] == c and (
                        self.key_window[i][2] == a):
                    return i
            return None

        def apply(w, abs_pos, action, reward):
            relativ_pos = [w[0] - abs_pos[0], w[1] - abs_pos[1]]

            s = self.get_window(w, demineur.get_player_board())
            hashage = self.hash_state(s)
            if hashage not in self.Q:
                self.create_state(hashage)

            a = get_action(relativ_pos[0], relativ_pos[1], action)

            # absolute_pos = [relativ_pos[0] + w[0], relativ_pos[1] + w[1]]
            # demineur.place_flag(
            #     absolute_pos[0],
            #     absolute_pos[1]
            # )

            # on modifie l'etat directement car on ne veut
            # pas modifier le board car doit pouvoir etre utilise
            # pour entrainer a partir d'autre etat
            # (si on place un flag, l'algo ne saura pas quoi entrainer)

            if action == 1: 
                # placer un flag
                to_place = -1
                to_place_second = demineur.board[abs_pos[0], abs_pos[1], 3]
                second_action = 3
            elif action == 3:  
                # remove flag
                to_place = demineur.board[abs_pos[0], abs_pos[1], 3]
                to_place_second = -1
                second_action = 1

            # reward pour placer flag
            n_s = s
            n_s[relativ_pos[0], relativ_pos[1]] = to_place

            ns_hashage = self.hash_state(s)
            if ns_hashage not in self.Q:
                self.create_state(ns_hashage)

            n_a = np.argmax(np.array(self.Q[ns_hashage]))

            self.update_Q(s, a, reward, n_s, n_a)

            # reward pour remove flag'
            second_a = get_action(relativ_pos[0], relativ_pos[1], second_action)
            
            s = n_s
            n_s[relativ_pos[0], relativ_pos[1]] = to_place_second

            ns_hashage = self.hash_state(s)
            if ns_hashage not in self.Q:
                self.create_state(ns_hashage)

            n_a = np.argmax(np.array(self.Q[ns_hashage]))

            self.update_Q(s, second_a, -(reward), n_s, n_a)

        w = [self.w_size // 2, self.w_size // 2]
        while True:

            for r in range(w[0] - (self.w_size // 2), w[0] + (self.w_size // 2) + 1):
                for c in range(w[1] - (self.w_size // 2), w[1] + (self.w_size // 2) + 1):

                    # Si bombe
                    if demineur.board[r, c, 1] == 1:
                        # et flag
                        if demineur.board[r, c, 2] == 1:
                            apply(w, [r, c], 1, 1)
                        # et pas flag
                        else:
                            apply(w, [r, c], 1, 1)
                    # Si pas bombe
                    elif demineur.board[r, c, 1] == 0:
                        # et flag
                        if demineur.board[r, c, 2] == 1:
                            apply(w, [r, c], 3, -1)
                            change(w, [r, c], "unflag")
                        # et pas flag
                        else:
                            pass
            if w[0] + w[1] <= (demineur.length + demineur.width - 4):
                break
            else:
                w = self.move_window(w, demineur)

    def train(self):
        demineur = Demineur()
        nb_win = 0
        nb_total = 0
        reward = []
        epsilon = 0.9

        for epoch in range(100000):
            w_pos = [self.w_size // 2, self.w_size // 2]
            s = self.get_window(w_pos, demineur.get_player_board())
            past = None
            count_same = 0

            while demineur.alive and not demineur.is_resolve():

                """
                1) On calcule un premier etat s auquel on associe une action a
                    - pour choisir l'action, en fonction d'epsilon et d'un nombre aleatoire
                        - soit exploration
                        - soit exploitation
                2) A partir de cet action a et cette etat s, on calcule l'etat
                   s+1 avec l'action a`
                """

                a, r = self.pick_action(s, epsilon, demineur, w_pos)
                n_s = self.get_window(w_pos, demineur.get_player_board())
                n_a, n_r = self.pick_action(n_s, epsilon, demineur, w_pos)

                self.update_Q(s, a, r, n_s, n_a)
                reward.append(r)
                reward.append(n_r)

                epsilon = max(0.1, epsilon * 0.999)
                if demineur.alive:
                    # pour ne pas brouiller les fonctions teach
                    w_pos = self.move_window(w_pos, demineur)
                    s = self.get_window(w_pos, demineur.get_player_board())

                current = demineur.get_player_board()
                if past is not None and (current == past).all:
                    count_same += 1
                    if count_same == demineur.length * 10:
                        # demineur.alive = False
                        count_same = 0
                        epsilon = 0.9
                        self.teach_for_unresolved(demineur)

                past = current

            if demineur.is_resolve():
                nb_win += 1
            elif not demineur.alive:
                self.teach_for_death(s, a)

            nb_total += 1

            if epoch % 100 == 0:
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                print("             EPOCH ", epoch)
                print("total = ", nb_total)
                print("nb_win = ", nb_win)
                print("mean reward = ", np.mean(np.array(reward)))
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                reward = []

            # on recharge le demineur
            demineur = Demineur()

        # on joue
        w_pos = [self.w_size // 2, self.w_size // 2]
        demineur = Demineur()
        print(demineur.get_player_board())
        while True:
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("position des bombes: ")
            print(demineur.board[:, :, 1])
            print("Board: ")
            print(demineur.get_player_board(type=1))
            s = self.get_window(w_pos, demineur.get_player_board())
            n_a, n_r = self.pick_action(s, 0, demineur, w_pos)
            w_pos = self.move_window(w_pos, demineur)
            input()
