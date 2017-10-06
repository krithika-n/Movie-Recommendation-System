import tasks
import loadDatabase
import numpy
PASSWORD='1234'
DATABASE_NAME='mwdb'
def task1_a(genre):
    con = loadDatabase.getOpenConnection('postgres', PASSWORD, DATABASE_NAME);
    finalMovieVector={}
    tags=loadDatabase.queryActioner(con, 'select distinct(tagid) from mltags')
    movies=loadDatabase.queryActioner(con,'select distinct(movieid) from mlmovies')
    count=0
    finalarray=[]
    for movie in movies:
        movieList=[]
        noOfTags=loadDatabase.queryActioner(con, 'select count(tagid) from mltags where movieid ='+str(movie[0]))[0][0]
        if noOfTags==0:
            finalarray.append([0.0 for tag in tags])
        else:
            for tag in tags:
                #print float((loadDatabase.queryActioner(con, 'select count(*) from mltags where tagid ='+str(tag[0])+' and movieid='+str(movie[0])))[0][0])
                idf=float(len(movies))/(loadDatabase.queryActioner(con, 'select count(distinct(movieid)) from mltags where tagid ='+str(tag[0])))[0][0]
                movieList.append((float((loadDatabase.queryActioner(con, 'select count(*) from mltags where tagid ='+str(tag[0])+' and movieid='+str(movie[0])))[0][0])/noOfTags)*idf)
            finalarray.append(movieList)
    x=numpy.array(finalarray)
    print numpy.nonzero(x)
    #for movie in finalMovieVector:

task1_a('Horror')
'''
    totalMovies=loadDatabase.queryActioner(con,'select * from mlmovies')
    # this block calculates tf for all the tags and maintains it in dictionary actualResult
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
    
'''