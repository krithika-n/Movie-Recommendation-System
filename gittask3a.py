import MySQLdb
import csv
import sys
import math
import datetime 
import time
import operator
import numpy 

from numpy import matrix
conn = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mwdb")
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

c.execute("SELECT count(distinct actorid) from movie_actor")
TotalNoOfActors = c.fetchone()[0]
#print(TotalNoOfActors)

k = 0
actorIndex = {}

for r in c.execute("SELECT distinct actorid from movie_actor"):
    actid = r[0]
    r11 = r[0]
    actorIndex[r11] = k
    k = k + 1
    Actorandtag[actid] = {}
    
    for r9 in c1.execute("SELECT distinct movieid from movie_actor where actorid = (%s)", (actid,)):
        movid = r9[0]
        #gets the count of all the tags associated with the movie
        c3.execute("SELECT distinct count(*) from mltags where movieid = (%s)", (movid,)) 
        ThisMovieAllTagCount = c3.fetchone()[0]
        #gets the rank of the actor in this movie
        c4.execute("SELECT actor_movie_rank from movie_actor where actorid = (%s) and movieid = (%s)", (actid, movid))
        ActorRank = c4.fetchone()[0]
        for r1 in c2.execute("SELECT distinct tagid from mltags where movieid = ?", (movid,) ):
            tag_id = r1[0]
            Taglist.append(tag_id)
            #Actorandtag.append(tagid)
            #gets the count of eacg tag in this movie
            c5.execute("SELECT distinct count(tagid) from mltags where tagid = (%s) and movieid = (%s)",(tag_id,movid) )
            ThisMovieThisTagCount = c5.fetchone()[0]
            #normalization of timestamp values associated with the tag
            c6.execute('SELECT min(strftime("%S", timst)) from mltags')
            mints = int(c6.fetchone()[0])
            c6.execute('SELECT max(strftime("%S", timst)) from mltags')
            maxts = int(c6.fetchone()[0])
            NormalizedTimeStampSum = 0
            for row3 in c4.execute('SELECT (strftime("%S", timst)) from mltags where tagid = (%s) ', (tag_id,)):
                timest = int(row3[0])
                timest = ((timest - mints) / (maxts - mints))
                NormalizedTimeStampSum = NormalizedTimeStampSum + timest

            #computes the tf value for this tag
            ThisTagTF = (ThisMovieThisTagCount * NormalizedTimeStampSum) / (ThisMovieAllTagCount * ActorRank)

            #gets the number of actors associated with the tag
            c5.execute("SELECT count(distinct actorid) from mltags inner join movie_actor on mltags.movieid = movie_actor.movieid where mltags.tagid = ?", (tag_id,))
            NoOfsActorThisTag = c5.fetchone()[0] #IDF Denominator

            #computes the idf value for this tag
            ThisTagIDF = math.log(TotalNoOfActors / NoOfsActorThisTag)

            #computes the tf idf value for this tag
            TFIDF = ThisTagTF * ThisTagIDF
            c6.execute("SELECT  distinct tag from genome where tagid = ? ", (tag_id,))
            TagName = c6.fetchone()[0]
            c6.execute("SELECT  distinct name from imdb_actor_info where actorid = ?",(actid,))
            Actname = c6.fetchone()[0]
            
            #Storing the actor and tag vector in the form of a nested dictionary
            Actorandtag[actid][tag_id] = TFIDF
            
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

#Computing dot product similarity
Simmatrix = numpy.matmul(A, Atrans)

#column-normalize the coactor-coactor matrix
    for i in range(Simmatrix.shape[1]):
        sum_column = numpy.sum((Simmatrix[:, i]))
        Simmatrix[:, i] /= sum_column


pers = {}
import networkx as nx
#creating a weighted graph
G = nx.DiGraph(Simmatrix.T)
gWeighted = nx.DiGraph()

for i, j  in G.edges:
    gWeighted.add_edge(i, j, weight = Simmatrix[i,j])

#getting the seed values from the command line arguments
seeds = []
for i in sys.argv:
    seeds.append(i) 

seeds.remove(sys.argv[0])

#calculation of pagerank
s1 = numpy.zeros((len(Simmatrix), 1))
p = numpy.zeros((len(Simmatrix), 1))
initialp = numpy.zeros((len(Simmatrix), 1))
initialp = p

for i in seeds:
    
    j = actorIndex[i]
    pers[j] = 1 / len(seeds)
    s1[j][0] = 1 / len(seeds)
    p[j][0] = 1

no_iter = 0
meanerror = 1    
beta = 0.85

while(meanerror > 0.00000005):
    term1 =  beta * numpy.matmul(Simmatrix, p)
    term2 = (1 - beta) * s1
    p = term1 + term2
    #calculate error between previous and current pagerank values
    diff = abs(p - initialp)
    meanerror = numpy.mean(diff)
    #set current pagerank scores as prevscore values
    initialp = p
    no_iter = no_iter + 1

print("Number of iterations -",no_iter)

#getting the indices with non-zero values
nodeswithValues = numpy.transpose((p).nonzero())

#forming a list of non zero nodes
nodelist = []
for i in nodeswithValues:
    nodelist.append(i[0])

nodeandvalues = {}
for i in nodelist:
    nodeandvalues[i] = p[i][0]

#sorting the list according to the page rank values
sorted_nodesvalues = sorted(nodeandvalues.items(), key=operator.itemgetter(1), reverse=True)   

#retrieving the corresponding actors 
relatedActorid = []

for i,i1 in sorted_nodesvalues:
    for j, j1 in actorIndex.items():
        if  j1 == i:
            relatedActorid.append(j)

for j in seeds:
    for i in relatedActorid:
        if i == j:
            relatedActorid.remove(i)

#displaying the actor names
for i in relatedActorid[:10]:
    c6.execute("SELECT  distinct name from imdb_actor_info where actorid = (%s)",(i,))
    Actname = c6.fetchone()[0]
    print(Actname)

conn.commit()
conn.close()
