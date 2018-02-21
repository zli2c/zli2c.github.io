a=int(raw_input())
b=int(raw_input())
c=int(raw_input())
def trier(a, b, c):
    if a<b<c:
        print "l'orde est le suivant : a, b, c"
    if b<c<a:
        print "l'ordre est le suivant : b, c, a"
    if a<c<b:
        print "l'ordre est le suivant : a, c, b"
    if b<a<c:
        print "l'ordre est le suivant : b, a, c"
    if c<b<a:
        print "l'ordre est le suivant : c, b, a"
    if c<a<b:
        print "l'ordre est le suivant : c, a, b"
trier(a, b, c)
