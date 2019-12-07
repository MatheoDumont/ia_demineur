import numpy as np

from env import Env
from genetic import *


class Gen_algo:
    def __init__(self, graphic=False, nb_steps=1000000000000000000, nb_start_pop=100, nb_gen=1000000000, load=False):
        self.nb_steps = nb_steps  # nb de move par run
        self.nb_start_pop = nb_start_pop  # nb de robot dans la pop de depart
        self.list_genes = []

        self.nb_gen = nb_gen
        models = []
        # on recupere des models sauvegardes sur le disk
        if load:
            models.append(self.load_genes_from_disk(2))
            models.append(self.load_genes_from_disk(2))
            models.append(self.load_genes_from_disk(2))
            models.append(self.load_genes_from_disk(2))
            models.append(self.load_genes_from_disk(2))
            models.append(self.load_genes_from_disk(2))
            models.append(self.load_genes_from_disk(2))
            models.append(self.load_genes_from_disk(2))
            models.append(self.load_genes_from_disk(2))
            models.append(self.load_genes_from_disk(2))

        self.env = Env(graphic=graphic, nb_robot=nb_start_pop, models=models)

        self.nb_boss = int(self.nb_start_pop * 0.1) if self.nb_start_pop > 10 else 10

        # *2 pour le croisement qui se fait par pair de parent
        self.nb_children_from_each_cross = int(self.nb_boss * 0.1) + 1
        self.nb_to_cross = self.nb_start_pop - int(self.nb_boss * 0.2)

        print("---------PARAMETERS----------")
        print("nb_start_pop: ", self.nb_start_pop)
        print("nb_boss: ", self.nb_boss)
        print("nb_children_from_each_cross: ", self.nb_children_from_each_cross)
        print("nb_to_cross: ", self.nb_to_cross)
        self.best_fitness = -1

    def start(self):
        # boucle de generation
        for num_gen in range(1, self.nb_gen):
            print(" ")
            print("======================================================")
            print("Generation: ", num_gen)

            # pas besoins de load_genes la premiere fois, alors que les robots
            # ont déjà été initialisés
            if num_gen != 1:
                # print("len: ", len(self.list_genes))
                self.env.load_genes(self.list_genes)
                self.list_genes = []

            # ON FAIT JOUER CHAQUE ROBOT
            self.env.computeGeneration(self.nb_steps)

            # TRIE DES ROBOTS CROISSANT AVEC LA FITNESS
            list_robots = self.env.robots
            list_robots.sort(key=lambda x: x.computeFitness(), reverse=True)

            # Notre liste robot est triée donc list_fitness_overall aussi
            list_fitness_overall = np.array(
                [robot.computeFitness() for robot in list_robots])

            print("Moyenne des fitness: ", np.mean(list_fitness_overall))
            print("Resultat des boss: ", list_fitness_overall[:self.nb_boss])

            if self.best_fitness < list_robots[0].computeFitness():
                print("############### Sauvegarde best Bot ##################")
                self.save_to_disk(list_robots[0].model)
                self.best_fitness = list_robots[0].computeFitness()

            # SELECTION DES MEILLEURS ROBOTS
            new_list_genes = []

            for robot in list_robots:
                new_list_genes.append(robot.model.get_weights())

            new_list_genes = selection(new_list_genes, self.nb_to_cross)

            # Si on selectionne pas assez de gene
            if len(new_list_genes) < self.nb_to_cross:
                for i in range(0, self.nb_to_cross - len(new_list_genes)):
                    new_list_genes.append(list_robots[i].model.get_weights())

            self.list_genes = first_cross_with_all_others(new_list_genes, self.nb_children_from_each_cross)

            self.list_genes = self.list_genes[:self.nb_to_cross]

            # On ajoute directement les meilleurs bots de cette génération à la suivante
            for i in range(0, self.nb_children_from_each_cross):
                self.list_genes.append(list_robots[i].model.get_weights())

            self.env.reset()

    def end_algo(self):
        self.env.disconnect()

    def save_to_disk(self, model):
        # sauvegarde le model dans le fichier best1.h5
        return model.save_weights('best1.h5')

    def load_genes_from_disk(self, choice):
        model = gen_NN()
        if choice == 1:
            # charge le best model de la session precedentes qui
            # est ensuite remplace par le best de la session en cours
            file = "best1.h5"
        elif choice == 2:
            file = "tient_debout.h5"

        model.load_weights(file)
        return model
