import MySQLdb
from sklearn.cluster import KMeans
import numpy 
ls=3


#Connecting to the database
db = MySQLdb.connect(host="127.0.0.1", 
                      user="root", 
                      passwd="haha123", 
                      db="mwdb") 

cursor = db.cursor()


#Retreiving all the actorids and the no of actors
q='select distinct actorid from imdb_actor_info'
size=cursor.execute(q);
actorid=cursor.fetchall();

CoactorMatrix=numpy.zeros((size, size))
#Creating a Coactor Coactor Matrix
for i,actorid_i in enumerate(actorid):
	for j,actorid_j in enumerate(actorid):
# i!=j because for same actor, value should be 0. 
		if (i!=j):
#Retrieving the count of movies acted by two actors		
			q1="select count(movieid) from movie_actor where actorid="+str(actorid_i[0])+" union (select movieid from movie_actor where actorid="+str(actorid_j[0])+")"
			cursor.execute(q1)
			CoactorMatrix[i,j]=float(cursor.fetchone()[0])
		

#print CoactorMatrix

#SVD from numpy
U, s, V = numpy.linalg.svd(CoactorMatrix, full_matrices=False)

#print U[:,0:3].shape

ls1=numpy.zeros((size,2))
ls2=numpy.zeros((size,2))
ls3=numpy.zeros((size,2))

ls1[:,1]=U[:,0]
ls2[:,1]=U[:,1]
ls3[:,1]=U[:,2]

for i in range(0,size):
    actorId=float(str(actorid[i]).translate(None,'(),\'L'))
    #print actorId
    #print len(actorId[0])
    ls1[i][0]=actorId
    #print ls1[i][0]
    ls2[i][0]=actorId
    ls3[i][0]=actorId

ls1=ls1[ls1[:,1].argsort()[::-1]]
ls2=ls2[ls2[:,1].argsort()[::-1]]
ls3=ls3[ls3[:,1].argsort()[::-1]]

print "Latent Semantic 1:\n",ls1
print "Latent Semantic 2:\n",ls2
print "Latent Semantic 3:\n",ls3

kmeans = KMeans(n_clusters=3).fit(U[:,0:3])

print "Labels: "
label0={}
label1={}
label2={}

for i in range(0,size):
  if(kmeans.labels_[i]==0):
    label0[str(actorid[i]).translate(None,'(),\'L')]=1
    #print str(actorid[i]).translate(None,'(),\'L')
  if(kmeans.labels_[i]==1):
    label1[str(actorid[i]).translate(None,'(),\'L')]=1
  if(kmeans.labels_[i]==2):
    label2[str(actorid[i]).translate(None,'(),\'L')]=1
    
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