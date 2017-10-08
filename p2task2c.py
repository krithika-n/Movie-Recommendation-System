import sys
import numpy as np
import math
import MySQLdb
from sktensor import dtensor, cp_als

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
querySetOfActors="select actorId from imdbActorInfo"
countOfActors=cursor.execute(querySetOfActors)
setOfAllActors=cursor.fetchall()
    
    # gives set of all movies
querySetOfMovies="select movieId from mlmovies"
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
        
            queryFill="select * from movieActor inner join mlmovies on mlmovies.movieID=movieActor.movieId where mlmovies.movieID="+str(movie[0])+" and actorId="+str(actor[0])+" and year="+str(year[0])
            #print queryFill
            ans=cursor.execute(queryFill)
            if ans!=0:
                amyTensor[setOfAllActors.index(actor),setOfAllMovies.index(movie),setOfAllYears.index(year)]=1
            

## perform CP decomposition on the 3D array
T = dtensor(amyTensor)
P, fit, itr, exectimes = cp_als(T, 5,max_iter=10000)

#print P.lmbda
 

