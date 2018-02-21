liste = [3, 15, 8, 13, 4]

# Une fonction min(liste) en Python donne le meme resultat
def minimum(liste):
    min_actuel = liste[0]
    indice_min = 0
    for indice in range(1, len(liste)):
        element = liste[indice]
        if element < min_actuel:
            min_actuel = element
            indice_min = indice
    return min_actuel, indice_min

def trier(liste):
    for i in range(len(liste)):
        min_i, indice_min = minimum(liste[i:])
        indice_originale = indice_min + i
        # Echange l'element d'indice i avec le i-eme plus grand element.
        liste[i], liste[indice_originale] = liste[indice_originale], liste[i]
    # Pas besoin de retour puisque cette fonction modifie la liste.

print "Liste originale %s" % liste
trier(liste)
print "Liste triee %s" % liste
