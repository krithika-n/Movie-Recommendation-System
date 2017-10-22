import MySQLdb
from sklearn.cluster import KMeans
import numpy 
ls=3


#Connecting to the database
db = MySQLdb.connect(host="127.0.0.1", 
                      user="root", 
                      passwd="bavani", 
                      db="mwdProject") 

cursor = db.cursor()


#Retreiving all the actorids and the no of actors
q='select distinct actorId from imdbActorInfo'
size=cursor.execute(q);
actorid=cursor.fetchall();



CoactorMatrix=numpy.zeros((size, size))
#Creating a Coactor Coactor Matrix
for i,actorid_i in enumerate(actorid):
	for j,actorid_j in enumerate(actorid):
# i!=j because for same actor, value should be 0. 
		if (i!=j):
#Retrieving the count of movies acted by two actors		
			q1="select count(movieId) from movieActor where actorId="+str(actorid_i[0])+" union (select movieId from movieActor where actorid="+str(actorid_j[0])+")"
			cursor.execute(q1)
			CoactorMatrix[i,j]=float(cursor.fetchone()[0])
		

#print CoactorMatrix

#SVD from numpy
U, s, V = numpy.linalg.svd(CoactorMatrix, full_matrices=False)
sizeU=U.shape
latentSemantics=numpy.zeros((size,ls))

print U[:,0:3].shape

ls1=numpy.zeros((309,2))
ls2=numpy.zeros((309,2))
ls3=numpy.zeros((309,2))

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

