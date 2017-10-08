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


            
 

