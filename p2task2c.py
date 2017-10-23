import sys
import numpy as np
import math
import MySQLdb
from sktensor import dtensor, cp_als
from sklearn.cluster import KMeans

#connect to database
try:
    moviedb = MySQLdb.connect(host='127.0.0.1',
        user='root',
        passwd='haha123',
        db='mwdb')
    cursor = moviedb.cursor()
    
except:
    print "Error Connecting to Database."
    exit()

#Create a 3 dimensional numpy array
    # gives set of all actors
querySetOfActors="select actorid from imdb_actor_info"
countOfActors=cursor.execute(querySetOfActors)
setOfAllActors=cursor.fetchall()
    
    # gives set of all movies
querySetOfMovies="select movieid from mlmovies"
countOfMovies=cursor.execute(querySetOfMovies)
setOfAllMovies=cursor.fetchall()
    
    # gives set of all years
querySetOfYears="select distinct year from mlmovies"
countOfYears=cursor.execute(querySetOfYears)
setOfAllYears=cursor.fetchall()
#print countOfActors,countOfMovies,countOfYears


amyTensor=np.zeros((countOfActors,countOfMovies,countOfYears))

for actor in setOfAllActors:
    for movie in setOfAllMovies:
        for year in setOfAllYears:
        
            queryFill="select * from movie_actor inner join mlmovies on mlmovies.movieid=movie_actor.movieid where mlmovies.movieid="+str(movie[0])+" and actorid="+str(actor[0])+" and year="+str(year[0])
            #print queryFill
            ans=cursor.execute(queryFill)
            if ans!=0:
                amyTensor[setOfAllActors.index(actor),setOfAllMovies.index(movie),setOfAllYears.index(year)]=1
            

## perform CP decomposition on the 3D array
T = dtensor(amyTensor)
P, fit, itr, exectimes = cp_als(T, 5,max_iter=10000, init='random')

print P.U[0].shape
print P.U[1].shape
print P.U[2].shape

#print P.lmbda

#Latent semantic in terms of actor
als1=np.zeros((309,2))
als2=np.zeros((309,2))
als3=np.zeros((309,2))
als4=np.zeros((309,2))
als5=np.zeros((309,2))

als1[:,1]=P.U[0][:,0]
als2[:,1]=P.U[0][:,1]
als3[:,1]=P.U[0][:,2]
als4[:,1]=P.U[0][:,3]
als5[:,1]=P.U[0][:,4]

for i in range(0,309):
    actorId=float(str(setOfAllActors[i]).translate(None,'(),\'L'))
    #print len(actorId[0])
    als1[i][0]=actorId
    als2[i][0]=actorId
    als2[i][0]=actorId
    als3[i][0]=actorId
    als4[i][0]=actorId
    als5[i][0]=actorId

#latent semantics of movie
mls1=np.zeros((86,2))
mls2=np.zeros((86,2))
mls3=np.zeros((86,2))
mls4=np.zeros((86,2))
mls5=np.zeros((86,2))

mls1[:,1]=P.U[1][:,0]
mls2[:,1]=P.U[1][:,1]
mls3[:,1]=P.U[1][:,2]
mls4[:,1]=P.U[1][:,3]
mls5[:,1]=P.U[1][:,4]

for i in range(0,86):
    movieId=float(str(setOfAllMovies[i]).translate(None,'(),\'L'))
    mls1[i][0]=movieId
    mls2[i][0]=movieId
    mls2[i][0]=movieId
    mls3[i][0]=movieId
    mls4[i][0]=movieId
    mls5[i][0]=movieId


#latent semantics of year
yls1=np.zeros((9,2))
yls2=np.zeros((9,2))
yls3=np.zeros((9,2))
yls4=np.zeros((9,2))
yls5=np.zeros((9,2))

yls1[:,1]=P.U[2][:,0]
yls2[:,1]=P.U[2][:,1]
yls3[:,1]=P.U[2][:,2]
yls4[:,1]=P.U[2][:,3]
yls5[:,1]=P.U[2][:,4]

for i in range(0,9):
    yearId=float(str(setOfAllYears[i]).translate(None,'(),\'L'))
    yls1[i][0]=yearId
    yls2[i][0]=yearId
    yls2[i][0]=yearId
    yls3[i][0]=yearId
    yls4[i][0]=yearId
    yls5[i][0]=yearId

#sorting the matrices in descending order
als1=als1[als1[:,1].argsort()[::-1]]
als2=als2[als2[:,1].argsort()[::-1]]
als3=als3[als3[:,1].argsort()[::-1]]
als4=als4[als4[:,1].argsort()[::-1]]
als5=als5[als5[:,1].argsort()[::-1]]

mls1=mls1[mls1[:,1].argsort()[::-1]]
mls1=mls2[mls2[:,1].argsort()[::-1]]
mls1=mls3[mls3[:,1].argsort()[::-1]]
mls1=mls4[mls4[:,1].argsort()[::-1]]
mls1=mls5[mls5[:,1].argsort()[::-1]]

yls1=yls1[yls1[:,1].argsort()[::-1]]
yls1=yls2[yls2[:,1].argsort()[::-1]]
yls1=yls3[yls3[:,1].argsort()[::-1]]
yls1=yls4[yls4[:,1].argsort()[::-1]]
yls1=yls5[yls5[:,1].argsort()[::-1]]

# top 5 latent semantics in descending order:
print "Latent Semantic for Year\n"
print yls1
print yls2
print yls3
print yls4
print yls5

print "Latent Semantic for Movie\n"
print mls1
print mls2
print mls3
print mls4
print mls5

print "Latent Semantic for Actor\n"
print als1
print als2
print als3
print als4
print als5

kmeansActor = KMeans(n_clusters=5).fit(P.U[0])
kmeansMovie = KMeans(n_clusters=5).fit(P.U[1])
kmeansYear = KMeans(n_clusters=5).fit(P.U[2])

print "Labels: "
actorLabel0={}
actorLabel1={}
actorLabel2={}
actorLabel3={}
actorLabel4={}

for i in range(0,309):
    if(kmeansActor.labels_[i]==0):
        actorLabel0[str(setOfAllActors[i]).translate(None,'(),\'L')]=1
    if(kmeansActor.labels_[i]==1):
        actorLabel1[str(setOfAllActors[i]).translate(None,'(),\'L')]=1
    if(kmeansActor.labels_[i]==2):
        actorLabel2[str(setOfAllActors[i]).translate(None,'(),\'L')]=1
    if(kmeansActor.labels_[i]==3):
        actorLabel3[str(setOfAllActors[i]).translate(None,'(),\'L')]=1
    if(kmeansActor.labels_[i]==4):
        actorLabel4[str(setOfAllActors[i]).translate(None,'(),\'L')]=1

print "group 0:\n"
for key,value in actorLabel0.items():
    if(value==1):
        print key
print "group 1:\n"
for key,value in actorLabel1.items():
    if(value==1):
        print key
print "group 2:\n"
for key,value in actorLabel2.items():
    if(value==1):
        print key
print "group 3:\n"
for key,value in actorLabel3.items():
    if(value==1):
        print key
print "group 4:\n"
for key,value in actorLabel4.items():
    if(value==1):
        print key
movieLabel0={}
movieLabel1={}
movieLabel2={}
movieLabel3={}
movieLabel4={}

for i in range(0,86):
    if(kmeansMovie.labels_[i]==0):
        movieLabel0[str(setOfAllMovies[i]).translate(None,'(),\'L')]=1
    if(kmeansMovie.labels_[i]==1):
        movieLabel1[str(setOfAllMovies[i]).translate(None,'(),\'L')]=1
    if(kmeansMovie.labels_[i]==2):
        movieLabel2[str(setOfAllMovies[i]).translate(None,'(),\'L')]=1
    if(kmeansMovie.labels_[i]==3):
        movieLabel3[str(setOfAllMovies[i]).translate(None,'(),\'L')]=1
    if(kmeansMovie.labels_[i]==4):
        movieLabel4[str(setOfAllMovies[i]).translate(None,'(),\'L')]=1

print "group 0:\n"
for key,value in movieLabel0.items():
    if(value==1):
        print key
print "group 1:\n"
for key,value in movieLabel1.items():
    if(value==1):
        print key
print "group 2:\n"
for key,value in movieLabel2.items():
    if(value==1):
        print key
print "group 3:\n"
for key,value in movieLabel3.items():
    if(value==1):
        print key
print "group 4:\n"
for key,value in movieLabel4.items():
    if(value==1):
        print key

yearLabel0={}
yearLabel1={}
yearLabel2={}
yearLabel3={}
yearLabel4={}

for i in range(0,9):
    if(kmeansYear.labels_[i]==0):
        yearLabel0[str(setOfAllYears[i]).translate(None,'(),\'L')]=1
    if(kmeansYear.labels_[i]==1):
        yearLabel1[str(setOfAllYears[i]).translate(None,'(),\'L')]=1
    if(kmeansYear.labels_[i]==2):
        yearLabel2[str(setOfAllYears[i]).translate(None,'(),\'L')]=1
    if(kmeansYear.labels_[i]==3):
        yearLabel3[str(setOfAllYears[i]).translate(None,'(),\'L')]=1
    if(kmeansYear.labels_[i]==4):
        yearLabel4[str(setOfAllYears[i]).translate(None,'(),\'L')]=1

print "group 0:\n"
for key,value in yearLabel0.items():
    if(value==1):
        print key
print "group 1:\n"
for key,value in yearLabel1.items():
    if(value==1):
        print key
print "group 2:\n"
for key,value in yearLabel2.items():
    if(value==1):
        print key
print "group 3:\n"
for key,value in yearLabel3.items():
    if(value==1):
        print key
print "group 4:\n"
for key,value in yearLabel4.items():
    if(value==1):
        print key