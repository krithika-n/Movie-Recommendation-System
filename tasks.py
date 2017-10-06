import loadDatabase
import operator
import sys
from datetime import datetime
import math
DATABASE_NAME='mwdb'
PASSWORD='1234'
'''
function: loadAllTables
TO load the data from phase1_dataset directory to database
@:parameter
username: the username for postgres
          default:postgres
password: password for postgres
          default:1234
'''
def loadAllTables(username='postgres',password='postgres'):
    print "creating database named"+DATABASE_NAME
    loadDatabase.createDB('postgres',PASSWORD,DATABASE_NAME)

    print "getting connection from database"+DATABASE_NAME
    con=loadDatabase.getOpenConnection('postgres',PASSWORD,DATABASE_NAME)

    '''print "loading table genomeTags in database"+DATABASE_NAME
    loadDatabase.loadtable('genomeTags','Phase2_data/genome-tags.csv',con,'(tagID INT,tag VARCHAR)','(tagID,tag)','(%s,%s)')
    print "data loaded into table mltags"

    print "loading table imdb-actor-info.csv from database"+DATABASE_NAME
    loadDatabase.loadtable('actorinfo','Phase2_data/imdb-actor-info.csv',con,'(actorId INT,actorname VARCHAR, gender VARCHAR)','(actorid,actorname,gender)','(%s,%s,%s)')
    print "data loaded into table actorinfo"

    print "loading table mlratings from database"+DATABASE_NAME
    loadDatabase.loadtable('mlratings','Phase2_data/mlratings.csv',con,'(movieid INT,userid INT,imdbid INT,rating INT,timestamp TIMESTAMP)','(movieid,userid,imdbid,rating,timestamp)','(%s,%s,%s,%s,%s)')
    print "data loaded into table mlratings"

    print "loading table mltags from database" + DATABASE_NAME
    loadDatabase.loadtable('mltags', 'Phase2_data/mltags.csv', con,
                           '(userid INT,movieid INT,tagid INT,timestamp TIMESTAMP)',
                           '(userid,movieid,tagid,timestamp)', '(%s,%s,%s,%s)')
    print "data loaded into table mltags"

    print "loading table mlusers from database" + DATABASE_NAME
    loadDatabase.loadtable('mlusers', 'Phase2_data/mlusers.csv', con,
                           '(userid INT)',
                           '(userid)', '(%s)')
    print "data loaded into table mlusers"

    print "loading table movieactor from database" + DATABASE_NAME
    loadDatabase.loadtable('movieactor', 'Phase2_data/movie-actor.csv', con,
                           '(movieid INT,actorid INT,actorrank INT)',
                           '(movieid,actorid,actorrank)', '(%s,%s,%s)')
    print "data loaded into table movieactor"'''

    print ("loading table mlmovies from database"+DATABASE_NAME)
    loadDatabase.loadtable('mlmovies', 'Phase2_data/mlmovies.csv', con,
                            '(movieid INT,moviename VARCHAR,year INT, genre VARCHAR)',
                            '(movieid,moviename,year,genre)', '(%s,%s,%s,%s)')
    print "data loaded into table mlmovies"
'''
@function: Function for task 1 , to find the tag vector for given actor
@:parameter
actorId: the id of the actor
model: 0 for tf, 1 for tf-idf
'''
def print_actor_vector(actorIdInput,model):
    if model>1 or model<0:
        print "please enter model value 0 or 1"
        exit()
    con = loadDatabase.getOpenConnection('postgres', PASSWORD, DATABASE_NAME)
    actualResult={}
    actorVector={}
    recentTag = loadDatabase.queryActioner(con, 'select timestamp from mltags order by timestamp desc')[0]#the most recent tag from database
    oldTag = loadDatabase.queryActioner(con, 'select timestamp from mltags order by timestamp asc')[0]#the oldest tag from database
    #converting to milliseconds
    recentTag = int(datetime.strptime(str(recentTag[0]), '%Y-%m-%d %H:%M:%S').strftime('%s'))
    oldTag = int(datetime.strptime(str(oldTag[0]), '%Y-%m-%d %H:%M:%S').strftime('%s'))
    actor = loadDatabase.queryActioner(con, 'select * from actorinfo where actorid='+str(actorIdInput))[0]
    noOfActors=loadDatabase.queryActioner(con,'select count(*) from actorinfo')
    movies=loadDatabase.queryActioner(con,'select * from movieactor where actorid='+str(actor[0]))
    actorFinalVectortf={}
    actorFinalVectoridf={}
    #this block calculates tf for all the tags and maintains it in dictionary actorVector
    for movie in movies:
        actorrank=loadDatabase.queryActioner(con,'select actorrank from movieactor where actorid='+str(actor[0])+'and movieid='+str(movie[0]))[0][0]
        totalcount=0
        actualResult[movie[0]]={}
        tags = loadDatabase.queryActioner(con, 'select * from mltags where movieid=' + str(movie[0]))
        for tag in tags:
            if(tag[2] in actualResult[movie[0]]):
                actualResult[movie[0]][tag[2]]=(actualResult[movie[0]][tag[2]][0]+1,actualResult[movie[0]][tag[2]][1]+(float(int(datetime.strptime(str(tag[3]),'%Y-%m-%d %H:%M:%S').strftime('%s')))-oldTag)/(recentTag-oldTag))
                totalcount+=1
            else:
                actualResult[movie[0]][tag[2]]=(1,float((int(datetime.strptime(str(tag[3]),'%Y-%m-%d %H:%M:%S').strftime('%s')))-oldTag)/(recentTag-oldTag))
                totalcount+=1
        for tag in actualResult[movie[0]].keys():
            if (tag in actorVector):
                actorVector[tag] = actorVector[tag] + (float(actualResult[movie[0]][tag][0]) / totalcount) *(float(1)/actorrank)*actualResult[movie[0]][tag][1]
            else:
                actorVector[tag] = (float(actualResult[movie[0]][tag][0] )/ totalcount) * (float(1)/actorrank) *(actualResult[movie[0]][tag][1])
    #this block calculates the idf for all the tags and multiplies with tf
    for tags in actorVector.keys():
        moviesForTags=loadDatabase.queryActioner(con,'select distinct(movieid) from mltags where tagid='+str(tags))
        tagname=loadDatabase.queryActioner(con,'select tag from genometags where tagid='+str(tags))
        string1=''
        for i in moviesForTags[:-1]:
            string1+=str(i[0])+' or movieid='
        string1+=str(moviesForTags[-1][0])
        actorsForTags=loadDatabase.queryActioner(con,'select distinct(actorid) from movieactor where movieid='+string1)
        idf=math.log(noOfActors[0][0]/(len(actorsForTags)))/math.log(2)
        actorFinalVectortf[tagname[0]]=actorVector[tags]
        actorFinalVectoridf[tagname[0]]=actorVector[tags]*idf
    #final sorting according to score
    if model==0:
        sorted_tf = sorted(actorFinalVectortf.items(), key=operator.itemgetter(1), reverse=True)
        print sorted_tf
    else:
        sorted_idf = sorted(actorFinalVectoridf.items(), key=operator.itemgetter(1), reverse=True)
        print sorted_idf


'''
@function: Function for task 2 , to find the tag vector for given genre
@:parameter
genre: the genre in string format
model: 0 for tf, 1 for tf-idf
'''

def print_genre_vector(genre,model):
    if model>1 or model<0:
        print "please enter model number 0 or 1"
        exit()
    con = loadDatabase.getOpenConnection('postgres', PASSWORD, DATABASE_NAME);
    actualResult = {}

    recentTag = loadDatabase.queryActioner(con, 'select timestamp from mltags order by timestamp desc')[0]#the most recent tag from database
    oldTag = loadDatabase.queryActioner(con, 'select timestamp from mltags order by timestamp asc')[0]#the oldest tag from database
    # converting to milliseconds
    recentTag = int(datetime.strptime(str(recentTag[0]), '%Y-%m-%d %H:%M:%S').strftime('%s'))
    oldTag = int(datetime.strptime(str(oldTag[0]), '%Y-%m-%d %H:%M:%S').strftime('%s'))
    movies = loadDatabase.queryActioner(con, 'select * from mlmovies where genre like \'%' + genre+'%\'')
    totalMovies=loadDatabase.queryActioner(con,'select * from mlmovies')
    noOfGenres={}
    finalGenreVectortf={}
    finalGenreVectoridf={}
    totalcount = 0
    # this block calculates tf for all the tags and maintains it in dictionary actualResult
    for movie in totalMovies:
        genres = loadDatabase.queryActioner(con, 'select genre from mlmovies where movieid=' + str(movie[0]))[0][0].split('|')
        for i in genres:
            noOfGenres[i]=True
    for movie in movies:
        tags = loadDatabase.queryActioner(con, 'select * from mltags where movieid=' + str(movie[0]))
        for tag in tags:
            if(tag[2] in actualResult):
                actualResult[tag[2]]=(actualResult[tag[2]][0]+1,actualResult[tag[2]][1]+(float(int(datetime.strptime(str(tag[3]),'%Y-%m-%d %H:%M:%S').strftime('%s')))-oldTag)/(recentTag-oldTag))
                totalcount+=1
            else:
                actualResult[tag[2]]=(1,float((int(datetime.strptime(str(tag[3]),'%Y-%m-%d %H:%M:%S').strftime('%s')))-oldTag)/(recentTag-oldTag))
                totalcount+=1

    # this block calculates the idf for all the tags and multiplies with tf
    for tag in actualResult.keys():
        noOfIndividualGenres = {}
        moviesForTags = loadDatabase.queryActioner(con, 'select distinct(movieid) from mltags where tagid=' + str(tag))
        tagname = loadDatabase.queryActioner(con, 'select tag from genometags where tagid=' + str(tag))
        string1 = ''
        for i in moviesForTags[:-1]:
            string1 += str(i[0]) + ' or movieid='
        string1 += str(moviesForTags[-1][0])
        genres= (loadDatabase.queryActioner(con,'select distinct(genre) from mlmovies where movieid=' + string1))
        for g in genres:
            for k in g[0].split('|'):
                noOfIndividualGenres[k]=True
        idf=math.log(len(noOfGenres.keys())/len(noOfIndividualGenres.keys()))/math.log(2)
        finalGenreVectortf[tagname[0]]=(float(actualResult[tag][0])/totalcount)*actualResult[tag][1]
        finalGenreVectoridf[tagname[0]]=(float(actualResult[tag][0])/totalcount)*actualResult[tag][1]*idf
    # final sorting according to score
    if model==0:
        sorted_tf = sorted(finalGenreVectortf.items(), key=operator.itemgetter(1), reverse=True)
        print sorted_tf
    else:
        sorted_idf=sorted(finalGenreVectoridf.items(), key=operator.itemgetter(1), reverse=True)
        print sorted_idf

'''
@function: Function for task 3 , to find the tag vector for given user
@:parameter
userId: the id of the user
model: 0 for tf, 1 for tf-idf
'''

def print_user_vector(userid,model):
    if model>1 or model<0:
        print "please enter model number 0 or 1"
        exit()
    con = loadDatabase.getOpenConnection('postgres', PASSWORD, DATABASE_NAME)
    actualResult = {}
    userVectortf = {}
    userVectoridf={}
    recentTag = loadDatabase.queryActioner(con, 'select timestamp from mltags order by timestamp desc')[0]#the most recent tag from database
    oldTag = loadDatabase.queryActioner(con, 'select timestamp from mltags order by timestamp asc')[0]#the oldest tag from database
    # converting to milliseconds
    recentTag = int(datetime.strptime(str(recentTag[0]), '%Y-%m-%d %H:%M:%S').strftime('%s'))
    oldTag = int(datetime.strptime(str(oldTag[0]), '%Y-%m-%d %H:%M:%S').strftime('%s'))
    tags = loadDatabase.queryActioner(con, 'select * from mltags where userid='+str(userid))
    noOfUsers=loadDatabase.queryActioner(con,'select count(*) from mlusers')
    totalcount=0
    # this block calculates tf for all the tags and maintains it in dictionary actorVector
    for tag in tags:
        if(tag[2] in actualResult):
            actualResult[tag[2]]=(actualResult[tag[2]][0]+1,actualResult[tag[2]][1]+(float(int(datetime.strptime(str(tag[3]),'%Y-%m-%d %H:%M:%S').strftime('%s')))-oldTag)/(recentTag-oldTag))
            totalcount+=1
        else:
            actualResult[tag[2]]=(1,float((int(datetime.strptime(str(tag[3]),'%Y-%m-%d %H:%M:%S').strftime('%s')))-oldTag)/(recentTag-oldTag))
            totalcount+=1
    # this block calculates the idf for all the tags and multiplies with tf
    for tag in actualResult.keys():
        tagname = loadDatabase.queryActioner(con, 'select tag from genometags where tagid=' + str(tag))
        usersForTags = len(loadDatabase.queryActioner(con, 'select distinct(userid) from mltags where tagid=' + str(tag)))
        idf=math.log(noOfUsers[0][0]/usersForTags)/math.log(2)
        userVectortf[tagname[0]] = (float(actualResult[tag][0]) / totalcount) * actualResult[tag][1]
        userVectoridf[tagname[0]]=(float(actualResult[tag][0])/totalcount)*actualResult[tag][1]*idf
    # final sorting according to score
    if model==0:
        sorted_tf = sorted(userVectortf.items(), key=operator.itemgetter(1), reverse=True)
        print sorted_tf
    else:
        sorted_idf = sorted(userVectoridf.items(), key=operator.itemgetter(1), reverse=True)
        print sorted_idf

'''
function
The main function for finding the genre difference which will call the subsequent functions according to module.
@:parameter
genre1,genre2: the genres
model: 0 for tf-idf-diff, 1 for pdiff1 , 2 for pdiff2
'''
def differentiate_genre(genre1,genre2,model):
    genre1=genre1.strip('\'')
    if model==0:
        differentiate_genre_tf_idf(genre1,genre2)
    elif model==1:
        differentiate_genre_pdiff1(genre1,genre2)
    elif model==2:
        differentiate_genre_pdiff2(genre1,genre2)
    else:
        print "invalid input , please enter within 0,1,2"


'''
function: function for calculating tf-idf-diff
@:parameter
genre1,genre2: the genres
'''
def differentiate_genre_tf_idf(genre1,genre2):
    con = loadDatabase.getOpenConnection('postgres', PASSWORD, DATABASE_NAME)
    noOfMoviesBothGenre=loadDatabase.queryActioner(con,'select distinct(movieid) from mlmovies where genre like \'%'+genre1+'%\' or genre like \'%'+genre2+'%\'')#total number of movies in both the genres
    totalTagsGenre1=loadDatabase.queryActioner(con,'select mltags.tagid from mlmovies inner join mltags on (mltags.movieid = mlmovies.movieid) where genre like \'%' + genre1 + '%\'')#tags in genre 1
    movieVector={}
    tags = loadDatabase.queryActioner(con, 'select distinct(mltags.tagid) from mlmovies inner join mltags on (mltags.movieid = mlmovies.movieid) where genre like \'%' + genre1 + '%\'')
    for tag in tags:
        tfnum=loadDatabase.queryActioner(con,'select mltags.tagid from mlmovies inner join mltags on (mltags.movieid = mlmovies.movieid) where genre like \'%' + genre1 + '%\' and tagid='+str(tag[0]))#Calculation of Numerator of TF
        tf=float(len(tfnum))/len(totalTagsGenre1)#tf cacluation
        idfden=loadDatabase.queryActioner(con,'select distinct(mltags.movieid) from mlmovies inner join mltags on (mltags.movieid = mlmovies.movieid) where genre like \'%' + genre1 +'%\' or genre like\'%'+genre2+'%\' and tagid='+str(tag[0]))#Calculation of denominator of IDF
        idf=float(len(noOfMoviesBothGenre))/len(idfden)#idf calculation
        tagname=loadDatabase.queryActioner(con, 'select tag from genometags where tagid=' + str(tag[0]))#selecting tags for getting tagname
        movieVector[tagname[0]]=tf*math.log(idf)
    sorted_x = sorted(movieVector.items(), key=operator.itemgetter(1), reverse=True)
    print sorted_x

'''
function: function for calculating pdiff-1
@:parameter
genre1,genre2: the genres
'''
def differentiate_genre_pdiff1(genre1,genre2):
    con = loadDatabase.getOpenConnection('postgres', PASSWORD, DATABASE_NAME)
    noOfMovies=loadDatabase.queryActioner(con,'select distinct(movieid) from mlmovies where genre like \'%'+genre1+'%\' or genre like \'%'+genre2+'%\'')#total number of movies in both the genres
    noOfMoviesGenre1=loadDatabase.queryActioner(con,'select distinct(movieid) from mlmovies where genre like  \'%'+genre1+'%\'')#movies in genre 1
    tags = loadDatabase.queryActioner(con, 'select distinct(mltags.tagid) from mlmovies inner join mltags on (mltags.movieid = mlmovies.movieid) where genre like \'%' + genre1 + '%\'')#tags from genre1
    rj={}
    mj={}
    finalVector={}
    for tag in tags:
        rj[tag[0]] = len(loadDatabase.queryActioner(con,'select distinct(mlmovies.movieid) from mlmovies inner join mltags on (mltags.movieid = mlmovies.movieid) where genre like\'%' + genre1 + '%\' and tagid=' + str(tag[0])))#calculating r1,j
        mj[tag[0]] = len(loadDatabase.queryActioner(con,'select distinct (mlmovies.movieid) from mlmovies inner join mltags on (mltags.movieid = mlmovies.movieid) where genre like \'%' + genre1 + '%\' or genre like \'%' + genre2 + '%\' and tagid=' + str(tag[0])))#calculating m1,j
        tagname = loadDatabase.queryActioner(con, 'select tag from genometags where tagid=' + str(tag[0]))#getting name of the tag
        firstTermnum = (float(rj[tag[0]]) / (len(noOfMoviesGenre1) - rj[tag[0]]))
        firstTermDenom = (float(mj[tag[0]] - rj[tag[0]]) / abs(len(noOfMovies) - mj[tag[0]] - len(noOfMoviesGenre1) + rj[tag[0]]))
        secondTerm = abs((float(rj[tag[0]]) / len(noOfMoviesGenre1)) - (float(mj[tag[0]] - rj[tag[0]]) / (len(noOfMovies) - len(noOfMoviesGenre1))))
        finalVector[tagname[0]] = (math.log(1+firstTermnum / firstTermDenom)) * secondTerm
    sorted_x = sorted(finalVector.items(), key=operator.itemgetter(1), reverse=True)#sorting finally
    print sorted_x

'''
function: function for calculating p-diff2
@:parameter
genre1,genre2: the genres
'''
def differentiate_genre_pdiff2(genre1,genre2):
    con = loadDatabase.getOpenConnection('postgres', PASSWORD, DATABASE_NAME)
    totalMovies=loadDatabase.queryActioner(con,'select distinct(movieid) from mlmovies where genre like\'%'+genre1+'%\''' or genre like\'%'+genre2+'%\'')#total number of movies
    totalMoviesGenre2=loadDatabase.queryActioner(con,'select distinct(movieid) from mlmovies where genre like\'%'+genre2+'%\'')#total number of movies in genre 2
    rj={}
    mj={}
    finalVector={}
    tags=loadDatabase.queryActioner(con,'select distinct(mltags.tagid) from mlmovies inner join mltags on (mltags.movieid = mlmovies.movieid) where genre like \'%'+genre1+'%\'')#getting tags from genre1
    for tag in tags:
        rj[tag[0]]=len(loadDatabase.queryActioner(con,'select distinct(mlmovies.movieid) from mlmovies inner join mltags on (mltags.movieid = mlmovies.movieid) where genre like\'%'+genre2+'%\' and tagid!='+str(tag[0])))
        mj[tag[0]]=len(loadDatabase.queryActioner(con,'select distinct (mlmovies.movieid) from mlmovies inner join mltags on (mltags.movieid = mlmovies.movieid) where genre like \'%'+genre1 +'%\' or genre like \'%'+ genre2+'%\' and tagid!='+str(tag[0])))
    for tag in rj.keys():
        tagname=loadDatabase.queryActioner(con, 'select tag from genometags where tagid=' + str(tag))#getting name of tag
        FirstTermnum=(float(rj[tag])/(len(totalMoviesGenre2)-rj[tag]))
        denominatorFirstTerm=(float(mj[tag]-rj[tag])/(len(totalMovies)-mj[tag]-len(totalMoviesGenre2)+rj[tag]))
        secondTerm=abs((float(rj[tag])/len(totalMoviesGenre2))-(float(mj[tag]-rj[tag])/(len(totalMovies)-len(totalMoviesGenre2))))
        finalVector[tagname[0]]=math.log(FirstTermnum/denominatorFirstTerm)*secondTerm
    sorted_x = sorted(finalVector.items(), key=operator.itemgetter(1), reverse=True)
    print sorted_x
