import numpy as np
import MySQLdb
from sktensor import cp_als,dtensor
from operator import itemgetter
from datetime import datetime

taglist = []
tag_cnt=0
movielist = []
movie_cnt=0
userlist = []
user_cnt=0
ans={}
movie={}
userid=80010

def build_tensor():
    # connect to the database
    conn = mysql.connector.connect(user='root',
                                   password='haha123',
                                   host='localhost',
                                   database='mwdb')

    # get the db cursor object to interact with db
    cur = conn.cursor()


    cur.execute("Select max(timestamp) from mltags")
    maxt = cur.fetchone()[0]
    cur.execute("Select min(timestamp) from mltags")
    mint = cur.fetchone()[0]
    mint2=mint
    denom = maxt - mint

    umtTensor = np.zeros((user_cnt, movie_cnt, tag_cnt))
    np.set_printoptions(threshold=np.nan)

    print(umtTensor.shape)
    for i in range(user_cnt):
        u = userlist[i]
        print(i,u)

        for j in range((movie_cnt)):
            m = movielist[j]

            for k in range(tag_cnt):
                t = taglist[k]

                cur.execute("select timestamp from mltags where userid={} and movieid={} and tagid={}".format(u, m, t))
                res = cur.fetchall()

                if (len(res) != 0):
                    for temp in res:
                        dt = temp[0]
                    weight = ((dt - mint2).total_seconds() / (denom.total_seconds()))
                    umtTensor[i, j, k] = 1 * weight

                else:
                    continue
    return (umtTensor)


try:
    # connect to the database
    conn = mysql.connector.connect(user='root',
                                   password='haha123',
                                   host='localhost',
                                   database='mwdb')

    # get the db cursor object to interact with db
    cur = conn.cursor()
    #taglist
    cur.execute("select distinct tagid from mltags ")
    res = cur.fetchall()
    for r in res:
        taglist.append(r[0])
    tag_cnt = len(taglist)
    if (tag_cnt > 50):
        tag_cnt = 50
    #movielist
    cur.execute("Select movieid from mltags where movieid in(Select movieid from mlmovies where year >= 2004)")
    res = cur.fetchall()
    for r in res:
        movielist.append(r[0])
    movie_cnt = len(movielist)
    if (movie_cnt > 75):
        movie_cnt = 75
    #userlist
    cur.execute("select distinct userid from mlusers where userid > 80000")
    res = cur.fetchall()
    for r in res:
        userlist.append(r[0])
    user_cnt=5

    np.set_printoptions(threshold=np.nan)
    A=build_tensor()
    np.save('umttensor',A)
    #A = np.load('umttensor2.npy')

    T=dtensor(A)
    P, fit, itr, exectimes = cp_als(T, 4, max_iter=10000, init='random')
    C = dtensor(P.toarray())

    index=userlist.index(userid)
    for j in range(movie_cnt):
        for k in range(tag_cnt):
            if(C[index,j,k]>0.0):
                ans[j]=C[index,j,k]


    # index-movie mapping
    for j in range(movie_cnt):
        movieid = movielist[j]
        cur.execute("Select moviename from mlmovies where movieid={}".format(movieid))
        name = cur.fetchone()[0]
        movie[j] = name
    #get user's previous movies
    resultset=[]
    print("Movies watched by user are:")
    cur.execute("select moviename from mlmovies where movieid in (Select movieid from mltags where userid={} order by timestamp)".format(userid))
    res=cur.fetchall()
    for r in res:
        resultset.append(r[0])
        print(r[0])

    #sort the results
    val=0
    print("\nTop recommended movies are:")
    for k, v in sorted(ans.items(), key=itemgetter(1), reverse=True):
        if(k in range(movie_cnt) and (movie[k] not in resultset) and val<5):
            print(movie[k])
            val=val+1

    if(val==0):
        for i in range(0,5):
            if(movie[2*i +2] not in resultset ):
                print(movie[2*i +2])


except MySQLdb.Error as e:
    print(e)