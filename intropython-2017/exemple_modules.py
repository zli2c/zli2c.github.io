import math
print math.pow(2,10)   #Exposant

import os
code_retour = os.system("echo 123")  #Executer une commande externe

import random
random.randint(0,10)  #Choisis un entier au hasard
random.choice(["a", "b", 3, "d"])  #Choisis un element d'une liste

import time
time.time()  # Nombre de secondes depuis 1970-01-01
print "Avant sleep"
time.sleep(3)  # Attendre 3 seconds
print "Après sleep"

import profile
print profile.run("time.sleep(3)")  # Calcule le temps d'excution

import handle
handle = urllib.urlopen("http://www.google.com")
html = handle.read()  # Lire le contenu d'une page comme un fichier (que nous allons voir prochainement)
print html

# Recherche des chaines de caractere dans un texte.
# Dans cet exemple, on trouve les liens sur la page web'.
import re
print re.findall('href="(.*?)"', html)

# Sauvegarde de variables dans des fichiers et lecture
import pickle
pickle.dump(liste, open("sauvegarde.pkl", "w"))
listelue = pickle.load(open("sauvegarde.pkl"))
print listelue
