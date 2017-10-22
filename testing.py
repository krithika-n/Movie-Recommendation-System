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
        passwd='bavani',
        db='mwdProject')
    cursor = moviedb.cursor()
    # get the db cursor object to interact with db
    cur = conn.cursor()
    cur.execute(("SELECT distinct (actorId) FROM movieActor"))
    for row in cur.fetchall():
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
                cur.execute(("SELECT movieId FROM movieActor where actorId={} and movieId in (select movieId from movieActor where actorId={})".format(actorA,actorB)))
                res=cur.fetchall()
                entry=len(res)
            one_row_in_array.append(entry)
        list_of_list.append(one_row_in_array) #make a list of rows with each row being a list of all values in that row
        one_row_in_array=[]
    my_array2 = np.array(list_of_list) #stack rows in a vertical fashion

    #print(my_array2.shape)
except mysql.connector.Error as e:
    print(e.msg)

# my_array_2 is the actor-actor similarity matrix

# decomposing the actor similarity matrix using SVD
#SVD from numpy
U, s, V = np.linalg.svd(my_array2, full_matrices=False)
sizeU=U.shape
latentSemantics=np.zeros((no_actors,ls))

print U[:,0:3]

ls1=np.zeros((309,2))
ls2=np.zeros((309,2))
ls3=np.zeros((309,2))

ls1[:,1]=U[:,0]
ls2[:,1]=U[:,1]
ls3[:,1]=U[:,2]

for i in range(0,309):
    actorId=float(str(actorid[i]).translate(None,'(),\'L'))
    #print len(actorId[0])
    ls1[i][0]=actorId
    ls2[i][0]=actorId
    ls3[i][0]=actorId

ls1[ls1[:,1].argsort()[::-1]]
ls2[ls2[:,1].argsort()[::-1]]
ls3[ls3[:,1].argsort()[::-1]]

print ls1
print ls2
print ls3

kmeans = KMeans(n_clusters=5).fit(U)
print "Labels: ", kmeans.labels_


print kmeans.cluster_centers_