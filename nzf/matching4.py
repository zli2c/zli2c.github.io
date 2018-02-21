#Files written:
#primallp
#duallp
#primallpsetcols	Set colours to 0
#duallpsetcols		Set colours to free
#matrices		M matrix, rref, etc
#matrixkernel		Primal constraints for vector to be in span(M)
#varlist		Variable list (y,d,f,k)
#planarparts		Planar partitions (basic graphs)
#megavarlist		For drawing y,d,f variables
#ccomplement		Index of complement of listcol

from Numeric import *
from copy import deepcopy
from sys import *

if __name__ == '__main__':
 import sys
 n=6
 dontusechains=False
 dontusematrix=False
 writetofiles=True	#Otherwise, write everything to stdout
 cplexformat=False	#Otherwise, write in lp format (except for semi-colons)
 readlistcol=True	#Read list of colours from file "listcol"?
 planaronly=True	#Do we have planarity?

 for arg in sys.argv[1:]: 
  if arg=="-np" or arg=="--non-planar":
    print "Non-planar graph mode"
    planaronly=False
  elif arg=="-p" or arg=="--planar":
    print "Planar graph mode"
    planaronly=True
  elif arg=="-f" or arg=="--tofiles":
    print "Writing to files"
    writetofiles=True
  elif arg=="-o" or arg=="--tostdout":
    print "Writing to standard output"
    writetofiles=False
  elif arg=="-k" or arg=="--usechains":
    print "Using Kempe chains"
    dontusechains=False
  elif arg=="-nk" or arg=="--nochains":
    print "Not using Kempe chains"
    dontusechains=True
  elif arg=="-m" or arg=="--usematrix":
    print "Using matrix kernel constraints"
    dontusematrix=False
  elif arg=="-nm" or arg=="--nomatrix":
    print "Not using matrix kernel constraints"
    dontusematrix=True
  elif arg=="-r" or arg=="--readlistcol":
    print "Reading list of colours from file"
    readlistcol=True
  elif arg=="-h" or arg=="--hardcodedcol":
    print "Reading hard coded list of colours (empty list)"
    readlistcol=False
  elif arg=="-c" or arg=="--cplexformat":
    print "Writting in CPLEX (lp) format"
    cplexformat=True
  elif arg=="-l" or arg=="--lpformat":
    print "Writting in LP format"
    cplexformat=False
  elif arg.split("=")[0]=="-s" or arg.split("=")[0]=="--size":
    try:
      n=int(arg.split("=")[1])
      print "Setting size to", arg.split("=")[1]
    except:
      print "Error reading argument "+arg
  else:
    print "Error reading argument "+arg
    print "Argument "+arg+" is ignored" 

 if not writetofiles: f=stdout
 if cplexformat: lpeol="\n"
 else: lpeol=";\n"

 varlistd=[]
 varliste=[]
 varlistx=[]
 #ccount=0
 varlistprimm=[]
 varlistprimk=[]
 leadingones=[]

def nextsubset(subset,setsize):
 if len(subset)<1: return 0
 c=0
 while 1:
  if c==len(subset)-1:
   subset[c]=subset[c]+1
   break
  if subset[c]<subset[c+1]-1:
   subset[c]=subset[c]+1
   break
  else:
   subset[c]=c
   c=c+1
 if subset[c]==setsize: return 0
 return 1

def npm(n,cm):
  return nextpm(range(n),cm)

def nextpm(set,cm):
  if len(set)==0 or len(set)==1: return 0
  #print cm[0][0], set
  i=set.index(cm[0][0])
  j=set.index(cm[0][1])
  set.pop(j)
  set.pop(i)
  if nextpm(set,cm[1:]): return 1
  set.insert(i,cm[0][0])
  set.insert(j,cm[0][1])
  if j==len(set)-1:
    #if i==len(set)-2: return 0
    return 0
    i=i+1
    cm[0][0]=set[i]
  else:
    j=j+1
    cm[0][1]=set[j]
  set.pop(j)
  set.pop(i)
  #cm.append(firstpm(set)[0])
  firstpmcm(set,cm)
  set.insert(i,cm[0][0])
  set.insert(j,cm[0][1])
  return 1

def firstpmcm(set,cm):
  for x in range(len(set)/2):
    cm[x+1][0]=set[2*x]
    cm[x+1][1]=set[2*x+1]

def firstpm(set):
  cm=[]
  for x in range(len(set)/2):
    cm.append([set[2*x],set[2*x+1]])
  return cm

def nextpart(curpart,start,n):
  if (n==1): return 0
  if (nextpart(curpart,start+1,n-1)): return 1
  if (len(curpart[start])<=1): return 0
  compl=[]
  for x in curpart[start+1:]:
    compl=compl+x
  set=curpart[start]+compl
  set.sort()
  for x in set[1:]:
    if x in curpart[start]:
      curpart[start].remove(x)
      compl.append(x)
      break
    else:
      compl.remove(x)
      curpart[start].append(x)
  del curpart[start+1:]
  curpart.append(compl)
  for x in range(n-2):
    curpart.append([])
  return 1

def onlyeven(curpart):
  return isflow(curpart)
  #for x in curpart:
  #  if len(x)%2==1: return 0
  #return 1

def isflow(curpart):
  parity=len(curpart[0])%2
  for p in curpart:
    if len(p)%2!=parity: return 0
  return 1

def minorder(curpart):
  prev=-1
  for x in curpart:
   if len(x)>0:
    if min(x)>prev: prev=min(x)
    else: return 0
   else:
    prev=999
  return 1

def printconstraints(curpart):
    #for x in curpart:
    #  x.sort()
    #curpart.sort()
    for m in range(3):
      f.write(printprimk(curpart))
      set=[]
      for x in range(3):
        if x!=m: set=set+curpart[x]
      set.sort()
      pm=firstpm(set)
      while 1:
        #print "-m",pm,"m",
        if (planar(pm,n)): f.write("-"+printprimm(pm,spm(pm,curpart,m)))
        if not nextpm(set[:],pm): break
      f.write("<0"+lpeol)

    for m in range(3):
      set=[]
      for x in range(3):
        if x!=m: set=set+curpart[x]
      set.sort()
      pm=firstpm(set)
      while 1:
        #print "m",pm,spm(pm,curpart,m),"m","-x",curpart,"x","<0"
        if (planar(pm,n)): f.write(printprimm(pm,spm(pm,curpart,m))+"-"+printprimk(curpart)+"<0"+lpeol)
	if not nextpm(set[:],pm): break

def printdualconstraints1(curpart):
    #for x in curpart:
    #  x.sort()
    for m in range(3):
      f.write("+"+printdvar(curpart,m))
      set=[]
      for x in range(3):
        if x!=m: set=set+curpart[x]
      set.sort()
      pm=firstpm(set)
      while 1:
        if (planar(pm,n)): f.write("-"+printevar(curpart,pm,spm(pm,curpart,m)))
        if not nextpm(set[:],pm): break
    #print ">0"
    f.write("=0"+lpeol)
    #global ccount
    #print "-c",ccount,"=0"
    #ccount=ccount+1

def printdualconstraints2(pm,s,set,n):
    #build compliment compl
    compl=range(n)
    set.reverse()
    for i in set:
      compl.pop(i)
    set.reverse()
    s2=[1]*len(s)
    nonempty=False
    while 1:
      for m in range(3):
        curpart=[[],[],[]]
        curpart[m]=compl
        for i in range(len(s)):
          curpart[(m+s2[i])%3].append(pm[i][0])
          curpart[(m+s[i]*s2[i])%3].append(pm[i][1])
        #print pm,m,s,s2,curpart
        if onlyeven(curpart) and minorder(curpart):
          #for x in curpart:
          #  x.sort()
          f.write("-"+printdvar(curpart,m)+"+"+printevar(curpart,pm,s))
          nonempty=True
        curpart[(m+1)%3]=[]
        curpart[(m-1)%3]=[]
      if not nextbin(s2): break
    if (nonempty): f.write(">0"+lpeol)

def spm(pm,curpart,m):
  col=[]
  for x in range(3):
    if x!=m: col.append(curpart[x])
  s=[]
  for p in pm:
    if (p[0] in col[0]) ^ (p[1] in col[0]): s.append(-1)
    else: s.append(1)
  return s

def planar(pm,n):
  if not planaronly: return 1
  regions=[range(n)]
  for m in pm:
    #print " pm",pm,"m",m," Regions", regions
    for i in range(len(regions)):
      r=regions[i]
      if (m[0] in r) and (m[1] in r):
        r1=r.index(m[0])
	r2=r.index(m[1])
        if r1>r2: r1,r2=r2,r1
        regions.append(r[r1+1:r2])
        del r[r1:r2+1]
      else:
        if (m[0] in r) or (m[1] in r): return 0
  return 1

def nextbin(b):
  for i in range(len(b)):
    b[i]=-b[i]
    if b[i]==-1: return 1
  return 0

def printdvar(curpart,m):
  curpart2=deepcopy(curpart)
  for x in curpart2:
    x.sort()
  s=str(curpart2)+str(m)
  if s not in varlistd: varlistd.append(s)
  return "d"+str(varlistd.index(s))
  #return "d"+s+"d"

def printevar(curpart,pm,sign):
  curpart2=deepcopy(curpart)
  for x in curpart2:
    x.sort()
  s=str(curpart2)+str(pm)+str(sign)
  if s not in varliste: varliste.append(s)
  return "f"+str(varliste.index(s))
  #return "f"+s+"f"

def printxvar(curpart):
  curpart2=deepcopy(curpart)
  for x in curpart2:
    x.sort()
  s=str(curpart2)
  if s not in varlistx: varlistx.append(s)
  return "y"+str(varlistx.index(s))
  #return "y"+s+"y"

def printprimk(curpart):
  curpart2=deepcopy(curpart)
  for x in curpart2:
    x.sort()
  s=str(curpart2)
  if s not in varlistx: varlistx.append(s)
  return "k"+str(varlistx.index(s))
  #if s not in varlistprimk: varlistprimk.append(s)
  #return "k"+str(varlistprimk.index(s))
  #return "k"+s+"k"

def printprimm(pm,sign):
  s=str(pm)+str(sign)
  if s not in varlistprimm: varlistprimm.append(s)
  return "m"+str(varlistprimm.index(s))
  #return "m"+s+"m"

if __name__ == '__main__':
 elem=range(n)
 parts=[]
 planarparts=[]

def listpart(n):
  if len(elem)==1: return
  if len(elem)==0:
    ptmp=deepcopy(parts)
    ptmp.sort()
    planarparts.append(ptmp)
    return
  for i in range(2,n+1):
    for j in range(i-1):
      p=[]
      for k in range(i-1,j-1,-1):
        p.append(elem.pop(k))
      p.reverse()
      parts.append(p)
      #print "enter",j,i,p,elem,parts,n
      listpart(n-i+j)
      #print "exit",j,i,p,elem,parts,n
      parts.remove(p)
      for k in range(j,i):
        elem.insert(k,p[k-j])
      #print "exit",j,i,p,elem,parts

def allpartitions(part,set):
  if len(set)==0:
    #print part
    planarparts.append(deepcopy(part))
    return
  if len(set)==1: return
  for s in range(1,len(set)):
    sub=range(s)
    while 1:
      p=[]
      p.append(set.pop(0))
      sub.reverse()
      #print sub, set
      for i in sub: p.append(set.pop(i))
      p.reverse()
      #print "a",sub, set
      sub.reverse()
      part.append(p)
      allpartitions(part,set)
      del part[-1]
      #print "ret",sub, set,p
      for x in p: set.append(x)
      set.sort()
      #print "ret2",sub, set
      if not nextsubset(sub,len(set)-1): break


def M(part,col):
  numcol=[False]*len(col)
  for p in part:
    for e in p:
      for i in range(len(col)):
        if e in col[i]: numcol[i]=not numcol[i]
    b=numcol[0]
    #print p,col,numcol
    for i in range(len(col)):
      if b ^ numcol[i]: return 0
  return 1
  #return numnonempty(col)

def numnonempty(curpart):
  #print curpart
  count=len(curpart)
  num=1
  for x in curpart:
    if len(x)>0:
      num=num*count
      count=count-1
  return num

def rref(A):
  global leadingones
  B=identity(shape(A)[0],Float)
  for i in range(shape(A)[1]):
    nonzero=-1
    for j in range(shape(A)[0]):
     if A[j][i]!=0:
      leading=True
      for k in range(i):
        if A[j][k]!=0: leading=False
      if (leading):
       nonzero=j
       B[j]=(1/A[j][i])*B[j]
       A[j]=(1/A[j][i])*A[j]
       #print B
       leadingones.append(i)
       break
    if nonzero==-1: continue

    for j in range(shape(A)[0]):
     if A[j][i]!=0 and j!=nonzero:
        B[j]=B[j]-A[j][i]*B[nonzero]
        A[j]=A[j]-A[j][i]*A[nonzero]
        #print B
  return B

def rowsort(A):
  row=0
  for i in range(shape(A)[1]):
    numnonzero=0
    nzrow=-1
    for j in range(shape(A)[0]):
     if A[j][i]!=0: 
       numnonzero=numnonzero+1
       nzrow=j
    if numnonzero==1 and nzrow>=row:
      print "Swapping",row,"and",nzrow
      for j in range(shape(A)[1]):
        A[row][j],A[nzrow][j]=A[nzrow][j],A[row][j]
      row=row+1
  return

def oldmain():
 initset=[0,1,2,3]
 count=0
 while(nextsubset(initset,10)):
   count=count+1
   print initset
 print count
 n=4
 initpm=firstpm(range(n))
 print initpm
 #while(npm(n,initpm)):
 #  print initpm
 curpart=[range(n),[],[]]
 print "curpart", curpart
 while(nextpart(curpart,0,3)):
   if (onlyeven(curpart)): print "curpart", curpart

def matrices():
 global f
 if writetofiles: f=open('matrices','w')
 print "NEW MATRIX"
 MA=zeros([len(varlistx),len(planarparts)],Float)
 for i in range(len(varlistx)):
  curpart=[range(n),[],[]]
  while 1:
    if (onlyeven(curpart) and printxvar(curpart)=="y"+str(i)): 
     #for p in planarparts: print M(p,curpart),
     j=0
     for p in planarparts:
       MA[i][j]=M(p,curpart)
       j=j+1
     #print
    if not nextpart(curpart,0,3): break

 #print planarparts

 MA=transpose(MA)
 #print shape(array([-31, 11, 20, 0, 0, 0, 21, 3, -17, 7, -14, 0, -7, 7, 0, 0, 0, 14, -28, 4, -7, 17, 0, 24, -4, 0, -27, 0, 0, 0, 7]))
 f.write(str(shape(MA))+"\n")
 #MA[len(planarparts)]=array([-31, 11, 20, 0, 0, 0, 21, 3, -17, 7, -14, 0, -7, 7, 0, 0, 0, 14, -28, 4, -7, 17, 0, 24, -4, 0, -27, 0, 0, 0, 7])
 #MA[len(planarparts)]=array([1,1,0,0,0,0,1,1,1,0,0,0,0,0,0,1,1,0,0,0,1,1,1,0,0,1,1,0,1,1,0])
 #MA[len(planarparts)]=array([1,1,0,0,0,0,1,1,1,0,0,0,0,0,0,1,1,0,0,0,1,2,1,0,0,1,1,0,1,1,0])

 #vee=array([30,-8,0,0,-7,23,1,-17,-8,1,0,1,-6,1,1,2,1,-28,-1,12,1,15,1,-9,1,11,6,0,-5,-5,1])
 #vee=transpose(vee)
 #print shape(vee),shape(MA)
 #print dot(MA,vee)
 f.write(str(MA)+"\n")
 f.write("RREF\n")
 f.write(str(rref(MA))+"\n")
 f.write("MA IN RREF"+"\n")
 f.write(str(MA)+"\n")
 #f.write(str(transpose(MA))+"\n")
 f.write("MA_SWAPPED"+"\n")
 rowsort(MA)
 f.write("KERNEL CONSTRAINTS"+"\n")
 if writetofiles: f.close()
 printkernelconstraints(MA)
 #print "LINCOMB CONSTRAINTS"
 #printmatrixconstraints(MA)
 #print transpose(concatenate([MA,identity(shape(MA)[1])]))
 #print "Leading ones"
 #print leadingones
 #print dot(MA,vee)

#This says k must be in the kernel.
#def printkernelconstraints(A):
#  for j in range(shape(A)[0]):
#   for i in range(shape(A)[1]):
#    if i not in leadingones:
#      coeff=A[j][i]
#      if coeff>0: print "+"+str(coeff)+"t"+str(i),
#      if coeff<0: print str(coeff)+"t"+str(i),
#   print "-k"+str(leadingones[j])+"=0"
#  for i in range(shape(A)[1]):
#   if i not in leadingones:
#    print "t"+str(i)+"-k"+str(i)+"=0"
#  print "free",
#  for i in range(shape(A)[1]):
#   if i not in leadingones:
#    print "t"+str(i)+",",

def printkernelconstraints(A):
  global f
  if writetofiles: f=open('matrixkernel','w')
  for i in range(shape(A)[1]):
   for j in range(shape(A)[0]):
      coeff=A[j][i]
      if coeff>0: f.write("+"+str(coeff)+"t"+str(j))
      if coeff<0: f.write(str(coeff)+"t"+str(j))
   f.write("-k"+str(i)+"=0"+lpeol)
  if cplexformat:
   for j in range(shape(A)[0]):
    f.write("t"+str(j)+" free\n")
  else:
   f.write("free ")
   for j in range(shape(A)[0]):
    f.write("t"+str(j))
    if j<shape(A)[0]-1: f.write(",")
  f.write("\n")
  if writetofiles: f.close()

def printallvars():
 global f
 if writetofiles: f=open('varlist','w')
 f.write("YVARLIST and KVARLIST\n")
 for i in range(len(varlistx)):
   f.write(str(i)+" "+str(varlistx[i])+"\n")
 
 f.write("DVARLIST\n")
 for i in range(len(varlistd)):
   f.write(str(i)+" "+str(varlistd[i])+"\n")
 
 f.write("FVARLIST\n")
 for i in range(len(varliste)):
   f.write(str(i)+" "+str(varliste[i])+"\n")

 f.write("KVARLIST\n")
 for i in range(len(varlistx)):
   f.write(str(i)+" "+str(varlistx[i])+"\n")

 f.write("MVARLIST\n")
 for i in range(len(varlistprimm)):
   f.write(str(i)+" "+str(varlistprimm[i])+"\n")
 if writetofiles: f.close()

if __name__ == '__main__':
 print "PRIMAL"
 if writetofiles: f=open('primallp','w')
 curpart=[range(n),[],[]]
 printconstraints(curpart[:])
 while(nextpart(curpart,0,3)):
   if (onlyeven(curpart)): printconstraints(curpart[:])

 if planaronly: listpart(n)
 else: allpartitions([],range(n))
 planarparts.sort()
 last=planarparts[len(planarparts)-1]
 for i in range(len(planarparts)-2,-1,-1):
   if planarparts[i]==last: planarparts.pop(i)
   last=planarparts[i]

 if writetofiles: f=open('planarparts','w') 
 f.write(str(planarparts))
 if writetofiles: f.close()
 
 if writetofiles: f=open('duallp','w')
 print "KERNEL VECTOR"
 if cplexformat:
   f.write("max 0\n")
   f.write("s.t.\n")

 for p in planarparts:
   curpart=[range(n),[],[]]
   while 1:
     if (onlyeven(curpart)): 
       if M(p,curpart)>0: f.write("+"+str(M(p,curpart))+printxvar(curpart))
       #print
       #print "one-",curpart
     if not nextpart(curpart,0,3): break
   f.write("=0"+lpeol)
 if writetofiles: f.close()
 
 if writetofiles: f=open('duallp','a')
 print "DUAL 1"
 curpart=[range(n),[],[]]
 while 1:
   if (onlyeven(curpart)):
     f.write(printxvar(curpart))
     #print curpart,
     f.write("-c"+printxvar(curpart))
     printdualconstraints1(curpart[:])
   if not nextpart(curpart,0,3): break
 
 print "DUAL 2"
 for size in range(0,n+1,2):
   set=range(size)
   while 1:
     #print "set",set
     pm=firstpm(set)
     if planar(pm,n):
      while 1:
       if planar(pm,n): 
        s=[1]*len(pm)
        while 1:
          #print size,set,pm,s
          printdualconstraints2(pm,s,set,n)
          if not nextbin(s): break
       if not nextpm(set[:],pm): break
     if not nextsubset(set,n): break
 
 if dontusechains:
  for i in range(len(varlistd)):
    f.write("d"+str(i)+" = 0"+lpeol)

 if dontusematrix:
  for i in range(len(varlistx)):
    f.write("y"+str(i)+" = 0"+lpeol)

 if cplexformat:
  f.write("bounds\n")
  for i in range(len(varlistx)):
   f.write("y"+str(i)+" free\n")
 else:
  f.write("free ")
  for i in range(len(varlistx)):
   f.write("y"+str(i))
   if i<len(varlistx)-1: f.write(",")
  f.write(lpeol)

 if writetofiles: f.close()

 #Wrong (bad nextpart function) imp2
 #listcol=[[[0, 2, 4, 5, 6], [1], [3]] , [[0, 1, 3, 5, 6], [2], [4]] , [[0, 5, 6], [1, 3, 4], [2]] , [[0, 5, 6], [1, 2, 4], [3]] , [[0, 2, 6], [1, 3, 4], [5]] , [[0, 2, 6], [1], [3, 4, 5]] , [[0, 1, 6], [2, 3, 5], [4]] , [[0, 1, 6], [2, 3, 4], [5]] , [[0, 2, 3, 4, 5], [1], [6]] , [[0, 1, 2, 4, 5], [3], [6]] , [[0, 4, 5], [1, 2, 6], [3]] , [[0, 4, 5], [1, 2, 3], [6]] , [[0, 1, 2, 3, 5], [4], [6]] , [[0, 1, 5], [2, 3, 6], [4]] , [[0, 1, 5], [2, 3, 4], [6]] , [[0, 2, 4], [1, 5, 6], [3]] , [[0, 2, 4], [1, 3, 6], [5]] , [[0, 1, 4], [2, 3, 6], [5]] , [[0, 1, 4], [2, 3, 5], [6]] , [[0, 2, 3], [1, 5, 6], [4]] , [[0, 2, 3], [1], [4, 5, 6]] , [[0, 1, 3], [2, 4, 5], [6]] , [[0, 1, 3], [2], [4, 5, 6]] , [[0, 1, 2], [3, 5, 6], [4]] , [[0, 1, 2], [3], [4, 5, 6]]]

 #colours for imp after nextpart fix
 #listcol=[[[0,2,4,5],[1,3],[]],[[0,1,4,5],[2,3],[]],[[0,1,3,5],[2,4],[]],[[0,5],[1,3],[2,4]],[[0,5],[1,2],[3,4]],[[0,2,3,4],[1,5],[]],[[0,1,2,4],[3,5],[]],[[0,4],[1,2,3,5],[]],[[0,4],[1,2],[3,5]],[[0,1,2,3],[4,5],[]],[[0,2],[1,3,4,5],[]],[[0,2],[1,5],[3,4]],[[0,1],[2,3,4,5],[]],[[0,1],[2,3],[4,5]]]

 #Colour for imp2 after nextpart fix
 #listcol=[[[0,2,4,5,6],[1],[3]],[[0,1,3,5,6],[2],[4]],[[0,5,6],[1,3,4],[2]],[[0,5,6],[1,2,4],[3]],[[0,2,6],[1,3,4],[5]],[[0,2,6],[1],[3,4,5]],[[0,1,6],[2,3,5],[4]],[[0,1,6],[2,3,4],[5]],[[0,2,3,4,5],[1],[6]],[[0,1,2,4,5],[3],[6]],[[0,4,5],[1,2,6],[3]],[[0,4,5],[1,2,3],[6]],[[0,1,2,3,5],[4],[6]],[[0,1,5],[2,3,6],[4]],[[0,1,5],[2,3,4],[6]],[[0,2,4],[1,5,6],[3]],[[0,2,4],[1,3,6],[5]],[[0,1,4],[2,3,6],[5]],[[0,1,4],[2,3,5],[6]],[[0,2,3],[1,5,6],[4]],[[0,2,3],[1],[4,5,6]],[[0,1,3],[2,4,5],[6]],[[0,1,3],[2],[4,5,6]],[[0,1,2],[3,5,6],[4]],[[0,1,2],[3],[4,5,6]],[[0],[1,3,4,5,6],[2]],[[0],[1,2,4,5,6],[3]],[[0],[1,2,3,5,6],[4]],[[0],[1,3,6],[2,4,5]],[[0],[1,2,6],[3,4,5]],[[0],[1,2,4],[3,5,6]],[[0],[1,2,3],[4,5,6]]]

 #colour for line
 #listcol=[[[0,1,2,3,4,5],[],[]],[[0,3,4,5],[1,2],[]],[[0,1,4,5],[2,3],[]],[[0,2,3,5],[1,4],[]],[[0,5],[1,2,3,4],[]],[[0,5],[1,2],[3,4]],[[0,1,2,3],[4,5],[]],[[0,3],[1,2,4,5],[]],[[0,3],[1,5],[2,4]],[[0,2],[1,5],[3,4]],[[0,2],[1,4],[3,5]],[[0,1],[2,4],[3,5]],[[0,1],[2,3],[4,5]]]

 #colour for bd
 listcol=[[[0,2,4,5],[1,3],[]],[[0,1,4,5],[2,3],[]],[[0,2,3,5],[1,4],[]],[[0,1,2,5],[3,4],[]],[[0,5],[1,2,3,4],[]],[[0,5],[1,4],[2,3]],[[0,1,3,4],[2,5],[]],[[0,1,2,4],[3,5],[]],[[0,4],[1,2,3,5],[]],[[0,4],[1,2],[3,5]],[[0,3],[1,2,4,5],[]],[[0,3],[1,2],[4,5]],[[0,2],[1,3,4,5],[]],[[0,2],[1,3],[4,5]],[[0,1],[2,3,4,5],[]],[[0,1],[2,5],[3,4]]]

 listcol=[]
 if readlistcol: 
  fr=open("listcol",'r')
  listcol=pickle.load(fr)
  fr.close()
  #print listcol

 if writetofiles: f=open('duallpsetcols','w')
 if cplexformat:
  for x in listcol:
    f.write("cy"+str(varlistx.index(str(x)))+" free\n")
 else:
  f.write("free ")
  for x in listcol:
    f.write("cy"+str(varlistx.index(str(x))))
    if x!=listcol[-1]: f.write(",")
  f.write(lpeol)
 if writetofiles: f.close()

 if writetofiles: f=open('primallpsetcols','w')
 for x in listcol:
   f.write("k"+str(varlistx.index(str(x)))+"=0"+lpeol)
   #print "k"+str(varlistprimk.index(str(x)))+"=0"
 if writetofiles: f.close()

 if writetofiles: f=open('ccomplement','w')
 tmplist=range(len(varlistx))
 for x in listcol:
   tmplist.remove(varlistx.index(str(x)))
 for x in tmplist:
   f.write(str(x)+"\n")
 if writetofiles: f.close()

 #testfctn()

 printallvars()

 matrices()

 #Wrong soln triangle 1
 listf=[4,7,17,18,20,21,24,29,41,43,63,70,74,79,83,84,86,97,102,103,105,114,116,118,127,135,146,159,162,172,175,183,185,187,191,194,202,204,215]
 listd=[5,14,19,21,26,38,45,49,59,61,63,67,75,80,84,89]
 listy=[3,19,22,24,27,29,30]

 #Wrong soln triangle 2
 listy=[0,1,4,5,6,7,8,9,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,28,29,30,]
 listd=[5,14,38,88,]
 listf=[4,17,18,20,21,29,39,41,43,83,84,86,103,135,151,194]

 #Soln bd
 listy=[]
 listd=[1,5,17,27,31,35,47,49,56,62,65,74,75,87,92]
 listf=[8,17,20,21,25,26,29,33,35,49,50,52,58,62,66,70,72,75,78,94,102,111,122,126,131,143,172,185,187,189,198,201,203,207,211,213]

 #Soln wrong imp2 (bad nextpart)
 #listf=[8,9,14,15,16,32,35,37,45,46,48,49,50,52,53,54,71,74,75,78,80,82,94,96,144,145,147,162,163,164,175,195,207,228,238,240,244,245,247,249,251,253,264,266,269,271,275,276,280,281,283,285,293,298,299,304,315,318,321,322,327,333,336,346,350,362,365,367,390,405,416,428,430,433,454,456,458,465,477,481,489,496,508,509,521,525,528,542,544,571,575,586,588,598,602,615,630,634,644,646,651,659,663,666,670,677,687,689,717,719,725,737,743,746,751,752,753,754,755,757,758,759,761,762,763,764,772,775,776,777]
 #listd=[1,7,11,17,24,29,31,34,38,39,44,45,50,53,56,58,61,64,66,71,78,89,95,99,110,116,119,122,124,126,131,133,137,139,148,152,154,158,161,162,173,174,177,187,192,197,203,204,216,221]

 #listy=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,28,29,30]

 #listd=[1,5,17,27,31,35,47,49,56,62,63,74,75,87,92]
 #listf=[8,17,20,21,25,26,29,33,35,49,50,52,58,62,66,70,72,75,78,94,102,111,126,131,143,146,159,172,185,187,189,198,203,207,211,213]

 listf=[]
 listd=[]
 listy=[]

 if writetofiles: f=open('megavarlist','w')
 f.write("megalistf=[")
 for x in listf:
   f.write("["+str(varliste[x]).replace("]][","]],[")+"],")
 f.write("]\n")

 f.write("megalistd=[")
 for x in listd:
   f.write("["+str(varlistd[x]).replace("]]","]],")+"],")
 f.write("]\n")

 f.write("megalisty=[")
 for x in listy:
   f.write(str(varlistx[x])+",")
 f.write("]\n")
 if writetofiles: f.close()

 print "colourings"
 counter=0 
 curpart=[range(n),[],[]]
 while 1:
  if (onlyeven(curpart)): 
   counter=counter+1
   cp2=deepcopy(curpart)
   for x in cp2: x.sort()
   #print cp2
   #print curpart
  if not nextpart(curpart,0,3): break
 print counter

 #curpart=[[0,5,2,3],[4,1],[]]
 #nextpart(curpart,0,3)
 #print curpart
 #nextpart(curpart,0,3)
 #print curpart
