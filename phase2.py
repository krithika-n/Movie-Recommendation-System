import tasks
import loadDatabase
import numpy
import lda
import lda.datasets
import gensim
PASSWORD='1234'
DATABASE_NAME='mwdb'
def task1_a(genre):
    con = loadDatabase.getOpenConnection('postgres', PASSWORD, DATABASE_NAME);
    finalMovieVector={}
    tags=loadDatabase.queryActioner(con, 'select distinct(tagid) from mltags')
    tagnames=loadDatabase.queryActioner(con,'select * from genometags')
    tag_tagnames={}
    for i in tagnames:
        tag_tagnames[i[0]]=i[1]
    movies=loadDatabase.queryActioner(con,'select distinct(movieid) from mlmovies where genre like \'%'+genre+'%\'')
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
    x=numpy.matrix.transpose(x)
    U, s, V = numpy.linalg.svd(x, full_matrices=True)
    latent_semantics=U[:,0:3]
    transpose=numpy.matrix.transpose(latent_semantics)
    finalString=[]
    for (key,topic) in enumerate(transpose):
        string='topic'+str(key)+'='
        tagscores={}
        sorted_tags=numpy.argsort(transpose[key])[::-1]
        for tag in sorted_tags:
            string+=tag_tagnames[tags[tag][0]]+'*'+str(transpose[key][tag])
        print string
        print '--------------'

def task1_b(genre,model):
    con = loadDatabase.getOpenConnection('postgres', PASSWORD, DATABASE_NAME);
    actornames=loadDatabase.queryActioner(con,'select * from actorinfo')
    actor_actornames={}
    for i in actornames:
        actor_actornames[i[0]]=i[1]
    movies=loadDatabase.queryActioner(con,'select distinct(movieid) from mlmovies where genre like \'%'+genre+'%\'')
    actors=loadDatabase.queryActioner(con,'select distinct(movieactor.actorid) from movieactor inner join mlmovies on (movieactor.movieid = mlmovies.movieid) where genre like \'%'+genre+'%\'')
    finalarray=[]
    if model==0 or model==1:
        for movie in movies:
            movieList=[]
            noOfActors=loadDatabase.queryActioner(con, 'select count(actorid) from movieactor where movieid ='+str(movie[0]))[0][0]
            for actor in actors:
                #print float((loadDatabase.queryActioner(con, 'select count(*) from mltags where tagid ='+str(tag[0])+' and movieid='+str(movie[0])))[0][0])
                idf=float(len(movies))/(loadDatabase.queryActioner(con, 'select count(distinct(movieid)) from movieactor where actorid ='+str(actor[0])))[0][0]
                movieList.append((float((loadDatabase.queryActioner(con, 'select count(*) from movieactor where actorid ='+str(actor[0])+' and movieid='+str(movie[0])))[0][0])/noOfActors)*idf)
            finalarray.append(movieList)
        x=numpy.array(finalarray)
        x=numpy.matrix.transpose(x)
        if model==1:
            x=numpy.cov(x)
        U, s, V = numpy.linalg.svd(x, full_matrices=True)
        latent_semantics=U[:,0:3]
        transpose=numpy.matrix.transpose(latent_semantics)
        for (key,topic) in enumerate(transpose):
            string='topic'+str(key)+'='
            sorted_actors=numpy.argsort(transpose[key])[::-1]
            for actor in sorted_actors:
                string+=actor_actornames[actors[actor][0]]+'*'+str(transpose[key][actor])
            print string
            print '--------------'
    if model==2:
        for movie in movies:
            movieList=[]
            for actor in actors:
                #print float((loadDatabase.queryActioner(con, 'select count(*) from mltags where tagid ='+str(tag[0])+' and movieid='+str(movie[0])))[0][0])
                #idf=float(len(movies))/(loadDatabase.queryActioner(con, 'select count(distinct(movieid)) from movieactor where actorid ='+str(actor[0])))[0][0]
                movieList.append(loadDatabase.queryActioner(con, 'select count(*) from movieactor where actorid ='+str(actor[0])+' and movieid='+str(movie[0]))[0][0])
            finalarray.append(movieList)
        #print (finalarray)
        x = numpy.array(finalarray)
        #x = numpy.matrix.transpose(x)
        model = lda.LDA(n_topics=4, n_iter=1, random_state=1)
        model.fit(x)
        topic_word = model.topic_word_
        string=''
        for key,topic in enumerate(topic_word):
            string=str([actor_actornames[actors[i][0]]for i in numpy.argsort(topic)[::-1]])
            print 'topic'+str(key)+string
        #print len(actors)
x=task1_b('Crime',2)

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
