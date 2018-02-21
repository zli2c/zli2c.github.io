import scipy as sp
contenu = open("ages-2013.csv").read()
lignes = contenu.split("\n")
rangees_hommes = []
rangees_femmes = []

for ligne in lignes[1:-1]:
    rangee = []
    for entree in ligne.split(",")[1:]:
        pop = int(entree)
        rangee.append(pop)
    rangees_hommes.append(rangee[:5])
    rangees_femmes.append(rangee[5:])

hommes = sp.array(rangees_hommes)
femmes = sp.array(rangees_femmes)
