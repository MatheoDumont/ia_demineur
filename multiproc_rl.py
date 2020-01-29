from rl import RL
from multiprocessing import Process


def ite():
    n_proc = 7

    # init rl
    rls = []
    for i in range(n_proc):
        rls.append(RL())

    # init proc
    procs = []
    for i in range(n_proc):
        procs.append(Process(target=rls[i].train, args=[101, False]))

    # launch proc
    for i in range(n_proc):
        procs[i].start()

    # joins
    for i in range(n_proc):
        procs[i].join()

    return rls


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
                for i in range(others):
                    new_val_by_actions[i] += others[i]

            d = len(val)
            for i in range(new_val_by_actions):
                new_val_by_actions[i] /= d


def train_multiproc(n):

    for i in range(n):
        pass


if __name__ == '__main__':
    train_multiproc_mean()
