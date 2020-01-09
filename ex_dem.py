#########################################
### Info224, TP5 : démineur en Python ###

import random
from tkinter import *

# https://www.lama.univ-savoie.fr/pagesmembres/hyvernat/Enseignement/1112/info224/tp5.html#toc8
##################
# Plateau de jeu
# Le plateau est simplement représenté par une matrice (un tableau de
# tableaux).
# La case de coordonnées "(i,j)" est un dictionnaire à deux champs :
# - "mine" qui est un booléen et qui indique si la case contient une mine
# - "etat" qui indique l'état de la case :
# - INCONNU quand le joueur n'a pas découvert la case
# - un entier entre 0 et 8 qui indique le nombre de mines voisines,
# quand le joueur a découvert la case
# - DRAPEAU quand le joueur a mis un drapeau sur la case
# - QUESTION quand le joueur n'est pas sûr.
# - PERDU quand il s'agit d'une case avec une mine, sur laquelle le
# joueur a cliqué
# Les 13 états possibles sont modélisés par des entiers, avec les
# déclarations suivantes :
INCONNU = -1
PERDU = -2
DRAPEAU = -3
QUESTION = -4


# QUESTION : à compléter
def dans_plateau(plateau, x, y):
    """Teste si une case est sur le plateau."""
    return False


# QUESTION : à modifier
def genere_plateau(largeur, hauteur, probabilite_mine=0):
    """Génère un plateau de jeu de taille donnée."""
    plateau = []
    for i in range(largeur):
        plateau.append([])
        for j in range(hauteur):
            plateau[i].append({"mine": False,
                               "etat": INCONNU})
    return(plateau)


# QUESTION : à écrire
def total_mines(plateau):
    """Compte le nombre total de mines sur le plateau."""
    return 0


# QUESTION : écrire les deux fonctions suivantes
def cases_voisines(plateau, x, y):
    """Donne la liste des cases voisines de la case "(x,y)"."""
    return []


def compte_mines_voisines(plateau, x, y):
    """Compte le nombre de mines voisines de la case "(x,y)" sur le plateau
"plateau"."""
    return 0


# QUESTION : écrire la procédure récursive suivante
def composante_connexe(plateau, x, y):
    """Met le plateau à jour en ouvrant toutes les cases vides à partir de la
case "(x,y)".
Attention, c'est une procédure..."""
    # pour le moment, il n'y a aucune propagation, et on compte simplement le
    # nombre de mines autours de la case (x,y)
    plateau[x][y]["etat"] = compte_mines_voisines(plateau, x, y)


def decouvre_case(plateau, x, y):
    """Découvre une case sur le plateau. Le plateau est mis à jours en
découvrant toute la composante connexe de la case "(x,y)", et la fonction
renvoie un booléen pour dire si la case "(x,y)" était une mine ou pas.
Attention, c'est à la fois une procédure (modification de l'argument "plateau"
et une fonction (qui renvoie un booléen)."""
    if plateau[x][y]["mine"]:
        plateau[x][y]["etat"] = PERDU
        #print("OUPS... La case ({},{}) contenait une mine !".format(x,y))
        return False
    composante_connexe(plateau, x, y)
    return True


def compte_mines_solution(plateau):
    """Met le plateau à jour en comptant le nombre de mines partout.
Attention, ceci est une procédure."""
    l = len(plateau)
    h = len(plateau[0])
    for x in range(l):
        for y in range(h):
            if plateau[x][y]["etat"] == INCONNU and not plateau[x][y]["mine"]:
                plateau[x][y]["etat"] = compte_mines_voisines(plateau, x, y)


#######################################
# Fonctions d'affichage sur la grille
# La fonction "dessine_case" utilise une constante globale (définie plus
# bas) "grille" qui représente la grille.
# Cette grille est un objet de type "Canvas" et a des méthodes de dessin
# comme "create_rectangle" et autre

def dessine_case(plateau, x, y, solution=False):
    """Dessine la case "(x,y)" sur le plateau.
Si "solution" est vraie, dessine aussi les mines qui sont dans des cases
fermées."""
    x1 = x * (largeur_case + 1) + 2
    y1 = y * (hauteur_case + 1) + 2
    x2 = (x + 1) * (largeur_case + 1)
    y2 = (y + 1) * (hauteur_case + 1)
    etat = plateau[x][y]["etat"]
    if etat == 0:
        grille.create_rectangle(
            x1, y1, x2, y2, outline='#c0c0c0', fill='#c0c0c0')
    elif 0 < etat < 9:
        grille.create_rectangle(
            x1, y1, x2, y2, outline='#c0c0c0', fill='#c0c0c0')
        x1 = x1 + largeur_case // 2
        y1 = y1 + hauteur_case // 2
        grille.create_text(x1, y1, justify=CENTER, text=str(etat))
    elif etat == DRAPEAU:
        grille.create_image(x1, y1, image=drapeau_img, anchor=NW)
    elif etat == QUESTION:
        grille.create_image(x1, y1, image=question_img, anchor=NW)
    elif etat == INCONNU:
        if plateau[x][y]["mine"] and solution:
            grille.create_image(x1, y1, image=mine_img, anchor=NW)
        else:
            grille.create_image(x1, y1, image=inconnu_img, anchor=NW)
    elif etat == PERDU:
        grille.create_image(x1, y1, image=perdu_img, anchor=NW)
    else:
        assert(False)


def dessine_plateau(plateau, solution=False):
    l = len(plateau)
    h = len(plateau[0])
    grille.delete(ALL)
    for x in range(l):
        for y in range(h):
            dessine_case(plateau, x, y, solution)


#######################################
# Fonctions pour gérer les évènements
# Dans ces fonctions,
# - "plateau" est une variable globale qui contient le plateau courant,
# - "grille" est une constante globale qui contient la fenêtre.
###

def __action_clic(clic):
    """Fonction appelée quand on fait un clic sur la fenêtre."""
    # clic.x et clic.y contiennent les coordonnées, en pixel,
    # du clic à l'intérieur de la fenêtre
    x = clic.x // (largeur_case + 1)  # x et y contiennent les
    y = clic.y // (hauteur_case + 1)  # coordonnées de la case
    if not dans_plateau(plateau_courant, x, y):
        return
    if plateau_courant[x][y]["etat"] != INCONNU:
        return
    ok = decouvre_case(plateau_courant, x, y)
    dessine_plateau(plateau_courant)


def __action_m(e):
    """Permet d'afficher la solution pendant 1 seconde."""
    import copy
    from time import sleep
    p = copy.deepcopy(plateau_courant)
    compte_mines_solution(p)
    dessine_plateau(p, True)
    grille.update_idletasks()
    sleep(1)
    dessine_plateau(plateau_courant)


def __action_q(e):
    """Permet de quitter le jeux."""
    root.destroy()


###############################################################
# initialisation de la fenêtre, et autres constantes globales
###

# quelques variables globales, modifiable par l'utilisateur
largeur = 10            # largeur du plateau, en nombre de cases
hauteur = 20            # hauteur du plateau, en nombre de cases
probabilite_mine = 0.15  # probabilité qu'une case contienne une mine


# fenêtre principale
root = Tk()
root.title("Démineur")
root.resizable(width=False, height=False)
Label(text="Info224 : démineur en Python").pack()

# les images utilisées pour les cases spéciales
mine_img = PhotoImage(file="mine.gif")
perdu_img = PhotoImage(file="mine_perdu.gif")
drapeau_img = PhotoImage(file="drapeau.gif")
mauvais_drapeau_img = PhotoImage(file="mauvais_drapeau.gif")
question_img = PhotoImage(file="interogation.gif")
inconnu_img = PhotoImage(file="inconnu.gif")

# on vérifie que les images ont toute les même dimensions
assert (mine_img.height() == perdu_img.height()
                          == drapeau_img.height()
                          == mauvais_drapeau_img.height()
                          == question_img.height()
                          == inconnu_img.height())
assert (mine_img.width() == perdu_img.width()
                         == drapeau_img.width()
                         == mauvais_drapeau_img.width()
                         == question_img.width()
                         == inconnu_img.width())
largeur_case = mine_img.width()
hauteur_case = mine_img.height()


# la grille : un objet de type "Canvas" pour pouvoir dessiner dedans.
grille = Canvas(root, width=largeur * (largeur_case + 1) + 1,
                height=hauteur * (hauteur_case + 1) + 1,
                bg="#7f7f7f")
grille.pack()

# les évènements à gérer
root.bind("q", __action_q)
root.bind("m", __action_m)
grille.bind("<Button-1>", __action_clic)


# création du plateau, et début du programme...
plateau_courant = genere_plateau(largeur, hauteur, probabilite_mine)
dessine_plateau(plateau_courant)
grille.mainloop()


### Fin du fichier ###
######################
