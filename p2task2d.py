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
querySetOfTags="select TagId from genome"
countOfTags=cursor.execute(querySetOfTags)
setOfAllTags=cursor.fetchall()
    
    # gives set of all movies
querySetOfMovies="select movieid from mlmovies"
countOfMovies=cursor.execute(querySetOfMovies)
setOfAllMovies=cursor.fetchall()
    
    # gives set of all years
querySetOfRatings="select distinct rating from mlratings"
countOfRatings=cursor.execute(querySetOfRatings)
setOfAllRatings=cursor.fetchall()

tmrTensor=np.zeros((countOfTags,countOfMovies,countOfRatings))

for tag in setOfAllTags:
    for movie in setOfAllMovies:
        for rating in setOfAllRatings:
        
            queryCheck="select * from mlratings inner join mltags on mlratings.movieid=mltags.movieid where mlratings.movieid="+str(movie[0])+" and mltags.TagId="+str(tag[0])
            check=cursor.execute(queryCheck)
            queryFill="select avg(rating) from mlratings where movieid="+str(movie[0])
            #print queryFill
            cursor.execute(queryFill)
            avgRating=float(cursor.fetchone()[0])
            if check!=0 and avgRating<=rating:
                tmrTensor[setOfAllTags.index(tag),setOfAllMovies.index(movie),setOfAllRatings.index(rating)]=1
                
#print np.any(tmrTensor==1)

## perform CP decomposition on the 3D array
T = dtensor(tmrTensor)
P, fit, itr, exectimes = cp_als(T, 5,max_iter=10000, init='random')

#print P.lmbda
#Latent semantic in terms of actor
tls1=np.zeros((countOfTags,2))
tls2=np.zeros((countOfTags,2))
tls3=np.zeros((countOfTags,2))
tls4=np.zeros((countOfTags,2))
tls5=np.zeros((countOfTags,2))

tls1[:,1]=P.U[0][:,0]
tls2[:,1]=P.U[0][:,1]
tls3[:,1]=P.U[0][:,2]
tls4[:,1]=P.U[0][:,3]
tls5[:,1]=P.U[0][:,4]

for i in range(0,countOfTags):
    tagId=float(str(setOfAllTags[i]).translate(None,'(),\'L'))
    #print len(actorId[0])
    tls1[i][0]=tagId
    tls2[i][0]=tagId
    tls2[i][0]=tagId
    tls3[i][0]=tagId
    tls4[i][0]=tagId
    tls5[i][0]=tagId

#latent semantics of movie
mls1=np.zeros((countOfMovies,2))
mls2=np.zeros((countOfMovies,2))
mls3=np.zeros((countOfMovies,2))
mls4=np.zeros((countOfMovies,2))
mls5=np.zeros((countOfMovies,2))

mls1[:,1]=P.U[1][:,0]
mls2[:,1]=P.U[1][:,1]
mls3[:,1]=P.U[1][:,2]
mls4[:,1]=P.U[1][:,3]
mls5[:,1]=P.U[1][:,4]

for i in range(0,countOfMovies):
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

for i in range(0,countOfRatings):
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

print "Latent Semantic for Tag\n"
print tls1
print tls2
print tls3
print tls4
print tls5

print "Latent Semantic for Movie\n"
print mls1
print mls2
print mls3
print mls4
print mls5

print "Latent Semantic for Rating\n"
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

for i in range(0,countOfTags):
    if(kmeansTag.labels_[i]==0):
        tagLabel0[str(setOfAllTags[i]).translate(None,'(),\'L')]=1
    if(kmeansTag.labels_[i]==1):
        tagLabel1[str(setOfAllTags[i]).translate(None,'(),\'L')]=1
    if(kmeansTag.labels_[i]==2):
        tagLabel2[str(setOfAllTags[i]).translate(None,'(),\'L')]=1
    if(kmeansTag.labels_[i]==3):
        tagLabel3[str(setOfAllTags[i]).translate(None,'(),\'L')]=1
    if(kmeansTag.labels_[i]==4):
        tagLabel4[str(setOfAllTags[i]).translate(None,'(),\'L')]=1

print "group 0:\n"
for key,value in tagLabel0.items():
    if(value==1):
        print key
print "group 1:\n"
for key,value in tagLabel1.items():
    if(value==1):
        print key
print "group 2:\n"
for key,value in tagLabel2.items():
    if(value==1):
        print key
print "group 3:\n"
for key,value in tagLabel3.items():
    if(value==1):
        print key
print "group 4:\n"
for key,value in tagLabel4.items():
    if(value==1):
        print key

movieLabel0={}
movieLabel1={}
movieLabel2={}
movieLabel3={}
movieLabel4={}

for i in range(0,countOfMovies):
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
for key,value in movieLabel0.items():
    if(value==1):
        print key
print "group 2:\n"
for key,value in movieLabel0.items():
    if(value==1):
        print key
print "group 3:\n"
for key,value in movieLabel0.items():
    if(value==1):
        print key
print "group 4:\n"
for key,value in movieLabel0.items():
    if(value==1):
        print key

ratingLabel0={}
ratingLabel1={}
ratingLabel2={}
ratingLabel3={}
ratingLabel4={}

for i in range(0,countOfRatings):
    if(kmeansRating.labels_[i]==0):
        ratingLabel0[str(setOfAllRatings[i]).translate(None,'(),\'L')]=1
    if(kmeansRating.labels_[i]==1):
        ratingLabel1[str(setOfAllRatings[i]).translate(None,'(),\'L')]=1
    if(kmeansRating.labels_[i]==2):
        ratingLabel2[str(setOfAllRatings[i]).translate(None,'(),\'L')]=1
    if(kmeansRating.labels_[i]==3):
        ratingLabel3[str(setOfAllRatings[i]).translate(None,'(),\'L')]=1
    if(kmeansRating.labels_[i]==4):
        ratingLabel4[str(setOfAllRatings[i]).translate(None,'(),\'L')]=1

print "group 0:\n"
for key,value in ratingLabel0.items():
    if(value==1):
        print key
print "group 1:\n"
for key,value in ratingLabel1.items():
    if(value==1):
        print key
print "group 2:\n"
for key,value in ratingLabel2.items():
    if(value==1):
        print key
print "group 3:\n"
for key,value in ratingLabel3.items():
    if(value==1):
        print key
print "group 4:\n"
for key,value in ratingLabel0.items():
    if(value==1):
        print key