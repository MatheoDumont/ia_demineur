"""
En appliquant la policy designee
Q(St, At) = Q(St, At)old + lr * (r + Y * max(at+1)(Q(St`, At`)) - Q(St, At)old)
"""
from demineur import *
from itertools import product


class RL(object):

    def __init__(self):
        super().__init__()
        self.Q = {}
        self.w_size = 3

        # learning rate
        self.lr = 0.1
        self.Y = 0.9

        self.key_window = []

        pair_pos = product(range(3), repeat=self.w_size)
        for p in pair_pos:
            self.key_window.append((p[0], p[1], 1))
            self.key_window.append((p[0], p[1], 2))

    def pick_action(self, state, epsilon, demineur, w_pos):
        hashage = self.hash_state(state)
        action = None
        reward = None

        if hashage not in self.Q:
            self.Q[hashage] = []
            for i in range(self.w_size**2):
                self.Q[hashage].append(0)

        if random.random() < epsilon:
            # exploration
            action = int(random.uniform(0, self.w_size**2))

        else:
            # exploitation
            action = np.argmax(np.array(self.Q[hashage]))

        if self.key_window[action][2] == 1:
            reward = demineur.place_flag(
                self.key_window[action][0] + w_pos[0],
                self.key_window[action][1] + w_pos[1]
            )
        elif self.key_window[action][2] == 2:
            reward = demineur.discover_case(
                self.key_window[action][0] + w_pos[0],
                self.key_window[action][1] + w_pos[1]
            )
        print(action)

        return action, reward[1]

    def hash_state(self, state):
        hashage = ""

        for row in range(self.w_size):
            for col in range(self.w_size):
                hashage += str(state[row][col])

        return hashage

    def get_window(self, w, board):
        """
        w : [x, y]

        """
        window = []
        rng = -(self.w_size // 2)
        for i in range(self.w_size):
            row = rng + i + w[0]
            window.append(board[row][w[1]:self.w_size + 1])

        return window

    def move_window(self, w, demineur):
        marge = self.w_size // 2

        if w[1] + marge == demineur.width:
            w[1] = marge
            w[0] += 1
        elif w[0] + marge == demineur.length and w[1] + marge == demineur.width:
            w[0] = marge
            w[1] = marge

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

    def train(self):
        demineur = Demineur()
        epsilon = 0.9
        w_pos = (self.w_size // 2, self.w_size // 2)
        nb_win = 0
        nb_total = 0
        reward = []

        for epoch in range(10000):
            s = self.get_window(w_pos, demineur.get_player_board())

            while demineur.alive and not demineur.is_resolve():
                print(demineur.get_player_board())
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

                epsilon = max(0.1, epsilon * 0.996)
                w_pos = self.move_window(w_pos, demineur)
                s = self.get_window(w_pos, demineur.get_player_board())

            if demineur.is_resolve():
                nb_win += 1
            nb_total += 1

            if epoch % 10 == 0:
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                print("             EPOCH ", epoch)
                print("total = ", nb_total)
                print("nb_win = ", nb_win)
                print("mean reward = ", nb.mean(np.array(reward)))
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

            # on recharge le demineur
            demineur = Demineur()
