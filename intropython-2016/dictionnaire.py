nombre = {"giraffe":3, "singe":5}
emplacement = {"giraffe":"Cage nord-ouest"}
nombre['dahu'] = 1
nombre["singe"] = 6
print nombre
print 'singe' in nombre
print 'ornithorynque' in nombre
print nombre.keys()
print nombre.values()
print nombre.items()
liste_de_paires = nombre.items()
print dict(liste_de_paires)
for cle in nombre:
    print cle
del nombre['giraffe']
print nombre
ordre = {cara: ord(cara) for cara in 'abcde' if cara != 'd'}
print ordre
