def consecutifs(texte):
    mots = texte.split()
    liste_paires = []
    for i in range(len(mots)-1):
        liste_paires.append((mots[i], mots[i+1]))
    return liste_paires

texte = "Ecrire un programme Python qui genere une liste des mots consecutifs d'un texte. Une autre phrase de ce texte. En une derniere."
consecutifs(texte)
# Sortie attendue
[('Ecrire', 'un'), ('un', 'programme'), ('programme', 'Python'), ('Python', 'qui'), ('qui', 'genere'),

