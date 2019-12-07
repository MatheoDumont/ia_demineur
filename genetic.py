import numpy as np
import random
import math
from networkGen import NetworkGen


def gen_NN(genes=[]):
    # # Inputs
    # input = Input(shape=(7,))

    # x = Dense(10, activation='tanh')(input)
    # x = Dense(10, activation='tanh')(x)

    # predictions = Dense(2, activation='tanh')(x)

    # model = Model(inputs=input, outputs=predictions)

    # if len(genes) > 0:
    #     model.set_weights(genes)

    # model._make_predict_function()

    model = NetworkGen(6, 1)

    return model


def croisement(w1, w2, nb_enfants):
    """
    b1.fitness > b2.fitness
    renvoie le croisement entre les poids des 2 parents
    c'est a dire 2 enfants avec des poids qui seront un mixte des parents
    """
    list_genes_children = []

    for i in range(0, nb_enfants):
        # nombre aleatoire compris entre - 0.5 et 1.5
        # utiliser pour faire le croisement
        p = random.uniform(-0.5, 1.5)

        # poids du nouvel enfant
        e = np.multiply(p, w1) + np.multiply(w2, (1 - p))

        list_genes_children.append(e)
    return list_genes_children


def mutate(genes, nb, coeff):
    for k in range(0, len(genes)):

        # on skip les couches qui qui n'ont pas de poids
        # ou celles qu'on ne veut pas muter pour les garder
        # telles qu'elles sont

        if len(genes[k].shape) > 1 and random.randint(0, nb) == 0:

            matrice_muta = np.random.random(genes[k].shape)

            genes[k] += np.multiply(matrice_muta - 0.5, coeff)


def mutate_list(list_genes, nb, coeff):

    size_list_genes = len(list_genes)

    # En fonction de nb, les plus ou mois premiers genes reçus ne seront pas mutés
    # si n est égale à la moitié de size_list_genes donc à la moitié des genes donnés à mutés
    # seulement la seconde partie sera muté

    for i in range(0, size_list_genes):
        mutate(list_genes[i], max(0, nb - (size_list_genes - i)), coeff)

    return list_genes


def selection(list_genes, max):  # max: le nombre maximale de bot qui seront selectionne
    new_list_genes = []
    new_list_genes.append(list_genes[0])  # on selectionne le premier notament car log(0) existe pas

    for i in range(1, len(list_genes)):
        # les bots sont tries par fitness, plus le bot courant est loin dans la liste moins il a de chances d'etre selectionne
        if not len(new_list_genes) > max and random.uniform(0, math.log(i)) <= 1:
            new_list_genes.append(list_genes[i])
    return new_list_genes


def pair_cross(list_genes, nb_children_from_cross):
    # POUR LES PAIRS DE BOSS(meilleurs robots)
    to_return_list_genes = []
    size_genes_from_boss = len(list_genes)
    for k in range(0, size_genes_from_boss-1, 2):

        b1 = list_genes[k]
        b2 = list_genes[k+1]

        # CROISEMENT
        # list_genes_croisement = croisement(b1, b2, self.nb_children_from_cross)
        for gene in croisement(b1, b2, nb_children_from_cross):
            to_return_list_genes.append(gene)

        # MUTATIONS
        """for gene in mutate_list(list_genes_croisement, self.nb_children_from_cross / 2, 2):
                                                                self.list_genes.append(gene)"""


def first_cross_with_all_others(list_genes, nb_children_from_cross):
    to_return_list_genes = []
    first_gene = list_genes[0]

    for i in range(1, len(list_genes)):

        for gene in croisement(first_gene, list_genes[i], nb_children_from_cross):
            to_return_list_genes.append(gene)

    return to_return_list_genes
