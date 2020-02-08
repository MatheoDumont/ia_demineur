from demineur import *
from collections import namedtuple
from itertools import product
import numpy as np
import random
import torch
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F

"""
https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html

"""


class Net(nn.Module):
    """docstring for Net"""

    def __init__(self, in_args, out_args):
        super(Net, self).__init__()
        self.nb_in = in_args
        self.lin1 = nn.Linear(in_args, 100)
        self.lin2 = nn.Linear(100, out_args)

    def forward(self, x):
        x = x.detach().view(-1, self.nb_in)
        x = F.relu(self.lin1(x))
        return self.lin2(x)

    def learn(self):
        pass


Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward'))


class ReplayMemory(object):

    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, *args):
        """Saves a transition."""
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        self.memory[self.position] = Transition(*args)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)


class DRL(object):

    def __init__(self, reset_reward=True, print_result=True):
        """
        reset_reward = each 100 games, reset reward
        print_result = print result each 100 games
        """
        super().__init__()
        self.Q = {}
        self.w_size = 3

        # learning rate
        self.Y = 0.9
        self.batch_size = 100

        # nb d'actions pour une position
        self.nb_action = 3

        self.nn = Net(self.w_size**2, self.w_size**2 * self.nb_action)
        self.target_n = Net(self.w_size**2, self.w_size**2 * self.nb_action)

        # on ne l'entrainera pas, utile pour optimiser self.nn
        self.target_n.eval()

        self.rm = ReplayMemory(10000)

        self.optimizer = optim.RMSprop(self.nn.parameters())

        self.nb_win = 0
        self.nb_total = 0
        self.reward = []
        self.reset_reward = reset_reward
        self.print_result = print_result

        self.key_window = []
        pair_pos = product(range(-self.w_size // 2 + 1,
                                 self.w_size // 2 + 1),
                           repeat=2)

        for p in pair_pos:
            for i in range(1, self.nb_action + 1):
                self.key_window.append((p[0], p[1], i))

    def pick_action(self, state, epsilon, demineur, w_pos):
        action = None
        reward = None

        if random.uniform(0, 1) < epsilon:
            # exploration
            action = int(random.uniform(0, self.w_size**2 * self.nb_action))

        else:
            # exploitation
            with torch.no_grad():

                action = self.nn(torch.tensor(
                    state, dtype=torch.float)).argmax().item()

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

        return action, torch.tensor([reward[1]])

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

    def optimize(self):
        if len(self.rm) < self.batch_size:
            return
        transitions = self.rm.sample(self.batch_size)

        self.target_n.load_state_dict(self.nn.state_dict())

        batch = Transition(*zip(*transitions))

        mask_next_state_action = torch.tensor(
            tuple(map(lambda x: x is not None, batch.next_state)), dtype=torch.bool)

        next_state_action = torch.cat(
            [s for s in batch.next_state if s is not None])

        batch_states = torch.cat(batch.state)
        batch_actions = torch.tensor([*batch.action], dtype=torch.long)
        batch_reward = torch.cat(batch.reward)

        current_state_action_values = self.nn(
            batch_states).gather(1, batch_actions.unsqueeze(1))

        next_state_action_values = torch.zeros(
            self.batch_size, dtype=torch.float)

        next_state_action_values[mask_next_state_action] = self.target_n(
            next_state_action).max(1)[0].detach()

        expected_state_action_values = (next_state_action_values * self.Y) + batch_reward

        # Compute Huber loss
        loss = F.smooth_l1_loss(current_state_action_values,
                                expected_state_action_values.unsqueeze(1))

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        for param in self.nn.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()

    def train(self, n, play_after=False):
        demineur = Demineur()
        epsilon = 0.9

        for epoch in range(n):
            w_pos = [self.w_size // 2, self.w_size // 2]
            s = self.get_window(w_pos, demineur.get_player_board())

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

                if demineur.alive:
                    n_s = torch.tensor(self.get_window(
                        w_pos, demineur.get_player_board()), dtype=torch.float).unsqueeze(0)
                else:
                    n_s = None

                self.rm.push(
                    torch.tensor(s, dtype=torch.float).unsqueeze(0),
                    a,
                    n_s,
                    r
                )
                self.reward.append(r)

                self.optimize()

                epsilon = max(0.1, epsilon * 0.999)

                if demineur.alive:
                    # pour ne pas brouiller les fonctions teach
                    w_pos = self.move_window(w_pos, demineur)
                    s = self.get_window(w_pos, demineur.get_player_board())

            if demineur.is_resolve():
                self.nb_win += 1

            if self.print_result:
                if epoch != 0 and epoch % 100 == 0:
                    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    print("             EPOCH ", epoch)
                    print("total = ", self.nb_total)
                    print("nb_win = ", self.nb_win)
                    print("mean reward = ", np.mean(np.array(self.reward)))
                    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    if self.reset_reward:
                        self.reward = []

            self.nb_total += 1
            # on recharge le demineur
            demineur = Demineur()

        if play_after:
            self.play()

    def play(self):
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
