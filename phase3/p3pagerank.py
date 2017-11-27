import MySQLdb
import numpy as np
from operator import itemgetter
import math
import collections
import pandas as pd

def get_movie_tag():
    conn = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mwdb")
    cur=conn.cursor();
    movietag={}
    movies_with_tag={}
    #Get maximum timestamp
    cur.execute("select max(timestamp) from mltags;")
    max_time=cur.fetchone()[0]    
    conn.commit()

    #Get minimum timestamp
    cur.execute("select min(timestamp) from mltags;")
    min_time=cur.fetchone()[0]
    conn.commit()

    #For normalization
    time_denom=max_time-min_time;
    cur.execute("SELECT distinct movieid FROM mlmovies;")
    allmovies=cur.fetchall()
    cur.execute("SELECT count(distinct movieid) FROM mlmovies;")
    no_of_movies=cur.fetchone()[0]
    no_of_movies=20
    conn.commit()
    for m in allmovies:
        final_tfidf=0
        taglist=[]
        
        cur.execute("SELECT tagid FROM mltags WHERE movieid={}".format (m[0]))
        tags=cur.fetchall()
        taglist=[t[0] for t in tags]
        no_of_tags=len(taglist)
        counter=collections.Counter(taglist)
        movietag[m[0]] = {}
        for k,v in counter.items():
                final_tfidf=0
                norm_tim_sum=0
                #Get set of timestamps for this tag in this movie for time-weighted TF-IDF
                cur.execute("select timestamp from mltags where movieid={} and tagid={}".format(m[0],k))
                times=cur.fetchall()
                conn.commit()        
                #Normalize and add all timestamps of occurences of tag

                for tim in times:
                    norm_tim_sum+=((tim[0]-min_time)/time_denom)
                
                timestamps=norm_tim_sum
                cur.execute("SELECT count(distinct movieid) from mltags where tagid={}".format(k))
                movies_with_tag=int(cur.fetchone()[0])
                tfscore=v/no_of_tags
                idf=math.log((no_of_movies)/movies_with_tag)
                final_tfidf=tfscore*idf*timestamps
                
                movietag[m[0]][k]=final_tfidf
    A=pd.DataFrame(movietag).T.fillna(0)
    conn.close()
    
    return A

movietag={}
movie_name={}
seed = []
personal_dict = {}
movie_to_index={}
index_to_movie={}
timestamp={}
sortedtime={}

try:
    userid=31
    # connect to the database
    conn =  mysql.connector.connect(user='root',
                                   password='haha123',
                                   host='localhost',
                                   database='mwdb')

    # get the db cursor object to interact with db
    k=0
    
    cur = conn.cursor()
    
    #map movieid to movie name
    cur.execute(("SELECT movieid,moviename FROM mwdb.mlmovies;"))
    for row in cur.fetchall():
        id=row[0]
        name=row[1]
        movie_name[id]=name;
    #get the number of movies
    cur.execute(("SELECT distinct (tagid) FROM mwdb.mltags;"))
    res=cur.fetchall()
    no_tags=len(res)
    cur.execute(("SELECT distinct (movieid) FROM mwdb.movie_actor;"))
    
    for row in cur.fetchall():
        row_ele=row[0]
        movie_to_index[row_ele]=k
        index_to_movie[k]=row_ele
        k=k+1
    no_movies=k
    A=np.array((no_movies,no_tags),float) 
         #initialize numpy array
    np.set_printoptions(threshold=np.nan)

    A = get_movie_tag()
    
    Atrans = np.transpose(A)
    
    Simmatrix = np.matmul(A, Atrans)
    
    #column-normalize the similarity matrix
    for i in range(Simmatrix.shape[1]):
        sum_column = np.sum((Simmatrix[:, i]))
        if(sum_column!=0):
            Simmatrix[:, i] /= sum_column
            
    teleport = np.zeros((no_movies, 1))  # teleportation matrix
    prscore = np.zeros((no_movies, 1))  # matrix for pagerank scores
    print("Movies watched by user are:")
#    #construct a teleport and initial pagerank matrix from user input
    cur.execute("SELECT movieid FROM mwdb.mltags where userid={} union select movieid from mlratings where userid={}".format(userid,userid))
    for row in cur.fetchall():
        seed.append(row[0])
        print(movie_name[row[0]])
       
    for mov in seed:
         cur.execute("SELECT (timestamp)  FROM mwdb.mltags where movieid={} and userid={} union SELECT (timestamp)  FROM mwdb.mlratings where movieid={} and userid={} order by timestamp desc".format(mov,userid,mov,userid))
         timestamp[mov]=cur.fetchall()[0]
        
    #account for recency in movies     
    temp=1
    SeedLen=len(seed)
    Denom=sum(range(1,SeedLen+1))
    for k, v in sorted(timestamp.items(), key=itemgetter(1), reverse=False):  
        sortedtime[k]=temp/Denom
        temp=temp+1
    
    
    for mov in seed:
        key=mov
        
        prscore[movie_to_index[key]][0] = 1
        teleport[movie_to_index[key]][0] = sortedtime[k]
       
  #calculate pagerank with personalization

    mean_error = 1
    alpha = 0.85
    no_iter = 0
    prevscore = np.zeros((len(Simmatrix), 1)) 
    prevscore=prscore
    while (no_iter<1000):
        #calculate pagerank with rwr approach
        term1 = alpha * np.matmul(Simmatrix, prscore)
        term2 = (1 - alpha) * teleport
        prscore = term1 + term2
        #calculate error between previous and current pagerank values
        diff = abs(prscore - prevscore)
        mean_error = np.mean(diff)
        #set current pagerank scores as prevscore values
        prevscore=prscore
        no_iter = no_iter + 1

    print("\nNumber of iterations -",no_iter)

    #sort the pagerank scores and store the rank of the sorted values in sortlist
    sortlist = np.argsort(prscore, axis=0)

    #store (index,rank) values in a dictionary
    sortdict = {}
    k = 0
    for val in sortlist:
        sortdict[k] = val[0]
        k = k + 1

    #sort the dictionary and print the actors with the top 10 ppr values
    k = 0
    
    print("\nTop five movies recommended are:\n")
    for i in reversed(range(no_movies)):
        if (k >= 5):
            break
        else:
            movipos = [key for key, value in sortdict.items() if value == i]
            temp=index_to_movie[movipos[0]]
            if(temp not in seed):
                print(movie_name[temp])
                k = k + 1
    

except  MySQLdb.Error as e:
       print(e)