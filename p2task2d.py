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
        passwd='bavani',
        db='mwdProject')
    cursor = moviedb.cursor()
    
except:
    print "Error Connecting to Database."
    exit()

#Create a 3 dimensional numpy array
    # gives set of all actors
querySetOfTags="select tagId from genomeTags"
countOfTags=cursor.execute(querySetOfTags)
setOfAllTags=cursor.fetchall()
    
    # gives set of all movies
querySetOfMovies="select movieId from mlmovies"
countOfMovies=cursor.execute(querySetOfMovies)
setOfAllMovies=cursor.fetchall()
    
    # gives set of all years
querySetOfRatings="select distinct rating from mlratings"
countOfRatings=cursor.execute(querySetOfRatings)
setOfAllRatings=cursor.fetchall()
#print countOfActors,countOfMovies,countOfYears
tmrTensor=np.zeros((countOfTags,countOfMovies,countOfRatings))

for tag in setOfAllTags:
    for movie in setOfAllMovies:
        for rating in setOfAllRatings:
        
            queryCheck="select * from mlratings inner join mltags on mlratings.movieId=mltags.movieId where mlratings.movieId="+str(movie[0])+" and mltags.tagId="+str(tag[0])
            check=cursor.execute(queryCheck)
            queryFill="select avg(rating) from mlratings where movieId="+str(movie[0])
            #print queryFill
            cursor.execute(queryFill)
            avgRating=float(cursor.fetchone()[0])
            if check!=0 and avgRating<=rating:
                tmrTensor[setOfAllTags.index(tag),setOfAllMovies.index(movie),setOfAllRatings.index(rating)]=1
                
#print np.any(tmrTensor==1)

## perform CP decomposition on the 3D array
T = dtensor(tmrTensor)
P, fit, itr, exectimes = cp_als(T, 5,max_iter=10000, init='random')

print P.U[0].shape
print P.U[1].shape
print P.U[2].shape

#print P.lmbda
#Latent semantic in terms of actor
tls1=np.zeros((79,2))
tls2=np.zeros((79,2))
tls3=np.zeros((79,2))
tls4=np.zeros((79,2))
tls5=np.zeros((79,2))

tls1[:,1]=P.U[0][:,0]
tls2[:,1]=P.U[0][:,1]
tls3[:,1]=P.U[0][:,2]
tls4[:,1]=P.U[0][:,3]
tls5[:,1]=P.U[0][:,4]

for i in range(0,79):
    tagId=float(str(setOfAllTags[i]).translate(None,'(),\'L'))
    #print len(actorId[0])
    tls1[i][0]=tagId
    tls2[i][0]=tagId
    tls2[i][0]=tagId
    tls3[i][0]=tagId
    tls4[i][0]=tagId
    tls5[i][0]=tagId

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
rls1=np.zeros((5,2))
rls2=np.zeros((5,2))
rls3=np.zeros((5,2))
rls4=np.zeros((5,2))
rls5=np.zeros((5,2))

rls1[:,1]=P.U[2][:,0]
rls2[:,1]=P.U[2][:,1]
rls3[:,1]=P.U[2][:,2]
rls4[:,1]=P.U[2][:,3]
rls5[:,1]=P.U[2][:,4]

for i in range(0,5):
    rateId=float(str(setOfAllRatings[i]).translate(None,'(),\'L'))
    rls1[i][0]=rateId
    rls2[i][0]=rateId
    rls2[i][0]=rateId
    rls3[i][0]=rateId
    rls4[i][0]=rateId
    rls5[i][0]=rateId

#sorting the matrices in descending order
tls1=tls1[tls1[:,1].argsort()[::-1]]
tls2=tls2[tls2[:,1].argsort()[::-1]]
tls3=tls3[tls3[:,1].argsort()[::-1]]
tls4=tls4[tls4[:,1].argsort()[::-1]]
tls5=tls5[tls5[:,1].argsort()[::-1]]

mls1=mls1[mls1[:,1].argsort()[::-1]]
mls2=mls2[mls2[:,1].argsort()[::-1]]
mls3=mls3[mls3[:,1].argsort()[::-1]]
mls4=mls4[mls4[:,1].argsort()[::-1]]
mls5=mls5[mls5[:,1].argsort()[::-1]]

rls1=rls1[rls1[:,1].argsort()[::-1]]
rls2=rls2[rls2[:,1].argsort()[::-1]]
rls3=rls3[rls3[:,1].argsort()[::-1]]
rls4=rls4[rls4[:,1].argsort()[::-1]]
rls5=rls5[rls5[:,1].argsort()[::-1]]

# top 5 latent semantics in descending order:
print rls1
print rls2
print rls3
print rls4
print rls5



kmeansTag = KMeans(n_clusters=5).fit(P.U[0])
kmeansMovie = KMeans(n_clusters=5).fit(P.U[1])
kmeansRating = KMeans(n_clusters=5).fit(P.U[2])

print "Labels: "
tagLabel0={}
tagLabel1={}
tagLabel2={}
tagLabel3={}
tagLabel4={}

for i in range(0,309):
    if(kmeansTag.labels_[i]==0):
        tagLabel0[1]=str(setOfAllActors[i]).translate(None,'(),\'L')
    if(kmeansTag.labels_[i]==1):
        tagLabel1[1]=str(setOfAllActors[i]).translate(None,'(),\'L')
    if(kmeansTag.labels_[i]==2):
        tagLabel2[1]=str(setOfAllActors[i]).translate(None,'(),\'L')
    if(kmeansTag.labels_[i]==3):
        tagLabel3[1]=str(setOfAllActors[i]).translate(None,'(),\'L')
    if(kmeansTag.labels_[i]==4):
        tagLabel4[1]=str(setOfAllActors[i]).translate(None,'(),\'L')

print "group 0:\n", tagLabel0.get(1)
print "group 1:\n", tagLabel1.get(1)
print "group 2:\n", tagLabel2.get(1)
print "group 3:\n", tagLabel3.get(1)
print "group 4:\n", tagLabel4.get(1)

movieLabel0={}
movieLabel1={}
movieLabel2={}
movieLabel3={}
movieLabel4={}

for i in range(0,86):
    if(kmeansMovie.labels_[i]==0):
        movieLabel0[1]=str(setOfAllMovies[i]).translate(None,'(),\'L')
    if(kmeansMovie.labels_[i]==1):
        movieLabel1[1]=str(setOfAllMovies[i]).translate(None,'(),\'L')
    if(kmeansMovie.labels_[i]==2):
        movieLabel2[1]=str(setOfAllMovies[i]).translate(None,'(),\'L')
    if(kmeansMovie.labels_[i]==3):
        movieLabel3[1]=str(setOfAllMovies[i]).translate(None,'(),\'L')
    if(kmeansMovie.labels_[i]==4):
        movieLabel4[1]=str(setOfAllMovies[i]).translate(None,'(),\'L')

print "group 0:\n", movieLabel0.get(1)
print "group 1:\n", movieLabel1.get(1)
print "group 2:\n", movieLabel2.get(1)
print "group 3:\n", movieLabel3.get(1)
print "group 4:\n", movieLabel4.get(1)

ratingLabel0={}
ratingLabel1={}
ratingLabel2={}
ratingLabel3={}
ratingLabel4={}

for i in range(0,9):
    if(kmeansRating.labels_[i]==0):
        ratingLabel0[1]=str(setOfAllYears[i]).translate(None,'(),\'L')
    if(kmeansRating.labels_[i]==1):
        ratingLabel1[1]=str(setOfAllYears[i]).translate(None,'(),\'L')
    if(kmeansRating.labels_[i]==2):
        ratingLabel2[1]=str(setOfAllYears[i]).translate(None,'(),\'L')
    if(kmeansRating.labels_[i]==3):
        ratingLabel3[1]=str(setOfAllYears[i]).translate(None,'(),\'L')
    if(kmeansRating.labels_[i]==4):
        ratingLabel4[1]=str(setOfAllYears[i]).translate(None,'(),\'L')

print "group 0:\n", ratingLabel0.get(1)
print "group 1:\n", ratingLabel1.get(1)
print "group 2:\n", ratingLabel2.get(1)
print "group 3:\n", ratingLabel3.get(1)
print "group 4:\n", ratingLabel4.get(1)