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

c.execute("SELECT count(distinct MovieID) from Movieactor")
TotalNoOfMovies = c.fetchone()[0]

Taglist = []
Movieandtag = {}
k = 0
movieIndex = {}


for r9 in c1.execute("SELECT distinct MovieID from Movieactor "):
    movid = r9[0]
    r11 = r9[0]
    movieIndex[r11] = k
    k = k + 1
    Movieandtag[movid] = {}

    
    #gets the count of all the tags associated with the movie
    c3.execute("SELECT distinct count(*) from Tags where MovieID = ?", (movid,)) 
    ThisMovieAllTagCount = c3.fetchone()[0]
    for r1 in c2.execute("SELECT distinct TagID from Tags where MovieID = ?", (movid,) ):
        tagid = r1[0]
        Taglist.append(tagid)
        
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
        ThisTagTF = (ThisMovieThisTagCount * NormalizedTimeStampSum) / (ThisMovieAllTagCount )

        #gets the number of movies associated with the tag
        c5.execute("SELECT count(distinct Movieactor.MovieID) from Tags inner join Movieactor on Tags.MovieID = Movieactor.MovieID where Tags.TagID = ?", (tagid,))
        NoOfsMoviesThisTag = c5.fetchone()[0] #IDF Denominator

        #computes the idf value for this tag
        ThisTagIDF = math.log(TotalNoOfMovies / NoOfsMoviesThisTag)

        #computes the tf idf value for this tag
        TFIDF = ThisTagTF * ThisTagIDF
        c6.execute("SELECT  distinct Tag from GenomeTags where TagID = ? ", (tagid,))
        TagName = c6.fetchone()[0]
        
            
            
        Movieandtag[movid][tagid] = TFIDF

def myprint(d):
    for key, value in d.items() :
        print ("Movie ID: " + str(key))
        for val, value1 in value.items():
            print("\tTagID:" + str(val))
            print("\tScore:" + str(value1))

       

#myprint(Movieandtag)      

from pandas import *
A = DataFrame(Movieandtag).T.fillna(0)


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
    j = int(i)
    k1 = movieIndex[j]
    
    s1[k1][0] = 1 / len(seeds)
    p[k1][0] = 1

    
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

    

relatedMovieid = []

for i,i1 in sorted_nodesvalues:
    for j, j1 in movieIndex.items():
        if  j1 == i:
            relatedMovieid.append(j)

for j in seeds:
    for i in relatedMovieid:
        if i == j:
            relatedMovieid.remove(i)

for i in relatedMovieid[:10]:
    c6.execute("SELECT  distinct Moviename from Movies where MovieID = ?",(i,))
    movname = c6.fetchone()[0]
    print(movname)
  

conn.commit()
conn.close()