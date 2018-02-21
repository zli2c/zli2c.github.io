import random

vers = open("vers.txt").readlines()

liste_liste_vers = []
for num_vers in range(14):
    liste_vers = vers[num_vers*11: num_vers*11+10]
    liste_liste_vers.append(liste_vers)

for num_vers in range(14):
    alea = random.randint(0,9)
    vers_alea = liste_liste_vers[num_vers][alea]
    open("poeme.txt","a").write(vers_alea)
