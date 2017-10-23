import queryexecutioner
import numpy
import lda
import lda.datasets
import MySQLdb
import math
def task1_a(genre,model):
    try:
        con = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mwdb")
        tags=queryexecutioner.queryActioner(con, 'select distinct(tagid) from mltags')#collecting all the distinct tags from mltags
        tagnames=queryexecutioner.queryActioner(con,'select * from genome')
        tag_tagnames={}
        for i in tagnames:
            tag_tagnames[i[0]]=i[1]#maintaining a dictionary for tag to tagname reference
        movies=queryexecutioner.queryActioner(con,'select distinct(movieid) from mlmovies where genres like \'%'+genre+'%\'')#selecting all the movies with the particular genre
        finalarray=[]#this is the final movie to tag tf-idf score vector
        #
        #We are looping over each movies and making a movie to tag tf-idf score matrix.
        #if there are no tags for the movies then the score is zero.
        #
        if model=='1' or model=='0':
            for movie in movies:
                movieList=[]
                noOfTags=queryexecutioner.queryActioner(con, 'select count(tagid) from mltags where movieid ='+str(movie[0]))[0][0]
                if noOfTags==0:
                    finalarray.append([0.0 for tag in tags])
                else:
                    for tag in tags:
                        idf=float(len(movies))/(queryexecutioner.queryActioner(con, 'select count(distinct(movieid)) from mltags where tagid ='+str(tag[0])))[0][0]
                        movieList.append((float((queryexecutioner.queryActioner(con, 'select count(*) from mltags where tagid ='+str(tag[0])+' and movieid='+str(movie[0])))[0][0])/noOfTags)*math.log(idf))
                    finalarray.append(movieList)
            x=numpy.array(finalarray)
            print x.shape
            if model=='1':
                x=numpy.cov(numpy.matrix.transpose(x))#covariance of x
            print x.shape
            U, s, V = numpy.linalg.svd(x, full_matrices=False)
            print V.shape
            latent_semantics = V[0:4, :]
            print 'The top 4 latent semantics are'
            print latent_semantics
            for (key,topic) in enumerate(latent_semantics):
                print '/-----------------------------------/'
                print 'The topic is ' + str(key)
                print '/-----------------------------------/'
                sorted_tags=numpy.argsort(latent_semantics[key])[::-1]
                for tag in sorted_tags:
                    print tag_tagnames[tags[tag][0]]+'='+str(latent_semantics[key][tag])
        if model=='2':
            for movie in movies:
                movieList=[]
                for tag in tags:
                    movieList.append(queryexecutioner.queryActioner(con,'select count(*) from mltags where tagid='+str(tag[0])+' and movieid='+str(movie[0]))[0][0])
                finalarray.append(movieList)
            x=numpy.array(finalarray)
            model = lda.LDA(n_topics=4, n_iter=100, random_state=1)
            model.fit(x)
            topic_word = model.topic_word_
            print 'The top 4 latent topics are'
            print topic_word
            for key, topic in enumerate(topic_word):
                print '/-----------------------------------/'
                print 'The topic is '+str(key)
                print '/-----------------------------------/'
                for i in numpy.argsort(topic)[::-1]:
                    print tag_tagnames[tags[i][0]] + '=' + str(topic[i])
    except Exception as e:
        print e
def task1_b(genre,model):
    con = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mwdb")
    actornames=queryexecutioner.queryActioner(con,'select * from imdb_actor_info')
    actor_actornames={}
    for i in actornames:
        actor_actornames[i[0]]=i[1]
    movies=queryexecutioner.queryActioner(con,'select distinct(movieid) from mlmovies where genres like \'%'+genre+'%\'')
    actors=queryexecutioner.queryActioner(con,'select distinct(movie_actor.actorid) from movie_actor inner join mlmovies on (movie_actor.movieid = mlmovies.movieid) where genres like \'%'+genre+'%\'')
    finalarray=[]
    if model=='0' or model=='1':
        for movie in movies:
            movieList=[]
            noOfActors=queryexecutioner.queryActioner(con, 'select count(actorid) from movie_actor where movieid ='+str(movie[0]))[0][0]
            for actor in actors:
                idf=float(len(movies))/(queryexecutioner.queryActioner(con, 'select count(distinct(movieid)) from movie_actor where actorid ='+str(actor[0])))[0][0]
                movieList.append((float((queryexecutioner.queryActioner(con, 'select count(*) from movie_actor where actorid ='+str(actor[0])+' and movieid='+str(movie[0])))[0][0])/noOfActors)*math.log(idf))
            finalarray.append(movieList)
        x=numpy.array(finalarray)
        if model=='1':
            x=numpy.cov(numpy.matrix.transpose(x))
        U, s, V = numpy.linalg.svd(x, full_matrices=False)
        latent_semantics=V[0:4,:]
        print 'The top 4 latent semantics are'
        print latent_semantics
        for (key,topic) in enumerate(latent_semantics):
            print '/-----------------------------------/'
            print 'The topic is ' + str(key)
            print '/-----------------------------------/'
            sorted_actors=numpy.argsort(latent_semantics[key])[::-1]
            for actor in sorted_actors:
                print actor_actornames[actors[actor][0]]+'='+str(latent_semantics[key][actor])
    if model=='2':
        for movie in movies:
            movieList=[]
            for actor in actors:
                movieList.append(queryexecutioner.queryActioner(con, 'select count(*) from movie_actor where actorid ='+str(actor[0])+' and movieid='+str(movie[0]))[0][0])
            finalarray.append(movieList)
        x = numpy.array(finalarray)
        model = lda.LDA(n_topics=4, n_iter=100, random_state=1)
        model.fit(x)
        topic_word = model.topic_word_
        print topic_word
        for key,topic in enumerate(topic_word):
            print '/-----------------------------------/'
            print 'The topic is ' + str(key)
            print '/-----------------------------------/'
            for i in numpy.argsort(topic)[::-1]:
                print actor_actornames[actors[i][0]] + '=' + str(topic[i])

