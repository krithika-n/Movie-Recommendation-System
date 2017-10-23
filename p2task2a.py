import MySQLdb
import sys
import numpy as np
import networkx as nx
from sklearn.cluster import KMeans

one_row_in_array=[]
list_of_list=[]
no_actors_set=[]
ls=3

try:
    # connect to the database
    conn = MySQLdb.connect(host='127.0.0.1',
        user='root',
        passwd='haha123',
        db='mwdb')
    # get the db cursor object to interact with db
    cur = conn.cursor()
    numberofactors=cur.execute(("SELECT distinct (actorid) FROM movie_actor"))
    setOfAllActors=cur.fetchall()
    for row in setOfAllActors:
        row_ele=row[0]
        no_actors_set.append(row_ele)

    no_actors=len(no_actors_set)
    #print(no_actors)


    my_array2 = np.array([], float)
    np.set_printoptions(threshold=np.nan)

    for actorA in no_actors_set:
        for actorB in no_actors_set:
            if(actorB==actorA):
                entry=0.0
            else:
                cur.execute(("SELECT movieid FROM movie_actor where actorid={} and movieid in (select movieid from movie_actor where actorid={})".format(actorA,actorB)))
                res=cur.fetchall()
                entry=len(res)
            one_row_in_array.append(entry)
        list_of_list.append(one_row_in_array) #make a list of rows with each row being a list of all values in that row
        one_row_in_array=[]
    my_array2 = np.array(list_of_list) #stack rows in a vertical fashion

    #print(my_array2.shape)
except Exception as e: 
    print e

# my_array_2 is the actor-actor similarity matrix

# decomposing the actor similarity matrix using SVD
#SVD from numpy
U, s, V = np.linalg.svd(my_array2, full_matrices=False)
sizeU=U.shape
latentSemantics=np.zeros((no_actors,ls))

print U[:,0:3]

ls1=np.zeros((numberofactors,2))
ls2=np.zeros((numberofactors,2))
ls3=np.zeros((numberofactors,2))

ls1[:,1]=U[:,0]
ls2[:,1]=U[:,1]
ls3[:,1]=U[:,2]

for i in range(0,numberofactors):
    actorId=float(str(setOfAllActors[i]).translate(None,'(),\'L'))
    #print len(actorId[0])
    ls1[i][0]=actorId
    ls2[i][0]=actorId
    ls3[i][0]=actorId

ls1=ls1[ls1[:,1].argsort()[::-1]]
ls2=ls2[ls2[:,1].argsort()[::-1]]
ls3=ls3[ls3[:,1].argsort()[::-1]]

print ls1
print ls2
print ls3

kmeans = KMeans(n_clusters=3).fit(U[:,0:3])
print "Labels: "
label0={}
label1={}
label2={}

for i in range(0,numberofactors):
  if(kmeans.labels_[i]==0):
    label0[str(setOfAllActors[i]).translate(None,'(),\'L')]=1
  if(kmeans.labels_[i]==1):
    label1[str(setOfAllActors[i]).translate(None,'(),\'L')]=1
  if(kmeans.labels_[i]==2):
  	label2[str(setOfAllActors[i]).translate(None,'(),\'L')]=1

print "group 0:\n"
for key,value in label0.items():
    if(value==1):
        print key
print "group 1:\n"
for key,value in label1.items():
    if(value==1):
        print key
print "group 2:\n"
for key,value in label2.items():
    if(value==1):
        print key
