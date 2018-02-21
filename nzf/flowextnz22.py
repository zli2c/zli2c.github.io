from Numeric import *
from copy import deepcopy
from copy import copy
from matching3 import isflow,nextpart
import sys

#mode 0 for generating list of goodvectors, mode >0 for deleting [mode] edges and checking list of badvectors
#mode=int(sys.argv[2])
mode=0
#Somehow loop through all subsets of deleted edges of a certain size
delete=[0]*mode
#delete=[2,3,7,9,12,14]

f=open(sys.argv[1],'r')
#lam is lambda, the flow number
r=f.readline()
lam=int(r)
r=f.readline()
vertnumber=int(r)
r=f.readline()
edgenumber=int(r)
#sizev is the number of vertices (excluding other side of half edges)
r=f.readline()
sizev=int(r)
#norig is the original set of incidence vectors
r=f.readline()
norig=[]
for n in r.split(','):
  n=n.split()
  norig.append([int(n[0]),int(n[1]),int(n[2])])
#cutedges are the edges on the ouside cut (must direct them all in the same direction)
r=f.readline()
cutedges=[]
for n in r.split(','):
  n=n.split()
  cutedges.append([int(n[0]),int(n[1])])


f.close()

if mode:
 f=open(sys.argv[3],'r')
 badvectlist=f.readlines()
 f.close()

#fl=[[0]*vertnumber]*vertnumber
fl=zeros([vertnumber,vertnumber], Int)

def extend():
   #s=[]
   if len(edgelist)==0: 
     #print fl
     return 1
   short=range(lam)
   for e in edgelist:
    se=range(1,lam)
    degu=len(n[e[0]])
    degv=len(n[e[1]])
    for v in n[e[0]]:
      if fl[e[0]][v] in se: se.remove(fl[e[0]][v])
    for v in n[e[1]]:
      if fl[v][e[1]] in se: se.remove(fl[v][e[1]])
    if 0 in se: se.remove(0)
    if len(se)==0: return 0
    if len(se)<len(short):
       short=copy(se)
       shortu=e[0]
       shortv=e[1]
   #if delete==[1,3,6,11]:
   for c in short:
     #if vect=="11211222\n" and delete==[0,0,0,6]:
     #if curpart==[[0, 1], [5, 4, 3, 2], []]: print short, shortv, shortu, e, len(n[shortu]), len(n[shortv]), n[shortu],n[shortv]
     fl[shortu][shortv]=c
     fl[shortv][shortu]=c
     i=edgelist.index([shortu,shortv])
     edgelist.pop(i)
     #print "recurse",degu,degv,shortu,shortv,short
     res=extend()
     #print "unrecurse"
     edgelist.insert(i,[shortu,shortv])
     fl[shortu][shortv]=0
     fl[shortv][shortu]=0
     if res: return 1
   return 0

def nextdelete():
 c=0
 while 1:
  if delete[c]<delete[c+1]-1:
   delete[c]=delete[c]+1
   break
  else:
   delete[c]=0
   c=c+1
   if c==len(delete)-1:
    delete[c]=delete[c]+1
    break
 if delete[c]==edgenumber+1: return 1
 return 0

def vecttolist(vect):
  vect=vect.strip()
  print vect
  #print list(vect)
  l=[[],[],[]]
  for i in range(len(vect)):
    l[int(vect[i])-1].append(i)
  l.sort()
  return l

if not mode: listcol=[]
while 1:
 n=deepcopy(norig)
 c=0
 edgelist=[]
 for x in range(len(n)):
  for y in copy(n[x]):
   #print x,y,n[x],n[y]
   if x<y and x<sizev and y<sizev:
    #print x,y,c in delete,n[x],n[y] 
    #c=-1
    if c in delete:
     n[y].remove(x)
     n[x].remove(y)
    else:
     #print edgelist,x,y
     edgelist.append([x,y])
    c=c+1
 singleton=0
 for x in n:
  if len(x)==1:
   singleton=1
   break
 if singleton:
  print "Singleton:", delete
  if nextdelete(): break
  continue
 #print n, delete
 #print len(badvectlist)
 curpart=[range(len(cutedges)),[],[]]
 while 1:
  #print vect
  if mode:
   c=0
   for e in cutedges:
    fl[e[0]][e[1]]=int(vect[c])
    fl[e[1]][e[0]]=(-int(vect[c]))%lam
    c=c+1
   badflow=extend()
   if badflow:
    print "Bad:", vect, delete
    break
  else:
   if isflow(curpart):
    #print curpart
    for y in range(len(curpart)):
     for x in curpart[y]:
      fl[cutedges[x][0]][cutedges[x][1]]=y+1
      fl[cutedges[x][1]][cutedges[x][0]]=y+1
    badflow=extend()
    if badflow:
      cp2=deepcopy(curpart)
      for p in cp2:
        p.sort()
      print cp2,","
      listcol.append(cp2)
    #if curpart==[[0, 1], [5, 2], [4, 3]]:  print "part", curpart
  #if badflow: print "Good:", vect
  if not nextpart(curpart,0,3): break
 if mode and not badflow:
  print "Good:", vect, delete
 if not mode: break
 if nextdelete(): break
if not mode:
 f=open("listcol",'w')
 pickle.dump(listcol,f)
 f.close()