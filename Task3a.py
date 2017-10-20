import sqlite3
import csv
import sys
import math
import datetime 
import time
import operator
import numpy 

from numpy import matrix
conn = sqlite3.connect('projphase2.db')
c = conn.cursor()
c1 = conn.cursor()
c2 = conn.cursor()
c3 = conn.cursor()
c4 = conn.cursor()
c5 = conn.cursor()
c6 = conn.cursor()
c7 = conn.cursor()
c8 = conn.cursor()


Taglist = []
Actorandtag = {}

c.execute("SELECT count(distinct ActorID) from Movieactor")
TotalNoOfActors = c.fetchone()[0]
#print(TotalNoOfActors)

k = 0
actorIndex = {}

for r in c.execute("SELECT distinct ActorID from Movieactor"):
    actid = r[0]
    r11 = r[0]
    actorIndex[r11] = k
    k = k + 1
    Actorandtag[actid] = {}
    
    for r9 in c1.execute("SELECT distinct MovieID from Movieactor where ActorID = ?", (actid,)):
        movid = r9[0]
        #gets the count of all the tags associated with the movie
        c3.execute("SELECT distinct count(*) from Tags where MovieID = ?", (movid,)) 
        ThisMovieAllTagCount = c3.fetchone()[0]
        #gets the rank of the actor in this movie
        c4.execute("SELECT Actormovierank from Movieactor where ActorID = ? and MovieID = ?", (actid, movid))
        ActorRank = c4.fetchone()[0]
        for r1 in c2.execute("SELECT distinct TagID from Tags where MovieID = ?", (movid,) ):
            tagid = r1[0]
            Taglist.append(tagid)
            #Actorandtag.append(tagid)
            #gets the count of eacg tag in this movie
            c5.execute("SELECT distinct count(TagID) from Tags where TagID = ? and MovieID = ?",(tagid,movid) )
            ThisMovieThisTagCount = c5.fetchone()[0]
            #normalization of timestamp values associated with the tag
            c6.execute('SELECT min(strftime("%S", tstamp)) from Tags')
            mints = int(c6.fetchone()[0])
            c6.execute('SELECT max(strftime("%S", tstamp)) from Tags')
            maxts = int(c6.fetchone()[0])
            NormalizedTimeStampSum = 0
            for row3 in c4.execute('SELECT (strftime("%S", tstamp)) from Tags where TagID = ? ', (tagid,)):
                timest = int(row3[0])
                timest = ((timest - mints) / (maxts - mints))
                NormalizedTimeStampSum = NormalizedTimeStampSum + timest

            #computes the tf value for this tag
            ThisTagTF = (ThisMovieThisTagCount * NormalizedTimeStampSum) / (ThisMovieAllTagCount * ActorRank)

            #gets the number of actors associated with the tag
            c5.execute("SELECT count(distinct ActorID) from Tags inner join Movieactor on Tags.MovieID = Movieactor.MovieID where Tags.TagID = ?", (tagid,))
            NoOfsActorThisTag = c5.fetchone()[0] #IDF Denominator

            #computes the idf value for this tag
            ThisTagIDF = math.log(TotalNoOfActors / NoOfsActorThisTag)

            #computes the tf idf value for this tag
            TFIDF = ThisTagTF * ThisTagIDF
            c6.execute("SELECT  distinct Tag from GenomeTags where TagID = ? ", (tagid,))
            TagName = c6.fetchone()[0]
            c6.execute("SELECT  distinct ActorName from ActorInfo where ActorID = ?",(actid,))
            Actname = c6.fetchone()[0]
            
            
            Actorandtag[actid][tagid] = TFIDF
            
def myprint(d):
    for key, value in d.items() :
        print ("Actor ID: " + key)
        for val, value1 in value.items():
            print("\tTagID:" + str(val))
            print("\tScore:" + str(value1))

       

#myprint(Actorandtag)  


from pandas import *
A = DataFrame(Actorandtag).T.fillna(0)

Atrans = numpy.transpose(A)


Simmatrix = numpy.matmul(A, Atrans)



pers = {}
import networkx as nx

G = nx.DiGraph(Simmatrix.T)
gWeighted = nx.DiGraph()

for i, j  in G.edges:
    gWeighted.add_edge(i, j, weight = Simmatrix[i,j])

seeds = []
for i in sys.argv:
    seeds.append(i) 

seeds.remove(sys.argv[0])

s1 = numpy.zeros((len(Simmatrix), 1))
p = numpy.zeros((len(Simmatrix), 1))
for i in seeds:
    
    j = actorIndex[i]
    pers[j] = 1 / len(seeds)
    s1[j][0] = 1 / len(seeds)
    p[j][0] = 1

    
beta = 0.85
term1 =  beta * numpy.matmul(Simmatrix, p)


term2 = (1 - beta) * s1

finalvector = term1 + term2

nodeswithValues = numpy.transpose((finalvector).nonzero())



nodelist = []
for i in nodeswithValues:
    nodelist.append(i[0])

nodeandvalues = {}
for i in nodelist:
    nodeandvalues[i] = finalvector[i][0]

sorted_nodesvalues = sorted(nodeandvalues.items(), key=operator.itemgetter(1), reverse=True)   

    

relatedActorid = []

for i,i1 in sorted_nodesvalues:
    for j, j1 in actorIndex.items():
        if  j1 == i:
            relatedActorid.append(j)

for j in seeds:
    for i in relatedActorid:
        if i == j:
            relatedActorid.remove(i)

for i in relatedActorid[:10]:
    c6.execute("SELECT  distinct ActorName from ActorInfo where ActorID = ?",(i,))
    Actname = c6.fetchone()[0]
    print(Actname)

conn.commit()
conn.close()
