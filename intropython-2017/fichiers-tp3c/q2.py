une_liste = [1, 2, 10, 3, 4]

def doublon(liste):
    for indice in range(len(liste)):
        for n in range(1, len(liste) - indice):
            if liste[indice] == liste[indice + n]:
                return True
    return False

print doublon(une_liste)
