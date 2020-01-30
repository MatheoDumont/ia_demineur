from rl import RL
from multiprocessing import Process, Manager
import numpy as np
from functools import reduce


def ite_one_proc(return_list, n, q_table=None):
    rl = RL(False, False)

    if q_table is not None:
        rl.load_Q_table(q_table)

    rl.train(n)

    return_list.append(rl)


def ite(n, n_proc, q_table=None):

    manager = Manager()
    return_list = manager.list()

    # init proc
    procs = []
    for i in range(n_proc):
        procs.append(Process(target=ite_one_proc,
                             args=[return_list, n, q_table]))

    # launch proc
    for i in range(n_proc):
        procs[i].start()

    # joins
    for i in range(n_proc):
        procs[i].join()

    return return_list


def train_multiproc_mean(it):

    map_by_key = {}
    for rl_obj in it:
        for key, val in rl_obj.Q.items():
            if key not in map_by_key:
                map_by_key[key] = []

            map_by_key[key].append(val)

    new_Q_table = {}
    for key, val in map_by_key.items():
        if len(val) == 1:
            new_Q_table[key] = val[0]
        else:
            new_val_by_actions = val[0]
            for others in val[1::]:
                for i in range(len(others)):
                    new_val_by_actions[i] += others[i]

            d = len(val)
            for i in range(len(new_val_by_actions)):
                new_val_by_actions[i] /= d

    return new_Q_table


def train_multiproc(epoch, n):
    # train une fois
    n_proc = 8
    total = 0
    reward = 0
    win = 0

    # premiere iteration pour init
    it = ite(n, n_proc)
    Q_table = train_multiproc_mean(it)

    for i in range(epoch - 1):
        it = ite(n, n_proc, Q_table)
        
        Q_table = train_multiproc_mean(it)
        total += n * n_proc

        win += reduce(lambda x, y: x + y, [rl.nb_win for rl in it])
        res = []
        for rl in it:
            res += rl.reward
        reward = np.mean(np.array(res))
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("             EPOCH ", i)
        print("total = ", total)
        print("nb_win = ", win)
        print("mean reward = ", reward)


if __name__ == '__main__':
    train_multiproc(100, 100)
